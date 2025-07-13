''' Agent Schema '''

from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_query: str

class ChatResponse(BaseModel):
    response: str