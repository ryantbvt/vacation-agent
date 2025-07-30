''' 
General Gateway Schemas

Mainly contains the Request/Response schemas
'''

from pydantic import BaseModel
from typing import Optional, List

class GatewayRequest(BaseModel):
    model_name: str
    user_prompt: str
    system_prompt: str = "You are a helpful assistant."
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 4096
    top_p: Optional[float] = 1.0
    top_k: Optional[int] = 40
    web_search: Optional[bool] = False

class LLMResponse(BaseModel):
    response: str

class EmbeddingRequest(BaseModel):
    text: str
    model_name: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]

class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    model_name: str

class BatchEmbeddingResponse(BaseModel):
    embeddings: List[List[float]]