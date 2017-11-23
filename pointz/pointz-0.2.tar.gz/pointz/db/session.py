from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pointz import settings

Session = sessionmaker(bind=create_engine(
    settings.DATABASE_URL
))