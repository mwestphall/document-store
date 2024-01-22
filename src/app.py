from os import environ
from fastapi import FastAPI, APIRouter, Header
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import select
from db import db
from uuid import UUID
from typing import Optional
from model.api_models import Article, DocumentType
from pdf.pdf_operations import PdfOperator, PdfPageOperator, PdfPageSnippetOperator

api_prefix = environ['API_PREFIX']

app = FastAPI(title="xDD Article Store", docs_url=f"{api_prefix}/docs")
app.add_middleware(GZipMiddleware)

prefix_router = APIRouter(prefix=api_prefix)

@prefix_router.get("/documents")
def get_documents(page: int = 0, per_page: int = 25) -> list[Article]:
    """ Return a paginated list of alphabetically-sorted documents """
    return db.get_article_list(page, per_page)

@prefix_router.get("/documents/{document_id}")
def get_document(document_id: UUID) -> Article:
    """ Return the metadata for the given document """
    return Article.from_db_article(db.get_article(document_id, None, False))


@prefix_router.get("/documents/{document_id}/content")
def get_document_contents(document_id: UUID, x_api_key: Optional[str] = Header(None)) -> RedirectResponse:
    """ Return a redirect to the full PDF contents of the given document """
    article = db.get_article(document_id, x_api_key)
    operator = PdfOperator(article)
    return RedirectResponse(operator.get_presigned_document())

@prefix_router.get("/documents/{document_id}/page/{page_num}")
def get_document_page(
        document_id: UUID, page_num: int, content_type: DocumentType = 'pdf', 
        x_api_key: Optional[str] = Header(None)) -> RedirectResponse:
    """ Return a redirect to the contents of a single page of the given document
    in the specified output format
    """
    article = db.get_article(document_id, x_api_key)
    operator = PdfPageOperator(article, page_num, content_type)
    return RedirectResponse(operator.get_presigned_document())

@prefix_router.get("/documents/{document_id}/page/{page_num}/snippet/{snippet}")
def get_document_snippet(
        document_id: UUID, page_num: int, snippet: str, content_type: DocumentType = 'pdf', 
        x_api_key: Optional[str] = Header(None)) -> RedirectResponse:
    """ Return a redirect to the contents of a single page of the given document
    in the specified output format, with the region given by the comma-separated
    list of bounds highlighted
    """
    snippet_bb = [int(s) for s in snippet.split(',')]
    article = db.get_article(document_id, x_api_key)
    operator = PdfPageSnippetOperator(article, page_num, snippet_bb, content_type)
    return RedirectResponse(operator.get_presigned_document())

app.include_router(prefix_router)
