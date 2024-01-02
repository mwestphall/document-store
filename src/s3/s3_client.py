from os import environ
from uuid import UUID
from boto3 import Session
from typing import Literal

session = Session(aws_access_key_id=environ['S3_ACCESS_KEY'], aws_secret_access_key=environ['S3_SECRET_KEY'])
s3 = session.client("s3", endpoint_url="https://s3.xdd-pdfstore.chtc.io", region_name='us-east-1')


def get_article_path(id: UUID):
    return f"documents/{id}.pdf"

def get_page_path(id: UUID, page: int, content_type: Literal['pdf', 'webp'] = 'pdf'):
    return f"pages/{id}/{page}.{content_type}"

def get_snippet_path(id: UUID, page: int, bb: tuple[int, int, int, int], content_type: Literal['pdf', 'webp'] = 'pdf'):
    return f"snippets/{id}/{page}_{bb[0]}_{bb[1]}_{bb[2]}_{bb[3]}.{content_type}"


def get_presigned_url(bucket: str, path: str):
    return s3.generate_presigned_url('get_object', Params={'Bucket':bucket, 'Key':path})


def object_exists(bucket: str, path: str):
    try:
        s3.head_object(Bucket=bucket, Key=path)
        return True
    except:
        return False

def get_object_body(bucket: str, path: str):
    return s3.get_object(Bucket=bucket, Key=path).get('Body')


def put_object(bucket: str, path: str, body):
    return s3.put_object(Bucket=bucket, Key=path, Body=body)

