import re

from agent.bank import session_item


def extract_points(text, turn_id):
    """Bounded, verbatim sentence spans; not a claim of semantic summarisation."""
    points = []
    for sentence in re.split(r"(?<=[.!?])\s+|[\r\n]+", text.strip()):
        quote = sentence.strip()[:160]
        if quote:
            points.append({"turn_id": turn_id, "quote": quote})
        if len(points) == 4:
            break
    return points


def question_plan(session):
    item = session_item(session)
    index = len(session.followups)
    if not 0 <= index < 4:
        raise ValueError("Part 3 has exactly four discussion turns.")
    words = len(session.answers[-1].text.split()) if session.answers else 0
    support = "short_answer" if words <= 5 else "developed_answer" if words >= 35 else "standard"
    directions = item.get("part3_topics") or ["Reasons", "Comparison", "Change", "Consequences"]
    pool = item.get("part3_question_pool") or [None] * 4
    return {
        "focus_index": index, "discussion_focus": directions[index],
        "reference_question": pool[index], "response_support": support,
        "topic": item["topic"], "cue_card": item["cue_card"],
        "latest_answer_turn_id": session.answers[-1].turn_id if session.answers else None,
    }
