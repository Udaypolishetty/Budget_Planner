import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from datetime import datetime

class ExpensePredictor:
    """
    A simple ML model to predict future expenses based on historical data
    """
    
    def __init__(self):
        """Initialize the expense predictor model"""
        # Initialize model components
        self.model = LinearRegression()
        # Update the parameter name from 'sparse' to 'sparse_output'
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.is_trained = False
        
    def _prepare_data(self, expenses):
        """Prepare expense data for modeling"""
        if not expenses:
            return None, None
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(expenses)
        
        # Ensure required columns exist
        if 'category' not in df.columns or 'amount' not in df.columns or 'date' not in df.columns:
            return None, None
            
        # Convert date strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time-based features
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Prepare features
        X_cat = self.encoder.fit_transform(df[['category']])
        X_time = df[['month', 'day_of_week']].values
        X = np.hstack([X_cat, X_time])
        
        # Target variable
        y = df['amount'].values
        
        return X, y
    
    def train(self, expenses):
        """Train the expense prediction model"""
        X, y = self._prepare_data(expenses)
        
        if X is None or len(X) < 2:
            # Not enough data to train
            self.is_trained = False
            return False
            
        # Train the model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Save the training data categories for prediction
        df = pd.DataFrame(expenses)
        self.categories = df['category'].unique().tolist() if 'category' in df.columns else []
        
        return True
        
    def predict(self, expenses):
        """
        Predict next month's expenses based on historical data
        Returns a dictionary with total prediction and category breakdown
        """
        # Check if we have enough data
        if not expenses or len(expenses) < 3:
            return {
                'total': 0, 
                'categories': {
                    'housing': 0,
                    'utilities': 0,
                    'food': 0,
                    'transportation': 0,
                    'entertainment': 0,
                    'health': 0,
                    'education': 0,
                    'other': 0
                }
            }
        
        # Train the model if not already trained
        if not self.is_trained:
            self.train(expenses)
            
        # If training failed, return zeros
        if not self.is_trained:
            return {
                'total': 0,
                'categories': {cat: 0 for cat in ['housing', 'utilities', 'food', 'transportation', 
                                                'entertainment', 'health', 'education', 'other']}
            }
        
        # Analyze existing expenses to make predictions
        df = pd.DataFrame(expenses)
        
        # Default categories if none in data
        all_categories = ['housing', 'utilities', 'food', 'transportation', 
                          'entertainment', 'health', 'education', 'other']
                          
        # Get actual categories from data if available
        if 'category' in df.columns:
            categories = df['category'].unique().tolist()
            # Ensure all standard categories are included
            for cat in all_categories:
                if cat not in categories:
                    categories.append(cat)
        else:
            categories = all_categories
            
        # Get current month to predict for next month
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        
        # Make predictions for each category
        predictions = {}
        for category in categories:
            # Create feature vector for this category
            cat_encoded = self.encoder.transform([[category]])
            
            # For each day of the week
            category_pred = 0
            for day in range(7):
                X_pred = np.hstack([cat_encoded, [[next_month, day]]])
                pred = max(0, self.model.predict(X_pred)[0])  # Ensure no negative predictions
                category_pred += pred / 7  # Average across days
                
            predictions[category] = category_pred
            
        # Calculate total prediction
        total_prediction = sum(predictions.values())
        
        # Return results
        return {
            'total': total_prediction,
            'categories': predictions
        }
