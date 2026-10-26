import re
import time
from uuid import uuid4

from agent.adaptive import extract_points, question_plan
from agent.bank import bank_version, session_item
from agent.config import DISCLAIMER, TEXT_LIMITATION
from agent.graph import SpeakingAgent
from agent.models import Answer, Session, SpeakingAssessment
from agent.storage import Store
from agent.tools import bank_get_item, compute_band
from agent.trace import Trace

INJECTION = re.compile(
    r"ignore.{0,40}(instructions|rubric)|system\s*:|set all criteria|"
    r"give.{0,30}(band\s*9|pronunciation)|teacher.{0,20}approved", re.I,
)
PREVIEW = re.compile(
    r"(show|reveal|preview|see|xem|cho).{0,55}(part\s*3|phần\s*3|future questions)", re.I,
)


class SpeakingService:
    def __init__(self, model, store=None, knowledge_path=None, clock=None, trace_dir=None):
        self.store = store or Store()
        self.agent = SpeakingAgent(model, knowledge_path)
        self.clock = clock or time.time
        self.trace_dir = trace_dir

    def trace(self, session=None, callback=None):
        trace = Trace(self.trace_dir, callback)
        trace.emit("run_started", use_case="UC03",
                   data_version=session.bank_version if session else "speaking-bank-v2")
        if session:
            session.run_ids.append(trace.run_id)
        return trace

    def start(self, item_id, callback=None):
        trace = self.trace(callback=callback)
        item = bank_get_item(item_id)
        trace.emit("tool_completed", tool="bank_get_item", arguments={"item_id": item_id},
                   result={"source": item["source"], "license": item["license"],
                           "verification": item.get("verification", {}).get("status"),
                           "bank_version": bank_version(item)})
        session = Session(
            session_id=uuid4().hex, item_id=item_id, bank_item=item,
            bank_version=bank_version(item), part="part1", created_at=self.clock(),
            current_question=item["part1"][0], asked_questions=[item["part1"][0]],
            run_ids=[trace.run_id],
        )
        self.store.save_attempt(session, trace)
        return session

    def begin_part2(self, session_id):
        session = self.store.get(session_id)
        if session.part != "part2_prepare":
            raise ValueError("Không ở bước chuẩn bị Part 2.")
        if self.clock() - session.preparation_started_at < 60:
            raise ValueError("Cần đủ 60 giây chuẩn bị trước khi bắt đầu Part 2.")
        session.part = "part2"
        session.elapsed_seconds = max(0, self.clock() - session.created_at)
        self.store.save_attempt(session)
        return session

    def answer(self, session_id, text, callback=None):
        session = self.store.get(session_id)
        if session.pending_action:
            raise ValueError("Câu trước đã lưu; bấm Thử lại bước agent, không nộp lặp.")
        if session.part not in {"part1", "part2", "part3"}:
            raise ValueError("Phiên hiện không nhận câu trả lời.")
        text = text.strip()
        if not text or len(text) > 6000:
            raise ValueError("Nhập câu trả lời từ 1 đến 6000 ký tự.")
        trace = self.trace(session, callback)
        if PREVIEW.search(text):
            if "future_question_request_blocked" not in session.flags:
                session.flags.append("future_question_request_blocked")
            trace.emit("guardrail", rule="no_future_question_preview", blocked=True)
            self.store.save_attempt(session, trace)
            return session
        if INJECTION.search(text):
            if "injection_detected" not in session.flags:
                session.flags.append("injection_detected")
            trace.emit("guardrail", rule="candidate_instruction_is_data", blocked=True)
        part = int(session.part[-1])
        answer = Answer(
            turn_id=len(session.answers) + 1, part=part,
            question=session.current_question, text=text,
        )
        session.answers.append(answer)
        # Exact spans, not invented summaries. Model can refer to any earlier answer.
        safe_text = INJECTION.split(text)[0].strip()
        session.candidate_points.extend(extract_points(safe_text, answer.turn_id))
        session.elapsed_seconds = max(0, self.clock() - session.created_at)
        count = sum(a.part == part for a in session.answers)
        item = session_item(session)
        if part == 1 and count < len(item["part1"]):
            session.current_question = item["part1"][count]
            session.asked_questions.append(session.current_question)
        elif part == 1:
            session.part = "part2_prepare"
            session.preparation_started_at = self.clock()
            cue = item["cue_card"]
            session.current_question = cue["prompt"] + "\n" + "\n".join(cue["bullets"])
            session.asked_questions.append(session.current_question)
        elif part == 2 or (part == 3 and count < 4):
            session.part = "part3"
            session.pending_action = "next_question"
        else:
            session.part = "assessment"
            session.pending_action = "assess"
        # Persist the answer BEFORE a network operation. Retry only generates the missing result.
        self.store.save_attempt(session, trace)
        return self._continue(session, trace)

    def retry(self, session_id, callback=None):
        session = self.store.get(session_id)
        if not session.pending_action:
            raise ValueError("Không có bước agent đang chờ thử lại.")
        return self._continue(session, self.trace(session, callback))

    def _continue(self, session, trace):
        try:
            if session.pending_action == "next_question":
                plan = question_plan(session)
                result = self.agent.run("question", session, trace)
                session.current_question = result["question"]
                session.asked_questions.append(result["question"])
                session.followups.append({**result, **{
                    k: plan[k] for k in ["focus_index", "discussion_focus", "response_support"]
                }})
                session.pending_action = None
            elif session.pending_action == "assess":
                draft = self.agent.run("assessment", session, trace)
                session.assessment = self._assessment(draft, session)
                session.part = "completed"
                session.pending_action = None
            session.elapsed_seconds = max(0, self.clock() - session.created_at)
            self.store.save_attempt(session, trace)
            trace.emit("run_completed", part=session.part, answer_count=len(session.answers))
            return session
        except Exception as error:
            trace.emit("run_failed", error_type=type(error).__name__, recoverable=True)
            self.store.save_attempt(session, trace)
            raise

    def _assessment(self, draft, session):
        transcript = "\n".join(a.text for a in session.answers)
        offset = {}
        position = 0
        for answer in session.answers:
            offset[answer.turn_id] = position
            position += len(answer.text) + 1
        for criterion in draft["criteria"]:
            for evidence in criterion["evidence"]:
                answer = next(a for a in session.answers if a.turn_id == evidence["turn_id"])
                start = offset[answer.turn_id] + answer.text.index(evidence["quote"])
                evidence.update(start_char=start, end_char=start + len(evidence["quote"]))
        bands = [c["band"] for c in draft["criteria"]]
        draft["criteria"].append({
            "criterion": "pronunciation", "band": None, "status": "not_assessed",
            "evidence": [], "descriptor_refs": [], "comment": "Không chấm phát âm từ text.",
        })
        result = {
            **draft, "overall_band": compute_band(bands),
            "bank_provenance": {
                "item_id": session.item_id, "version": session.bank_version,
                "source": session_item(session)["source"],
                "verification": session_item(session).get("verification", {}).get("status"),
            },
            "mode": "text", "disclaimer": DISCLAIMER, "limitations": TEXT_LIMITATION,
            "confidence": "low" if len(transcript.split()) < 200 else "medium",
            "flags": session.flags, "transcript": transcript,
        }
        return SpeakingAssessment.model_validate(result).model_dump()
