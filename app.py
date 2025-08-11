import streamlit as st
import google.generativeai as genai
import json

# Application Title and Description
st.title("PSX Stock Price and Volume Analysis")
st.write("This application provides a streamlined analysis of PSX stocks, including support/resistance levels and price movement forecasts.")

# Load Gemini API key securely from .streamlit/secrets.toml
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Use gemini-1.5-pro or another suitable model if gemini-pro is not available
    model = genai.GenerativeModel('gemini-1.5-pro') 
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}. Please ensure your API key is correctly saved in `.streamlit/secrets.toml`.")
    st.stop()

# Input for company_symbol
company_symbol = st.text_input("Enter PSX Ticker Symbol (e.g., LUCK, TRG):", value="")

# Input for analysis_type
analysis_options = ['All Analysis', 'Support & Resistance Only', 'Price Forecast Only']
analysis_type = st.selectbox("Select Analysis Type:", analysis_options)

# Submit button
if st.button("Run Analysis"):
    if not company_symbol:
        st.warning("Please enter a company symbol.")
    else:
        with st.spinner("Running analysis... Please wait."):
            # Construct the prompt for the Gemini model based on user input and MCP configuration
            prompt = f"""
You are a financial analyst specializing in the Pakistan Stock Exchange (PSX).
Please perform a {analysis_type} on the stock with the ticker symbol '{company_symbol}'.

Your analysis should strictly adhere to the following configuration:
{json.dumps({
    "mcp_configuration": {
      "description": "Configuration for requesting a streamlined price and volume analysis of a PSX stock, providing support/resistance and price movement forecasts.",
      "instructions_for_user": "Please fill in the 'company_symbol' with the PSX ticker (e.g., 'LUCK', 'TRG'). For 'analysis_type', choose one of the following: 'All Analysis', 'Support & Resistance Only', 'Price Forecast Only'.",

      "user_input": {
        "company_symbol": company_symbol,
        "analysis_type": analysis_type
      },

      "default_analysis_parameters": {
        "data_fetch": {
          "historical_periods_available": ["1_month", "6_months", "1_year"],
          "default_period_for_analysis": "1_year",
          "interval": "daily"
        },
        "technical_indicators": {
          "moving_averages": {
            "enable": True,
            "types": ["SMA", "EMA"],
            "periods": [10, 20, 50, 200]
          },
          "rsi": {
            "enable": True,
            "period": 14,
            "overbought_level": 70,
            "oversold_level": 30
          },
          "macd": {
            "enable": True,
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
          },
          "bollinger_bands": {
            "enable": True,
            "period": 20,
            "std_dev_multiplier": 2
          },
          "volume_indicators": {
            "enable": True,
            "obv": True,
            "chaikin_oscillator": True
          }
        },
        "chart_patterns_detection": {
          "enable": True,
          "candlestick_patterns": True,
          "major_chart_patterns": True
        },
        "support_resistance_analysis": {
          "enable": True,
          "method": "pivot_points_and_historical_levels"
        },
        "volatility_assessment": {
          "enable": True,
          "method": "atr",
          "atr_period": 14
        }
      },

      "expected_output_structure_based_on_type": {
        "All Analysis": {
          "sections": [
            "current_market_data",
            "support_resistance_levels",
            "expected_price_movement",
            "technical_indicator_summary",
            "market_considerations"
          ]
        },
        "Support & Resistance Only": {
          "sections": [
            "current_market_data",
            "support_resistance_levels",
            "market_considerations"
          ]
        },
        "Price Forecast Only": {
          "sections": [
            "current_market_data",
            "expected_price_movement",
            "technical_indicator_summary",
            "market_considerations"
          ]
        }
      },

      "output_preferences": {
        "report_format": "Structured Text",
        "include_disclaimer": True
      }
    }
}, indent=2)}

Provide a detailed report in a structured text format based on the above configuration.
"""
            try:
                response = model.generate_content(prompt)
                # Display the response from Gemini
                st.subheader(f"Analysis for {company_symbol}")
                st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred while generating the analysis: {e}")
