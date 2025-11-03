import pandas as pd
import os
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.cache = {}
        
        # Supported stock market suffixes
        self.supported_markets = {
            # Hong Kong
            '.HK': 'Hong Kong',
            # Korea
            '.KS': 'Korea (KOSPI)',
            '.KQ': 'Korea (KOSDAQ)',
            # China
            '.SS': 'China (Shanghai)',
            '.SH': 'China (Shanghai)',
            '.SZ': 'China (Shenzhen)',
            '.ZK': 'China (Shenzhen)',
            # Japan
            '.T': 'Japan (Tokyo)',
            '.TO': 'Japan (Tokyo)',
            # Australia
            '.AX': 'Australia (ASX)',
            # Thailand
            '.BK': 'Thailand (SET)',
            '.TB': 'Thailand (SET)',
            # Malaysia
            '.KL': 'Malaysia (KLSE)',
            # India
            '.NS': 'India (NSE)',
            '.BO': 'India (BSE)',
            # Singapore
            '.SI': 'Singapore (SGX)',
            # Taiwan
            '.TW': 'Taiwan',
            '.TWO': 'Taiwan (OTC)',
            # Indonesia
            '.JK': 'Indonesia (IDX)',
            # Philippines
            '.PS': 'Philippines (PSE)',
            # Vietnam
            '.HN': 'Vietnam (HNX)',
            '.HP': 'Vietnam (HOSE)',
            # US (for completeness)
            '.US': 'United States',
            '.NASDAQ': 'United States (NASDAQ)',
            '.NYSE': 'United States (NYSE)'
        }
        
    def extract_date_from_filename(self, filename: str) -> Optional[date]:
        """Extract date from filename like ClientExecution_20251025.csv"""
        try:
            match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
            if match:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return date(year, month, day)
        except Exception as e:
            logger.error(f"Error extracting date from {filename}: {e}")
        return None
    
    def get_market_info(self, stock_code: str) -> Dict[str, str]:
        """Get market information for a stock code"""
        for suffix, market_name in self.supported_markets.items():
            if stock_code.upper().endswith(suffix):
                return {
                    'suffix': suffix,
                    'market': market_name,
                    'base_code': stock_code.upper().replace(suffix, '')
                }
        
        # If no known suffix found, assume it's a local market code
        return {
            'suffix': '',
            'market': 'Unknown Market',
            'base_code': stock_code.upper()
        }
    
    def is_valid_stock_code(self, stock_code: str) -> bool:
        """Check if stock code has a valid market suffix"""
        if not stock_code or len(stock_code) < 3:
            return False
        
        # Check if it has any known market suffix
        for suffix in self.supported_markets.keys():
            if stock_code.upper().endswith(suffix):
                return True
        
        # Also allow numeric codes without suffixes (for flexibility)
        if re.match(r'^\d+$', stock_code):
            return True
            
        return False
    
    def normalize_stock_code(self, stock_code: str) -> str:
        """Normalize stock code to uppercase"""
        return stock_code.upper()
    
    def get_available_dates(self) -> List[date]:
        """Get all available dates from CSV files"""
        dates = []
        if not os.path.exists(self.data_dir):
            logger.warning(f"Data directory {self.data_dir} does not exist")
            return dates
            
        for filename in os.listdir(self.data_dir):
            if filename.startswith("ClientExecution_") and filename.endswith(".csv"):
                file_date = self.extract_date_from_filename(filename)
                if file_date:
                    dates.append(file_date)
        
        return sorted(dates)
    
    def parse_date_from_query(self, query: str) -> Optional[date]:
        """Extract date from natural language query"""
        query_lower = query.lower()
        
        # Today
        if any(word in query_lower for word in ['today', 'current day', 'now']):
            return date.today()
        
        # Yesterday
        if any(word in query_lower for word in ['yesterday', 'previous day']):
            return date.today() - timedelta(days=1)
        
        # Day before yesterday
        if any(word in query_lower for word in ['day before yesterday', '2 days ago']):
            return date.today() - timedelta(days=2)
        
        # This week
        if any(word in query_lower for word in ['this week', 'current week']):
            return date.today()
        
        # Last week
        if any(word in query_lower for word in ['last week', 'previous week']):
            return date.today() - timedelta(days=7)
        
        # Specific date patterns
        patterns = [
            r'(\d{4})[-/](\d{2})[-/](\d{2})',  # 2025-10-25, 2025/10/25
            r'(\d{2})[-/](\d{2})[-/](\d{4})',  # 25-10-2025, 25/10/2025
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',  # 25 Oct 2025
            r'(\d{1,2})[a-z]+\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*',  # 25th October (current year assumed)
        ]
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    if pattern == patterns[0]:  # YYYY-MM-DD
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    elif pattern == patterns[1]:  # DD-MM-YYYY
                        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    elif pattern == patterns[2]:  # DD Month YYYY
                        day, month_str, year = int(match.group(1)), match.group(2).lower(), int(match.group(3))
                        month = month_map.get(month_str[:3], 1)
                    else:  # DD Month (current year)
                        day, month_str = int(match.group(1)), match.group(2).lower()
                        month = month_map.get(month_str[:3], 1)
                        year = date.today().year
                    
                    return date(year, month, day)
                except Exception as e:
                    logger.error(f"Error parsing date from query: {e}")
                    continue
        
        # Default to today if no date specified
        return date.today()
    
    def load_csv_data(self, target_date: date) -> Optional[pd.DataFrame]:
        """Load CSV data for specific date"""
        cache_key = target_date.isoformat()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Find matching CSV file
        csv_files = []
        for filename in os.listdir(self.data_dir):
            if filename.startswith("ClientExecution_") and filename.endswith(".csv"):
                file_date = self.extract_date_from_filename(filename)
                if file_date == target_date:
                    csv_files.append(filename)
        
        if not csv_files:
            logger.warning(f"No CSV file found for date {target_date}")
            return None
        
        # Load the first matching file
        filepath = os.path.join(self.data_dir, csv_files[0])
        try:
            df = pd.read_csv(filepath, delimiter=';')
            
            # Normalize Instrument column to uppercase
            if 'Instrument' in df.columns:
                df['Instrument'] = df['Instrument'].str.upper()
            
            # Calculate notional amount (Quantity * Price)
            if 'Quantity' in df.columns and 'Price' in df.columns:
                df['Notional'] = df['Quantity'] * df['Price']
            
            # Add market information
            df['Market'] = df['Instrument'].apply(
                lambda x: self.get_market_info(x)['market']
            )
            
            # Cache the result
            self.cache[cache_key] = df
            logger.info(f"Loaded data from {filepath} with {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV file {filepath}: {e}")
            return None
    
    def get_stock_notional(self, stock_code: str, query_date: date = None) -> Dict[str, Any]:
        """Get notional amount for a specific stock on a specific date"""
        if query_date is None:
            query_date = date.today()
        
        # Normalize stock code
        normalized_code = self.normalize_stock_code(stock_code)
        
        # Get market info
        market_info = self.get_market_info(normalized_code)
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return {
                'success': False,
                'notional': 0,
                'message': f"No trading data found for {stock_code} ({market_info['market']}) on {query_date}",
                'date': query_date,
                'stock_code': stock_code,
                'market': market_info['market'],
                'normalized_code': normalized_code
            }
        
        # Filter for the specific stock
        stock_data = df[df['Instrument'] == normalized_code]
        
        if stock_data.empty:
            return {
                'success': False,
                'notional': 0,
                'message': f"No trading data found for {stock_code} ({market_info['market']}) on {query_date}",
                'date': query_date,
                'stock_code': stock_code,
                'market': market_info['market'],
                'normalized_code': normalized_code
            }
        
        total_notional = stock_data['Notional'].sum()
        total_quantity = stock_data['Quantity'].sum()
        avg_price = stock_data['Price'].mean()
        trade_count = len(stock_data)
        
        # Calculate additional statistics
        high_price = stock_data['Price'].max()
        low_price = stock_data['Price'].min()
        price_volatility = high_price - low_price
        
        return {
            'success': True,
            'notional': total_notional,
            'quantity': total_quantity,
            'average_price': avg_price,
            'high_price': high_price,
            'low_price': low_price,
            'price_volatility': price_volatility,
            'trade_count': trade_count,
            'date': query_date,
            'stock_code': stock_code,
            'market': market_info['market'],
            'normalized_code': normalized_code,
            'message': f"Found {trade_count} trades for {stock_code} ({market_info['market']}) on {query_date}"
        }
    
    def get_available_stocks(self, query_date: date = None) -> List[Dict[str, str]]:
        """Get list of available stocks for a specific date with market info"""
        if query_date is None:
            query_date = date.today()
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return []
        
        stocks = []
        for instrument in df['Instrument'].unique():
            market_info = self.get_market_info(instrument)
            stocks.append({
                'code': instrument,
                'market': market_info['market'],
                'base_code': market_info['base_code']
            })
        
        return stocks
    
    def get_market_summary(self, query_date: date = None) -> Dict[str, Any]:
        """Get summary of trading by market for a specific date"""
        if query_date is None:
            query_date = date.today()
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return {
                'success': False,
                'message': f"No data available for {query_date}",
                'date': query_date
            }
        
        market_summary = df.groupby('Market').agg({
            'Notional': 'sum',
            'Quantity': 'sum',
            'Instrument': 'nunique',
            'Price': ['mean', 'count']
        }).round(2)
        
        # Flatten column names
        market_summary.columns = ['Total_Notional', 'Total_Quantity', 'Unique_Stocks', 'Avg_Price', 'Total_Trades']
        market_summary = market_summary.reset_index()
        
        total_market_notional = market_summary['Total_Notional'].sum()
        
        return {
            'success': True,
            'date': query_date,
            'total_markets': len(market_summary),
            'total_notional': total_market_notional,
            'market_breakdown': market_summary.to_dict('records'),
            'message': f"Trading summary for {query_date}: {len(market_summary)} markets, total notional {total_market_notional:,.0f}"
        }
    
    def get_stocks_by_market(self, market_suffix: str, query_date: date = None) -> List[Dict[str, Any]]:
        """Get all stocks for a specific market on a given date"""
        if query_date is None:
            query_date = date.today()
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return []
        
        # Filter stocks by market suffix
        market_stocks = []
        for instrument in df['Instrument'].unique():
            if instrument.upper().endswith(market_suffix.upper()):
                stock_data = df[df['Instrument'] == instrument]
                market_info = self.get_market_info(instrument)
                
                stock_summary = {
                    'code': instrument,
                    'market': market_info['market'],
                    'total_notional': stock_data['Notional'].sum(),
                    'total_quantity': stock_data['Quantity'].sum(),
                    'average_price': stock_data['Price'].mean(),
                    'trade_count': len(stock_data)
                }
                market_stocks.append(stock_summary)
        
        return sorted(market_stocks, key=lambda x: x['total_notional'], reverse=True)

# Global instance
csv_processor = CSVProcessor()