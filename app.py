import streamlit as st
import pandas as pd
import hashlib
import json
import plotly.express as px
from datetime import datetime

# --- Initialize Databases ---
if 'user_credentials' not in st.session_state:
    st.session_state.user_credentials = {
        "admin@psx.com": {
            "name": "Admin",
            "password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # 123
        }
    }

if 'stock_database' not in st.session_state:
    # Pre-loaded 10 PSX stocks
    st.session_state.stock_database = {
        "LUCK": {
            "name": "Lucky Cement",
            "sector": "Cement",
            "analysis": {
                "current_price": 850.25,
                "52_week_high": 920.50,
                "52_week_low": 720.75,
                "support_levels": [820, 800, 780],
                "resistance_levels": [860, 880, 900],
                "rsi": 58.4,
                "volume": 4500000,
                "pe_ratio": 18.7,
                "dividend_yield": 3.2,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
        },
        # 9 more stocks...
        "ENGRO": {
            "name": "Engro Corporation",
            "sector": "Chemicals",
            "analysis": {
                "current_price": 320.75,
                "52_week_high": 350.00,
                "52_week_low": 295.50,
                "support_levels": [310, 300, 295],
                "resistance_levels": [330, 340, 350],
                "rsi": 45.2,
                "volume": 3200000,
                "pe_ratio": 15.2,
                "dividend_yield": 2.8,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
        },
        "HBL": {
            "name": "Habib Bank",
            "sector": "Banking",
            "analysis": {
                "current_price": 125.60,
                "52_week_high": 135.75,
                "52_week_low": 98.25,
                "support_levels": [120, 115, 110],
                "resistance_levels": [130, 135, 140],
                "rsi": 62.1,
                "volume": 5800000,
                "pe_ratio": 7.5,
                "dividend_yield": 5.1,
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
        }
        # Add 7 more stocks following the same format...
    }

# --- Authentication Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user(email, name, password):
    if email in st.session_state.user_credentials:
        return False, "Email already registered"
    st.session_state.user_credentials[email] = {
        "name": name,
        "password": make_hashes(password)
    }
    return True, "Registration successful!"

# --- Stock Analysis Functions ---
def import_stocks(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ['symbol','name','sector','current_price']
        if not all(col in df.columns for col in required_cols):
            return False, "Missing required columns"
        
        for _, row in df.iterrows():
            st.session_state.stock_database[row['symbol']] = {
                "name": row['name'],
                "sector": row['sector'],
                "analysis": {
                    "current_price": float(row['current_price']),
                    "52_week_high": float(row.get('52_week_high', 0)),
                    "52_week_low": float(row.get('52_week_low', 0)),
                    "support_levels": json.loads(row.get('support_levels', '[0,0,0]')),
                    "resistance_levels": json.loads(row.get('resistance_levels', '[0,0,0]')),
                    "rsi": float(row.get('rsi', 50)),
                    "volume": int(row.get('volume', 0)),
                    "pe_ratio": float(row.get('pe_ratio', 0)),
                    "dividend_yield": float(row.get('dividend_yield', 0)),
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
            }
        return True, f"Imported {len(df)} stocks"
    except Exception as e:
        return False, str(e)

def create_price_chart(symbol):
    # Mock historical data - replace with real data in production
    dates = pd.date_range(end=datetime.today(), periods=30).tolist()
    prices = [st.session_state.stock_database[symbol]['analysis']['current_price'] * (0.95 + 0.1*(i/30)) 
              for i in range(30)]
    
    fig = px.line(
        x=dates, 
        y=prices,
        title=f"{symbol} Price Trend (Last 30 Days)",
        labels={'x': 'Date', 'y': 'Price (Rs.)'}
    )
    fig.update_layout(showlegend=False)
    return fig

# --- UI Components ---
def auth_section():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("Login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if email in st.session_state.user_credentials:
                    if make_hashes(password) == st.session_state.user_credentials[email]['password']:
                        st.session_state.authenticated = True
                        st.session_state.current_user = email
                        st.rerun()
                    else:
                        st.error("Invalid password")
                else:
                    st.error("Account not found")
    
    with tab2:
        with st.form("Register"):
            new_email = st.text_input("Email")
            new_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    success, message = register_user(new_email, new_name, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def admin_panel():
    with st.expander("💾 ADMIN: Stock Data Management"):
        st.download_button(
            label="📥 Download Template",
            data=pd.DataFrame({
                'symbol': ['LUCK', 'ENGRO', 'HBL'],
                'name': ['Lucky Cement', 'Engro Corp', 'Habib Bank'],
                'sector': ['Cement', 'Chemicals', 'Banking'],
                'current_price': [850.25, 320.50, 125.60],
                '52_week_high': [920.50, 350.00, 135.75],
                '52_week_low': [720.75, 295.50, 98.25],
                'support_levels': ['[820,800,780]', '[310,300,295]', '[120,115,110]'],
                'resistance_levels': ['[860,880,900]', '[330,340,350]', '[130,135,140]'],
                'rsi': [58.4, 45.2, 62.1],
                'volume': [4500000, 3200000, 5800000],
                'pe_ratio': [18.7, 15.2, 7.5],
                'dividend_yield': [3.2, 2.8, 5.1]
            }).to_csv(index=False),
            file_name="psx_stock_template.csv"
        )
        
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            success, message = import_stocks(uploaded_file)
            st.success(message) if success else st.error(message)

# --- Main App Flow ---
if not st.session_state.get('authenticated'):
    st.title("PSX Stock Analysis Portal")
    auth_section()
else:
    st.set_page_config(layout="wide")
    user = st.session_state.user_credentials[st.session_state.current_user]
    
    # Header
    st.title(f"📈 Welcome, {user['name']}")
    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    # Admin Panel
    if st.session_state.current_user == "admin@psx.com":
        admin_panel()
    
    # Stock Analysis Dashboard
    selected_symbol = st.selectbox(
        "Select Stock", 
        options=list(st.session_state.stock_database.keys()),
        format_func=lambda x: f"{x} - {st.session_state.stock_database[x]['name']}"
    )
    
    if selected_symbol:
        stock = st.session_state.stock_database[selected_symbol]
        analysis = stock['analysis']
        
        # Key Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"Rs. {analysis['current_price']:.2f}")
        col2.metric("52-Week Range", 
                   f"Rs. {analysis['52_week_low']:.2f} - {analysis['52_week_high']:.2f}")
        col3.metric("Volume", f"{analysis['volume']:,}")
        
        # Charts
        tab1, tab2, tab3 = st.tabs(["Price Trend", "Technical Analysis", "Fundamentals"])
        
        with tab1:
            st.plotly_chart(create_price_chart(selected_symbol), use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Support Levels")
                for level in analysis['support_levels']:
                    st.write(f"- Rs. {level:,.2f}")
            with col2:
                st.subheader("Resistance Levels")
                for level in analysis['resistance_levels']:
                    st.write(f"- Rs. {level:,.2f}")
            
            st.subheader("Indicators")
            st.write(f"**RSI (14-day):** {analysis['rsi']:.1f}")
            st.progress(min(int(analysis['rsi']), 100)/100)
        
        with tab3:
            col1, col2 = st.columns(2)
            col1.metric("P/E Ratio", analysis['pe_ratio'])
            col2.metric("Dividend Yield", f"{analysis['dividend_yield']}%")
            
            st.write("**Last Updated:**", analysis['last_updated'])
