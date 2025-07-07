''' Consolidate v1 routers '''

from fastapi import APIRouter
from app.api.v1.endpoints import rag_engine

api_router = APIRouter()

# Load endpoints
api_router.include_router(rag_engine.router, prefix="/rag")