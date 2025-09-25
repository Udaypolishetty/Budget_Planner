import numpy as np
import pandas as pd

class BudgetOptimizer:
    """
    A model that optimizes budget allocations based on spending patterns and financial goals
    """
    
    def __init__(self):
        """Initialize the budget optimizer"""
        # Ideal budget allocation percentages based on common financial advice
        self.ideal_allocations = {
            'housing': 30,  # 30% of income
            'utilities': 10,
            'food': 15,
            'transportation': 10,
            'entertainment': 5,
            'health': 10,
            'education': 5,
            'other': 15
        }
        
        # Minimum allocations to ensure basic needs are met
        self.minimum_allocations = {
            'housing': 20,  # At least 20% of income for housing
            'utilities': 5,
            'food': 10,
            'transportation': 5,
            'health': 5,
            'education': 2,
            'entertainment': 2,
            'other': 5
        }
    
    def analyze_spending_patterns(self, expenses):
        """Analyze historical spending patterns"""
        if not expenses:
            return {}
            
        # Convert to DataFrame
        df = pd.DataFrame(expenses)
        
        # Ensure we have category and amount columns
        if 'category' not in df.columns or 'amount' not in df.columns:
            return {}
            
        # Calculate spending by category
        try:
            spending_by_category = df.groupby('category')['amount'].sum().to_dict()
            total_spending = sum(spending_by_category.values())
            
            # Calculate percentages
            spending_percentages = {}
            for category, amount in spending_by_category.items():
                if total_spending > 0:
                    spending_percentages[category] = (amount / total_spending) * 100
                else:
                    spending_percentages[category] = 0
                    
            return spending_percentages
        except:
            return {}
    
    def calculate_total_income(self, income):
        """Calculate total monthly income"""
        if not income:
            return 0
            
        # Convert to DataFrame
        df = pd.DataFrame(income)
        
        # Ensure we have the amount column
        if 'amount' not in df.columns:
            return 0
            
        # If we have date information, calculate monthly average
        if 'date' in df.columns and len(df) > 0:
            try:
                # Convert to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Extract month and year
                df['month_year'] = df['date'].dt.strftime('%Y-%m')
                
                # Get monthly averages
                monthly_income = df.groupby('month_year')['amount'].sum().mean()
                return monthly_income
            except:
                # If there's an error in the date calculation, use a simple average
                return df['amount'].sum() / max(1, len(df))
        else:
            # Without dates, just use the total
            return df['amount'].sum()
    
    def optimize(self, expenses, income, current_budget=None):
        """
        Optimize budget allocation based on spending patterns and income
        
        Parameters:
        expenses - list of expense records
        income - list of income records
        current_budget - current budget allocations (optional)
        
        Returns optimized budget allocations by category
        """
        # Get spending patterns
        spending_patterns = self.analyze_spending_patterns(expenses)
        
        # Calculate monthly income
        monthly_income = self.calculate_total_income(income)
        if monthly_income <= 0:
            # If we can't determine income, use total expenses as a baseline
            if expenses:
                df = pd.DataFrame(expenses)
                if 'amount' in df.columns:
                    monthly_income = df['amount'].sum()
                    
            # If still no income data, use a reasonable default
            if monthly_income <= 0:
                monthly_income = 50000  # Default assumption
        
        # Start with ideal allocations
        optimized_budget = {}
        for category, percentage in self.ideal_allocations.items():
            optimized_budget[category] = (percentage / 100) * monthly_income
            
        # Adjust based on spending patterns
        if spending_patterns:
            for category, percentage in spending_patterns.items():
                # Only consider categories in our standard list
                if category in optimized_budget:
                    # Calculate current spending in this category
                    current_spending = (percentage / 100) * monthly_income
                    
                    # If current spending is less than ideal, use current spending
                    if current_spending < optimized_budget[category]:
                        optimized_budget[category] = current_spending
                        
        # Ensure minimum allocations are met
        for category, min_percentage in self.minimum_allocations.items():
            min_amount = (min_percentage / 100) * monthly_income
            if category in optimized_budget and optimized_budget[category] < min_amount:
                optimized_budget[category] = min_amount
                
        # If we have a current budget, make gradual adjustments
        if current_budget:
            for category, amount in current_budget.items():
                if category in optimized_budget:
                    # Move 50% of the way from current to optimized (gradual change)
                    optimized_budget[category] = (amount + optimized_budget[category]) / 2
        
        # Round amounts to 2 decimal places
        for category in optimized_budget:
            optimized_budget[category] = round(optimized_budget[category], 2)
            
        return optimized_budget
