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

async def embed(texts):

    try:   
        result = await asyncio.wait_for(
                client.aio.models.embed_content(
                    model="gemini-embedding-001",
                    contents=texts,
                    config={"output_dimensionality": 384,
                            "task_type": "RETRIEVAL_DOCUMENT"}
                ),
                timeout=120,
            )    
        return result
    except Exception as e:
        logger.info("Error while generating embeddings")
        raise
        

async def embed_pairs(parsed):
    """
    Embed pairs with gemini-001 model with asyncio
    """
    logger.info(f"Started Embeddings Creation")
    batch_texts = []
    temp = []
    c = 0
    for pair in parsed['pairs']:
        temp.append(pair['incoming'])
        if c<=95:
            c+=1
        else:
            c = 0
            batch_texts.append(temp)
            temp = []

    if temp:
        batch_texts.append(temp)
    embeddings = []
    try:
        for text in batch_texts:
            result = await embed(text)
            embeddings.append(result.embeddings)

        all_embeddings = [embed for sub_embed in embeddings for embed in sub_embed]

        for pair, emb in zip(parsed['pairs'], all_embeddings):
            pair['embedding'] = emb.values

        return parsed    
    except Exception as e:
        logger.error(f"Error while generating embeddings {e}")
        raise
