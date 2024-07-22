import json
from db_setup import Email, session

def load_rules(filename='rules.json'):
    with open(filename, 'r') as file:
        return json.load(file)

def process_emails():
    rules = load_rules()['rules']
    emails = session.query(Email).all()

if __name__ == '__main__':
    process_emails()
