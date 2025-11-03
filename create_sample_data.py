import os
import pandas as pd
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample CSV log files"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create data for last 3 days
    base_date = datetime.now().date()
    
    for days_ago in range(3):
        date = base_date - timedelta(days=days_ago)
        filename = f"data/ClientExecution_{date.strftime('%Y%m%d')}.csv"
        
        # Sample data
        data = {
            'Timestamp': [
                '09:30:15.048448', '10:15:22.123456', '11:30:45.789123',
                '14:20:33.456789', '15:45:12.987654', '16:10:05.111222'
            ],
            'ClientName': ['ABC', 'XYZ', 'DEF', 'ABC', 'GHI', 'XYZ'],
            'AccountName': ['ABC_account', 'XYZ_invest', 'DEF_trading', 
                           'ABC_account', 'GHI_fund', 'XYZ_invest'],
            'Instrument': ['0148.HK', '0148.HK', '0700.HK', 
                          '0148.HK', '0700.HK', '0148.HK'],
            'Quantity': [10000, 5000, 2000, 8000, 1500, 12000],
            'Price': [27.44, 27.50, 320.15, 27.60, 321.00, 27.55]
        }
        
        # Adjust prices slightly for different days
        price_adjust = days_ago * 0.1
        data['Price'] = [p + price_adjust for p in data['Price']]
        
        df = pd.DataFrame(data)
        df.to_csv(filename, sep=';', index=False)
        print(f"Created {filename}")

if __name__ == "__main__":
    create_sample_data()