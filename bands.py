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

# Creating a PDF file in which we will save all charts
with PdfPages('SMI_Report.pdf') as pdf:
    for i, (symbol, company_name) in enumerate(companies.items()):
        file_path_d1 = os.path.join(historical_dir, f"{company_name}_data_D1.csv")
        if not os.path.exists(file_path_d1):
            print(f"No data for {company_name}. The file does not exist.")
            continue
        data_d1 = pd.read_csv(file_path_d1, index_col=0, parse_dates=True)

        data_d1 = data_d1.tail(100)  # Limited to the last 100 observations

        file_path_1w = os.path.join(historical_dir, f"{company_name}_data_W1.csv")
        if not os.path.exists(file_path_1w):
            print(f"No data for {company_name}. The file does not exist")
            continue
        data_1w = pd.read_csv(file_path_1w, index_col=0, parse_dates=True)

        # Calculate the median of 6 periods for daily data (D1)
        data_d1['6_Period_Median_D1'] = data_d1['Close'].rolling(window=6).median()

        # Calculate the median of 6 periods for weekly data (W1)
        data_1w['6_Period_Median_W1'] = data_1w['Close'].rolling(window=6).median()

        # Calculate the standard deviation for Bollinger Bands
        data_1w['Rolling_Std'] = data_1w['Close'].rolling(window=6).std()

        # Determine the upper and lower bands based on Bollinger Bands with a modified coefficient
        data_1w['Upper_Bollinger'] = data_1w['6_Period_Median_W1'] + band_width_factor * data_1w['Rolling_Std']
        data_1w['Lower_Bollinger'] = data_1w['6_Period_Median_W1'] - band_width_factor * data_1w['Rolling_Std']

        # Align weekly data to the same index as daily data
        data_1w_reindexed = data_1w.reindex(data_d1.index, method='ffill')

        data_d1['RSI'] = calculate_rsi(data_d1)

        data_d1.index = pd.to_datetime(data_d1.index)

        # Retrieving the last median value and bands with appropriate rounding for EURUSD
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

        # Create additional data for drawing (median, bands, RSI)
        ap = [
            mpf.make_addplot(data_d1['6_Period_Median_D1'], color='orange', label=f'6-Period Median D1: {last_median_d1:.5f}' if symbol == 'EURUSD=X' else f'6-Period Median D1: {last_median_d1:.2f}'),
            mpf.make_addplot(data_1w_reindexed['6_Period_Median_W1'], color='purple', label=f'6-Period Median W1: {last_median_w1:.5f}' if symbol == 'EURUSD=X' else f'6-Period Median W1: {last_median_w1:.2f}'),
            mpf.make_addplot(data_1w_reindexed['Upper_Bollinger'], color='green', linestyle='dashed', label=f'Upper Bollinger W1: {last_upper_bollinger:.5f}' if symbol == 'EURUSD=X' else f'Upper Bollinger W1: {last_upper_bollinger:.2f}'),
            mpf.make_addplot(data_1w_reindexed['Lower_Bollinger'], color='red', linestyle='dashed', label=f'Lower Bollinger W1: {last_lower_bollinger:.5f}' if symbol == 'EURUSD=X' else f'Lower Bollinger W1: {last_lower_bollinger:.2f}'),
            mpf.make_addplot(data_d1['RSI'], color='blue', panel=1, ylabel='RSI')
        ]

        # Check if the instrument is EURUSD=X and disable volume, otherwise enable volume
        if symbol == 'EURUSD=X':
            fig, ax = mpf.plot(data_d1, type='candle', style='charles', addplot=ap, volume=False,
                               ylabel='Price', returnfig=True)
        else:
            fig, ax = mpf.plot(data_d1, type='candle', style='charles', addplot=ap, volume=True,
                               ylabel='Price', returnfig=True)

        # Title font
        ax[0].set_title(company_name, fontsize=10)

        # Adding a legend in the lower left corner with a smaller font
        handles, labels = ax[0].get_legend_handles_labels()
        ax[0].legend(handles=handles, labels=labels, loc='lower left', fontsize=8)

        # Saving the chart to a PDF file
        pdf.savefig(fig)
        plt.close(fig)