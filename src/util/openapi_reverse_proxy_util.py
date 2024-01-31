"""
FastAPI does not like hosting swagger docs behind a reverse proxy. This is a shim to fetch
the data structure from localhost.

TODO A more elegant solution
"""
import requests
from fastapi import APIRouter
from os import environ

OPENAPI_JSON_PATH='/openapi.json'
api_prefix = environ['API_PREFIX']

def _get_local_openapi_json():
    doc = requests.get(f'http://localhost:8089{OPENAPI_JSON_PATH}').json()
    # remove the reverse proxy prefix from the doc
    for server in doc['servers']:
        server['url'] = server['url'].replace(api_prefix, '/')

    return doc


def add_openapi_route(router: APIRouter, path = OPENAPI_JSON_PATH):
    """ Add a route to a router that returns the app's openAPI JSON document """
    router.add_api_route(path=path, endpoint=_get_local_openapi_json)
