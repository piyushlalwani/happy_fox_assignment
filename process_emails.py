import json
from db_setup import Email, session
from fetch_emails import authenticate_gmail

def load_rules(filename='rules.json'):
    with open(filename, 'r') as file:
        return json.load(file)

def process_emails(service):
    rules = load_rules()['rules']
    emails = session.query(Email).all()

    for email in emails:
        for rule in rules:
            if rule['predicate'] == 'contains' and rule['value'] in getattr(email, rule['field']):
                if rule['action'] == 'mark_as_read':
                    mark_as_read(service, email.email_id)

def mark_as_read(service, email_id):
    service.users().messages().modify(
        userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}
    ).execute()

if __name__ == '__main__':
    service = authenticate_gmail()
    process_emails(service)
