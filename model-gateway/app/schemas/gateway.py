''' 
General Gateway Schemas

Mainly contains the Request/Response schemas
'''

from pydantic import BaseModel
from typing import Optional, List

class GatewayRequest(BaseModel):
    model_name: str
    prompt: str
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 4096

class LLMResponse(BaseModel):
    response: str

class EmbeddingRequest(BaseModel):
    text: str
    model_name: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]