"""Download official descriptors to ignored runtime; split by criterion x band.

Run from repository root: uv run python scripts/bootstrap_descriptors.py
No official PDF or extracted text is redistributed in the repository.
"""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://ielts.org/cdn/ielts-guides/ielts-speaking-band-descriptors.pdf"
CRITERIA = [
    "fluency_coherence", "lexical_resource", "grammatical_range_accuracy", "pronunciation",
]


def main():
    directory = ROOT / "runtime" / "knowledge"
    directory.mkdir(parents=True, exist_ok=True)
    response = httpx.get(SOURCE, timeout=60, follow_redirects=True)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Source did not return a PDF; ingestion stopped.")
    digest = hashlib.sha256(response.content).hexdigest()
    pdf = directory / "speaking-descriptors.pdf"
    pdf.write_bytes(response.content)
    chunks = []
    with pymupdf.open(pdf) as document:
        for page_number, page in enumerate(document):
            # Detect table layout, then extract columns inside each band row. Column
            # extraction preserves semantic criterion boundaries, unlike fixed text chunks.
            tables = page.find_tables()
            for table in tables.tables:
                for row in table.extract():
                    if len(row) < 5:
                        continue
                    label = (row[0] or "").strip()
                    if not label.isdigit() or not 1 <= int(label) <= 9:
                        continue
                    band = int(label)
                    for criterion, text in zip(CRITERIA, row[1:5], strict=True):
                        if not text or len(text.strip()) < 10:
                            continue
                        chunks.append({
                            "chunk_id": f"speaking:{criterion}:{band}:{digest[:8]}",
                            "test_part": "speaking", "criterion": criterion, "band": band,
                            "version": digest[:12], "source_url": SOURCE,
                            "page": page_number + 1,
                            "text": " ".join(text.split()),
                        })
    assessed = [c for c in chunks if c["criterion"] != "pronunciation"]
    expected = {(criterion, band) for criterion in CRITERIA[:3] for band in range(1, 10)}
    found = {(c["criterion"], c["band"]) for c in assessed}
    if found != expected or len(chunks) != len({c["chunk_id"] for c in chunks}):
        raise RuntimeError(
            f"Official PDF layout changed; missing={sorted(expected - found)}. "
            "Inspect the source and update parser, do not use partial descriptors."
        )
    payload = {
        "source_url": SOURCE, "sha256": digest,
        "downloaded_at": datetime.now(UTC).isoformat(), "chunks": chunks,
    }
    target = directory / "descriptors.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    print(f"Indexed {len(chunks)} Speaking criterion x band chunks; sha256={digest[:12]}.")


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, RuntimeError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        raise SystemExit(1) from None
