from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, Any
from uuid import UUID
from db.db_models import DbArticle

DocumentType = Literal['pdf', 'webp', 'svg']

class Article(BaseModel):
    """ JSON model for user-facing document metadata """
    id: UUID = Field(..., description="The internal ID of the document")
    title: str = Field(..., description="Title of the document")
    xdd_id: Optional[str] = Field(None, description="The XDD Canonical ID of the document, if present")
    doi: Optional[str] = Field(None, description="The digital object identifier of the document, if present")
    pages: Optional[int] = Field(None, description="Document page count")
    page_width: Optional[int] = Field(None, description="Width of a page in the document")
    page_height: Optional[int] = Field(None, description="Height of a page in the document")
    ingest_date: Optional[Any] = Field(None, description="Article ingest date")
    ingest_batch: Optional[Any] = Field(None, description="Article ingest batch")

    xdd_link: Optional[str] = Field(None, description="xdd api link to the article")
    doi_link: Optional[str] = Field(None, description="doi.org link to the article")


    @staticmethod
    def from_db_article(db_article: DbArticle) -> "Article":
        return Article(
            id = db_article.id,
            title = db_article.title,
            xdd_id = db_article.xdd_doc_id,
            doi = db_article.doi,
            pages = db_article.page_count,
            page_width = db_article.page_width,
            page_height = db_article.page_height,
            xdd_link = db_article.xdd_link,
            doi_link = db_article.doi_link,
            ingest_date = db_article.ingest_date,
            ingest_batch = db_article.ingest_batch
        )


class DatabaseMetrics(BaseModel):
    """ JSON model for database metrics """
    document_count: int = Field(..., description="The count of documents in the database")


class ArticleQuery(BaseModel):
    """ Query parameters model for searching articles """
    xdd_id: Optional[str] = Field(None, description="The XDD Canonical ID of the document to search")
    doi: Optional[str] = Field(None, description="The digital object identifier of the document to search")

    @model_validator(mode='after')
    def check_not_empty(self):
        assert self.xdd_id or self.doi, "Must provide at least one query parameter"
