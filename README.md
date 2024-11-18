```markdown
# Swiss Stock Market Analysis

This project automates the analysis and reporting of stock data for companies listed in 
the Swiss Market Index (SMI). It collects historical price data, calculates technical 
indicators (like RSI and Bollinger Bands), generates charts, and automates the emailing 
of reports. 

## Features

- **Data Collection**: Downloads daily and weekly stock price data for a predefined list of 
  Swiss companies from Yahoo Finance.
- **Technical Analysis**: Computes technical indicators such as:
  - Relative Strength Index (RSI)
  - 6-period median (median of the last 6 price points)
  - Bollinger Bands (based on a 6-period median and a customizable width factor)
- **Chart Generation**: Creates detailed candlestick charts with overlays for indicators and 
  saves them in a PDF report.
- **Automated Emailing**: Sends the generated PDF report via email.

## Project Structure

- **`main.py`**: Main entry point that manages overall data flow and processing.
- **`smi_index.py`**: Retrieves daily and weekly data for each company in the SMI, calculates RSI 
  and median values, and saves the results in CSV format.
- **`bands.py`**: Generates and saves the technical analysis charts for each company’s stock data, 
  including median prices and Bollinger Bands.
- **`send_email.py`**: Sends the PDF report as an email attachment to a specified recipient.

## Prerequisites

- Python 3.x
- Install dependencies with `pip install -r requirements.txt`.

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```
2. Set up a virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Email Configuration

To enable automated emailing, update the following in `send_email.py`:

- **Sender email and password**: Replace `sender_email` and `sender_password` with your email credentials.
- **Recipient email**: Replace `recipient_email` with the desired recipient address.

> **Note**: For security, it’s recommended to use environment variables or a secrets manager to store 
> sensitive information instead of hardcoding credentials in the code.

### Stocks List

Update the `companies` dictionary in `smi_index.py` to modify the list of stocks you want to analyze.

## Usage

1. **Fetch Stock Data**:
   Run `smi_index.py` to fetch historical data and save it in CSV files:
   ```bash
   python smi_index.py
   ```

2. **Generate Analysis Report**:
   Run `bands.py` to generate charts and save them in a PDF report:
   ```bash
   python bands.py
   ```

3. **Send Report via Email**:
   Run `send_email.py` to email the report:
   ```bash
   python send_email.py
   ```

Alternatively, to execute the entire process in one go, run:
   ```bash
   screen
   python3 main.py
   ```
You can check if the script is working using the command:
   ```bash
  ps aux | grep python
   ```
## Example

- **CSV Output**: `historical_quotes/ABB_Ltd_data_D1.csv` – contains the daily stock data 
with calculated RSI and 6-period median.
- **PDF Report**: `SMI_Report.pdf` – includes technical analysis charts for each stock.

## Future Enhancements

- Add more technical indicators.
- Schedule automated daily/weekly data updates and report generation.
- Implement error handling for data fetching failures.
- Enhance email security by integrating OAuth for authentication.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 2, June 1991.

See the LICENSE file for details.
