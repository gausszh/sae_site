#!/usr/bin/python
#coding=utf8

import datetime
from sqlalchemy import (
    MetaData, Table, Column,  Integer, BigInteger, Float, String, Text, DateTime,
    ForeignKey, Date, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models import sae_engine
from models import create_session

Base = declarative_base()
metadata = MetaData()


class BlogArticle(Base):

    """
    发布历史日志
    """

    __tablename__ = 'blog_article'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    markdown = Column(Text)
    html = Column(Text)
    create_by = Column(String(30), index=True, nullable=False)
    create_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, index=True, nullable=False,)
    is_active = Column(Integer, nullable=False, default=1)

if __name__ == '__main__':
    Base.metadata.create_all(bind=sae_engine)
