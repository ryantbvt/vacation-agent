from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_agent():
    return {"message": "Agent endpoint"} 