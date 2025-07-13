from fastapi import APIRouter
from python_utils.logging.logging import init_logger

from app.schemas.agent import ChatRequest, ChatResponse
from app.modules.intent_skill import IntentSkill

# Initialize modules and logger
logger = init_logger()
router = APIRouter()
intent_skill = IntentSkill()

@router.post("/chat")
async def chat(request: ChatRequest):
    '''
    Description: Agent endpoint for chat

    Args:
        request (ChatRequest): The chat request

    Returns:
        ChatResponse: The chat response
    '''
    logger.info(f"Received chat request: {request.user_query}")

    # Step 1: Classify intent
    intent_classification = intent_skill.classify_intent(request.user_query)
    
    logger.info(f"Intent classification: {intent_classification.intent}")
    logger.info(f"Reasoning: {intent_classification.reasoning}")

    # Step 2: Route to appropriate skill based on intent
    if intent_classification.intent == "kb":
        # Route to KB skill (RAG)
        logger.info("Routing to KB skill (RAG)")
        response = "KB response placeholder"  # TODO: Implement KB routing
    elif intent_classification.intent == "realtime":
        # Route to realtime skill (LLM + web search)
        logger.info("Routing to realtime skill (LLM + web search)")
        response = "Realtime response placeholder"  # TODO: Implement realtime routing
    else:
        # Route to general skill (LLM only)
        logger.info("Routing to general skill (LLM only)")
        response = "General response placeholder"  # TODO: Implement general routing

    # Step 3: Return response
    return ChatResponse(response=response)
