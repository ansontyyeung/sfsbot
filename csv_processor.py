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
        
        # Specific date patterns
        patterns = [
            r'(\d{4})[-/](\d{2})[-/](\d{2})',  # 2025-10-25, 2025/10/25
            r'(\d{2})[-/](\d{2})[-/](\d{4})',  # 25-10-2025, 25/10/2025
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',  # 25 Oct 2025
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
                    else:  # DD Month YYYY
                        day, month_str, year = int(match.group(1)), match.group(2).lower(), int(match.group(3))
                        month = month_map.get(month_str[:3], 1)
                    
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
            
            # Calculate notional amount (Quantity * Price)
            if 'Quantity' in df.columns and 'Price' in df.columns:
                df['Notional'] = df['Quantity'] * df['Price']
            
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
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return {
                'success': False,
                'notional': 0,
                'message': f"No trading data found for {stock_code} on {query_date}",
                'date': query_date,
                'stock_code': stock_code
            }
        
        # Normalize stock code comparison
        stock_code_upper = stock_code.upper()
        
        # Filter for the specific stock
        stock_data = df[df['Instrument'].str.upper() == stock_code_upper]
        
        if stock_data.empty:
            return {
                'success': False,
                'notional': 0,
                'message': f"No trading data found for {stock_code} on {query_date}",
                'date': query_date,
                'stock_code': stock_code
            }
        
        total_notional = stock_data['Notional'].sum()
        total_quantity = stock_data['Quantity'].sum()
        avg_price = stock_data['Price'].mean()
        trade_count = len(stock_data)
        
        return {
            'success': True,
            'notional': total_notional,
            'quantity': total_quantity,
            'average_price': avg_price,
            'trade_count': trade_count,
            'date': query_date,
            'stock_code': stock_code,
            'message': f"Found {trade_count} trades for {stock_code} on {query_date}"
        }
    
    def get_available_stocks(self, query_date: date = None) -> List[str]:
        """Get list of available stocks for a specific date"""
        if query_date is None:
            query_date = date.today()
        
        df = self.load_csv_data(query_date)
        if df is None or df.empty:
            return []
        
        return df['Instrument'].str.upper().unique().tolist()

# Global instance
csv_processor = CSVProcessor()