import discord
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from app.utils.logger import get_logger

load_dotenv()

token = os.getenv('SECRET_KEY')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')

logger = get_logger(__name__)


class MyClient(discord.Client):
    """Discord bot client"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seen_messages = set()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged on as {self.user}!')

    async def on_message(self, message):
        """
        Handle incoming messages — reply when the bot is mentioned.
        """
        logger.debug(f"Message received from {message.author}: {message.content[:50]}")
        
        if message.author.bot:
            return
            
        if self.user not in message.mentions:
            #Reply only when its tagged
            return

        if message.guild is None:
            await message.channel.send("I only work in servers, not DMs!")
            return
        
        # Deduplicate — ignore if we already processed this message
        if message.id in self._seen_messages:
            return
        self._seen_messages.add(message.id)
        # Cap the set size to prevent unbounded growth
        if len(self._seen_messages) > 1000:
            self._seen_messages.clear()           

        # Strip the mention from the message content
        content = (
            message.content
            .replace(f"<@{self.user.id}>", "")
            .replace(f"<@!{self.user.id}>", "")
            .strip()
        )

        payload = {
            "user_id": str(message.author),
            "server_id": str(message.guild.id),
            "channel_id": str(message.channel.id),
            "content": content,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{API_URL}/chat",
                    json=payload,
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"API returned {resp.status}: {await resp.text()}")
                        await message.channel.send("⚠️ Something went wrong, please try again.")
                        return

                    data = await resp.json()

            reply = data.get("reply", "I didn't get a response.")
            await message.channel.send(reply)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await message.channel.send("⚠️ I'm having trouble right now, please try again later.")


async def run_bot():
    """Initialize and run the Discord bot"""
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MyClient(intents=intents)
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(run_bot())
