from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agent.config import DISCLAIMER

CriterionName = Literal["fluency_coherence", "lexical_resource", "grammatical_range_accuracy"]
CRITERIA = ("fluency_coherence", "lexical_resource", "grammatical_range_accuracy")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    turn_id: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=600)


class CriterionDraft(StrictModel):
    criterion: CriterionName
    band: float = Field(ge=0, le=9, multiple_of=0.5)
    evidence: list[Evidence] = Field(min_length=1, max_length=3)
    descriptor_refs: list[str] = Field(min_length=1, max_length=4)
    comment: str = Field(min_length=10, max_length=1500)


class AssessmentDraft(StrictModel):
    criteria: list[CriterionDraft] = Field(min_length=3, max_length=3)
    improvements: list[str] = Field(min_length=1, max_length=3)


class QuestionDraft(StrictModel):
    question: str = Field(min_length=15, max_length=400)
    anchor_turn_id: int = Field(ge=1)
    anchor_quote: str = Field(min_length=3, max_length=160)


class QuestionReview(StrictModel):
    duplicate: bool


class FinalEvidence(Evidence):
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)


class AssessedCriterion(CriterionDraft):
    evidence: list[FinalEvidence] = Field(min_length=1, max_length=3)
    status: Literal["assessed"] = "assessed"


class PronunciationCriterion(StrictModel):
    criterion: Literal["pronunciation"] = "pronunciation"
    band: None = None
    status: Literal["not_assessed"] = "not_assessed"
    evidence: list[FinalEvidence] = Field(default_factory=list, max_length=0)
    descriptor_refs: list[str] = Field(default_factory=list, max_length=0)
    comment: str = Field(min_length=1)


class SpeakingAssessment(StrictModel):
    criteria: list[AssessedCriterion | PronunciationCriterion] = Field(min_length=4, max_length=4)
    improvements: list[str] = Field(min_length=1, max_length=3)
    overall_band: float = Field(ge=0, le=9, multiple_of=0.5)
    mode: Literal["text"]
    disclaimer: Literal[DISCLAIMER]
    limitations: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]
    flags: list[str]
    transcript: str = Field(min_length=1)
    bank_provenance: dict

    @model_validator(mode="after")
    def validate_final(self):
        if {c.criterion for c in self.criteria} != {*CRITERIA, "pronunciation"}:
            raise ValueError("Exactly four distinct Speaking criteria are required.")
        for criterion in self.criteria:
            for evidence in criterion.evidence:
                if self.transcript[evidence.start_char:evidence.end_char] != evidence.quote:
                    raise ValueError("Final evidence offsets must match the transcript exactly.")
        return self


class ToolAction(StrictModel):
    type: Literal["tool_call"]
    name: str
    arguments: dict


class FinalAction(StrictModel):
    type: Literal["final"]
    result: dict


class Answer(StrictModel):
    turn_id: int
    part: int
    question: str
    text: str


class Session(StrictModel):
    session_id: str
    item_id: str
    bank_item: dict
    bank_version: str
    part: Literal["part1", "part2_prepare", "part2", "part3", "assessment", "completed"]
    asked_questions: list[str] = Field(default_factory=list)
    candidate_points: list[dict] = Field(default_factory=list)
    elapsed_seconds: float = 0
    created_at: float
    preparation_started_at: float | None = None
    answers: list[Answer] = Field(default_factory=list)
    current_question: str
    followups: list[dict] = Field(default_factory=list)
    assessment: dict | None = None
    pending_action: Literal["next_question", "assess"] | None = None
    flags: list[str] = Field(default_factory=list)
    run_ids: list[str] = Field(default_factory=list)
