#coding=utf-8


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from configs import settings
sae_engine = create_engine(settings.DB_SAE_URI+'?charset=utf8', encoding='utf-8', 
	convert_unicode=True, pool_recycle=settings.DB_POOL_RECYCLE_TIMEOUT, 
	echo=settings.DB_ECHO)

create_session = sessionmaker(autocommit=False, autoflush=False, 
    bind=sae_engine)


Base = declarative_base()