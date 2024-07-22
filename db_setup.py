from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    email_id = Column(String, unique=True, nullable=False)
    from_email = Column(String, nullable=False)
    subject = Column(String)
    message = Column(Text)
    received_date = Column(DateTime)

engine = create_engine('sqlite:///emails.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
