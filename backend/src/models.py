import datetime
import os

from sqlalchemy import create_engine, Column, DateTime, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class Sighting(Base):
    __tablename__ = "sighting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String)

    def __init__(self, timestamp: datetime.datetime, ip_address: str):
        self.timestamp = timestamp
        self.ip_address = ip_address

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ["id", "timestamp", "ip_address"]
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
