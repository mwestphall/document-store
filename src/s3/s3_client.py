from os import environ
from boto3 import Session
from db.db_models import DbArticle

session = Session(aws_access_key_id=environ['S3_ACCESS_KEY'], aws_secret_access_key=environ['S3_SECRET_KEY'])
s3 = session.client("s3", endpoint_url="https://s3.xdd-pdfstore.chtc.io", region_name='us-east-1')


def get_presigned_url(article: DbArticle):
    return s3.generate_presigned_url('get_object',Params={'Bucket':f'{article.bucket_name}','Key':f'{article.id}.pdf'})
