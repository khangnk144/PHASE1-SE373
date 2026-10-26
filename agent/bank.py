"""Question-bank provenance, local draft access and immutable per-session snapshots."""

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from agent.config import ROOT


def drafts_enabled():
    load_dotenv(ROOT / ".env")
    # This project is a local prototype; the user explicitly enabled draft testing.
    return os.getenv("ALLOW_DRAFT_BANK", "1") == "1"


def validate_bank(items, *, allow_drafts):
    if not isinstance(items, list) or not items:
        raise ValueError("Question bank must be a non-empty array.")
    required = {
        "item_id", "skill", "question_type", "topic", "target_band", "source", "license",
        "author", "created_at", "part1", "cue_card",
    }
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not required <= item.keys():
            raise ValueError("Invalid question bank metadata.")
        for key in ["item_id", "topic", "license", "author", "created_at"]:
            if not isinstance(item[key], str) or not item[key].strip():
                raise ValueError(f"Missing bank metadata: {key}.")
        if item["item_id"] in seen:
            raise ValueError("Duplicate bank item ID.")
        seen.add(item["item_id"])
        if item["skill"] != "speaking" or item["question_type"] != "mock_test_parts_1_3":
            raise ValueError("Expected a three-part Speaking item.")
        if item["license"] not in {"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0"}:
            raise ValueError("Unsupported question bank license.")
        source = item["source"]
        verification = item.get("verification") or {}
        if not isinstance(verification, dict):
            raise ValueError("Invalid bank verification metadata.")
        bands = item["target_band"]
        if (not isinstance(bands, list) or len(bands) != 2
                or any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in bands)
                or not 0 <= bands[0] <= bands[1] <= 9):
            raise ValueError("Invalid target band practice range.")
        if source == "llm_generated":
            if verification.get("status") != "pending_human_review":
                raise ValueError("LLM drafts must honestly retain pending_human_review.")
            if verification.get("reviewer") or verification.get("reviewed_at"):
                raise ValueError("A pending draft must not claim completed human review.")
            if not allow_drafts:
                raise ValueError("Draft bank disabled. This item still needs human review.")
        elif source == "llm_generated_verified":
            if verification.get("status") != "approved" or not all(
                verification.get(k) for k in ["reviewer", "reviewed_at"]
            ):
                raise ValueError("Verified LLM items require recorded human approval.")
        elif source not in {"self_written", "open_license"}:
            raise ValueError("Unknown bank provenance.")
        p1 = item["part1"]
        cue = item["cue_card"]
        if not isinstance(p1, list) or not 4 <= len(p1) <= 6:
            raise ValueError("Part 1 requires 4–6 questions.")
        if not isinstance(cue, dict) or not isinstance(cue.get("prompt"), str):
            raise ValueError("Invalid cue card.")
        bullets = cue.get("bullets")
        if not cue["prompt"].strip() or not isinstance(bullets, list) or not 3 <= len(bullets) <= 4:
            raise ValueError("A cue card requires a prompt and 3–4 bullets.")
        for values in [p1, bullets, item.get("part3_topics", []), item.get("part3_question_pool", [])]:
            if not isinstance(values, list) or any(not isinstance(s, str) or not s.strip() for s in values):
                raise ValueError("Bank question lists must contain non-empty strings.")
        directions = item.get("part3_topics", [])
        pool = item.get("part3_question_pool", [])
        if directions and len(directions) != 4:
            raise ValueError("The demo requires four Part 3 discussion directions.")
        if pool and len(pool) != len(directions):
            raise ValueError("Part 3 reference questions must match the discussion directions.")
    return items


def load_bank(path: Path | None = None, *, allow_drafts: bool | None = None):
    path = path or ROOT / "data/bank/speaking.json"
    return validate_bank(
        json.loads(path.read_text(encoding="utf-8")),
        allow_drafts=drafts_enabled() if allow_drafts is None else allow_drafts,
    )


def bank_get_item(item_id):
    for item in load_bank():
        if item["item_id"] == item_id:
            return item
    raise ValueError("Unknown speaking item.")


def bank_version(item):
    digest = hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return "speaking-bank-v2:" + digest[:12]


def session_item(session):
    return session.bank_item
