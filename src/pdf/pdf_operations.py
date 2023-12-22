from db.db_models import DbArticle
from s3.s3_client import *
import fitz


def extract_page(article: DbArticle, page: int) -> str:
    # Return a cached result if it exists
    bucket = article.bucket_name
    page_path = get_page_path(article.id, page)

    if not object_exists(bucket, page_path):
        with fitz.Document() as doc:
            source_pdf = fitz.Document("pdf", get_object_body(bucket, get_article_path(article.id)).read())
            doc.insert_pdf(source_pdf, from_page=page, to_page=page)
            put_object(bucket, page_path, doc.write())

    return get_presigned_url(bucket, page_path)
    


    
