from os import environ
from fastapi import FastAPI, APIRouter, Header
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import select
from db.db import DbSession, DbArticle, get_article_with_auth
from uuid import UUID
from model.models import Document, DocumentType
from typing import Optional
from pdf.pdf_operations import PdfOperator, PdfPageOperator, PdfPageSnippetOperator

api_prefix = environ['API_PREFIX']

app = FastAPI(title="xDD Document Store", docs_url=f"{api_prefix}/docs")
app.add_middleware(GZipMiddleware)

prefix_router = APIRouter(prefix=api_prefix)

@prefix_router.get("/documents")
def get_documents(page: int = 0, per_page: int = 25) -> list[Document]:
    """ Return a paginated list of alphabetically-sorted documents """
    with DbSession() as session:
        articles = session.scalars(select(DbArticle)
            .order_by(DbArticle.title).limit(per_page).offset(page * per_page)).all()
        return [Document(id=a.id, xdd_id=a.xdd_doc_id, title=a.title, doi=a.doi) for a in articles]

@prefix_router.get("/documents/{document_id}")
def get_document(document_id: UUID) -> Document:
    """ Return the metadata for the given document """
    with DbSession() as session:
        article = session.get(DbArticle, document_id)
        return Document(
            id=article.id, xdd_id=article.xdd_doc_id, title=article.title, doi=article.doi)


@prefix_router.get("/documents/{document_id}/content")
def get_document_contents(document_id: UUID, x_api_key: Optional[str] = Header(None)) -> RedirectResponse:
    """ Return a redirect to the full PDF contents of the given document """
    article = get_article_with_auth(document_id, x_api_key)
    operator = PdfOperator(article)
    return RedirectResponse(operator.get_presigned_document())

@prefix_router.get("/documents/{document_id}/page/{page_num}")
def get_document_page(
        document_id: UUID, page_num: int, content_type: DocumentType = 'pdf', 
        x_api_key: Optional[str] = Header(None)) -> RedirectResponse:
    """ Return a redirect to the contents of a single page of the given document
    in the specified output format
    """
    article = get_article_with_auth(document_id, x_api_key)
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
    article = get_article_with_auth(document_id, x_api_key)
    operator = PdfPageSnippetOperator(article, page_num, snippet_bb, content_type)
    return RedirectResponse(operator.get_presigned_document())

app.include_router(prefix_router)
