import base64
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
import mimetypes
import os
import csv

from src.path_setup import input_dir, output_dir
from src.template.email_template import get_email_body
from src.bulk_reply_to_email import mail_block_team

def re_reply_to_failed_emails(csv_file_path):
    file_attachments = [] 
    body = get_email_body()
    subject = "Reply email"

    retry_log = []

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['sent'] == '0':  # Check for failed emails
                message_id = row['ID']
                receiver_email = row['Sender Email']
                try:
                    is_mail_sent = mail_block_team(file_attachments, body=body, subject=subject, receiver_email=receiver_email, message_id=message_id)
                except HttpError as http_err:
                    print(f"Retry: HTTP error occurred while sending email to {receiver_email} for message ID {message_id}: {http_err}")
                    is_mail_sent = False
                except Exception as ex:
                    print(f"Retry: General error occurred while sending email to {receiver_email} for message ID {message_id}: {ex}")
                    is_mail_sent = False

                retry_log.append({
                    'Sender Email': receiver_email,
                    'ID': message_id,
                    'sent': 1 if is_mail_sent else 0
                })

                if is_mail_sent:
                    print(f"Retry: Reply sent to {receiver_email} for message ID {message_id}")
                else:
                    print(f"Retry: Failed to send reply to {receiver_email} for message ID {message_id}")

    # Read original sent_mail.csv
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        original_log = list(reader)

    # Update original log with retry log
    for retry_entry in retry_log:
        for original_entry in original_log:
            if retry_entry['ID'] == original_entry['ID']:
                original_entry['sent'] = retry_entry['sent']

    # Write updated log back to sent_mail.csv
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Sender Email', 'ID', 'sent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log in original_log:
            writer.writerow(log)


if __name__ == '__main__':
    csv_file_path = os.path.join(output_dir, 'sent/sent_mail.csv')
    re_reply_to_failed_emails(csv_file_path)
