import re

def extract_email(email_str):
    pttrn = r'<(.*?)>'
    match = re.search(pttrn, email_str)
    if match:
        return match.group(1)
    return None
