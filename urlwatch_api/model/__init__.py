from pecan                  import conf
from sqlalchemy             import create_engine, MetaData, Column, String, DateTime, Float, Integer
from sqlalchemy.orm         import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = scoped_session(sessionmaker())
metadata = MetaData()

def _engine_from_config(configuration):
    configuration = dict(configuration)
    url = configuration.pop('url')
    return create_engine(url, **configuration)

def init_model():
    conf.sqlalchemy.engine = _engine_from_config(conf.sqlalchemy)

def start():
    Session.bind = conf.sqlalchemy.engine
    metadata.bind = Session.bind

def commit():
    Session.commit()

def rollback():
    Session.rollback()

def clear():
    Session.remove()

Base = declarative_base()

class Site(Base):
    __tablename__ = 'site'

    guid = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    last_check = Column(DateTime)
    last_up = Column(DateTime)
    last_down = Column(DateTime)
    last_change = Column(DateTime)
    uptime_hour = Column(Float)
    uptime_day = Column(Float)
    uptime_week = Column(Float)
    uptime_30 = Column(Float)
    uptime_90 = Column(Float)
    
class SiteCheck(Base):
    __tablename__ = 'site_check'

    id = Column(Integer, primary_key=True)
    guid = Column(String)
    timestamp = Column(DateTime)
    data = Column(String)
    data_unfiltered = Column(String)
    tries = Column(Integer)
    etag = Column(String)
    error = Column(String)
    proxy = Column(String)

class Blob(Base):
    __tablename__ = 'blob'

    guid = Column(String, primary_key=True)
    data = Column(String)
