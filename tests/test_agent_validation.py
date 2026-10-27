"""Offline protocol regression; this scripted model does not assess model quality."""

import json

from agent.graph import SpeakingAgent
from agent.models import Answer, Session
from agent.trace import Trace


def test_repairs_transcript_anchor_outside_candidate_points(tmp_path):
    class AnchorRepairModel:
        def complete(self, messages, trace):
            if messages[0]["content"].startswith("You check whether"):
                return json.dumps({"type": "final", "result": {"duplicate": False}})
            if len(messages) == 2:
                return json.dumps({
                    "type": "tool_call", "name": "load_skill",
                    "arguments": {"name": "speaking-examiner"},
                })
            repair = next((m["content"] for m in messages if m["role"] == "user"
                           and "Allowed candidate_points: " in m["content"]), None)
            if repair:
                point = json.loads(repair.split("Allowed candidate_points: ", 1)[1])[0]
                quote, turn_id = point["quote"], point["turn_id"]
            else:
                # This is in the transcript, but was not retained as a candidate point.
                quote, turn_id = "Local residents", 1
            return json.dumps({"type": "final", "result": {
                "question": f"You mentioned '{quote}'. How could parks serve different age groups?",
                "anchor_turn_id": turn_id, "anchor_quote": quote,
            }})

    session = Session(
        session_id="synthetic-anchor-repair", item_id="synthetic-park", bank_version="test-only",
        bank_item={"topic": "Parks", "cue_card": {"prompt": "Describe a park.", "bullets": []},
                   "part3_topics": ["Access", "Change", "Funding", "Future"],
                   "part3_question_pool": ["Who uses parks?", "How have parks changed?",
                                           "Who pays for parks?", "What will parks need?"]},
        part="part3", created_at=0, current_question="Describe a park.",
        answers=[Answer(turn_id=1, part=2, question="Describe a park.",
                        text="I walk in the park. Local residents also visit it.")],
        candidate_points=[{"turn_id": 1, "quote": "I walk in the park."}],
    )
    trace = Trace(tmp_path / "traces")
    result = SpeakingAgent(AnchorRepairModel()).run("question", session, trace)

    assert result["anchor_quote"] == "I walk in the park."
    assert result["anchor_turn_id"] == 1
    assert result["anchor_quote"] in result["question"]
    assert sum(event["event"] == "schema_repair" for event in trace.events) == 1
