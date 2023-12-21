from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ
import urllib.parse
from .db_models import Base, DbArticle

def setup_engine():
    """ Create a new postgres connection based on environment variables """
    return create_engine(f'postgresql://{environ["PG_USER"]}:{urllib.parse.quote_plus(environ["PG_PASSWORD"])}@{environ["PG_HOST"]}:{environ["PG_PORT"]}/{environ["PG_DATABASE"]}')

engine = setup_engine()

# Create tables if they don't exist
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
