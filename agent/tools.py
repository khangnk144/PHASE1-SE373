import hashlib
import json
import time
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Literal

from pydantic import Field

from agent.bank import bank_get_item, load_bank  # noqa: F401 — existing public import paths
from agent.config import ROOT
from agent.models import CRITERIA, CriterionName, StrictModel


class SkillArgs(StrictModel):
    name: Literal["speaking-examiner"]


class RetrieveArgs(StrictModel):
    test_part: Literal["speaking"]
    criterion: CriterionName
    band: int = Field(ge=1, le=9)


class BandArgs(StrictModel):
    bands: list[float] = Field(min_length=3, max_length=3)


def compute_band(bands: list[float]) -> float:
    if len(bands) != 3 or any(
        isinstance(x, bool) or not isinstance(x, (int, float))
        or not 0 <= x <= 9 or x * 2 != int(x * 2) for x in bands
    ):
        raise ValueError("Exactly three numeric half-step bands from 0 to 9 are required.")
    average = sum(Decimal(str(x)) for x in bands) / Decimal(3)
    return float((average * 2).quantize(Decimal(1), rounding=ROUND_HALF_UP) / 2)


class Toolset:
    schemas = {"load_skill": SkillArgs, "retrieve_descriptors": RetrieveArgs, "compute_band": BandArgs}

    def __init__(self, knowledge_path: Path | None = None):
        self.knowledge_path = knowledge_path or ROOT / "runtime/knowledge/descriptors.json"
        self.skill_loaded = False
        self.retrieved: dict[str, dict] = {}
        self.computed_bands: list[list[float]] = []

    def definitions(self):
        return [{"name": name, "parameters": schema.model_json_schema()}
                for name, schema in self.schemas.items()]

    def execute(self, name: str, arguments: dict, trace) -> dict:
        if name not in self.schemas:
            raise ValueError("Tool not allowed in this task.")
        args = self.schemas[name].model_validate(arguments)
        started = time.perf_counter()
        trace.emit("tool_started", tool=name, arguments=args.model_dump())
        if name == "load_skill":
            content = (ROOT / "skills/speaking-examiner/SKILL.md").read_text(encoding="utf-8")
            result = {"name": args.name, "content": content}
            log_result = {"name": args.name, "sha256": hashlib.sha256(content.encode()).hexdigest()}
            self.skill_loaded = True
            trace.emit("skill_loaded", skill=args.name, version=2)
        elif name == "retrieve_descriptors":
            if not self.knowledge_path.exists():
                raise ValueError("Descriptors chưa cài. Chạy scripts/bootstrap_descriptors.py.")
            all_chunks = json.loads(self.knowledge_path.read_text(encoding="utf-8"))["chunks"]
            # UC03 allows metadata/rule-based RAG: criterion filter + adjacent band window.
            selected = [c for c in all_chunks if c["test_part"] == args.test_part
                        and c["criterion"] == args.criterion and abs(c["band"] - args.band) <= 1]
            if not selected:
                raise ValueError("No matching Speaking descriptor chunks.")
            self.retrieved.update({c["chunk_id"]: c for c in selected})
            result = {"chunks": selected[:3]}
            log_result = {"chunk_ids": [c["chunk_id"] for c in selected[:3]]}
        else:
            result = {"overall_band": compute_band(args.bands), "criteria_count": 3}
            self.computed_bands.append(args.bands)
            log_result = result
        trace.emit(
            "tool_completed", tool=name, arguments=args.model_dump(), result=log_result,
            duration_ms=round((time.perf_counter() - started) * 1000),
        )
        return result

    def validate_assessment(self, draft, answers):
        if not self.skill_loaded:
            raise ValueError("Call load_skill first.")
        if {c.criterion for c in draft.criteria} != set(CRITERIA):
            raise ValueError("Use each assessed criterion exactly once.")
        lookup = {a.turn_id: a for a in answers}
        for criterion in draft.criteria:
            for evidence in criterion.evidence:
                if evidence.turn_id not in lookup or evidence.quote not in lookup[evidence.turn_id].text:
                    raise ValueError("Evidence must be an exact quote from its candidate turn.")
            for ref in criterion.descriptor_refs:
                chunk = self.retrieved.get(ref)
                if not chunk or chunk["criterion"] != criterion.criterion:
                    raise ValueError("Cite only retrieved Speaking chunks for this criterion.")
        bands = [c.band for c in draft.criteria]
        if not any(sorted(bands) == sorted(previous) for previous in self.computed_bands):
            raise ValueError("Call compute_band with the exact three final criterion bands.")
