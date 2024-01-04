from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from uuid import uuid4

class Base(DeclarativeBase):
    pass

class DbArticle(Base):
    """ ORM Mapping for articles in the document store """
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String)
    xdd_doc_id = Column(String, unique=True, default=None)
    doi = Column(String, unique=True, default=None)
    bucket_name = Column(String)

class DbApiKey(Base):
    """ ORM Mapping for simple API key based authorization to access copyright-protected documents """
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    api_key = Column(String, unique=True)
    enabled = Column(Boolean, default=True)



