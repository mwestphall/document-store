from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class Document(BaseModel):
    id: UUID = Field(..., description="The internal ID of the document")
    title: str = Field(..., description="Title of the document")
    xdd_id: Optional[str] = Field(None, description="The XDD Canonical ID of the document, if present")
    doi: Optional[str] = Field(None, description="The digital object identifier of the document, if present")
