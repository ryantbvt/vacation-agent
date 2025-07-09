''' consolidates all v1 routers to a single router '''

from fastapi import APIRouter
from app.api.v1.endpoints import llm, slm, embedding

api_router = APIRouter()

# Load all endpoints
api_router.include_router(llm.router, prefix="/llm")
api_router.include_router(slm.router, prefix="/slm")
api_router.include_router(embedding.router, prefix="/embedding")