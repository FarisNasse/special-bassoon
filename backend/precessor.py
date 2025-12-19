import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self):
        # Expandable keyword map
        self.categories = {
            'Groceries': ['kroger', 'whole foods', 'walmart', 'trader joes', 'safeway'],
            'Dining': ['mcdonalds', 'starbucks', 'uber eats', 'doordash', 'restaurant', 'cafe'],
            'Transport': ['uber', 'lyft', 'shell', 'bp', 'chevron', 'parking', 'amtrak'],
            'Utilities': ['att', 'verizon', 'pge', 'water', 'electric', 'internet'],
            'Subscriptions': ['netflix', 'spotify', 'hulu', 'apple', 'amazon prime'],
            'Income': ['payroll', 'deposit', 'transfer', 'zelle']
        }

    def normalize_columns(self, df):
        # Map various bank column names to a standard format
        df.columns = df.columns.str.lower()
        col_map = {
            'posted date': 'date', 'transaction date': 'date',
            'description': 'desc', 'payee': 'desc', 'merchant': 'desc',
            'debit': 'amount', 'amount': 'amount'
        }
        df = df.rename(columns=col_map)
        
        # Ensure we have 'date', 'desc', 'amount'
        required = ['date', 'desc', 'amount']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Clean amount (remove '$', convert to float)
        df['amount'] = df['amount'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
        
        # Make expenses positive for visualization, income negative (or filter out income)
        # Assuming typical bank CSV where debits are negative:
        df['amount'] = df['amount'].abs() 
        
        df['date'] = pd.to_datetime(df['date'])
        return df[required]

    def categorize(self, desc):
        desc = str(desc).lower()
        for category, keywords in self.categories.items():
            if any(k in desc for k in keywords):
                return category
        return 'Uncategorized'

    def process(self, filepath):
        df = pd.read_csv(filepath)
        df = self.normalize_columns(df)
        df['category'] = df['desc'].apply(self.categorize)
        
        # Extract Month-Year for grouping
        df['month'] = df['date'].dt.strftime('%Y-%m')
        return df

    def detect_anomalies(self, df):
        # Calculate monthly spending per category
        monthly = df.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
        
        anomalies = []
        if len(monthly) < 2:
            return ["Not enough data history for anomaly detection."]

        # Compare last month to the average of previous months
        last_month = monthly.iloc[-1]
        history = monthly.iloc[:-1]
        avg_history = history.mean()
        std_history = history.std()

        for cat in last_month.index:
            current_spend = last_month[cat]
            avg_spend = avg_history[cat]
            
            # Threshold: Spend > $50 AND (Spend > 3x Average OR Spend > Average + 2 Standard Deviations)
            if current_spend > 50 and current_spend > (avg_spend * 3):
                anomalies.append({
                    "category": cat,
                    "message": f"Spending on {cat} is {current_spend:.2f}, which is 300% higher than your average of {avg_spend:.2f}."
                })
        return anomalies