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
    prompt: str,
    temperature: float,
    max_tokens: int
) -> LLMResponse:
    '''
    Description: Inference handler for Anthropic models

    Args:
        model_name: the model we're sending the request to
        prompt: the prompt we're sending to the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM.

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    # Initialize Anthropic client
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    logger.info(f'Starting Anthropic Inference: {model_name}')

    # Send Anthropic Request
    response_chat_completions = anthropic_client.messages.create(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': prompt
                }
            ]
        }],
        temperature=temperature,
        max_tokens=max_tokens
    )

    llm_response = LLMResponse(
        response=response_chat_completions.content[0].text
    )

    logger.info(f'Successful Anthropic Inference: {model_name}')

    return llm_response

async def inference_openai(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int
) -> LLMResponse:
    '''
    Description: Inference handler for OpenAI models

    Args:
        model_name: the model we're sending the request to
        prompt: the prompt we're sending to the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM.

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    logger.info(f"Starting OpenAI Inference: {model_name}")

    # Initialize openai client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # send request to openai
    response_chat_completions = client.chat.completions.create(
        model=model_name,
        messages=[{
            'role': 'user',
            'content': prompt
        }],
        temperature=temperature,
        max_tokens=max_tokens
    )

    logger.info(f"Successfully recieved response from: {model_name}")

    resp = response_chat_completions.model_dump_json()
    resp = json.loads(resp)
    resp = resp['choices'][0]['message']['content']

    logger.info(f"Returning response for {model_name}")

    return LLMResponse(response=resp)

async def inference_ollama(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int
) -> LLMResponse:
    '''
    Description: Inference handler for Ollama models

    Args:
        model_name: the model we're sending the request to
        prompt: the prompt we're sending to the LLM
        temperature: Variable for randomness, if 0, it'll return the least random answer
        max_tokens: the max_token input for the LLM.

    Returns:
        llm_response (LLMResponse): Output of the model
    '''
    logger.info(f'Starting Ollama Inference: {model_name}')

    response = ollama.generate(
            model=model_name, 
            prompt=prompt,
            options = {
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        )

    logger.info(f'Ollama inference completed: {model_name}')

    return LLMResponse(response=response['response'])
