import discord
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('SECRET_KEY')


class MyClient(discord.Client):
    """Discord bot client"""
    
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        """
        Handle incoming messages
        
        :param message: Discord message object
        """
        if message.author.bot:
            return
            
        print(message.author)
        
        payload = {
            "user_id": str(message.author),
            "server_id":str(message.guild.id),
            "channel_id": str(message.channel.id),
            "content": message.content
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8000/chat",
                json=payload
            ) as resp:
                data = await resp.json()

        await message.channel.send(data['reply'])
        print(f'Message from {message.author}: {message.content}')


def run_bot():
    """Initialize and run the Discord bot"""
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MyClient(intents=intents)
    client.run(token)


if __name__ == "__main__":
    run_bot()
