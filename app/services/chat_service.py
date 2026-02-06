from app.schemas.chat import Payload
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import role_service
from app.services import message_service
from app.schemas.chat import BotMessageRecieve
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

def createMessage(payload:Payload, reply:str):
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
    
    roles = role_obj.role if role_obj else {}
    
    # Getting the previous messages of the user if exist
    prev_messages = await message_service.get_user_messages(payload.user_id, db)

    #formatting the previous messages 
    prev_msg_format = [{'user':m.user_id, 'content':m.content} for m in prev_messages]

    prompt = f"""You're an AI bot pretending to be me. Your task is to reply to text messages which you receive in a way I do. I will provide you with the roles and all the necessary information you will be expecting to communicate with a person I do. The roles I provide will be specific to that person you're communicating with. Don't generalize the roles. Let me tell you about myself which will help you to answer better. I will also provide you the previous messages for that particular person so that you will know which topics you were talking about earlier. If the previous messages are null dont worry you'll answer normally.

    Name: Pratik
    Age: 18
    Nature: Funny, Introvert, Loves Technology, Plays Roblox, Favorite programming language: c++, Also working on a startup, Favourite color: black, confident 

    Now this is an example of role you will be expecting user_id = 'hani' user_name = Suhani
    {{"role":['friend'] "nicknames":['rocky', 'buddy', 'pal', 'dawg'] "nature":["introvert", "loves maths", "plays Roblox"]}}

    Now based on the role you have to answer to that person. Try using nicknames more and answer in the language the user is communicating through. (Language: ENGLISH/BEN/ENGLISH/HIN/ENGLISH)

    roles = {roles}
    user_id = {payload.user_id}
    message = {payload.content}
    prev_messages = {prev_msg_format}
"""
    return prompt


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

