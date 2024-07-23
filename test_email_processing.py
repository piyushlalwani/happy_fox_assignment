import unittest
from unittest.mock import patch, MagicMock
from fetch_emails import fetch_emails
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Email
from process_emails import process_emails
from datetime import datetime

TEST_DB_URL = 'sqlite:///test_email.db'

engine = create_engine(TEST_DB_URL)
Session = sessionmaker(bind=engine)

class TestEmailProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(engine)
    
    def setUp(self):
        self.session = Session()
    
    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    
    def insert_test_email(self, email_id, from_email, subject, message, received_date):
        email_record = Email(
            email_id=email_id,
            from_email=from_email,
            subject=subject,
            message=message,
            received_date=received_date
        )
        self.session.add(email_record)
        self.session.commit()

    def test_fetch_emails(self):
        mock_service = MagicMock()

        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': '1'}, {'id': '2'}]
        }

        mock_service.users().messages().get().execute.side_effect = [
            {
                'id': '1',
                'snippet': 'Message 1',
                'payload': {
                    'headers': [
                        {'name': 'From', 'value': 'AZ <az@amazon.com>'},
                        {'name': 'Subject', 'value': 'Subject 1'},
                        {'name': 'Date', 'value': 'Mon, 22 Jul 2024 02:24:22 +0530 (IST)'}
                    ]
                },
            },
            {
                'id': '2',
                'snippet': 'Message 2',
                'payload': {
                    'headers': [
                        {'name': 'From', 'value': 'New <new@amazon.com>'},
                        {'name': 'Subject', 'value': 'Subject 2'},
                        {'name': 'Date', 'value': 'Tue, 21 Jul 2024 03:24:22 +0530 (IST)'}
                    ]
                },
            }
        ]

        fetch_emails(mock_service, self.session)

        email_record_1 = self.session.query(Email).filter_by(email_id='1').first()
        self.assertIsNotNone(email_record_1)
        self.assertEqual(email_record_1.from_email, 'az@amazon.com')
        self.assertEqual(email_record_1.subject, 'Subject 1')
        self.assertEqual(email_record_1.message, 'Message 1')
    
    @patch('process_emails.load_rules')
    def test_process_emails(self, mock_load_rules):
        mock_service = MagicMock()

        rules_config = {
            "rules": [
                {
                    "field": "from_email",
                    "predicate": "contains",
                    "value": "amazon"
                }
            ],
            "parent_condition": "All",
            "actions": [
                {
                    "action": "mark_as_read"
                },
                {
                    "action": "move_message",
                    "folder": "IMPORTANT"
                }
            ]
        }
        mock_load_rules.return_value = rules_config

        self.insert_test_email(
            email_id='1',
            from_email='AZ <az@amazon.com>',
            subject='Subject 1',
            message='Message 1',
            received_date=datetime.strptime('2024-07-22 02:24:22', '%Y-%m-%d %H:%M:%S')
        )

        process_emails(mock_service, rules_config, self.session)

        mock_service.users().messages().modify.assert_any_call(
            userId='me', id='1', body={'removeLabelIds': ['UNREAD']}
        )
        mock_service.users().messages().modify.assert_any_call(
            userId='me', id='1', body={'addLabelIds': ['IMPORTANT'], 'removeLabelIds': ['INBOX']}
        )

if __name__ == '__main__':
    unittest.main()
