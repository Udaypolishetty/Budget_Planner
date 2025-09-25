from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import numpy as np
import json
import os
import pickle
from datetime import datetime
from models.expense_predictor import ExpensePredictor
from models.income_predictor import IncomePredictor
from models.savings_predictor import SavingsPredictor
from models.budget_optimizer import BudgetOptimizer

app = Flask(__name__)
app.secret_key = 'budget_planner_secret_key'

# Initialize models
expense_predictor = ExpensePredictor()
income_predictor = IncomePredictor()
savings_predictor = SavingsPredictor()
budget_optimizer = BudgetOptimizer()

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Helper functions
def load_data():
    """Load user data from JSON file"""
    if not os.path.exists('data/user_data.json'):
        return {'expenses': [], 'income': [], 'savings': [], 'budget': {}}
    
    with open('data/user_data.json', 'r') as f:
        return json.load(f)

def save_data(data):
    """Save user data to JSON file"""
    with open('data/user_data.json', 'w') as f:
        json.dump(data, f)

# @app.route('/')
# def index():
#     """Home page"""
#     data = load_data()
    
#     # Calculate totals
#     total_income = sum(item['amount'] for item in data['income'])
#     total_expenses = sum(item['amount'] for item in data['expenses'])
#     total_savings = sum(item['amount'] for item in data['savings'])
    
#     # Get predictions
#     expense_prediction = expense_predictor.predict(data['expenses'])
#     income_prediction = income_predictor.predict(data['income'])
#     savings_prediction = savings_predictor.predict(data['savings'])
    
#     return render_template('index.html', 
#                           data=data,
#                           total_income=total_income,
#                           total_expenses=total_expenses,
#                           total_savings=total_savings,
#                           expense_prediction=expense_prediction,
#                           income_prediction=income_prediction,
#                           savings_prediction=savings_prediction)
@app.route('/')
def index():
    """Home page"""
    data = load_data()
    
    # Calculate totals
    total_income = sum(item['amount'] for item in data['income'])
    total_expenses = sum(item['amount'] for item in data['expenses'])
    total_savings = sum(item['amount'] for item in data['savings'])
    
    # Get predictions
    expense_prediction = expense_predictor.predict(data['expenses'])
    income_prediction = income_predictor.predict(data['income'])
    savings_prediction = savings_predictor.predict(data['savings'])
    
    # ✅ Calculate forecast total in Python
    # savings_forecast_total = sum(savings_prediction.six_month_forecast)
    # savings_forecast_total = sum(savings_prediction["six_month_forecast"])
    # six_month_forecast_total = sum(savings_prediction.six_month_forecast)
    six_month_forecast_total = sum(savings_prediction['six_month_forecast'])



    # return render_template('index.html', 
    #                       data=data,
    #                       total_income=total_income,
    #                       total_expenses=total_expenses,
    #                       total_savings=total_savings,
    #                       expense_prediction=expense_prediction,
    #                       income_prediction=income_prediction,
    #                       savings_prediction=savings_prediction,
    #                       savings_forecast_total=savings_forecast_total)
    return render_template('index.html',
                       data=data,
                       total_income=total_income,
                       total_expenses=total_expenses,
                       total_savings=total_savings,
                       expense_prediction=expense_prediction,
                       income_prediction=income_prediction,
                       savings_prediction=savings_prediction,
                       six_month_forecast_total=six_month_forecast_total)


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    """Add a new expense"""
    if request.method == 'POST':
        data = load_data()
        
        # Get form data
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        description = request.form.get('description')
        
        # Add new expense
        data['expenses'].append({
            'category': category,
            'amount': amount,
            'date': date,
            'description': description
        })
        
        save_data(data)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    """Add a new income entry"""
    if request.method == 'POST':
        data = load_data()
        
        # Get form data
        source = request.form.get('source')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        description = request.form.get('description')
        
        # Add new income
        data['income'].append({
            'source': source,
            'amount': amount,
            'date': date,
            'description': description
        })
        
        save_data(data)
        flash('Income added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_income.html')

@app.route('/add_savings', methods=['GET', 'POST'])
def add_savings():
    """Add a new savings entry"""
    if request.method == 'POST':
        data = load_data()
        
        # Get form data
        goal = request.form.get('goal')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        notes = request.form.get('notes')
        
        # Add new savings
        data['savings'].append({
            'goal': goal,
            'amount': amount,
            'date': date,
            'notes': notes
        })
        
        save_data(data)
        flash('Savings added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_savings.html')

@app.route('/create_budget', methods=['GET', 'POST'])
def create_budget():
    """Create or update budget"""
    data = load_data()
    
    if request.method == 'POST':
        # Get form data for each category
        housing = float(request.form.get('housing', 0))
        utilities = float(request.form.get('utilities', 0))
        food = float(request.form.get('food', 0))
        transportation = float(request.form.get('transportation', 0))
        entertainment = float(request.form.get('entertainment', 0))
        health = float(request.form.get('health', 0))
        education = float(request.form.get('education', 0))
        other = float(request.form.get('other', 0))
        
        # Update budget
        data['budget'] = {
            'housing': housing,
            'utilities': utilities,
            'food': food,
            'transportation': transportation,
            'entertainment': entertainment,
            'health': health,
            'education': education,
            'other': other
        }
        
        save_data(data)
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_budget.html', budget=data.get('budget', {}))

@app.route('/optimize_budget')
def optimize_budget():
    """Get optimized budget suggestions"""
    data = load_data()
    
    # Calculate current spending patterns
    expenses_df = pd.DataFrame(data['expenses'])
    if len(expenses_df) == 0:
        flash('Not enough expense data to optimize budget', 'warning')
        return redirect(url_for('index'))
    
    # Get optimized budget from ML model
    optimized_budget = budget_optimizer.optimize(
        data['expenses'], 
        data['income'], 
        data['budget']
    )
    
    return render_template('optimize_budget.html', 
                          current_budget=data.get('budget', {}),
                          optimized_budget=optimized_budget)

@app.route('/reports')
def reports():
    """Generate and display reports"""
    data = load_data()
    
    # Convert to DataFrame for analysis
    expenses_df = pd.DataFrame(data['expenses']) if data['expenses'] else pd.DataFrame()
    income_df = pd.DataFrame(data['income']) if data['income'] else pd.DataFrame()
    
    # Prepare report data
    report_data = {
        'expenses_by_category': {},
        'monthly_expenses': {},
        'income_by_source': {},
        'monthly_income': {},
        'savings_rate': 0
    }
    
    # Calculate expenses by category
    if not expenses_df.empty and 'category' in expenses_df.columns:
        report_data['expenses_by_category'] = expenses_df.groupby('category')['amount'].sum().to_dict()
    
    # Calculate income by source
    if not income_df.empty and 'source' in income_df.columns:
        report_data['income_by_source'] = income_df.groupby('source')['amount'].sum().to_dict()
    
    # Calculate total income and expenses
    total_income = sum(item['amount'] for item in data['income'])
    total_expenses = sum(item['amount'] for item in data['expenses'])
    
    # Calculate savings rate
    if total_income > 0:
        report_data['savings_rate'] = ((total_income - total_expenses) / total_income) * 100
    
    return render_template('reports.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
