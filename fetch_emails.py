from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import pickle
from db_setup import Email, session
import email
from helper import extract_email

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    credentials = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        credentials = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build('gmail', 'v1', credentials=credentials)

def fetch_emails(service, session = session):
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        email_id = msg_data['id']
        headers = msg_data['payload']['headers']
        from_email = extract_email(next(header['value'] for header in headers if header['name'] == 'From'))
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        message = msg_data['snippet']
        date_str = next(header['value'] for header in headers if header['name'] == 'Date')
        received_date = email.utils.parsedate_to_datetime(date_str)

        email_record = Email(email_id=email_id, from_email=from_email, subject=subject, message=message, received_date=received_date)
        session.add(email_record)
    session.commit()
    print("Fetching of records completed")

if __name__ == '__main__':
    service = authenticate_gmail()
    fetch_emails(service)
