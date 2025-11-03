import re
import openai
from csv_processor import csv_processor
from typing import Dict, Any
from datetime import date
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self):
        self.csv_processor = csv_processor
        self.setup_openai()
        
    def setup_openai(self):
        """Setup OpenAI client with your API credentials"""
        try:
            # Get API key and endpoint from environment variables
            api_key = os.getenv('OPENAI_API_KEY')
            api_base = os.getenv('OPENAI_API_BASE')  # Your custom endpoint
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            # Initialize OpenAI client
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base if api_base else None
            )
            
            # Test the connection
            logger.info("✅ OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            raise
    
    def extract_stock_code(self, query: str) -> str:
        """Use OpenAI to extract stock code from natural language query"""
        try:
            system_prompt = """You are a financial data extraction assistant. Extract the stock code/ticker from the user's query. 
            Return ONLY the stock code in the format like "005930.KS", "0148.HK", "600036.SS" etc. 
            If no stock code is found, return 'None'."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            stock_code = response.choices[0].message.content.strip()
            return stock_code if stock_code != 'None' else None
            
        except Exception as e:
            logger.error(f"Error extracting stock code with OpenAI: {e}")
            # Fallback to regex extraction
            return self._fallback_extract_stock_code(query)
    
    def _fallback_extract_stock_code(self, query: str) -> str:
        """Fallback method using regex if OpenAI fails"""
        patterns = [
            r'(\d{4,6}\.(?:HK|KS|KQ|SS|SH|SZ|ZK|T|TO|AX|BK|TB|KL|NS|BO|SI|TW|TWO|JK|PS|HN|HP|US|NASDAQ|NYSE))',
            r'([A-Z]{1,5}\.(?:HK|KS|KQ|SS|SH|SZ|ZK|T|TO|AX|BK|TB|KL|NS|BO|SI|TW|TWO|JK|PS|HN|HP|US|NASDAQ|NYSE))',
            r'stock\s+(\S+\.\S{2,6})',
            r'for\s+(\S+\.\S{2,6})',
            r'(\S+\.\S{2,6})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                potential_code = match.group(1)
                if self.csv_processor.is_valid_stock_code(potential_code):
                    return potential_code
        return None
    
    def classify_intent_with_openai(self, query: str) -> Dict[str, Any]:
        """Use OpenAI to classify intent and extract entities"""
        try:
            system_prompt = """You are a financial trading data analyst. Analyze the user's query and return a JSON with:
            - intent: one of ['notional_query', 'volume_query', 'price_query', 'market_query', 'summary_query', 'date_query', 'greeting', 'help', 'general_query']
            - stock_code: the stock ticker if mentioned (e.g., "005930.KS")
            - date_context: one of ['today', 'yesterday', 'specific_date', 'unspecified']
            - market_focus: if the query is about a specific market/country (e.g., "korea", "china")
            
            Be precise and focus on financial trading data queries."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={ "type": "json_object" },
                max_tokens=150,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return eval(result)  # Parse JSON response
            
        except Exception as e:
            logger.error(f"Error classifying intent with OpenAI: {e}")
            return self._fallback_classify_intent(query)
    
    def _fallback_classify_intent(self, query: str) -> Dict[str, Any]:
        """Fallback intent classification"""
        query_lower = query.lower()
        
        # Simple keyword matching as fallback
        if any(word in query_lower for word in ['notional', 'traded amount', 'total value']):
            intent = 'notional_query'
        elif any(word in query_lower for word in ['volume', 'shares traded', 'quantity']):
            intent = 'volume_query'
        elif any(word in query_lower for word in ['price', 'how much', 'cost']):
            intent = 'price_query'
        elif any(word in query_lower for word in ['market', 'korea', 'china', 'japan']):
            intent = 'market_query'
        elif any(word in query_lower for word in ['summary', 'overview', 'all markets']):
            intent = 'summary_query'
        elif any(word in query_lower for word in ['hello', 'hi', 'hey']):
            intent = 'greeting'
        elif any(word in query_lower for word in ['help', 'what can you do']):
            intent = 'help'
        else:
            intent = 'general_query'
            
        return {
            "intent": intent,
            "stock_code": None,
            "date_context": "unspecified",
            "market_focus": None
        }
    
    def generate_openai_response(self, query: str, context_data: Dict[str, Any] = None) -> str:
        """Generate intelligent response using OpenAI with trading data context"""
        try:
            # Prepare context for the AI
            context_str = ""
            if context_data and context_data.get('success'):
                context_str = f"""
                Trading Data Context:
                - Stock: {context_data.get('stock_code', 'N/A')}
                - Market: {context_data.get('market', 'N/A')}
                - Date: {context_data.get('query_date', 'N/A')}
                - Notional: {context_data.get('notional_amount', 0):,.2f}
                - Quantity: {context_data.get('quantity', 0):,}
                - Average Price: {context_data.get('average_price', 0):.2f}
                - Trade Count: {context_data.get('trade_count', 0)}
                """
            
            system_prompt = f"""You are a professional financial trading assistant specializing in international stock markets. 
            You have access to trading execution data from CSV files.

            GUIDELINES:
            - Be precise, professional, and helpful
            - Use appropriate currency symbols for different markets
            - Format large numbers with commas (e.g., 1,000,000)
            - If trading data is available, present it clearly
            - If no data is found, suggest alternatives
            - Keep responses concise but informative
            - Use emojis sparingly for visual clarity

            Available Data: {context_str if context_str else 'No specific trading data available for this query.'}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return self._generate_fallback_response(query, context_data)
    
    def _generate_fallback_response(self, query: str, context_data: Dict[str, Any] = None) -> str:
        """Generate fallback response when OpenAI fails"""
        if context_data and context_data.get('success'):
            notional = context_data.get('notional_amount', 0)
            quantity = context_data.get('quantity', 0)
            avg_price = context_data.get('average_price', 0)
            trade_count = context_data.get('trade_count', 0)
            market = context_data.get('market', 'Unknown Market')
            
            return f"""📊 Trading Data for {context_data.get('stock_code')} ({market})

• Total Notional: {notional:,.2f}
• Shares Traded: {quantity:,}
• Average Price: {avg_price:.2f}
• Number of Trades: {trade_count}

This is automated trading data from our execution records."""
        else:
            return "I understand you're asking about trading data. Currently, I'm experiencing technical difficulties with my AI system. Please try again shortly or rephrase your query."
    
    def format_currency(self, amount: float, currency: str = "HK$") -> str:
        """Format currency with proper formatting"""
        if amount >= 1_000_000_000:
            return f"{currency}{amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"{currency}{amount/1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"{currency}{amount/1_000:.1f}K"
        else:
            return f"{currency}{amount:,.2f}"
    
    def get_currency_symbol(self, market: str) -> str:
        """Get appropriate currency symbol for different markets"""
        currency_map = {
            'Hong Kong': 'HK$',
            'Korea (KOSPI)': '₩', 'Korea (KOSDAQ)': '₩',
            'China (Shanghai)': '¥', 'China (Shenzhen)': '¥',
            'Japan (Tokyo)': '¥',
            'Australia (ASX)': 'A$',
            'Thailand (SET)': '฿',
            'Malaysia (KLSE)': 'RM',
            'India (NSE)': '₹', 'India (BSE)': '₹',
            'Singapore (SGX)': 'S$',
            'Taiwan': 'NT$',
            'Indonesia (IDX)': 'Rp',
            'Philippines (PSE)': '₱',
            'Vietnam (HNX)': '₫', 'Vietnam (HOSE)': '₫',
            'United States': '$', 'United States (NASDAQ)': '$', 'United States (NYSE)': '$'
        }
        return currency_map.get(market, '$')
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query using OpenAI AI"""
        logger.info(f"Processing query with OpenAI: {query}")
        
        try:
            # Step 1: Use OpenAI to classify intent and extract entities
            openai_analysis = self.classify_intent_with_openai(query)
            intent = openai_analysis.get('intent', 'general_query')
            stock_code = openai_analysis.get('stock_code')
            date_context = openai_analysis.get('date_context', 'unspecified')
            
            # Step 2: Parse date from query
            query_date = self.csv_processor.parse_date_from_query(query)
            
            # Step 3: Get trading data if relevant
            context_data = None
            if stock_code and intent in ['notional_query', 'volume_query', 'price_query']:
                context_data = self.csv_processor.get_stock_notional(stock_code, query_date)
            
            elif intent == 'summary_query':
                context_data = self.csv_processor.get_market_summary(query_date)
            
            elif intent == 'market_query':
                market_focus = openai_analysis.get('market_focus')
                if market_focus:
                    # Handle market-specific queries
                    market_mappings = {
                        'korea': '.KS', 'korean': '.KS',
                        'china': '.SS', 'chinese': '.SS', 
                        'japan': '.T', 'japanese': '.T',
                        'australia': '.AX', 'australian': '.AX',
                        'thai': '.BK', 'thailand': '.BK',
                        'malaysia': '.KL', 'malaysian': '.KL',
                        'india': '.NS', 'indian': '.NS'
                    }
                    if market_focus in market_mappings:
                        stocks = self.csv_processor.get_stocks_by_market(market_mappings[market_focus], query_date)
                        context_data = {'success': bool(stocks), 'stocks': stocks, 'market': market_focus}
            
            # Step 4: Generate intelligent response using OpenAI
            ai_response = self.generate_openai_response(query, context_data)
            
            # Step 5: Prepare return data
            result = {
                "success": True,
                "response": ai_response,
                "stock_code": stock_code,
                "query_date": query_date.isoformat() if query_date else None,
                "ai_processed": True
            }
            
            # Add trading data to result if available
            if context_data and context_data.get('success'):
                result.update({
                    "notional_amount": context_data.get('notional', 0),
                    "quantity": context_data.get('quantity', 0),
                    "average_price": context_data.get('average_price', 0),
                    "trade_count": context_data.get('trade_count', 0),
                    "market": context_data.get('market', 'Unknown')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in OpenAI processing: {e}")
            # Fallback to simple response
            return {
                "success": False,
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                "stock_code": None,
                "ai_processed": False
            }