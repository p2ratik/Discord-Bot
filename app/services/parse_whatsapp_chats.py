import re
import json
import asyncio
from app.schemas.whatsapp_info import Reciever
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Regex for WhatsApp exported chat lines (supports both 12h and 24h time formats)
_WHATSAPP_LINE = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{2,4}),\s([\d:]+(?:\s[apmAPM]+)?)\s-\s(.*?):\s(.*)"
)


def _parse_file(file_path: str) -> list[dict]:
    """Read the .txt export and return a flat list of messages."""
    messages: list[dict] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = _WHATSAPP_LINE.match(line)
            if not match:
                continue

            _date, _time, sender, text = match.groups()

            if "<Media omitted>" in text:
                continue

            messages.append({
                "sender": sender.strip(),
                "text": text.strip(),
            })

    return messages


def _merge_consecutive(messages: list[dict]) -> list[dict]:
    """Merge back-to-back messages from the same sender into one."""
    merged: list[dict] = []

    for msg in messages:
        if merged and merged[-1]["sender"] == msg["sender"]:
            merged[-1]["text"] += " " + msg["text"]
        else:
            merged.append(msg)

    return merged


def _pair_messages(messages: list[dict], sender_name: str, reciever_name: str) -> list[dict]:
    """
    Pair incoming (reciever) messages with outgoing (sender) replies.
    Only keeps pairs where the reciever speaks first and the sender replies.
    """
    pairs: list[dict] = []
    i = 0
    idx = 1

    while i < len(messages) - 1:
        current = messages[i]
        nxt = messages[i + 1]

        if current["sender"] == reciever_name and nxt["sender"] == sender_name:
            pairs.append({
                "id": idx,
                "incoming": current["text"],
                "reply": nxt["text"],
            })
            idx += 1
            i += 2
        else:
            i += 1

    return pairs


async def parse_whatsapp_chat(file_path: str, reciever: Reciever) -> dict:
    """
    Parse a WhatsApp chat export file and return structured JSON.

    :param file_path: Absolute path to the .txt chat export
    :param reciever: Reciever schema with sender/reciever names and IDs
    :return: dict with sender_id, reciever_id, total_pairs, and pairs list
    """
    logger.info(f"Parsing WhatsApp chat from {file_path}")

    messages = await asyncio.to_thread(_parse_file, file_path)
    logger.info(f"Parsed {len(messages)} raw messages")

    messages = _merge_consecutive(messages)
    logger.info(f"Merged into {len(messages)} messages")

    pairs = _pair_messages(messages, reciever.sender_name, reciever.reciever_name)
    logger.info(f"Created {len(pairs)} conversation pairs")

    return {
        "sender_id": reciever.sender_id,
        "sender_name": reciever.sender_name,
        "reciever_id": reciever.reciever_id,
        "reciever_name": reciever.reciever_name,
        "total_pairs": len(pairs),
        "pairs": pairs,
    }
