from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from os import environ
import urllib.parse
from uuid import UUID
from fastapi import HTTPException
from .db_models import Base, DbArticle, DbApiKey
from model.api_models import Article

def setup_engine():
    """ Create a new postgres connection based on environment variables """
    return create_engine(f'postgresql://{environ["PG_USER"]}:{urllib.parse.quote_plus(environ["PG_PASSWORD"])}@{environ["PG_HOST"]}:{environ["PG_PORT"]}/{environ["PG_DATABASE"]}')

engine = setup_engine()

# Create tables if they don't exist
Base.metadata.create_all(engine)
DbSession = sessionmaker(bind=engine)

# TODO don't hardcode which bucket is public
PUBLIC_PDF_BUCKET = "public-pdfs"

def _api_key_valid(session: Session, api_key: str):
    """ Check the API key exists and is enabled """
    return session.scalars(select(DbApiKey).filter_by(api_key=api_key, enabled=True)).first() is not None

def get_article_list(page_number: int, per_page: int) -> list[Article]:
    """ Retrieve a paginated list of article summaries """
    with DbSession() as session:
        articles = session.scalars(select(DbArticle)
            .order_by(DbArticle.title).limit(per_page).offset(page_number * per_page)).all()
        return [Article.from_db_article(a) for a in articles]

def get_article(article_id: UUID, api_key: str, auth_required: bool = True) -> Article:
    """ Retrieve an article's metadata, then optionally ensure the requesting user has permissions to access the document """
    with DbSession() as session:
        article = session.get(DbArticle, article_id)
        if auth_required and article.bucket_name != PUBLIC_PDF_BUCKET and not _api_key_valid(session, api_key):
            raise HTTPException(status_code=403, detail="Invalid API key")
        return Article.from_db_article(article)

