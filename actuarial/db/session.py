from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DRIVER_URI = "sqlite:///tables.db"

engine = create_engine(DRIVER_URI, future=True)
Base = declarative_base()
Session = sessionmaker(bind=engine, future=True)
