import os
import yaml
import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

# Function to calculate RSI rounded to whole units
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.round(0)

# Function to calculate the 6-period median
def calculate_rolling_median(data, window=6):
    return data['Close'].rolling(window=window).median()

# Load companies from settings.yml
try:
    with open("settings.yml", "r") as file:
        config = yaml.safe_load(file)
        companies = config["companies"]
except FileNotFoundError:
    logging.warning("settings.yml not found. Attempting to load settings_pv.yml.")
    try:
        # Fallback to settings_pv.yml
        with open("settings_pv.yml", "r") as file:
            config = yaml.safe_load(file)
            companies = config["companies"]
    except FileNotFoundError:
        logging.error("Neither settings.yml nor settings_pv.yml could be found. Exiting.")
        exit()

# Create a directory for quote files if it does not already exist
output_dir = 'historical_quotes'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set the date range - the last 4 years (approx. 1440 days)
end_date = datetime.today()
start_date = end_date - timedelta(days=1440)

# Iterate through each company in the dictionary
for symbol, company_name in companies.items():
    output_file_d1 = os.path.join(output_dir, f"{company_name}_data_D1.csv")
    output_file_1w = os.path.join(output_dir, f"{company_name}_data_W1.csv")

    # Download daily data (D1) with auto_adjust enabled and progress turned off
    data_d1 = yf.download(
        symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    # Check if daily data has been downloaded
    if not data_d1.empty:
        # Ensure the index is in DatetimeIndex format
        data_d1.index = pd.to_datetime(data_d1.index)
        data_d1.index.name = "Date"
        data_d1.index = data_d1.index.tz_localize(None)

        # Create 'Adj Close' column if it is missing (auto_adjust=True may remove it)
        if 'Adj Close' not in data_d1.columns:
            data_d1['Adj Close'] = data_d1['Close']

        # Calculation of RSI and 6-period Median
        data_d1['RSI'] = calculate_rsi(data_d1)
        data_d1['Median_6'] = calculate_rolling_median(data_d1)

        # Delete the oldest 13 rows (to account for rolling window calculations)
        data_d1 = data_d1.iloc[13:]

        # Set the columns in the desired order and rename them
        data_d1 = data_d1[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'RSI', 'Median_6']]
        data_d1.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "RSI", "Median_6"]

        # Save daily data to CSV file with the index labeled as "Date"
        data_d1.to_csv(output_file_d1, index_label="Date")
        print(f"Daily data saved to file {output_file_d1}")
    else:
        print(f"Failed to retrieve daily data for {symbol}.")

    # Download weekly data (1W) with auto_adjust enabled and progress turned off
    data_1w = yf.download(
        symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval="1wk",
        auto_adjust=True,
        progress=False
    )

    # Check if weekly data has been downloaded
    if not data_1w.empty:
        # Ensure the index is in DatetimeIndex format
        data_1w.index = pd.to_datetime(data_1w.index)
        data_1w.index.name = "Date"
        data_1w.index = data_1w.index.tz_localize(None)

        # Create 'Adj Close' column if it is missing
        if 'Adj Close' not in data_1w.columns:
            data_1w['Adj Close'] = data_1w['Close']

        # Calculation of RSI and 6-period Median
        data_1w['RSI'] = calculate_rsi(data_1w)
        data_1w['Median_6'] = calculate_rolling_median(data_1w)

        # Remove the oldest 15 rows due to rolling calculations
        data_1w = data_1w.iloc[15:]

        # Set the columns in the desired order and rename them
        data_1w = data_1w[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'RSI', 'Median_6']]
        data_1w.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "RSI", "Median_6"]

        # Save weekly data to CSV file with the index labeled as "Date"
        data_1w.to_csv(output_file_1w, index_label="Date")
        print(f"Weekly data saved to file {output_file_1w}")
    else:
        print(f"Failed to retrieve weekly data for {symbol}.")
