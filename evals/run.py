import argparse
import json
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from agent.config import PROMPT_VERSION, ROOT
from evals.cases import CASES


def main():
    parser = argparse.ArgumentParser(description="Phase 1 OFFLINE harness evaluation")
    parser.add_argument("--all", action="store_true", help="Run all harness cases")
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/evals/report.json")
    options = parser.parse_args()
    rows = []
    workspace_temp = ROOT / "runtime" / "evals" / "tmp"
    workspace_temp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ielts-eval-", dir=workspace_temp) as temp:
        for name, case in CASES:
            start = time.perf_counter()
            try:
                case(Path(temp) / name)
                row = {"case": name, "passed": True}
            except Exception as error:
                row = {"case": name, "passed": False, "error": f"{type(error).__name__}: {error}"}
            row["duration_ms"] = round((time.perf_counter() - start) * 1000)
            rows.append(row)
            print(f"{'PASS' if row['passed'] else 'FAIL'} {name}")
    report = {
        "mode": "offline_scripted_harness_only", "model": "SCRIPTED_OFFLINE_ONLY",
        "timestamp": datetime.now(UTC).isoformat(), "prompt_version": PROMPT_VERSION,
        "data_version": "speaking-bank-v2/synthetic-fixtures-v1", "cases": rows,
        "passed": sum(row["passed"] for row in rows), "total": len(rows),
        "band_accuracy": None,
        "limitations": "No live LLM or human-confirmed band labels. Does not prove grading quality.",
    }
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{report['passed']}/{report['total']} harness cases passed; report: {options.output}")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
