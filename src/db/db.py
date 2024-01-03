from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from os import environ
import urllib.parse
from uuid import UUID
from fastapi import HTTPException
from .db_models import Base, DbArticle, DbApiKey

def setup_engine():
    """ Create a new postgres connection based on environment variables """
    return create_engine(f'postgresql://{environ["PG_USER"]}:{urllib.parse.quote_plus(environ["PG_PASSWORD"])}@{environ["PG_HOST"]}:{environ["PG_PORT"]}/{environ["PG_DATABASE"]}')

engine = setup_engine()

# Create tables if they don't exist
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# TODO don't hardcode which bucket is public
PUBLIC_PDFS_BUCKET = "public-pdfs"

def get_article_with_auth(article_id: UUID, api_key: str) -> DbArticle:
    with Session() as session:
        article = session.get(DbArticle, article_id)
        if article.bucket_name != PUBLIC_PDFS_BUCKET:
            key = session.scalars(select(DbApiKey).filter_by(api_key=api_key, enabled=True)).first()
            if key is None:
                raise HTTPException(status_code=403, detail="Invalid API key")
        return article
