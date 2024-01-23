from sqlalchemy import select
from .db_models import DbArticle
from model.api_models import ArticleQuery


def build_article_query(api_query: ArticleQuery):
    """ Utility function for building an article `SELECT` query based off of an `ArticleQuery` 
    API request
    TODO: depending on application requirements, we'll want something more manageable
        than an if-else chain
    """
    base_query = select(DbArticle)

    if api_query.doi:
        base_query = base_query.where(DbArticle.doi == api_query.doi)

    if api_query.xdd_id:
        base_query = base_query.where(DbArticle.xdd_doc_id == api_query.xdd_id)

    return base_query
