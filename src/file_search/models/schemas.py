from pydantic import BaseModel, Field


class StoreInfo(BaseModel):
    name: str
    display_name: str | None = None
    create_time: str | None = None
    
class FileInfo(BaseModel):
    name: str
    display_name: str | None = None
    state: str | None = None

class Citation(BaseModel):
    title: str | None = None
    content: str | None = None
    
class SearchResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    model: str