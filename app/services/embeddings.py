import google.genai as genai
from app.utils.logger import get_logger
import asyncio
import os 

logger = get_logger(__name__)

apikey = os.getenv('LLM_API_KEY')

try:
    client = genai.Client(api_key=apikey)
    logger.info("LLM client initialized successfully")
except Exception as e:
    logger.error(f'Failed to initialize LLM client: {e}')
    raise    

# Unlike LLM calls there wont be any streaming here. 
async def embed_pairs(parsed):
    """
    Embed pairs with gemini-004 model with asyncio
    """
    logger.info(f"Started Embeddings Creation")

    texts = [pair['incoming'] for pair in parsed['pairs']]
    try:
 
        result = await asyncio.wait_for(
            client.aio.models.embed_content(
                model="text-embedding-004",
                contents=texts,
                config={"output_dimensionality": 384,
                        "task_type": "RETRIEVAL_DOCUMENT"}
            ),
            timeout=120,
        )

        for pair, emb in zip(parsed['pairs'], result.embeddings):
            pair['embedding'] = emb.values

        return parsed    
    except Exception as e:
        logger.error(f"Error while generating embeddings {e}")
        raise

