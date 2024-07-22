import json
from db_setup import Email, session
from fetch_emails import authenticate_gmail
from helper import extract_email

def load_rules(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def fetch_db_value(email_record, column):
    value = getattr(email_record, column)
    if column == 'from_email':
        return extract_email(value)
    elif column == 'received_date':
        return value.strftime('%Y-%m-%d')
    return value

def check_condition(email_record, field, predicate, value):
    db_value = fetch_db_value(email_record, field)
    if field in ["from_email", "subject", "message"]:
        if predicate == "contains":
            return value in db_value
        elif predicate == "does not contain":
            return value not in db_value
        elif predicate == "equals":
            return value == db_value
        elif predicate == "does not equal":
            return value != db_value
    elif field == "received_date":
        if predicate == "less than":
            return value < db_value
        elif predicate == "greater than":
            return value > db_value
        elif predicate == "equal to":
            return value == db_value

    return False

def apply_rules(email_record, rules, parent_condition):
    if parent_condition == "All":
        return all(check_condition(email_record, rule['field'], rule['predicate'], rule['value']) for rule in rules)
    elif parent_condition == "Any":
        return any(check_condition(email_record, rule['field'], rule['predicate'], rule['value']) for rule in rules)
    return False

def move_message(service, email_id, folder_name):
    service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [folder_name], 'removeLabelIds': ['INBOX']}).execute()

def mark_as_read(service, email_id):
    service.users().messages().modify(
        userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}
    ).execute()

def execute_actions(email_id, actions, service):
    for action in actions:
        if action['action'] == "mark_as_read":
            mark_as_read(service, email_id)
        elif action['action'] == "move_message":
            folder_name = action['folder']
            move_message(service, email_id, folder_name)

def process_emails(service, rules_config):
    rules = rules_config['rules']
    parent_condition = rules_config['parent_condition']
    actions = rules_config['actions']
    emails = session.query(Email).all()
    for email_record in emails:
        if apply_rules(email_record, rules, parent_condition):
            execute_actions(getattr(email_record, 'email_id'), actions, service)

if __name__ == '__main__':
    service = authenticate_gmail()
    # rules_config = load_rules("rules_any.json")
    # process_emails(service, rules_config)
    rules_config = load_rules("rules_all.json")
    process_emails(service, rules_config)
