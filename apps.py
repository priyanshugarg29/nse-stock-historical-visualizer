# Importing libraries

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

# ALpha_Vantage API Key
ALPHA_VANTAGE_API_KEY = "VLYQFAYWJDA79R9L"

# function to fetch historical daily data
def fetch_alpha_vantage_data(symbol):
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    try:
        # Use free daily endpoint instead of adjusted data
        data, meta = ts.get_daily(symbol=symbol, outputsize='full')
        data.reset_index(inplace=True)
        data.rename(columns={'date': 'date', '4. close': 'close'}, inplace=True)
        data['date'] = pd.to_datetime(data['date'])
        return data[['date', 'close']]
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

# Processing data for plotting
def process_data(df):
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    grouped = df.groupby(['year', 'month', 'day'])['adjusted_close'].mean().reset_index()
    return grouped

# Plotting monthly data with multiple years

def plot_monthly_data(df, month):
    month_data = df[df['month'] == month]
    plt.figure(figsize=(10,6))
    for year in sorted(month_data['year'].unique()):
        yearly_data = month_data[month_data['year'] == year]
        plt.plot(yearly_data['day'], yearly_data['adjusted_close'], label=str(year))
    plt.title(f'Average Daily Adjusted Close Price - Month {month}')
    plt.xlabel('Day of Month')
    plt.ylabel('Price (INR)')
    plt.legend()
    st.pyplot(plt)

# Main Streamlit app interface

def main():
    st.title("NSE Stock Historical Visualizer (Alpha Vantage)")
    symbol = st.text_input("Enter NSE Stock Symbol (e.g., TCS, RELIANCE)").upper()
    if st.button("Fetch and Visualize"):
        with st.spinner("Fetching data..."):
            df = fetch_alpha_vantage_data(symbol)
            if df is not None and not df.empty:
                processed_df = process_data(df)
                for month in sorted(processed_df['month'].unique()):
                    plot_monthly_data(processed_df, month)
            else:
                st.error("No data found or API limit reached.")

if __name__ == "__main__":
    main()

