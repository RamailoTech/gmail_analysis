import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.path_setup import input_dir
SCOPES = ["https://www.googleapis.com/auth/gmail.send","https://www.googleapis.com/auth/gmail.readonly"]


def generate_token():

  creds = None
  token_path = os.path.join(input_dir, "token.json")
  creds_path = os.path.join(input_dir, "credentials.json")

  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          creds_path, SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open(token_path, "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  generate_token()