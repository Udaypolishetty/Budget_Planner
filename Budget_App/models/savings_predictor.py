import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SavingsPredictor:
    """
    A model to predict future savings potential based on income and expense history
    """
    
    def __init__(self):
        """Initialize the savings predictor"""
        self.savings_rate = 0.1  # Default savings rate assumption if no data
    
    def calculate_monthly_savings(self, income_data, expense_data):
        """Calculate the average monthly savings based on income and expense data"""
        if not income_data or not expense_data:
            return 0
            
        # Convert to DataFrames
        income_df = pd.DataFrame(income_data)
        expense_df = pd.DataFrame(expense_data)
        
        # Verify needed columns exist
        if 'amount' not in income_df.columns or 'amount' not in expense_df.columns:
            return 0
            
        # Calculate totals
        total_income = income_df['amount'].sum()
        total_expenses = expense_df['amount'].sum()
        
        # Calculate savings
        total_savings = total_income - total_expenses
        
        # Calculate savings rate
        if total_income > 0:
            self.savings_rate = total_savings / total_income
        
        # If we have date information, calculate monthly average
        if 'date' in income_df.columns and len(income_df) > 0:
            try:
                # Convert to datetime
                income_df['date'] = pd.to_datetime(income_df['date'])
                
                # Get date range in months
                start_date = income_df['date'].min()
                end_date = income_df['date'].max()
                
                # Calculate number of months (minimum 1)
                months = max(1, (end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
                
                # Average monthly savings
                monthly_savings = total_savings / months
                return monthly_savings
            except:
                # If there's an error in the date calculation, use a simple approach
                return total_savings / max(1, len(income_data))
        else:
            # Without dates, just use the average over the number of records
            return total_savings / max(1, len(income_data))
    
    def predict(self, savings_data, income_data=None, expense_data=None):
        """
        Predict future savings potential
        
        Parameters:
        savings_data - list of savings records
        income_data - list of income records (optional)
        expense_data - list of expense records (optional)
        
        Returns a dictionary with next month prediction and 6-month forecast
        """
        # Start with historical savings data
        if savings_data and isinstance(savings_data, list) and len(savings_data) > 0:
            savings_df = pd.DataFrame(savings_data)
            if 'amount' in savings_df.columns:
                avg_monthly_savings = savings_df['amount'].mean()
            else:
                avg_monthly_savings = 0
        else:
            avg_monthly_savings = 0
            
        # If we have income and expense data, refine the prediction
        if income_data and expense_data:
            calculated_monthly_savings = self.calculate_monthly_savings(income_data, expense_data)
            
            # If we have both sources of information, use a weighted average
            if avg_monthly_savings > 0 and calculated_monthly_savings > 0:
                next_month_savings = (avg_monthly_savings + calculated_monthly_savings) / 2
            # Otherwise use whichever is positive
            else:
                next_month_savings = max(avg_monthly_savings, calculated_monthly_savings)
        else:
            next_month_savings = avg_monthly_savings
            
        # Generate 6-month forecast with slight growth assumption
        forecast = []
        growth_rate = 1.02  # Assume 2% growth month-to-month
        
        current_savings = next_month_savings
        for _ in range(6):
            forecast.append(current_savings)
            current_savings *= growth_rate
            
        # Return prediction results
        return {
            'next_month': next_month_savings,
            'six_month_forecast': forecast,
            'savings_rate': self.savings_rate * 100  # Convert to percentage
        }
