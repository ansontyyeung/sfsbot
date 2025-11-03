import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
from ai_model import AIModel
from csv_processor import CSVProcessor
import os

# Initialize AI model and CSV processor
@st.cache_resource
def load_ai_model():
    return AIModel()

@st.cache_resource
def load_csv_processor():
    return CSVProcessor()

# Initialize components
ai_model = load_ai_model()
csv_processor = load_csv_processor()

# Page configuration
st.set_page_config(
    page_title="International Stock Trading Chatbot",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 500px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #1f77b4;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        margin-left: auto;
        text-align: right;
    }
    .bot-message {
        background-color: #e6e6e6;
        color: black;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        margin-right: auto;
        white-space: pre-line;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .market-badge {
        display: inline-block;
        background-color: #6c757d;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

def create_sample_data():
    """Create sample CSV data with international stocks"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create data for last 3 days
    base_date = datetime.now().date()
    
    for days_ago in range(3):
        date_obj = base_date - timedelta(days=days_ago)
        filename = f"data/ClientExecution_{date_obj.strftime('%Y%m%d')}.csv"
        
        # Sample data with international stocks
        data = {
            'Timestamp': [
                '09:30:15.048448', '10:15:22.123456', '11:30:45.789123',
                '14:20:33.456789', '15:45:12.987654', '16:10:05.111222',
                '09:35:18.222333', '10:45:30.444555', '11:55:42.666777'
            ],
            'ClientName': ['ABC', 'XYZ', 'DEF', 'ABC', 'GHI', 'XYZ', 'JKL', 'MNO', 'PQR'],
            'AccountName': ['ABC_account', 'XYZ_invest', 'DEF_trading', 
                           'ABC_account', 'GHI_fund', 'XYZ_invest', 
                           'JKL_group', 'MNO_invest', 'PQR_fund'],
            'Instrument': [
                '0148.HK', '005930.KS', '600036.SS', 
                '7203.T', 'BHP.AX', '0148.HK',
                '035420.KQ', '000001.SZ', 'AIRTEL.NS'
            ],
            'Quantity': [10000, 500, 20000, 1000, 3000, 8000, 800, 15000, 2500],
            'Price': [27.44, 75000.0, 35.20, 2500.0, 45.50, 27.60, 180000.0, 15.80, 850.0]
        }
        
        # Adjust prices slightly for different days
        price_adjust = days_ago * 0.1
        data['Price'] = [p + price_adjust for p in data['Price']]
        
        df = pd.DataFrame(data)
        df.to_csv(filename, sep=';', index=False)

def main():
    # Header
    st.markdown('<div class="main-header">🌍 International Stock Trading Chatbot</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 System Info")
        
        # Available dates
        available_dates = csv_processor.get_available_dates()
        if available_dates:
            st.subheader("Available Dates")
            for d in available_dates:
                st.write(f"• {d.strftime('%Y-%m-%d')}")
        else:
            st.warning("No CSV data files found")
            
        # Available markets
        st.subheader("🌐 Supported Markets")
        markets = [
            ("🇭🇰 Hong Kong", ".HK"),
            ("🇰🇷 Korea", ".KS, .KQ"),
            ("🇨🇳 China", ".SS, .SH, .SZ, .ZK"),
            ("🇯🇵 Japan", ".T, .TO"),
            ("🇦🇺 Australia", ".AX"),
            ("🇹🇭 Thailand", ".BK, .TB"),
            ("🇲🇾 Malaysia", ".KL"),
            ("🇮🇳 India", ".NS, .BO"),
            ("🇺🇸 US", ".US, .NASDAQ, .NYSE")
        ]
        
        for flag, suffixes in markets:
            st.write(f"{flag} {suffixes}")
        
        # Quick actions
        st.header("🚀 Quick Actions")
        if st.button("Create Sample Data", use_container_width=True):
            try:
                create_sample_data()
                st.success("Sample international data created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating sample data: {e}")
        
        if st.button("Clear Chat History", use_container_width=True):
            if "messages" in st.session_state:
                st.session_state.messages = []
            st.rerun()
        
        # System status
        st.header("🔧 System Status")
        st.success("✅ CSV Processor: Ready")
        st.success("✅ AI Model: Ready")
        st.success(f"✅ Supported Markets: {len(csv_processor.supported_markets)}")
        
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input(
            "Ask about international stock trading data:", 
            placeholder="e.g., What is the notional for 005930.KS? or Show me Korean market summary"
        )
        
        col1_1, col1_2 = st.columns([1, 1])
        with col1_1:
            if st.button("Send Message", use_container_width=True, type="primary"):
                if user_input:
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # Get AI response
                    with st.spinner("Analyzing your query..."):
                        result = ai_model.process_query(user_input)
                    
                    # Add bot response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                    
                    # Rerun to update the display
                    st.rerun()
        
        with col1_2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.header("📈 Quick Queries")
        
        # International stock examples
        st.subheader("🇰🇷 Korean Stocks")
        korean_queries = [
            "What is the notional for 005930.KS?",
            "Show me KOSPI stocks today",
            "Korean market summary"
        ]
        
        for query in korean_queries:
            if st.button(query, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.spinner("Analyzing..."):
                    result = ai_model.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                st.rerun()
        
        st.subheader("🇨🇳 Chinese Stocks")
        chinese_queries = [
            "Trading volume for 600036.SS",
            "Chinese stocks today",
            "Shanghai market overview"
        ]
        
        for query in chinese_queries:
            if st.button(query, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.spinner("Analyzing..."):
                    result = ai_model.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                st.rerun()
        
        st.subheader("🇯🇵 Japanese Stocks")
        japanese_queries = [
            "Price information for 7203.T",
            "Japanese market data",
            "All Tokyo stocks today"
        ]
        
        for query in japanese_queries:
            if st.button(query, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.spinner("Analyzing..."):
                    result = ai_model.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                st.rerun()
        
        st.subheader("🌐 Market Overview")
        market_queries = [
            "Market overview for today",
            "All markets summary",
            "What trading data do you have?"
        ]
        
        for query in market_queries:
            if st.button(query, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.spinner("Analyzing..."):
                    result = ai_model.process_query(query)
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                st.rerun()
        
        st.header("ℹ️ How to Use")
        st.info("""
        **International Stock Examples:**
        - Korean: 005930.KS (Samsung), 035420.KQ (NAVER)
        - Chinese: 600036.SS (CM Bank), 000001.SZ (Ping An)
        - Japanese: 7203.T (Toyota), 9984.TO (SoftBank)
        - Australian: BHP.AX (BHP Group)
        - Indian: AIRTEL.NS (Bharti Airtel)
        
        **Market Queries:**
        - "Korean market summary"
        - "Show me Chinese stocks"
        - "All Japanese stocks today"
        
        **Date Formats:** today, yesterday, 2025-10-25
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "🌍 **International Stock Trading Chatbot** • "
        "Supporting 20+ global markets • "
        "Built with Streamlit"
    )

if __name__ == "__main__":
    main()