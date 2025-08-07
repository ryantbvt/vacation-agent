''' Gateway for Large Language Models (LLM) '''

from fastapi import APIRouter, HTTPException
from python_utils.logging.logging import init_logger

from app import gateway_config
from app.schemas.gateway import GatewayRequest, LLMResponse
from app.helper.inference import inference_anthropic, inference_openai, inference_ollama

# Initialize logger and FastAPI
logger = init_logger()
router = APIRouter()

# initialize configs
llm_models = gateway_config.llm_models

''' API '''

@router.post('/generate')
async def llm_generate(request: GatewayRequest) -> LLMResponse:
    '''
    Description: Forwards request to LLM

    Args:
        request: Request that'll be sent to the LLM

    Returns:
        llm_response(LLMResponse): returns LLM response
    '''

    # Get the vendor of the model
    vendor = gateway_config.get_vendor(
        llm_models=llm_models, 
        model_name=request.model_name
    )

    # Get the web search tool type for the model
    web_search_tool_type = gateway_config.get_web_search_tool_type(
        llm_models=llm_models,
        model_name=request.model_name
    )

    # Send request to model
    try:
        if vendor == "anthropic":
            llm_response = await inference_anthropic(
                model_name=request.model_name,
                user_prompt=request.user_prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                top_k=request.top_k,
                web_search=request.web_search,
                web_search_tool_type=web_search_tool_type
            )

            return llm_response
        
        if vendor == "openai":
            llm_response = await inference_openai(
                model_name=request.model_name,
                user_prompt=request.user_prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                top_k=request.top_k,
                web_search=request.web_search,
                web_search_tool_type=web_search_tool_type
            )

            return llm_response
        
        # default is local llms
        else:
            llm_response = await inference_ollama(
                model_name=request.model_name,
                user_prompt=request.user_prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                top_k=request.top_k
            )

            return llm_response

    except Exception as e:
        logger.error(f'Error occurred: {e}')
        raise HTTPException(status_code=500, detail="Inference failed")
