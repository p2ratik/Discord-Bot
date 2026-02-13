from app.schemas.chat import Payload
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import role_service
from app.services import message_service
from app.schemas.chat import BotMessageRecieve
from app.services import admin_service
from app.services import prompt
from app.utils.logger import get_logger
import google.genai as genai
from dotenv import load_dotenv
import asyncio
import os
import time 

load_dotenv()

# Initialize logger
logger = get_logger(__name__)

apikey = os.getenv('LLM_API_KEY')

try:
    client = genai.Client(api_key=apikey)
    logger.info("LLM client initialized successfully")
except Exception as e:
    logger.error(f'Failed to initialize LLM client: {e}')
    raise    

async def createMessage(payload:Payload, reply:str):
    """Create a message object for database storage"""
    try:
        bm_obj = BotMessageRecieve(
            channel_id=str(payload.channel_id),
            user_id=str(payload.user_id),
            content=str(payload.content),
            bot_reply = reply
        )
        logger.debug(f"Created message object for user {payload.user_id}")
        return bm_obj
    except Exception as e:
        logger.error(f"Error creating message object: {e}", exc_info=True)
        raise    


async def build_prompt(payload: Payload, db: AsyncSession) -> str:
    """
    Build a prompt for the LLM based on the chat payload
    
    :param payload: Chat payload containing user message
    :type payload: Payload
    :param db: Database session
    :type db: AsyncSession
    :return: Formatted prompt string
    """
    # Parallelize all database queries for better performance
    logger.info(f"Building prompt for user {payload.user_id} in channel {payload.channel_id}")
    start_time = time.time()
    
    # admin name for now is me later more admins will be added
    admin_username = os.getenv('ADMIN_USERNAME', 'pratik081978')
    
    try:
        role_obj, role_admin_obj, prev_messages = await asyncio.gather(
            role_service.get_roles_for_user(payload.user_id, db),
            admin_service.get_role_for_admin(admin_username, db),
            message_service.get_user_messages(payload.user_id, db)
        )
        
        db_time = (time.time() - start_time) * 1000
        logger.debug(f"Database queries completed in {db_time:.2f}ms")
        
        role_admin = role_admin_obj.role if role_admin_obj else {}
        roles = role_obj.role if role_obj else {}
        
        logger.debug(f"User has {len(prev_messages)} previous messages")
        
        # Format the previous messages
        prev_messages_format = [{'user_message': m.content, 'bot_reply': m.bot_reply} for m in prev_messages]

        prompt_text = prompt.develop_prompt(roles, payload.content, prev_messages_format, role_admin)
        logger.debug(f"Prompt built successfully (length: {len(prompt_text)} chars)")
        return prompt_text
    except Exception as e:
        logger.error(f"Error building prompt for user {payload.user_id}: {e}", exc_info=True)
        raise


async def call_llm(prompt: str, timeout: int = 30) -> str:
    """
    Native async call with streaming for lower perceived latency.
    """
    logger.info(f"Initiating streaming LLM call (timeout: {timeout}s)")
    start_time = asyncio.get_event_loop().time()
    full_response = []

    try:
        # 1. Use client.aio for native async support
        # 2. Use generate_content_stream (no stream=True argument needed)
        response_stream = await asyncio.wait_for(
            client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt,
            ),
            timeout=timeout
        )

        # Iterate through chunks as they arrive
        async for chunk in response_stream:
            if chunk.text:
                full_response.append(chunk.text)
                # OPTIONAL: Here is where you would update your Discord message!
                # await discord_message.edit(content="".join(full_response))

        elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
        result = "".join(full_response)
        
        logger.info(f"LLM stream finished in {elapsed:.2f}ms")
        return result

    except asyncio.TimeoutError:
        logger.error(f"LLM call timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}", exc_info=True)
        raise


async def process_chat(payload: Payload, db: AsyncSession) -> dict:
    """
    Process a chat message and generate a response
    
    :param payload: Chat payload
    :type payload: Payload
    :param db: Database session
    :type db: AsyncSession
    :return: Dictionary with reply
    """
    start_time = time.time()
    logger.info(f"Processing chat request from user {payload.user_id} - Message: '{payload.content[:50]}...'")
    
    try:
        prompt = await build_prompt(payload, db)
        llm_response = await call_llm(prompt)
        
        # Adding the current data to the db
        message = await createMessage(payload=payload, reply=llm_response)
        await message_service.add_user_messages(message=message, db=db)
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Chat request processed successfully in {elapsed:.2f}ms")
        return {'reply': llm_response}
        
    except asyncio.TimeoutError:
        elapsed = (time.time() - start_time) * 1000
        logger.warning(f"Chat request timed out after {elapsed:.2f}ms for user {payload.user_id}")
        return {'reply': 'Sorry, I took too long to respond. Please try again.'}
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(f"Chat request failed after {elapsed:.2f}ms for user {payload.user_id}: {e}", exc_info=True)
        return {'reply': 'Sorry, something went wrong. Please try again later.'}

