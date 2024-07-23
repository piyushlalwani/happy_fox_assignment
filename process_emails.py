import json
from db_setup import Email, session
from fetch_emails import authenticate_gmail
from sqlalchemy import or_, and_
from sqlalchemy.sql.elements import BooleanClauseList, BinaryExpression

def load_rules(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def filter_conditions(rules):
    conditions = []
    for rule in rules:
        field = getattr(Email, rule['field'])
        predicate = rule['predicate']
        value = rule['value']

        if rule['field'] in ["from_email", "subject", "message"]:
            if predicate == "contains":
                conditions.append(field.like(f"%{value}%"))
            elif predicate == "does not contain":
                conditions.append(~field.like(f"%{value}%"))
            elif predicate == "equals":
                conditions.append(field == value)
            elif predicate == "does not equal":
                conditions.append(field != value)
        elif rule['field'] == "received_date":
            if predicate == "less than":
                conditions.append(field < value)
            elif predicate == "greater than":
                conditions.append(field > value)
            elif predicate == "equal to":
                conditions.append(field == value)
    return conditions

def is_condition_empty(condition):
    if isinstance(condition, BooleanClauseList):
        return len(condition.clauses) == 0
    elif isinstance(condition, BinaryExpression):
        return False
    return True

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

def process_emails(service, rules_config, session = session):
    rules = rules_config['rules']
    parent_condition = rules_config['parent_condition']
    actions = rules_config['actions']
    filter_condition = and_(*filter_conditions(rules)) if parent_condition == "All" else or_(*filter_conditions(rules))

    if not is_condition_empty(filter_condition):
        emails = session.query(Email).filter(filter_condition).all()
        for email_record in emails:
            execute_actions(getattr(email_record, 'email_id'), actions, service)
    print("Processing Completed")

if __name__ == '__main__':
    service = authenticate_gmail()
    # rules_config = load_rules("rules_any.json")
    # process_emails(service, rules_config)
    rules_config = load_rules("rules_all.json")
    process_emails(service, rules_config)
