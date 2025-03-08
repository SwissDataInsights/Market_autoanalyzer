import warnings
warnings.filterwarnings("ignore", "Attempting to set identical low and high ylims.*")

import os
import yaml
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load companies from settings.yml
with open("settings.yml", "r") as file:
    config = yaml.safe_load(file)
companies = config["companies"]

# Function to calculate the RSI index
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Set the ratio for Bollinger Bands
band_width_factor = 1.5

historical_dir = 'historical_quotes'
# Define the expected column names
column_names = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume", "RSI", "Median_6"]

# Creating a PDF file in which we will save all charts
with PdfPages('SMI_Report.pdf') as pdf:
    for symbol, company_name in companies.items():
        # Load daily data (D1)
        file_path_d1 = os.path.join(historical_dir, f"{company_name}_data_D1.csv")
        if not os.path.exists(file_path_d1):
            print(f"No data for {company_name}. The file does not exist.")
            continue
        data_d1 = pd.read_csv(file_path_d1, index_col='Date', parse_dates=True)
        data_d1 = data_d1.tail(100)  # Limit to the last 100 observations

        # Load weekly data (W1)
        file_path_1w = os.path.join(historical_dir, f"{company_name}_data_W1.csv")
        if not os.path.exists(file_path_1w):
            print(f"No data for {company_name}. The file does not exist.")
            continue
        data_1w = pd.read_csv(file_path_1w, index_col='Date', parse_dates=True)

        # Recalculate 6-period median for daily and weekly data based on 'Close'
        data_d1['6_Period_Median_D1'] = data_d1['Close'].rolling(window=6).median()
        data_1w['6_Period_Median_W1'] = data_1w['Close'].rolling(window=6).median()

        # Calculate standard deviation on weekly data for Bollinger Bands
        data_1w['Rolling_Std'] = data_1w['Close'].rolling(window=6).std()
        data_1w['Upper_Bollinger'] = data_1w['6_Period_Median_W1'] + band_width_factor * data_1w['Rolling_Std']
        data_1w['Lower_Bollinger'] = data_1w['6_Period_Median_W1'] - band_width_factor * data_1w['Rolling_Std']

        # Align weekly data to the same index as daily data
        data_1w_reindexed = data_1w.reindex(data_d1.index, method='ffill')

        # Recalculate RSI for daily data
        data_d1['RSI'] = calculate_rsi(data_d1)
        data_d1.index = pd.to_datetime(data_d1.index)

        # Retrieve last values with appropriate rounding
        if symbol == 'EURUSD=X':
            last_median_d1 = round(data_d1['6_Period_Median_D1'].iloc[-1], 5)
            last_median_w1 = round(data_1w_reindexed['6_Period_Median_W1'].iloc[-1], 5)
            last_upper_bollinger = round(data_1w_reindexed['Upper_Bollinger'].iloc[-1], 5)
            last_lower_bollinger = round(data_1w_reindexed['Lower_Bollinger'].iloc[-1], 5)
        else:
            last_median_d1 = round(data_d1['6_Period_Median_D1'].iloc[-1], 2)
            last_median_w1 = round(data_1w_reindexed['6_Period_Median_W1'].iloc[-1], 2)
            last_upper_bollinger = round(data_1w_reindexed['Upper_Bollinger'].iloc[-1], 2)
            last_lower_bollinger = round(data_1w_reindexed['Lower_Bollinger'].iloc[-1], 2)

        # Prepare additional plots for median, Bollinger Bands, and RSI
        ap = [
            mpf.make_addplot(data_d1['6_Period_Median_D1'], color='orange',
                             label=(f'6-Period Median D1: {last_median_d1:.5f}' if symbol=='EURUSD=X'
                                    else f'6-Period Median D1: {last_median_d1:.2f}')),
            mpf.make_addplot(data_1w_reindexed['6_Period_Median_W1'], color='purple',
                             label=(f'6-Period Median W1: {last_median_w1:.5f}' if symbol=='EURUSD=X'
                                    else f'6-Period Median W1: {last_median_w1:.2f}')),
            mpf.make_addplot(data_1w_reindexed['Upper_Bollinger'], color='green', linestyle='dashed',
                             label=(f'Upper Bollinger W1: {last_upper_bollinger:.5f}' if symbol=='EURUSD=X'
                                    else f'Upper Bollinger W1: {last_upper_bollinger:.2f}')),
            mpf.make_addplot(data_1w_reindexed['Lower_Bollinger'], color='red', linestyle='dashed',
                             label=(f'Lower Bollinger W1: {last_lower_bollinger:.5f}' if symbol=='EURUSD=X'
                                    else f'Lower Bollinger W1: {last_lower_bollinger:.2f}')),
            mpf.make_addplot(data_d1['RSI'], color='blue', panel=1, ylabel='RSI')
        ]

        # Define marketcolors: green for up candles, red for down candles
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        custom_style = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

        # For forex instruments (e.g., EURUSD=X), if Volume is missing or zero, set it to a constant value
        if symbol == 'EURUSD=X':
            if 'Volume' not in data_d1.columns or (data_d1['Volume'] == 0).all():
                data_d1['Volume'] = 1
            fig, ax = mpf.plot(data_d1, type='candle', style=custom_style, addplot=ap, volume=False,
                               ylabel='Price', returnfig=True)
        else:
            fig, ax = mpf.plot(data_d1, type='candle', style=custom_style, addplot=ap, volume=True,
                               ylabel='Price', returnfig=True)

        # Remove date labels from x-axis on all axes
        for axis in fig.axes:
            axis.set_xticklabels([])

        ax[0].set_title(company_name, fontsize=10)
        handles, labels = ax[0].get_legend_handles_labels()
        ax[0].legend(handles=handles, labels=labels, loc='lower left', fontsize=8)

        pdf.savefig(fig)
        plt.close(fig)
