
This project helps to export send bulk email from a google account

## Setup

### Install the required packages
```
pip install -r requirements.txt
```
### Tokens
We need to get the google o auth credentials and keep it under `data/input/credentials.json` 

## Running the application

### Generating google api token
```
python -m src.token_generator'
```
### Exporting bulk email
```
python -m src.export_bulk_email'
```
It will ask for a date range between which you want the mail to be fetched.
The `start_date` is the date from which the code should start looking from.
The `end_date` is the end date till which the code will look upon

- Please ensure the date is in `yyyy/mm/dd` format
- Example: `2024/07/04`

### Sending Standard Email
After successfully exporting the email we can send standard email to the users.
```
python -m src.standard_mail_sender
```
### Sending bulk reply to the message received
We can also reply to the emails we get on bulk using 
```
python -m src.bulk_reply_to_email
```

### Re-sending mails
We can resend mail to the email again using
```
python -m src.re_send_email.py
```



