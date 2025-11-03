import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")

def create_sample_data():
    """Create sample CSV data"""
    try:
        from create_sample_data import create_sample_data
        create_sample_data()
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Setting up Stock Trading Chatbot...")
    install_requirements()
    create_sample_data()
    print("\n🎉 Setup complete! Run the app with: streamlit run app.py")