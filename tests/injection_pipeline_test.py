"""
Injection Pipeline Test
-----------------------
End-to-end script that:
  1. Parses a WhatsApp chat export  (parse_whatsapp_chats)
  2. Generates embeddings for pairs  (EmbeddingManager)
  3. Inserts the vectors into the DB  (insert_vectors)

Run:  python -m tests.injection_pipeline_test   (from project root)
"""

import sys
import os
import asyncio
import json

# ── make the project root importable ──
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.parse_whatsapp_chats import parse_whatsapp_chat
from app.schemas.whatsapp_info import Reciever
from app.services.embeddings import embed_pairs
from app.services.vector_store import insert_vectors
from app.db.session import AsyncSessionLocal

# ── constants ──
TEXT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "datasets", "text.txt")
)

RECIEVER = Reciever(
    sender_name="Pratik",
    reciever_name="Sagar",
    sender_id="sg",
    reciever_id="pc",
)


async def run_pipeline():
    """Execute the full parse → embed → inject pipeline."""

    # 1. Validate the input file
    if not os.path.exists(TEXT_PATH):
        print(f"❌ Chat file not found at {TEXT_PATH}")
        return

    # 2. Parse the WhatsApp chat export
    print("📄 Parsing WhatsApp chat …")
    parsed = await parse_whatsapp_chat(TEXT_PATH, RECIEVER)
    print(f"   → {parsed['total_pairs']} conversation pairs found\n")

    if not parsed["pairs"]:
        print("⚠️  No pairs to embed. Exiting.")
        return

    # 3. Generate embeddings
    print("🧠 Generating embeddings …")
  
    embedded_pairs = await embed_pairs(parsed)
    #print(f"   → Embedded {len(embedded_pairs)} pairs\n")
    #print(embedded_pairs)

    # 4. Insert vectors into the database
    print("💾 Injecting vectors into the database …")
    async with AsyncSessionLocal() as db:
        await insert_vectors(
            embedded_pairs, db
        )
    print("✅ Injection pipeline completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
