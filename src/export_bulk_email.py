import os
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from src.path_setup import input_dir, output_dir
from email import message_from_bytes
import csv
import re
import time
from datetime import datetime
def export_emails(after=None, before=None):
    creds = Credentials.from_authorized_user_file(os.path.join(input_dir, "token.json"))

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        query = ""
        if after:
            query += f" after:{after}"
        if before:
            query += f" before:{before}"
        
        profile = service.users().getProfile(userId='me').execute()
        user_email = profile['emailAddress']
        

        email_output_dir = os.path.join(output_dir, 'emails')
        os.makedirs(email_output_dir, exist_ok=True)
        
        csv_filename = "exported_data.csv"
        csv_file = os.path.join(email_output_dir, csv_filename)
        
        with open(csv_file, mode='w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Sender Name", "Sender Email", "Subject", "Timestamp", "Is Sent", "Content"])

            next_page_token = None

            while True:
                results = service.users().messages().list(userId='me', q=query, pageToken=next_page_token).execute()
                messages = results.get('messages', [])

                if not messages:
                    print("No more messages found.")
                    break

                print(f"Found {len(messages)} messages on this page.")

                for msg in messages:
                    msg_id = msg['id']
                    print(f"Processing message ID: {msg_id}")
                    message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
                    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
                    mime_msg = message_from_bytes(msg_str)
                    
                    if mime_msg.is_multipart():
                        save_email(mime_msg, msg_id, writer, user_email)
                    else:
                        save_non_multipart_email(mime_msg, msg_id, writer)

                next_page_token = results.get('nextPageToken')
                if not next_page_token:
                    break

                time.sleep(1)

    except HttpError as error:
        print(f"An error occurred: {error}")

def save_email(mime_msg, msg_id, writer, user_email):
    subject = mime_msg['subject']
    sender = mime_msg['from']
    timestamp = mime_msg['date']
    sender_name, sender_email = parse_sender(sender)
    content = get_email_content(mime_msg)
    is_sent = 1 if user_email in sender_email else 0

    writer.writerow([msg_id, sender_name, sender_email, subject, timestamp, is_sent, content])

    print(f"Email with subject '{subject}' written to CSV")


def save_non_multipart_email(mime_msg, msg_id, writer):
    sender = mime_msg['from'] if 'from' in mime_msg else '(Unknown Sender)'
    timestamp = mime_msg['date'] if 'date' in mime_msg else '(Unknown Date)'
    sender_name, sender_email = parse_sender(sender)
    is_sent = 0

    writer.writerow([msg_id, sender_name, sender_email, '(No Subject)', timestamp, is_sent, '(No Content)'])

    print(f"Non-multipart email ID {msg_id} written to CSV")

def parse_sender(sender):
    match = re.match(r'(.*)<(.*)>', sender)
    if match:
        name = match.group(1).strip()
        email = match.group(2).strip()
    else:
        name = ""
        email = sender
    return name, email

def get_email_content(mime_msg):
    for part in mime_msg.walk():
        if part.get_content_type() == "text/plain":
            try:
                return part.get_payload(decode=True).decode('utf-8')
            except UnicodeDecodeError:
                return part.get_payload(decode=True).decode('latin-1', errors='ignore')
    return ""

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y/%m/%d")
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    while True:
        after = input("Enter the start date (YYYY/MM/DD): ")
        before = input("Enter the end date (YYYY/MM/DD): ")
        if validate_date(after) and validate_date(before):
            break
        else:
            print("Invalid date format. Please enter dates in YYYY/MM/DD format.")

    export_emails(after=after, before=before)
