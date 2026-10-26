import json
import time
from pathlib import Path
from uuid import uuid4

from agent.config import ROOT


class Trace:
    """Metadata only: never store model prompts, candidate text, quotes or raw responses."""

    def __init__(self, directory: Path | None = None, callback=None):
        self.run_id = uuid4().hex
        self.directory = directory or ROOT / "runtime" / "traces"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / f"{self.run_id}.jsonl"
        self.callback = callback
        self.events = []

    def emit(self, event: str, **metadata):
        row = {"run_id": self.run_id, "timestamp": time.time(), "event": event, **metadata}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.events.append(row)
        if self.callback:
            self.callback(row)
