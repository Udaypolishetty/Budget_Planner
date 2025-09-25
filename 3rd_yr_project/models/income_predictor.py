import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from datetime import datetime

class IncomePredictor:
    """
    A simple ML model to predict future income based on historical data
    """
    
    def __init__(self):
        """Initialize the income predictor model"""
        # Initialize model components
        self.model = LinearRegression()
        # Update parameter name from 'sparse' to 'sparse_output'
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.is_trained = False
        
    def _prepare_data(self, income_data):
        """Prepare income data for modeling"""
        if not income_data:
            return None, None
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(income_data)
        
        # Ensure required columns exist
        if 'source' not in df.columns or 'amount' not in df.columns or 'date' not in df.columns:
            return None, None
            
        # Convert date strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time-based features
        df['month'] = df['date'].dt.month
        
        # Prepare features
        X_source = self.encoder.fit_transform(df[['source']])
        X_time = df[['month']].values
        X = np.hstack([X_source, X_time])
        
        # Target variable
        y = df['amount'].values
        
        return X, y
    
    def train(self, income_data):
        """Train the income prediction model"""
        X, y = self._prepare_data(income_data)
        
        if X is None or len(X) < 2:
            # Not enough data to train
            self.is_trained = False
            return False
            
        # Train the model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Save the training data sources for prediction
        df = pd.DataFrame(income_data)
        self.sources = df['source'].unique().tolist() if 'source' in df.columns else []
        
        return True
        
    def predict(self, income_data):
        """
        Predict next month's income based on historical data
        Returns a dictionary with total prediction and source breakdown
        """
        # Check if we have enough data
        if not income_data or len(income_data) < 2:
            return {'total': 0, 'sources': {}}
        
        # Train the model if not already trained
        if not self.is_trained:
            self.train(income_data)
            
        # If training failed, return zeros
        if not self.is_trained:
            return {'total': 0, 'sources': {}}
        
        # Analyze existing income to make predictions
        df = pd.DataFrame(income_data)
        
        # Get sources from data if available
        sources = df['source'].unique().tolist() if 'source' in df.columns else []
        if not sources:
            sources = ['salary', 'freelance', 'business', 'investments', 'rental', 'gifts', 'other']
            
        # Get current month to predict for next month
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        
        # Make predictions for each source
        predictions = {}
        for source in sources:
            # Create feature vector for this source
            source_encoded = self.encoder.transform([[source]])
            X_pred = np.hstack([source_encoded, [[next_month]]])
            
            # Make prediction and ensure no negative values
            pred = max(0, self.model.predict(X_pred)[0])
            predictions[source] = pred
            
        # Calculate total prediction
        total_prediction = sum(predictions.values())
        
        # For simple cases with consistent income, use average of past values
        if len(income_data) >= 2 and total_prediction == 0:
            amounts = [item['amount'] for item in income_data]
            total_prediction = sum(amounts) / len(amounts)
        
        # Return results
        return {
            'total': total_prediction,
            'sources': predictions
        }
