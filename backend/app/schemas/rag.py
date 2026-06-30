from pydantic import BaseModel


class RagIndexRequest(BaseModel):
    force_reindex: bool = False


class RagIndexResponse(BaseModel):
    status: str
    documents_indexed: int
