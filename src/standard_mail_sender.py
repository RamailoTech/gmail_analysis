import base64
import csv
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

def mail_block_team(file_attachments, body, subject, receiver_email):
    '''
    Test email sending function 
    '''
    creds = Credentials.from_authorized_user_file(os.path.join(input_dir, "token.json"))

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = receiver_email
        mimeMessage['subject'] = subject
        mimeMessage.attach(MIMEText(body, 'html'))

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
        
        message = service.users().messages().send(
            userId='me',
            body={'raw': raw_string}).execute()
        
        if message:
            return True
    except Exception as ex:
        print(f"Error occurred while sending email to {receiver_email}: {ex}")
        return False

def send_emails_from_csv(input_csv, output_csv):
    file_attachments = []  
    body = get_email_body()
    subject = "Test email"

    emails = set()
    with open(input_csv, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            emails.add(row['Sender Email'])

    results = []

    for email in emails:
        is_mail_sent = mail_block_team(file_attachments, body=body, subject=subject, receiver_email=email)
        results.append({'Email': email, 'Sent': 1 if is_mail_sent else 0})
        if is_mail_sent:
            print(f"Email sent to {email}")
        else:
            print(f"Failed to send email to {email}")

    with open(output_csv, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['Email', 'Sent'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    input_csv = os.path.join(output_dir, 'manish@ramailo.tech/2024-07-03_to_2024-07-04.csv')
    output_csv = os.path.join(output_dir, 'manish@ramailo.tech/standard_mail_sent.csv')
    send_emails_from_csv(input_csv, output_csv)
