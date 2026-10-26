import sqlite3
import time
from contextlib import closing, contextmanager
from pathlib import Path

from agent.config import ROOT
from agent.models import Session


class Store:
    def __init__(self, path: Path | None = None):
        self.path = path or ROOT / "runtime" / "speaking.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions "
                "(id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at REAL NOT NULL)"
            )
            # Demo retention: delete sessions older than seven days, including abandoned attempts.
            db.execute("DELETE FROM sessions WHERE updated_at < ?", (time.time() - 7 * 86400,))

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.path, timeout=10)) as db:
            with db:
                yield db

    def save_attempt(self, session: Session, trace=None):
        with self.connect() as db:
            db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "payload=excluded.payload, updated_at=excluded.updated_at",
                (session.session_id, session.model_dump_json(), time.time()),
            )
        if trace:
            trace.emit(
                "tool_completed", tool="save_attempt", scope="current_session",
                arguments={"session_id": session.session_id, "part": session.part},
                result={"saved": True, "answer_count": len(session.answers)},
            )

    def get(self, session_id: str) -> Session:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            raise ValueError("Không tìm thấy phiên local này.")
        return Session.model_validate_json(row[0])

    def delete(self, session_id: str):
        with self.connect() as db:
            db.execute("DELETE FROM sessions WHERE id=?", (session_id,))
