import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import yaml
import logging

# Logging configuration
logging.basicConfig(
    filename="email_log.log",  # Log file
    level=logging.INFO,  # Logging level
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Function to send an email with an attachment
def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_file):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Adding a date to the message subject
    current_date = datetime.now().strftime("%Y-%m-%d")
    msg['Subject'] = f"{subject} - {current_date}"

    # Adding message content
    msg.attach(MIMEText(body, 'plain'))

    # Open a PDF file and add it as an attachment
    with open(attachment_file, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_file)}')
        msg.attach(part)

    # Login to the SMTP server
    try:
        server = smtplib.SMTP('asmtp.mail.hostpoint.ch', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email. Error: {e}")
        print(f"Failed to send email. Error: {e}")
    finally:
        server.quit()

# Function to load email settings with fallback
def load_email_settings():
    try:
        with open("settings.yml", "r") as file:
            config = yaml.safe_load(file)
            logging.info("Loaded settings from settings.yml")
            return config
    except FileNotFoundError:
        logging.warning("settings.yml not found. Attempting to load settings_pv.yml.")
        try:
            with open("settings_pv.yml", "r") as file:
                config = yaml.safe_load(file)
                logging.info("Loaded settings from settings_pv.yml")
                return config
        except FileNotFoundError:
            logging.error("Neither settings.yml nor settings_pv.yml could be found. Exiting.")
            raise

# Main function
if __name__ == "__main__":
    try:
        # Load email settings
        config = load_email_settings()
        sender_email = config["sender_email"]
        sender_password = config["sender_password"]
        recipient_email = config["recipient_email"]
        subject = config["subject"]
        body = config["body"]
        attachment_file = config["attachment_file"]

        # Send the email
        send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_file)

    except FileNotFoundError:
        print("No valid settings file found.")
    except KeyError as e:
        logging.error(f"Missing required key in the settings file: {e}")
        print(f"Missing required key in the settings file: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
