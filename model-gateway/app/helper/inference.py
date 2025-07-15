''' Inference logic for LLM '''

import json
import os
from dotenv import load_dotenv

import anthropic
from openai import OpenAI
import ollama

from python_utils.logging.logging import init_logger

from app.schemas.gateway import LLMResponse

# Initialize logger
logger = init_logger()

# Initialize keys
try:
    load_dotenv()
except ImportError:
    logger.warning("Tried to load dotenv. Failed. Hopefully running in k8s.")
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if ANTHROPIC_API_KEY is None:
    logger.error('Missing Anthropic API key')
    raise ValueError("Missing Anthropic API key. Please set ANTHROPIC_API_KEY variable.")

if OPENAI_API_KEY is None:
    logger.error('Missing OpenAI API key')
    raise ValueError("Missing OpenAI API key. Please set ANTHROPIC_API_KEY variable.")

''' Inference Logic '''

async def inference_anthropic(
    model_name: str,
    user_prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float = 1.0,
    top_k: int = 40,
    web_search: bool = False
) -> LLMResponse:
    '''
    Description: Inference handler for Anthropic models

    Args:
        model_name: the model we're sending the request to
        user_prompt: the user prompt we're sending to the LLM
        system_prompt: the system prompt for the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM
        top_p: nucleus sampling parameter
        top_k: top-k sampling parameter
        web_search: whether to enable web search functionality

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    # Initialize Anthropic client
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    logger.info(f'Starting Anthropic Inference: {model_name}')

    # Prepare messages with system prompt if provided
    messages = []
    if system_prompt:
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
    messages.append({
        'role': 'user',
        'content': [
            {
                'type': 'text',
                'text': user_prompt
            }
        ]
    })

    # Prepare request parameters
    request_params = {
        'model': model_name,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'top_p': top_p,
        'top_k': top_k
    }

    # Add web search tools if enabled
    if web_search:
        request_params['tools'] = [
            {
                'type': 'web_search'
            }
        ]
        logger.info(f'Web search enabled for Anthropic model: {model_name}')

    # Send Anthropic Request
    response_chat_completions = anthropic_client.messages.create(**request_params)

    llm_response = LLMResponse(
        response=response_chat_completions.content[0].text
    )

    logger.info(f'Successful Anthropic Inference: {model_name}')

    return llm_response

async def inference_openai(
    model_name: str,
    user_prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float = 1.0,
    top_k: int = 40,
    web_search: bool = False
) -> LLMResponse:
    '''
    Description: Inference handler for OpenAI models

    Args:
        model_name: the model we're sending the request to
        user_prompt: the user prompt we're sending to the LLM
        system_prompt: the system prompt for the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM
        top_p: nucleus sampling parameter
        top_k: top-k sampling parameter
        web_search: whether to enable web search functionality

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    logger.info(f"Starting OpenAI Inference: {model_name}")

    # Initialize openai client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Prepare messages with system prompt if provided
    messages = []
    if system_prompt:
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
    messages.append({
        'role': 'user',
        'content': user_prompt
    })

    # Prepare request parameters
    request_params = {
        'model': model_name,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'top_p': top_p,
        'top_k': top_k
    }

    if web_search:
        request_params['tools'] = [
            {
                'type': 'web_search'
            }
        ]
        logger.info(f'Web search enabled for OpenAI model: {model_name}')

    # send request to openai
    response_chat_completions = client.chat.completions.create(**request_params)

    logger.info(f"Successfully recieved response from: {model_name}")

    resp = response_chat_completions.model_dump_json()
    resp = json.loads(resp)
    resp = resp['choices'][0]['message']['content']

    logger.info(f"Returning response for {model_name}")

    return LLMResponse(response=resp)

async def inference_ollama(
    model_name: str,
    user_prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float = 1.0,
    top_k: int = 40
) -> LLMResponse:
    '''
    Description: Inference handler for Ollama models

    Args:
        model_name: the model we're sending the request to
        user_prompt: the user prompt we're sending to the LLM
        system_prompt: the system prompt for the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM
        top_p: nucleus sampling parameter
        top_k: top-k sampling parameter

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    logger.info(f'Starting Ollama Inference: {model_name}')

    # Combine system and user prompts if system prompt is provided
    full_prompt = user_prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = ollama.generate(
            model=model_name, 
            prompt=full_prompt,
            options = {
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': top_p,
                'top_k': top_k
            }
        )

    logger.info(f'Ollama inference completed: {model_name}')

    return LLMResponse(response=response['response'])
