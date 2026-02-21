import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.parse_whatsapp_chats import parse_whatsapp_chat
from app.schemas.whatsapp_info import Reciever

# Path to the test chat file (relative to project root)
TEXT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "text.txt"))

reciever = Reciever(
    sender_name="Pratik",
    reciever_name="Sagar",
    sender_id="sg",
    reciever_id="pc",
)


async def main():
    if not os.path.exists(TEXT_PATH):
        print(f"Error: Chat file not found at {TEXT_PATH}")
        return

    result = await parse_whatsapp_chat(TEXT_PATH, reciever)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nTotal pairs: {result['total_pairs']}")


if __name__ == "__main__":
    asyncio.run(main())
