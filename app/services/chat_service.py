from app.schemas.chat import Payload
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import role_service
from app.services import message_service
from app.schemas.chat import BotMessageRecieve
from app.services import admin_service
from app.services import prompt
import google.genai as genai
from dotenv import load_dotenv
import asyncio
import os 

load_dotenv()

apikey = os.getenv('LLM_API_KEY')

try:
    client = genai.Client(api_key=apikey)
except Exception as e:
    print(f'API key not configured {e}')    

async def createMessage(payload:Payload, reply:str):
    try:
        bm_obj = BotMessageRecieve(
            channel_id=str(payload.channel_id),
            user_id=str(payload.user_id),
            content=str(payload.content),
            bot_reply = reply
        )
        return bm_obj
    except Exception as e:
        print(f"Some error occured {e}")    


async def build_prompt(payload: Payload, db: AsyncSession) -> str:
    """
    Build a prompt for the LLM based on the chat payload
    
    :param payload: Chat payload containing user message
    :type payload: Payload
    :param db: Database session
    :type db: AsyncSession
    :return: Formatted prompt string
    """
    # Getting role for the user_id 
    role_obj = await role_service.get_roles_for_user(payload.user_id, db)

    # Getting role for the admin

    role_admin_obj = await admin_service.get_role_for_admin('pratik081978', db)
    
    role_admin = role_admin_obj.role

    roles = role_obj.role if role_obj else {}
    
    # Getting the previous messages of the user if exist
    prev_messages = await message_service.get_user_messages(payload.user_id, db)

    #formatting the previous messages 
    prev_messages_format = [{'user_message':m.content , 'bot_reply':m.bot_reply} for m in prev_messages]

    return await prompt.develop_prompt(roles, payload.content , prev_messages_format, role_admin)


def _call_llm_sync(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt, 
    )
    return response.text


async def call_llm(prompt: str) -> str:
    return await asyncio.to_thread(_call_llm_sync, prompt)


async def process_chat(payload: Payload, db: AsyncSession) -> dict:
    """
    Process a chat message and generate a response
    
    :param payload: Chat payload
    :type payload: Payload
    :param db: Database session
    :type db: AsyncSession
    :return: Dictionary with reply
    """
    prompt = await build_prompt(payload, db)
    llm_response = await call_llm(prompt)
    # Adding the current data to the db
    message = await createMessage(payload=payload, reply=llm_response)
    await message_service.add_user_messages(message=message, db=db)
    return {'reply': llm_response}

