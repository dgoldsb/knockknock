import os
import time

from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class Device(Base):
    __tablename__ = "device"

    alias = Column(String, primary_key=True)
    ip_address = Column(String, default=None)
    owner = Column(String, default=None)

    def __init__(self, alias, ip_address=None, owner=None):
        self.alias = alias
        self.ip_address = ip_address
        self.owner = owner

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ["ip_address", "alias", "owner"]
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


class Sighting(Base):
    __tablename__ = "sighting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    current_timestamp = Column(Integer)
    last_activity_timestamp = Column(Integer)
    alias = Column(String, ForeignKey(Device.alias))

    def __init__(
        self, alias: str, last_activity_timestamp: int, current_timestamp=int(time.time())
    ):
        self.alias = alias
        self.current_timestamp = current_timestamp
        self.last_activity_timestamp = last_activity_timestamp

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ["id", "current_timestamp", "last_activity_timestamp", "alias"]
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


POSTGRES = {
    "db": os.environ["POSTGRES_DB"],
    "host": os.environ["POSTGRES_HOST"],
    "password": os.environ["POSTGRES_PASSWORD"],
    "port": os.environ["POSTGRES_PORT"],
    "user": os.environ["POSTGRES_USER"],
}
URI = "postgresql://{user}:{password}@{host}:{port}/{db}".format(**POSTGRES)

engine = create_engine(URI)
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
