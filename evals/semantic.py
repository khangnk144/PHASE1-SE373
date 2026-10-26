"""Live checks for semantic duplicate detection on explicitly authored question pairs."""

import json

from agent.config import PROMPT_VERSION, ROOT, Settings
from agent.graph import SpeakingAgent
from agent.provider import UITModel
from agent.trace import Trace

PAIRS = [
    ("reading_paraphrase", "Why do you like reading books?",
     "What makes reading enjoyable for you?", True),
    ("transport_paraphrase", "What benefits does public transport bring to cities?",
     "How can cities benefit from public transport?", True),
    ("quoted_paraphrase", "Why do you like reading books?",
     "You mentioned 'I read books'. What makes reading enjoyable for you?", True),
    ("causes_vs_solutions", "Why do people avoid cycling in busy cities?",
     "How can cities make cycling safer?", False),
    ("past_vs_future", "What did public parks look like in the past?",
     "What changes might public parks need in the future?", False),
]


def main():
    settings = Settings.load()
    agent = SpeakingAgent(UITModel(settings))
    rows = []
    for name, previous, proposed, expected in PAIRS:
        trace = Trace()
        actual = agent.review_question(proposed, [previous], trace).duplicate
        rows.append({"case": name, "expected_duplicate": expected, "actual_duplicate": actual,
                     "passed": expected == actual, "run_id": trace.run_id})
        print(f"{'PASS' if actual == expected else 'FAIL'} {name}", flush=True)
    report = {"model": settings.model, "prompt_version": PROMPT_VERSION, "cases": rows,
              "passed": sum(r["passed"] for r in rows), "total": len(rows),
              "limitations": "Five authored pairs, not proof of universal semantic accuracy."}
    path = ROOT / "runtime/evals/semantic-v2.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"{report['passed']}/{len(rows)} semantic checks passed. {path}")
    raise SystemExit(0 if all(r["passed"] for r in rows) else 1)


if __name__ == "__main__":
    main()
