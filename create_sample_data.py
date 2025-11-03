import os
import pandas as pd
from datetime import datetime, timedelta
import random

def create_international_sample_data():
    """Create comprehensive sample CSV files with international stocks"""
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create data for the last 7 days to have more variety
    base_date = datetime.now().date()
    
    # International stock universe with realistic data
    international_stocks = [
        # Hong Kong
        {'code': '0148.HK', 'name': 'Kingboard Holdings', 'base_price': 27.50, 'volatility': 0.02},
        {'code': '0700.HK', 'name': 'Tencent Holdings', 'base_price': 320.00, 'volatility': 0.03},
        {'code': '0941.HK', 'name': 'China Mobile', 'base_price': 52.00, 'volatility': 0.015},
        
        # Korea - KOSPI
        {'code': '005930.KS', 'name': 'Samsung Electronics', 'base_price': 75000.00, 'volatility': 0.025},
        {'code': '000660.KS', 'name': 'SK Hynix', 'base_price': 120000.00, 'volatility': 0.035},
        {'code': '051910.KS', 'name': 'LG Chem', 'base_price': 450000.00, 'volatility': 0.028},
        
        # Korea - KOSDAQ
        {'code': '035420.KQ', 'name': 'NAVER', 'base_price': 180000.00, 'volatility': 0.032},
        {'code': '067280.KQ', 'name': 'Kakao', 'base_price': 42000.00, 'volatility': 0.040},
        
        # China - Shanghai
        {'code': '600036.SS', 'name': 'China Merchants Bank', 'base_price': 35.20, 'volatility': 0.018},
        {'code': '601318.SS', 'name': 'Ping An Insurance', 'base_price': 45.80, 'volatility': 0.022},
        {'code': '600519.SS', 'name': 'Kweichow Moutai', 'base_price': 1600.00, 'volatility': 0.020},
        
        # China - Shenzhen
        {'code': '000001.SZ', 'name': 'Ping An Bank', 'base_price': 12.50, 'volatility': 0.015},
        {'code': '000858.SZ', 'name': 'Wuliangye', 'base_price': 180.00, 'volatility': 0.025},
        {'code': '002415.SZ', 'name': 'Hikvision', 'base_price': 35.00, 'volatility': 0.020},
        
        # Japan
        {'code': '7203.T', 'name': 'Toyota Motor', 'base_price': 2500.00, 'volatility': 0.016},
        {'code': '9984.TO', 'name': 'SoftBank Group', 'base_price': 6500.00, 'volatility': 0.030},
        {'code': '6758.T', 'name': 'Sony Group', 'base_price': 12000.00, 'volatility': 0.022},
        
        # Australia
        {'code': 'BHP.AX', 'name': 'BHP Group', 'base_price': 45.50, 'volatility': 0.020},
        {'code': 'CBA.AX', 'name': 'Commonwealth Bank', 'base_price': 85.00, 'volatility': 0.015},
        {'code': 'CSL.AX', 'name': 'CSL Limited', 'base_price': 260.00, 'volatility': 0.018},
        
        # Thailand
        {'code': 'PTT.BK', 'name': 'PTT PCL', 'base_price': 35.00, 'volatility': 0.012},
        {'code': 'AOT.BK', 'name': 'Airports of Thailand', 'base_price': 60.00, 'volatility': 0.025},
        
        # Malaysia
        {'code': 'MAYBANK.KL', 'name': 'Malayan Banking', 'base_price': 8.50, 'volatility': 0.010},
        {'code': 'TENAGA.KL', 'name': 'Tenaga Nasional', 'base_price': 9.20, 'volatility': 0.008},
        
        # India
        {'code': 'RELIANCE.NS', 'name': 'Reliance Industries', 'base_price': 2400.00, 'volatility': 0.018},
        {'code': 'AIRTEL.NS', 'name': 'Bharti Airtel', 'base_price': 850.00, 'volatility': 0.022},
        {'code': 'TCS.NS', 'name': 'Tata Consultancy', 'base_price': 3200.00, 'volatility': 0.015},
        
        # Singapore
        {'code': 'D05.SI', 'name': 'DBS Group', 'base_price': 28.00, 'volatility': 0.012},
        {'code': 'U11.SI', 'name': 'United Overseas Bank', 'base_price': 24.50, 'volatility': 0.010},
        
        # Taiwan
        {'code': '2330.TW', 'name': 'TSMC', 'base_price': 580.00, 'volatility': 0.020},
        {'code': '2454.TW', 'name': 'MediaTek', 'base_price': 720.00, 'volatility': 0.025},
        
        # US (for completeness)
        {'code': 'AAPL.US', 'name': 'Apple Inc', 'base_price': 180.00, 'volatility': 0.022},
        {'code': 'TSLA.US', 'name': 'Tesla Inc', 'base_price': 240.00, 'volatility': 0.045},
    ]
    
    # Client names for variety
    clients = ['ABC', 'XYZ', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZZ']
    account_suffixes = ['_account', '_invest', '_trading', '_fund', '_group', '_asset', '_wealth']
    
    for days_ago in range(7):  # Create 7 days of data
        date_obj = base_date - timedelta(days=days_ago)
        filename = f"data/ClientExecution_{date_obj.strftime('%Y%m%d')}.csv"
        
        all_trades = []
        
        # Generate 20-30 random trades per day
        num_trades = random.randint(20, 30)
        
        for _ in range(num_trades):
            # Select random stock
            stock = random.choice(international_stocks)
            
            # Generate realistic price based on base price and volatility
            days_effect = days_ago * 0.005  # Small daily trend
            random_effect = random.uniform(-stock['volatility'], stock['volatility'])
            price = stock['base_price'] * (1 + days_effect + random_effect)
            price = round(price, 2)
            
            # Generate realistic quantity based on stock price
            if price > 1000:  # High-priced stocks (Korean/Japanese)
                quantity = random.randint(10, 500)
            elif price > 100:  # Medium-priced stocks
                quantity = random.randint(100, 5000)
            else:  # Low-priced stocks
                quantity = random.randint(1000, 20000)
            
            # Generate random timestamp during trading hours
            hour = random.randint(9, 16)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            microsecond = random.randint(0, 999999)
            timestamp = f"{hour:02d}:{minute:02d}:{second:02d}.{microsecond:06d}"
            
            # Select random client and account
            client = random.choice(clients)
            account_suffix = random.choice(account_suffixes)
            account_name = client + account_suffix
            
            trade = {
                'Timestamp': timestamp,
                'ClientName': client,
                'AccountName': account_name,
                'Instrument': stock['code'],
                'Quantity': quantity,
                'Price': price
            }
            
            all_trades.append(trade)
        
        # Create DataFrame and save
        df = pd.DataFrame(all_trades)
        df.to_csv(filename, sep=';', index=False)
        print(f"Created {filename} with {len(all_trades)} trades")

def create_market_summary_report():
    """Create a summary report of all generated data"""
    print("\n" + "="*60)
    print("📊 INTERNATIONAL STOCK DATA SUMMARY")
    print("="*60)
    
    if not os.path.exists('data'):
        print("No data directory found. Please run create_sample_data() first.")
        return
    
    csv_files = [f for f in os.listdir('data') if f.startswith('ClientExecution_') and f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in data directory.")
        return
    
    print(f"Found {len(csv_files)} trading day files:")
    
    all_stocks = set()
    market_counts = {}
    total_trades = 0
    
    for filename in sorted(csv_files):
        filepath = os.path.join('data', filename)
        try:
            df = pd.read_csv(filepath, delimiter=';')
            date_str = filename.replace('ClientExecution_', '').replace('.csv', '')
            
            stocks_in_file = set(df['Instrument'].unique())
            all_stocks.update(stocks_in_file)
            
            # Count by market
            for stock in stocks_in_file:
                market = stock.split('.')[-1] if '.' in stock else 'Unknown'
                market_counts[market] = market_counts.get(market, 0) + 1
            
            total_trades += len(df)
            print(f"  📅 {date_str}: {len(df)} trades, {len(stocks_in_file)} stocks")
            
        except Exception as e:
            print(f"  ❌ Error reading {filename}: {e}")
    
    print(f"\n📈 TOTAL OVERVIEW:")
    print(f"  • Unique stocks: {len(all_stocks)}")
    print(f"  • Total trades: {total_trades}")
    print(f"  • Trading days: {len(csv_files)}")
    
    print(f"\n🌐 MARKET BREAKDOWN:")
    for market, count in sorted(market_counts.items()):
        print(f"  • {market}: {count} stocks")
    
    print(f"\n🎯 SAMPLE STOCKS BY MARKET:")
    markets = {}
    for stock in sorted(all_stocks):
        market = stock.split('.')[-1] if '.' in stock else 'Unknown'
        if market not in markets:
            markets[market] = []
        markets[market].append(stock)
    
    for market, stocks in markets.items():
        print(f"  {market}: {', '.join(stocks[:3])}{'...' if len(stocks) > 3 else ''}")
    
    print("\n✅ Sample data ready! You can now run: streamlit run app.py")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Creating International Stock Trading Sample Data...")
    print("This will generate 7 days of realistic trading data across multiple markets...")
    
    create_international_sample_data()
    create_market_summary_report()