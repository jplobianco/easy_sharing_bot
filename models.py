from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Service(Base):
    __tablename__ = "service"
    service_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_modified_by = Column(String, nullable=True)
    last_modified_at = Column(DateTime, nullable=True)
    accounts = relationship("Account", backref=backref("service"))

    def __repr__(self):
        return f'Service {self.name}'

    @classmethod
    def find_by_name(cls, session, chat_id: int, name: str):
        return session.query(cls).filter_by(chat_id=chat_id, name=name).all()

    @classmethod
    def find_by_chat(cls, session, chat_id: int):
        return session.query(cls).filter_by(chat_id=chat_id).order_by('name').all()


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("service.service_id"))
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    grabbed_at = Column(DateTime, nullable=True)
    grabbed_by = Column(String, nullable=True)
    released_at = Column(DateTime, nullable=True)

    last_modified_by = Column(String, nullable=True)
    last_modified_at = Column(DateTime, nullable=True)
    usages = relationship("Usage", backref=backref("account"))

    def __repr__(self):
        return f'Account {self.username}'

    @classmethod
    def find_by_service_id(cls, session, service_id: int):
        return session.query(cls).filter_by(service_id=service_id).all()


class Usage(Base):
    __tablename__ = "usage"
    action_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.account_id"))
    type = Column(String, nullable=False)  # Using | Releasing
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'{self.created_by} {self.type} {self.account.username} since {self.created_at}'
