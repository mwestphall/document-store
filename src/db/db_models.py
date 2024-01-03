from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from model.models import Document
from uuid import uuid4
from s3.s3_client import get_presigned_url, get_article_path


class Base(DeclarativeBase):
    pass



class DbArticle(Base):
    """ORM Mapping for articles in the document store"""
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String)
    xdd_doc_id = Column(String, unique=True, default=None)
    doi = Column(String, unique=True, default=None)
    bucket_name = Column(String)


    def as_model(self) -> Document:
        return Document(id=self.id, xdd_id=self.xdd_doc_id, title=self.title, doi=self.doi)

    def presigned_url(self) -> str:
        return get_presigned_url(self.bucket_name, get_article_path(self.id))



class DbApiKey(Base):
    """ORM Mapping for simple API key based authorization to access copyright-protected documents"""
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    api_key = Column(String, unique=True)
    enabled = Column(Boolean, default=True)



