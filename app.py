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
    page_title="Stock Trading Chatbot",
    page_icon="📈",
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
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">🤖 Stock Trading Chatbot</div>', unsafe_allow_html=True)
    
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
            
        # Quick actions
        st.header("🚀 Quick Actions")
        if st.button("Create Sample Data"):
            try:
                from create_sample_data import create_sample_data
                create_sample_data()
                st.success("Sample data created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating sample data: {e}")
        
        # System status
        st.header("🔧 System Status")
        st.success("✅ CSV Processor: Ready")
        st.success("✅ AI Model: Ready")
        
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
        user_input = st.text_input("Ask about stock trading data:", placeholder="e.g., What is the notional for 0148.HK today?")
        
        col1_1, col1_2 = st.columns([1, 1])
        with col1_1:
            if st.button("Send Message", use_container_width=True):
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
        
        quick_queries = [
            "What is the notional for 0148.HK?",
            "Show me yesterday's trading for 0700.HK",
            "What data do you have available?",
            "Help me with stock information"
        ]
        
        for query in quick_queries:
            if st.button(query, use_container_width=True):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": query})
                
                # Get AI response
                with st.spinner("Analyzing your query..."):
                    result = ai_model.process_query(query)
                
                # Add bot response to chat history
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                
                # Rerun to update the display
                st.rerun()
        
        st.header("ℹ️ How to Use")
        st.info("""
        **Example Queries:**
        - "Notional for 0148.HK today"
        - "Trading volume for 0700.HK yesterday"  
        - "Show available dates"
        - "Help with stock data"
        
        **Supported Stocks:** 0148.HK, 0700.HK
        **Date Formats:** today, yesterday, YYYY-MM-DD
        """)

if __name__ == "__main__":
    main()