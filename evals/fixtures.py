"""OFFLINE SCRIPTED MODEL. Only for harness tests; never used by the application."""

import json
from pathlib import Path

from agent.models import CRITERIA
from agent.service import SpeakingService
from agent.storage import Store

SYNTHETIC_ANSWERS = [
    "I study software engineering because I enjoy solving problems with my friends.",
    "The riverside park is peaceful and I often walk there with my sister on Sundays.",
    "Reading under the trees helps me concentrate after a busy day at university.",
    "I would like safer cycle lanes because the traffic near campus is very busy.",
    "The riverside park near my home has shaded paths and a small community garden. "
    "I visit with my sister and we read books together. It gives everyone a free place "
    "to relax, which matters because many local families have limited spare money.",
    "Public facilities should be affordable for people with different incomes.",
    "Local authorities could ask residents what improvements they need most.",
    "Young people spend more time online but still benefit from meeting neighbours.",
    "Cities will need more trees to cope with heat and improve residents' health.",
]


def action(tool_name, **arguments):
    return json.dumps({"type": "tool_call", "name": tool_name, "arguments": arguments})


class ScriptedModel:
    """Chooses prearranged actions, not an LLM. No claim about grading quality."""

    def __init__(self, corrupt=None):
        self.corrupt = corrupt

    def complete(self, messages, trace):
        trace.emit("model_completed", model="SCRIPTED_OFFLINE_ONLY", duration_ms=0,
                   prompt_tokens=None, completion_tokens=None, cost_usd=None)
        if messages[0]["content"].startswith("You check whether"):
            return json.dumps({"type": "final", "result": {"duplicate": False}})
        context = json.loads(messages[1]["content"].split("\n", 1)[1])
        observations = []
        for m in messages[2:]:
            if m["role"] == "user" and m["content"].startswith('{"tool_observation"'):
                observations.append(json.loads(m["content"]))
        used = [o["tool_observation"] for o in observations]
        if "load_skill" not in used:
            return action("load_skill", name="speaking-examiner")
        if context["task"] == "question":
            answers = context["candidate_answers"]
            source = answers[-1]
            quote = " ".join(source["text"].split()[:4])
            aspects = [
                "How could this affect people with different incomes?",
                "Why might local authorities have a different perspective?",
                "How has this issue changed compared with the past?",
                "What consequences could this have for future generations?",
            ]
            result = {
                "question": f"You mentioned '{quote}'. " + aspects[len(context["previous_followups"])],
                "anchor_turn_id": source["turn_id"], "anchor_quote": quote,
            }
        else:
            retrieved = [o for o in observations if o["tool_observation"] == "retrieve_descriptors"]
            if len(retrieved) < 3:
                return action("retrieve_descriptors", test_part="speaking",
                              criterion=CRITERIA[len(retrieved)], band=6)
            if "compute_band" not in used:
                return action("compute_band", bands=[6, 6, 6])
            evidence = context["candidate_answers"][0]
            result = {"criteria": [], "improvements": ["Practise linking one reason to a concrete example."]}
            for criterion, observation in zip(CRITERIA, retrieved, strict=True):
                ref = observation["result"]["chunks"][0]["chunk_id"]
                result["criteria"].append({
                    "criterion": criterion, "band": 6,
                    "evidence": [{"turn_id": evidence["turn_id"], "quote": evidence["text"]}],
                    "descriptor_refs": [ref], "comment": "Scripted test feedback, not an AI assessment.",
                })
            if self.corrupt == "evidence":
                result["criteria"][0]["evidence"][0]["quote"] = "THIS QUOTE DOES NOT EXIST"
            if self.corrupt == "descriptor":
                result["criteria"][0]["descriptor_refs"] = ["writing:fake:9"]
            if self.corrupt == "arithmetic":
                result["criteria"][0]["band"] = 9
        return json.dumps({"type": "final", "result": result})


def make_service(directory: Path, model=None):
    directory.mkdir(parents=True, exist_ok=True)
    chunks = [
        {"chunk_id": f"speaking:{criterion}:6:TEST_ONLY", "test_part": "speaking",
         "criterion": criterion, "band": 6, "version": "test-only",
         "source_url": "https://example.invalid/test-fixture",
         "text": "SYNTHETIC TEST FIXTURE. Not an official band descriptor."}
        for criterion in CRITERIA
    ]
    knowledge = directory / "test_descriptors.json"
    knowledge.write_text(json.dumps({"chunks": chunks}), encoding="utf-8")
    now = [1000.0]
    service = SpeakingService(
        model or ScriptedModel(), Store(directory / "test.sqlite3"), knowledge,
        clock=lambda: now[0], trace_dir=directory / "traces",
    )
    return service, now


def complete_session(service, now, answers=None):
    session = service.start("sp-riverside")
    for answer in answers or SYNTHETIC_ANSWERS:
        if session.part == "part2_prepare":
            now[0] += 61
            session = service.begin_part2(session.session_id)
        session = service.answer(session.session_id, answer)
    return session
