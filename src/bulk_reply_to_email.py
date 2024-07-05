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
from src.path_setup import input_dir, output_dir
from src.template.email_template import get_email_body
import csv


def mail_block_team(file_attachments, body, subject, receiver_email, message_id):
    '''
    Test email sending function 
    '''
    creds = Credentials.from_authorized_user_file(os.path.join(input_dir, "token.json"))

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # create email message
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = receiver_email
        mimeMessage['subject'] = subject
        mimeMessage.attach(MIMEText(body, 'html'))
        
        # Attach files
        for attachment in file_attachments:
            content_type, encoding = mimetypes.guess_type(attachment)
            main_type, sub_type = content_type.split('/', 1)
            file_name = os.path.basename(attachment)
        
            with open(attachment, 'rb') as f:
                myFile = MIMEBase(main_type, sub_type)
                myFile.set_payload(f.read())
                myFile.add_header('Content-Disposition', 'attachment', filename=file_name)
                encoders.encode_base64(myFile)
                mimeMessage.attach(myFile)
        
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
        
        # Use the message ID to reply to the email
        message = service.users().messages().send(
            userId='me',
            body={
                'raw': raw_string,
                'threadId': message_id
            }).execute()
        
        if message:
            return True
    except Exception as ex:
        print(f"Error occurred while sending email to {receiver_email}: {ex}")
        return False
    
def send_replies_from_csv(csv_file_path):
    file_attachments = [] 
    body = get_email_body()
    subject = ""

    sent_mail_log = []
    
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            message_id = row['ID']
            receiver_email = row['Sender Email']
            is_mail_sent = mail_block_team(file_attachments, body=body, subject=subject, receiver_email=receiver_email, message_id=message_id)
            sent_mail_log.append({
                'Sender Email': receiver_email,
                'ID': message_id,
                'sent': 1 if is_mail_sent else 0
            })
            if is_mail_sent:
                print(f"Reply sent to {receiver_email} for message ID {message_id}")
            else:
                print(f"Failed to send reply to {receiver_email} for message ID {message_id}")

    # Write sent mail log to CSV
    sent_mail_csv_path = os.path.join(output_dir, 'sent/sent_mail.csv')
    with open(sent_mail_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Sender Email', 'ID', 'sent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log in sent_mail_log:
            writer.writerow(log)


if __name__ == '__main__':
    csv_file_path = os.path.join(output_dir, 'emails/exported_data.csv')
    send_replies_from_csv(csv_file_path)
