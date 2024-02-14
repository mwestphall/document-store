"""
ElasticSearch client that piggybacks off of a cosmos set visualizer deployment's ES instance to 
grab info about document extractions
"""

import elasticsearch
from os import environ
from model.api_models import ArticleExtraction

client = elasticsearch.Elasticsearch(environ['ES_URL'])

# Interesting (non-text) extraction types
EXTRACTION_CLASSES = ["Table", "Figure", "Equation"]

def get_article_extractions(xdd_doc_id: str) -> list[ArticleExtraction]:
    es_data = client.search(index='page',size=500, query={
        "match_phrase": {
            "pdf_name": f"{xdd_doc_id}.pdf"
        }
    })
    hits = es_data['hits']['hits']

    extractions = []
    for hit in hits:
        source = hit['_source']
        indices = [i for i, pp_cls in enumerate(source['postprocess_cls']) if pp_cls in EXTRACTION_CLASSES]
        page_extractions = [ArticleExtraction(
            extraction_class=source['postprocess_cls'][index],
            score=source['postprocess_score'][index],
            bbox = source['bbox'][index],
            page_num=source['page_num']
        ) for index in indices]
        extractions.extend(page_extractions)
    
    return extractions
