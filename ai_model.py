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
        """Extract stock code from natural language query"""
        patterns = [
            r'(\d{4}\.HK)',  # 0148.HK format
            r'stock\s+(\d{4}\.HK)',  # "stock 0148.HK"
            r'for\s+(\d{4}\.HK)',  # "for 0148.HK"
            r'(\d{4}\.HK)',  # General pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def classify_intent(self, query: str) -> str:
        """Classify user intent"""
        query_lower = query.lower()
        
        intents = {
            'notional_query': [
                "notional", "traded amount", "trading value", "amount traded",
                "total value", "trade value", "notional amount", "how much was traded"
            ],
            'price_query': [
                "price", "current price", "stock price", "how much", "cost"
            ],
            'volume_query': [
                "volume", "trading volume", "shares traded", "quantity"
            ],
            'date_query': [
                "yesterday", "today", "specific date", "on date", "for date"
            ],
            'general_query': [
                "hello", "hi", "help", "what can you do", "hey"
            ]
        }
        
        # Simple keyword matching
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return 'general_query'
    
    def generate_response(self, context: str) -> str:
        """Generate response based on context"""
        # Simple rule-based response generation
        if "hello" in context.lower() or "hi" in context.lower():
            return "Hello! I'm your stock trading assistant. I can help you with trading data analysis including notional amounts, volumes, and prices for specific stocks and dates."
        
        if "help" in context.lower():
            return "I can help you with:\n• Stock notional amounts (e.g., 'What is the notional for 0148.HK?')\n• Trading volumes\n• Price information\n• Date-specific queries (today, yesterday, specific dates)\n\nTry asking me about a specific stock!"
        
        return "I understand your query. I specialize in stock trading information analysis from CSV log files. I can help you find notional amounts, trading volumes, and other trading metrics."
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and return response"""
        logger.info(f"Processing query: {query}")
        
        # Extract stock code
        stock_code = self.extract_stock_code(query)
        
        # Extract date from query
        query_date = self.csv_processor.parse_date_from_query(query)
        
        # Classify intent
        intent = self.classify_intent(query)
        logger.info(f"Detected intent: {intent}, Stock code: {stock_code}, Date: {query_date}")
        
        # Handle date-specific queries
        if intent == 'notional_query' and stock_code:
            result = self.csv_processor.get_stock_notional(stock_code, query_date)
            
            if result['success']:
                notional = result['notional']
                response = f"📊 **Trading Summary for {stock_code} on {query_date}**\n\n"
                response += f"• **Total Notional**: HK${notional:,.2f}\n"
                response += f"• **Total Quantity**: {result['quantity']:,.0f} shares\n"
                response += f"• **Average Price**: HK${result['average_price']:.2f}\n"
                response += f"• **Number of Trades**: {result['trade_count']}\n"
                
                return {
                    "success": True,
                    "response": response,
                    "stock_code": stock_code,
                    "notional_amount": notional,
                    "query_date": query_date.isoformat()
                }
            else:
                return {
                    "success": False,
                    "response": f"❌ {result['message']}",
                    "stock_code": stock_code,
                    "query_date": query_date.isoformat()
                }
        
        elif intent == 'date_query':
            available_dates = self.csv_processor.get_available_dates()
            if available_dates:
                dates_str = ", ".join([d.strftime("%Y-%m-%d") for d in available_dates])
                response = f"📅 **Available Trading Dates**\n\n{dates_str}"
            else:
                response = "❌ No trading data files found in the data directory."
            
            return {
                "success": True,
                "response": response,
                "stock_code": None
            }
        
        elif not stock_code and intent != 'general_query':
            response = "❌ I couldn't identify a stock code in your query. Please specify a stock like '0148.HK'."
            return {
                "success": False,
                "response": response,
                "stock_code": None
            }
        
        else:
            # Generate contextual response
            context = f"User query: {query}"
            if stock_code:
                context += f" Stock: {stock_code}"
            if query_date:
                context += f" Date: {query_date}"
            
            chat_response = self.generate_response(context)
            
            return {
                "success": True,
                "response": chat_response,
                "stock_code": stock_code,
                "query_date": query_date.isoformat() if query_date else None
            }