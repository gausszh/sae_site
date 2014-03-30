#coding=utf8
"""
基础类--用户信息
"""

from sqlalchemy import (
    MetaData, Table, Column,  Integer, BigInteger, Float, String, Text, DateTime,
    ForeignKey, Date, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models import sae_engine
from models import create_session

Base = declarative_base()
metadata = MetaData()


class User(Base):

    """
    发布历史日志
    """

    __tablename__ = 'user'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    open_id = Column(String(45), nullable=False, index=True)
    token = Column(String(64), nullable=False, index=True)
    name = Column(String(45))
    email = Column(String(60))
    address = Column(String(150))
    tel = Column(String(15))
    school = Column(String(45))
    create_time = Column(DateTime)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


if __name__ == '__main__':
    Base.metadata.create_all(bind=sae_engine)
