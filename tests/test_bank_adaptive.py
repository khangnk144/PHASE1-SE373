import copy
import json

import pytest
from pydantic import ValidationError

from agent.adaptive import extract_points, question_plan
from agent.bank import load_bank, validate_bank
from agent.graph import AgentError, validate_question
from agent.models import Answer, QuestionDraft, Session, SpeakingAssessment
from evals.fixtures import SYNTHETIC_ANSWERS, ScriptedModel, complete_session, make_service


def part3_session(service, now):
    session = service.start("sp-riverside")
    for answer in SYNTHETIC_ANSWERS[:4]:
        session = service.answer(session.session_id, answer)
    now[0] += 61
    service.begin_part2(session.session_id)
    return service.answer(session.session_id, SYNTHETIC_ANSWERS[4])


def test_new_bank_and_pending_provenance():
    items = load_bank(allow_drafts=True)
    assert len(items) == 10
    assert len({q for i in items for q in i["part1"]}) == 40
    assert all(i["source"] == "llm_generated" for i in items)
    assert all(i["verification"]["status"] == "pending_human_review" for i in items)
    with pytest.raises(ValueError, match="Draft bank disabled"):
        load_bank(allow_drafts=False)


def test_verified_source_requires_human_record():
    items = copy.deepcopy(load_bank(allow_drafts=True))
    items[0]["source"] = "llm_generated_verified"
    with pytest.raises(ValueError, match="human approval"):
        validate_bank(items, allow_drafts=True)


def test_snapshot_survives_bank_changes(tmp_path, monkeypatch):
    service, now = make_service(tmp_path)
    session = service.start("sp-riverside")
    original = copy.deepcopy(session.bank_item)
    monkeypatch.setattr("agent.bank.load_bank", lambda: [])
    session = service.answer(session.session_id, SYNTHETIC_ANSWERS[0])
    assert session.bank_item == original
    assert session.current_question == original["part1"][1]
    assert session.bank_version.startswith("speaking-bank-v2:")


def test_session_requires_bank_snapshot(tmp_path):
    service, _ = make_service(tmp_path)
    session = service.start("sp-riverside")
    data = session.model_dump()
    del data["bank_item"]
    with pytest.raises(ValidationError, match="bank_item"):
        Session.model_validate(data)


def test_points_cover_more_than_first_prefix():
    text = "First idea. " + "This second sentence adds another useful idea. " * 4
    points = extract_points(text, 5)
    assert len(points) == 4
    assert all(p["quote"] in text and p["turn_id"] == 5 for p in points)


def test_adaptive_plan_changes_support_and_follows_bank(tmp_path):
    service, now = make_service(tmp_path)
    session = part3_session(service, now)
    original = session.answers[-1]
    session.answers[-1] = Answer(turn_id=original.turn_id, part=2, question="cue", text="Yes.")
    short = question_plan(session)
    session.answers[-1] = original.model_copy(update={"text": "A meaningful word " * 20})
    developed = question_plan(session)
    assert short["response_support"] == "short_answer"
    assert developed["response_support"] == "developed_answer"
    assert short["discussion_focus"] == session.bank_item["part3_topics"][1]
    assert short["reference_question"] == session.bank_item["part3_question_pool"][1]


def test_only_candidate_point_anchors_accepted(tmp_path):
    service, now = make_service(tmp_path)
    session = part3_session(service, now)
    session.candidate_points = [{"turn_id": 5, "quote": "The riverside park"}]
    draft = QuestionDraft(question="You mentioned 'limited spare money'. Why does cost matter?",
                          anchor_turn_id=5, anchor_quote="limited spare money")
    with pytest.raises(ValueError, match="candidate_points"):
        validate_question(draft, session)


def test_short_answer_requires_concise_question(tmp_path):
    service, now = make_service(tmp_path)
    session = part3_session(service, now)
    session.answers[-1] = session.answers[-1].model_copy(update={"text": "Yes."})
    session.candidate_points.append({"turn_id": 5, "quote": "Yes."})
    draft = QuestionDraft(question="You said 'Yes.'. " + "Why should people consider this issue " * 7 + "?",
                          anchor_turn_id=5, anchor_quote="Yes.")
    with pytest.raises(ValueError, match="at most 28 words"):
        validate_question(draft, session)


def test_question_anchor_case_is_aligned_to_actual_candidate_span(tmp_path):
    service, now = make_service(tmp_path)
    session = part3_session(service, now)
    draft = QuestionDraft(question="You mentioned 'the riverside park is peaceful'. Why does noise matter?",
                          anchor_turn_id=2, anchor_quote="the riverside park is peaceful")
    validate_question(draft, session)
    assert draft.anchor_quote == "The riverside park is peaceful"
    assert draft.anchor_quote in session.answers[1].text


def test_semantic_review_rejects_paraphrase_then_repairs(tmp_path):
    class RejectOnce(ScriptedModel):
        reviews = 0

        def complete(self, messages, trace):
            if messages[0]["content"].startswith("You check whether"):
                self.reviews += 1
                return json.dumps({"type": "final", "result": {"duplicate": self.reviews == 1}})
            return super().complete(messages, trace)

    model = RejectOnce()
    service, now = make_service(tmp_path, model)
    session = part3_session(service, now)
    assert len(session.followups) == 1 and model.reviews == 2


def test_repeated_semantic_failure_is_bounded(tmp_path):
    class AlwaysDuplicate(ScriptedModel):
        reviews = 0

        def complete(self, messages, trace):
            if messages[0]["content"].startswith("You check whether"):
                self.reviews += 1
                return json.dumps({"type": "final", "result": {"duplicate": True}})
            return super().complete(messages, trace)

    model = AlwaysDuplicate()
    service, now = make_service(tmp_path, model)
    with pytest.raises(AgentError):
        part3_session(service, now)
    assert model.reviews == 3


def test_final_schema_rejects_numeric_pronunciation_and_bad_offsets(tmp_path):
    service, now = make_service(tmp_path)
    session = complete_session(service, now)
    result = session.assessment
    assert SpeakingAssessment.model_validate(result)
    bad = copy.deepcopy(result)
    bad["criteria"][-1]["band"] = 9
    with pytest.raises(ValidationError):
        SpeakingAssessment.model_validate(bad)
    bad = copy.deepcopy(result)
    bad["criteria"][0]["evidence"][0]["start_char"] += 1
    with pytest.raises(ValidationError):
        SpeakingAssessment.model_validate(bad)
