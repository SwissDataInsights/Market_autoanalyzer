import time
import datetime
import pytz
import subprocess
import sys
import logging

# Logging configuration
logging.basicConfig(
    filename="script_log.log",  # Log file
    level=logging.INFO,  # Logging level
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_scripts():
    python_path = sys.executable
    has_run_today_12 = False

    # Set timezone to Warsaw
    warsaw_tz = pytz.timezone("Europe/Warsaw")

    while True:
        # Get current date and time in the Warsaw timezone
        now = datetime.datetime.now(warsaw_tz)
        current_hour = now.hour
        current_minute = now.minute
        current_day = now.weekday()

        if current_day < 6:  # Monday - Saturday
            if current_hour == 5 and current_minute == 0 and not has_run_today_12:
                try:
                    logging.info("Starting script execution at 05:00")

                    # Execute scripts sequentially
                    subprocess.run([python_path, "smi_index.py"], check=True)
                    logging.info("Script smi_index.py completed successfully")

                    subprocess.run([python_path, "bands.py"], check=True)
                    logging.info("Script bands.py completed successfully")

                    subprocess.run([python_path, "send_email.py"], check=True)
                    logging.info("Script send_email.py completed successfully")

                    # Set flag to prevent scripts from running again at 05:00 on the same day
                    has_run_today_12 = True

                except subprocess.CalledProcessError as e:
                    logging.error(f"Error during script execution: {e}")

                except Exception as e:
                    logging.error(f"Unexpected error: {e}")

        # Reset the flag at midnight
        if current_hour == 0 and current_minute == 0:
            has_run_today_12 = False
            logging.info("Flag has_run_today_12 reset at midnight")

        # Check the time every minute
        time.sleep(60)

if __name__ == "__main__":
    logging.info("Starting the main loop")
    run_scripts()
