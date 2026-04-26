from pydantic import BaseModel

class AIRequest(BaseModel):
    book_id: str
    chapter_id: str
    query: str