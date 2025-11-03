import re
from csv_processor import csv_processor
from typing import Dict, Any
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self):
        self.csv_processor = csv_processor
        
    def extract_stock_code(self, query: str) -> str:
        """Extract stock code from natural language query with international support"""
        # Pattern for international stock codes with various suffixes
        patterns = [
            r'(\d{4,6}\.(?:HK|KS|KQ|SS|SH|SZ|ZK|T|TO|AX|BK|TB|KL|NS|BO|SI|TW|TWO|JK|PS|HN|HP|US|NASDAQ|NYSE))',  # Standard format
            r'([A-Z]{1,5}\.(?:HK|KS|KQ|SS|SH|SZ|ZK|T|TO|AX|BK|TB|KL|NS|BO|SI|TW|TWO|JK|PS|HN|HP|US|NASDAQ|NYSE))',  # Ticker symbols
            r'stock\s+(\S+\.\S{2,6})',  # "stock 005930.KS"
            r'for\s+(\S+\.\S{2,6})',  # "for 005930.KS"
            r'(\S+\.\S{2,6})',  # General pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                potential_code = match.group(1)
                # Validate it's a proper stock code
                if self.csv_processor.is_valid_stock_code(potential_code):
                    return potential_code
        
        return None
    
    def classify_intent(self, query: str) -> str:
        """Classify user intent with enhanced international support"""
        query_lower = query.lower()
        
        # Check for notional queries
        if any(word in query_lower for word in ['notional', 'traded amount', 'trading value', 
                                               'amount traded', 'total value', 'trade value', 
                                               'how much was traded', 'what is the notional',
                                               'trading volume in value', 'value traded']):
            return 'notional_query'
        
        # Check for volume queries
        if any(word in query_lower for word in ['volume', 'trading volume', 'shares traded', 
                                               'quantity', 'how many shares', 'number of shares',
                                               'share volume', 'volume traded']):
            return 'volume_query'
        
        # Check for price queries
        if any(word in query_lower for word in ['price', 'current price', 'stock price', 
                                               'how much', 'cost', 'what price', 'price level',
                                               'trading price', 'average price']):
            return 'price_query'
        
        # Check for market queries
        if any(word in query_lower for word in ['market', 'markets', 'korea', 'korean', 'china', 'chinese',
                                               'japan', 'japanese', 'australia', 'australian', 'thai', 'thailand',
                                               'malaysia', 'malaysian', 'india', 'indian', 'hong kong',
                                               'shanghai', 'shenzhen', 'kospi', 'kosdaq', 'asx', 'set']):
            return 'market_query'
        
        # Check for date queries
        if any(word in query_lower for word in ['yesterday', 'today', 'date', 'available dates', 
                                               'what data', 'which dates', 'last week', 'this week']):
            return 'date_query'
        
        # Check for summary queries
        if any(word in query_lower for word in ['summary', 'overview', 'all markets', 'market summary',
                                               'trading summary', 'daily summary']):
            return 'summary_query'
        
        # Check for greeting
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        # Check for help
        if any(word in query_lower for word in ['help', 'what can you do', 'how to use', 'supported']):
            return 'help'
        
        return 'general_query'
    
    def format_currency(self, amount: float, currency: str = "HK$") -> str:
        """Format currency with proper formatting for different markets"""
        if amount >= 1_000_000_000:
            return f"{currency}{amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"{currency}{amount/1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"{currency}{amount/1_000:.1f}K"
        else:
            return f"{currency}{amount:,.2f}"
    
    def format_number(self, number: float) -> str:
        """Format large numbers with commas"""
        return f"{number:,.0f}"
    
    def get_currency_symbol(self, market: str) -> str:
        """Get appropriate currency symbol for different markets"""
        currency_map = {
            'Hong Kong': 'HK$',
            'Korea (KOSPI)': '₩',
            'Korea (KOSDAQ)': '₩',
            'China (Shanghai)': '¥',
            'China (Shenzhen)': '¥',
            'Japan (Tokyo)': '¥',
            'Australia (ASX)': 'A$',
            'Thailand (SET)': '฿',
            'Malaysia (KLSE)': 'RM',
            'India (NSE)': '₹',
            'India (BSE)': '₹',
            'Singapore (SGX)': 'S$',
            'Taiwan': 'NT$',
            'Indonesia (IDX)': 'Rp',
            'Philippines (PSE)': '₱',
            'Vietnam (HNX)': '₫',
            'Vietnam (HOSE)': '₫',
            'United States': '$',
            'United States (NASDAQ)': '$',
            'United States (NYSE)': '$'
        }
        return currency_map.get(market, '$')
    
    def generate_natural_response(self, intent: str, result: Dict[str, Any] = None, 
                                stock_code: str = None, query_date: date = None) -> str:
        """Generate natural language responses with international market support"""
        
        if intent == 'greeting':
            return "👋 Hello! I'm your international stock trading assistant. I can help you analyze trading data from CSV log files for stocks across multiple markets including Hong Kong, Korea, China, Japan, Australia, Thailand, Malaysia, India, and more!"
        
        elif intent == 'help':
            return """🤖 How I can help you:

Stock Information (All Markets):
• What's the notional traded for 005930.KS today?
• Show me trading volume for 600036.SS yesterday
• What was the average price for 7203.T?
• Trading data for AAPL.US

Market Information:
• Show me Korean market summary
• What Chinese stocks do you have?
• Market overview for today
• All Japanese stocks

Date Queries:
• What trading data do you have available?
• Show me trades from 2025-10-25
• Last week's trading summary

Supported Markets:
• Hong Kong: .HK (0148.HK)
• Korea: .KS (KOSPI), .KQ (KOSDAQ) 
• China: .SS/.SH (Shanghai), .SZ/.ZK (Shenzhen)
• Japan: .T/.TO (Tokyo)
• Australia: .AX
• Thailand: .BK/.TB
• Malaysia: .KL
• India: .NS/.BO
• And many more...

Try asking me about any international stock! 🌍"""
        
        elif intent == 'notional_query' and result and result.get('success'):
            notional = result['notional']
            quantity = result['quantity']
            avg_price = result['average_price']
            trade_count = result['trade_count']
            market = result.get('market', 'Unknown Market')
            currency = self.get_currency_symbol(market)
            
            response = f"🌐 Trading Summary for {stock_code} ({market}) on {query_date}\n\n"
            response += f"I found {trade_count} trades for {stock_code} on {query_date}.\n\n"
            response += f"• Total Notional Value: {self.format_currency(notional, currency)}\n"
            response += f"• Total Shares Traded: {self.format_number(quantity)} shares\n"
            response += f"• Average Price per Share: {currency}{avg_price:.2f}\n"
            
            if 'high_price' in result and 'low_price' in result:
                response += f"• Price Range: {currency}{result['low_price']:.2f} - {currency}{result['high_price']:.2f}\n"
            
            if trade_count > 1:
                avg_trade_size = quantity / trade_count
                response += f"• Average Trade Size: {self.format_number(avg_trade_size)} shares per trade\n"
            
            return response
        
        elif intent == 'notional_query' and result and not result.get('success'):
            market = result.get('market', 'Unknown Market')
            return f"❌ I couldn't find any trading data for {stock_code} ({market}) on {query_date}. Please check if the stock code and date are correct, and ensure we have data for that date."
        
        elif intent == 'volume_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            if result and result.get('success'):
                quantity = result['quantity']
                trade_count = result['trade_count']
                market = result.get('market', 'Unknown Market')
                currency = self.get_currency_symbol(market)
                
                response = f"📈 Trading Volume for {stock_code} ({market}) on {query_date}\n\n"
                response += f"• Total Shares Traded: {self.format_number(quantity)} shares\n"
                response += f"• Number of Trades: {trade_count}\n"
                
                if trade_count > 0:
                    avg_trade_size = quantity / trade_count
                    response += f"• Average Trade Size: {self.format_number(avg_trade_size)} shares per trade\n"
                
                response += f"• Total Notional Value: {self.format_currency(result['notional'], currency)}"
                
                return response
            else:
                market = result.get('market', 'Unknown Market') if result else 'Unknown Market'
                return f"❌ I couldn't find any trading volume data for {stock_code} ({market}) on {query_date}."
        
        elif intent == 'price_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            if result and result.get('success'):
                avg_price = result['average_price']
                market = result.get('market', 'Unknown Market')
                currency = self.get_currency_symbol(market)
                
                response = f"💰 Price Information for {stock_code} ({market}) on {query_date}\n\n"
                response += f"• Average Trade Price: {currency}{avg_price:.2f}\n"
                
                if 'high_price' in result and 'low_price' in result:
                    response += f"• Daily Range: {currency}{result['low_price']:.2f} - {currency}{result['high_price']:.2f}\n"
                    response += f"• Price Volatility: {currency}{result.get('price_volatility', 0):.2f}\n"
                
                response += f"• Total Shares Traded: {self.format_number(result['quantity'])} shares\n"
                response += f"• Total Value Traded: {self.format_currency(result['notional'], currency)}"
                
                return response
            else:
                market = result.get('market', 'Unknown Market') if result else 'Unknown Market'
                return f"❌ I couldn't find any price data for {stock_code} ({market}) on {query_date}."
        
        elif intent == 'market_query':
            # Handle market-specific queries
            query_lower = stock_code.lower() if stock_code else ""
            market_mappings = {
                'korea': ['.KS', '.KQ'],
                'korean': ['.KS', '.KQ'],
                'china': ['.SS', '.SH', '.SZ', '.ZK'],
                'chinese': ['.SS', '.SH', '.SZ', '.ZK'],
                'japan': ['.T', '.TO'],
                'japanese': ['.T', '.TO'],
                'australia': ['.AX'],
                'australian': ['.AX'],
                'thai': ['.BK', '.TB'],
                'thailand': ['.BK', '.TB'],
                'malaysia': ['.KL'],
                'malaysian': ['.KL'],
                'india': ['.NS', '.BO'],
                'indian': ['.NS', '.BO'],
                'hong kong': ['.HK'],
                'shanghai': ['.SS', '.SH'],
                'shenzhen': ['.SZ', '.ZK']
            }
            
            for market_key, suffixes in market_mappings.items():
                if market_key in query_lower:
                    stocks = []
                    for suffix in suffixes:
                        market_stocks = self.csv_processor.get_stocks_by_market(suffix, query_date)
                        stocks.extend(market_stocks)
                    
                    if stocks:
                        response = f"🏢 {market_key.title()} Market Stocks on {query_date}\n\n"
                        for i, stock in enumerate(stocks[:10]):  # Show top 10
                            currency = self.get_currency_symbol(stock['market'])
                            response += f"{i+1}. {stock['code']}: {self.format_currency(stock['total_notional'], currency)} ({stock['trade_count']} trades)\n"
                        
                        if len(stocks) > 10:
                            response += f"\n... and {len(stocks) - 10} more stocks"
                        
                        return response
                    else:
                        return f"❌ No {market_key} stocks found in the trading data for {query_date}."
            
            return "🤔 I understand you're asking about a specific market. Please specify which market you're interested in (e.g., Korean stocks, Chinese market, Japanese stocks)."
        
        elif intent == 'summary_query':
            result = self.csv_processor.get_market_summary(query_date)
            if result and result.get('success'):
                response = f"📊 Market Trading Summary for {query_date}\n\n"
                response += f"Total Markets: {result['total_markets']}\n"
                response += f"Total Notional: {self.format_currency(result['total_notional'])}\n\n"
                
                for market in result['market_breakdown']:
                    currency = self.get_currency_symbol(market['Market'])
                    response += f"• {market['Market']}:\n"
                    response += f"  Notional: {self.format_currency(market['Total_Notional'], currency)}\n"
                    response += f"  Stocks: {market['Unique_Stocks']}\n"
                    response += f"  Trades: {market['Total_Trades']}\n"
                    response += f"  Volume: {self.format_number(market['Total_Quantity'])} shares\n\n"
                
                return response
            else:
                return f"❌ No market summary data available for {query_date}."
        
        elif intent == 'date_query':
            available_dates = self.csv_processor.get_available_dates()
            if available_dates:
                dates_list = "\n".join([f"• {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})" for d in available_dates])
                return f"📅 Available Trading Dates\n\nI have trading data for the following dates:\n\n{dates_list}\n\nYou can ask me about specific stocks or markets on any of these dates!"
            else:
                return "❌ I don't have any trading data files available at the moment. Please make sure CSV files are placed in the 'data' folder with the correct naming format."
        
        elif not stock_code and intent in ['notional_query', 'volume_query', 'price_query']:
            return "🤔 I understand you're asking about trading data, but I need to know which stock you're interested in. Please specify a stock code like '005930.KS', '600036.SS', or '7203.T'."
        
        else:
            return """🌍 I'm your international stock trading data assistant! I can help you analyze trading information from CSV log files across global markets.

Here's what I can do for you:
• Tell you the notional amount traded for specific stocks worldwide
• Show trading volumes and quantities for any market
• Provide price information with local currency symbols
• Analyze data for different dates and markets
• Give market summaries and overviews

Supported Markets:
• Hong Kong, Korea, China, Japan, Australia
• Thailand, Malaysia, India, Singapore, Taiwan
• Indonesia, Philippines, Vietnam, and more!

Try asking me something like:
• "What was the notional for 005930.KS yesterday?"
• "Show me Korean market summary"
• "Price information for 600036.SS"
• "All Japanese stocks today"

What would you like to know? 📊"""
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and return response with international support"""
        logger.info(f"Processing query: {query}")
        
        # Extract stock code
        stock_code = self.extract_stock_code(query)
        
        # Extract date from query
        query_date = self.csv_processor.parse_date_from_query(query)
        
        # Classify intent
        intent = self.classify_intent(query)
        logger.info(f"Detected intent: {intent}, Stock code: {stock_code}, Date: {query_date}")
        
        # Handle market queries (where stock_code might contain market name)
        if intent == 'market_query' and not self.csv_processor.is_valid_stock_code(stock_code or ""):
            # If it's a market query but the "stock_code" is actually a market name
            market_name = stock_code
            stock_code = None
        
        # Handle different intents
        if intent == 'notional_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            response = self.generate_natural_response(intent, result, stock_code, query_date)
            
            return {
                "success": result.get('success', False),
                "response": response,
                "stock_code": stock_code,
                "notional_amount": result.get('notional', 0),
                "market": result.get('market', 'Unknown'),
                "query_date": query_date.isoformat() if query_date else None
            }
        
        elif intent == 'volume_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            response = self.generate_natural_response(intent, result, stock_code, query_date)
            
            return {
                "success": result.get('success', False),
                "response": response,
                "stock_code": stock_code,
                "market": result.get('market', 'Unknown'),
                "query_date": query_date.isoformat() if query_date else None
            }
        
        elif intent == 'price_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            response = self.generate_natural_response(intent, result, stock_code, query_date)
            
            return {
                "success": result.get('success', False),
                "response": response,
                "stock_code": stock_code,
                "market": result.get('market', 'Unknown'),
                "query_date": query_date.isoformat() if query_date else None
            }
        
        elif intent == 'market_query':
            response = self.generate_natural_response(intent, stock_code=stock_code, query_date=query_date)
            return {
                "success": True,
                "response": response,
                "stock_code": stock_code,
                "query_date": query_date.isoformat() if query_date else None
            }
        
        elif intent == 'summary_query':
            result = self.csv_processor.get_market_summary(query_date)
            response = self.generate_natural_response(intent, result, query_date=query_date)
            
            return {
                "success": result.get('success', False) if result else False,
                "response": response,
                "query_date": query_date.isoformat() if query_date else None
            }
        
        elif intent == 'date_query':
            response = self.generate_natural_response(intent)
            return {
                "success": True,
                "response": response,
                "stock_code": None
            }
        
        elif intent == 'greeting':
            response = self.generate_natural_response(intent)
            return {
                "success": True,
                "response": response,
                "stock_code": None
            }
        
        elif intent == 'help':
            response = self.generate_natural_response(intent)
            return {
                "success": True,
                "response": response,
                "stock_code": None
            }
        
        elif not stock_code and intent in ['notional_query', 'volume_query', 'price_query']:
            response = self.generate_natural_response(intent, stock_code=stock_code)
            return {
                "success": False,
                "response": response,
                "stock_code": None
            }
        
        else:
            response = self.generate_natural_response('general_query')
            return {
                "success": True,
                "response": response,
                "stock_code": stock_code,
                "query_date": query_date.isoformat() if query_date else None
            }