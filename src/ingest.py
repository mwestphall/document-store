#!/usr/bin/env python3
from os import environ, path
import json
import fitz
from db.db import DbSession
from db.db_models import DbArticle
from s3.s3_client import s3
from uuid import uuid4

WORK_DIR = environ['WORK_DIR']
BUCKET = environ['S3_BUCKET']
BATCH = environ['INGEST_BATCH']
START_IDX = int(environ['START_IDX']) if 'START_IDX' in environ else None
STOP_IDX = int(environ['STOP_IDX']) if 'STOP_IDX' in environ else None

def article_from_bibjson(entry: dict) -> DbArticle:
    article = DbArticle()
    article.id = str(uuid4())
    article.bucket_name = BUCKET
    article.ingest_batch = BATCH

    # Info from BibJSON
    article.xdd_doc_id = [e["id"] for e in entry["identifier"] if e["type"] == "_xddid"][0]
    doi_entries = [e["id"] for e in entry["identifier"] if e["type"] == "doi"]
    article.doi = doi_entries[0] or None if doi_entries else None
    article.title = entry["title"]

    # Info from basic PDF metadata
    pdf_path = path.join(WORK_DIR,f'{article.xdd_doc_id}.pdf')
    doc = fitz.Document(pdf_path)
    article.page_count = doc.page_count
    article.page_width = int(doc[0].rect.width)
    article.page_height = int(doc[0].rect.height)
    
    return article

with open(path.join(WORK_DIR,'bibjson')) as f:
    bibjson = json.load(f)

for idx, entry in enumerate(bibjson[START_IDX:STOP_IDX]):

    print(f"Ingesting {entry['identifier'][0]['id']} (${idx})")
    try:
        # TODO creating a separate transaction for each article is going to be slow, want things to be
        # as atomic as possible (for starters) though
        with DbSession() as session:
            article = article_from_bibjson(entry)
            pdf_path = path.join(WORK_DIR,f'{article.xdd_doc_id}.pdf')
            s3_path = f"documents/{article.id}.pdf"
            session.add(article)
            session.commit()

    except Exception as e:
        print(f"Unable to write entry file {entry['identifier'][0]['id']} to db", e)
        continue
    

    try:
        with open(pdf_path, 'rb') as pdf:
            s3.put_object(Bucket=BUCKET, Body=pdf.read(), Key=s3_path)
    except Exception as e:
        print(f"Unable to upload file {pdf_path} to s3", e)
