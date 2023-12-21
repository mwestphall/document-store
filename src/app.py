from os import environ
from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.logger import logger
from sqlalchemy import select
from db.db import Session, DbArticle
from uuid import UUID
from model.models import Document
from s3.s3_client import get_presigned_url

api_prefix = environ['API_PREFIX']

app = FastAPI(title="xDD Document Store", docs_url=f"{api_prefix}/docs")
app.add_middleware(GZipMiddleware)

prefix_router = APIRouter(prefix=api_prefix)

@prefix_router.get("/documents")
def get_documents(page: int = 0, per_page: int = 25) -> list[Document]:
    with Session() as session:
        articles = session.scalars(select(DbArticle)
            .order_by(DbArticle.title).limit(per_page).offset(page * per_page)).all()
        return [Document(id=a.id, xdd_id=a.xdd_doc_id, title=a.title, doi=a.doi) for a in articles]

@prefix_router.get("/documents/{document_id}")
def get_document(document_id: UUID) -> Document:
    with Session() as session:
        return session.get(DbArticle, document_id).as_model()


@prefix_router.get("/documents/{document_id}/pdf")
def get_document_contents(document_id: UUID) -> RedirectResponse:
    with Session() as session:
        return RedirectResponse(
            get_presigned_url(
                session.get(DbArticle, document_id)
            )
        )

app.include_router(prefix_router)
