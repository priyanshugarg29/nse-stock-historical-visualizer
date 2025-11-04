# Importing libraries

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

# ALpha_Vantage API Key
ALPHA_VANTAGE_API_KEY = "VLYQFAYWJDA79R9L"

# Month mapping dictionary
month_map = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR",
    5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG",
    9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"
}

# function to fetch historical daily data
def fetch_alpha_vantage_data(symbol):
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    try:
        # Use free daily endpoint (not adjusted) to avoid premium error
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
    grouped = df.groupby(['year', 'month', 'day'])['close'].mean().reset_index()  # use 'close' here
    return grouped

# Plotting monthly data with multiple years
def plot_monthly_data(df, month):
    month_name = month_map.get(month, "UNKNOWN")
    month_data = df[df['month'] == month]
    plt.figure(figsize=(10,6))
    for year in sorted(month_data['year'].unique()):
        yearly_data = month_data[month_data['year'] == year]
        plt.plot(yearly_data['day'], yearly_data['close'], label=str(year))
    plt.title(f'Average Daily Close Price - {month_name}')
    plt.xlabel('Day of Month')
    plt.ylabel('Price (INR)')
    plt.legend(loc = 'best')
    st.pyplot(plt)

# Main Streamlit app interface
def main():
    st.title("BSE Stock Historical Visualizer (Alpha Vantage)")
    symbol = st.text_input("Enter BSE Stock Symbol (e.g., TCS, RELIANCE)").upper() + ".BSE"
    if st.button("Fetch and Visualize"):
        with st.spinner("Fetching data..."):
            df = fetch_alpha_vantage_data(symbol)
            if df is not None and not df.empty:
                processed_df = process_data(df)
                for month in sorted(processed_df['month'].unique()):
                    st.subheader(f"Month: {month_map.get(month)}")
                    month_df = processed_df[processed_df['month'] == month]

                    # Convert month data to CSV
                    csv_data = month_df.to_csv(index=False)

                    # Download button for CSV
                    st.download_button(
                        label=f"Download {month_map.get(month)} Data as CSV",
                        data=csv_data,
                        file_name=f"{symbol}_data_{month_map.get(month)}.csv",
                        mime='text/csv'
                    )

                    # Plot the monthly data
                    plot_monthly_data(processed_df, month)
            else:
                st.error("No data found or API limit reached.")

if __name__ == "__main__":
    main()
