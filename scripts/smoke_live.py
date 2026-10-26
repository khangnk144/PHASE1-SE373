"""Live UIT end-to-end service smoke test; synthetic candidate, accelerated prep clock."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.config import ROOT, Settings
from agent.provider import UITModel
from agent.service import SpeakingService

ANSWERS = [
    "I study software engineering at a university in Ho Chi Minh City. I enjoy building "
    "small applications because I can see the results of my work immediately. Although "
    "debugging can be frustrating, it has taught me to be patient and systematic.",
    "I like the riverside park near my flat. The paths are shaded by old trees, so it is "
    "comfortable even on warm mornings. I often walk there with my sister and we talk "
    "about our plans for the week.",
    "Quiet places help me concentrate after a busy day. I usually spend half an hour "
    "reading in the park instead of looking at my phone. This habit has improved my "
    "mood, especially when I have several university deadlines.",
    "I would like to travel by bicycle more often. Currently the traffic makes me "
    "nervous, and there are not many safe cycle lanes. If the city built protected "
    "lanes near campus, I would be happy to leave my motorbike at home.",
    "The quiet place I would describe is a riverside park about fifteen minutes from "
    "my home in Ho Chi Minh City. It has a long walking path, several benches and a "
    "small community garden. I first discovered it while visiting a friend last year. "
    "Now I go there on Sunday mornings with my sister. We normally take a short walk "
    "and then sit under the trees to read. What I appreciate most is the contrast "
    "with the noisy streets outside. The park gives local residents a place to meet "
    "without spending money, which is particularly valuable for students and older "
    "people. I hope the city will protect the trees as the neighbourhood develops.",
    "I think public spaces should be accessible to residents with different incomes. "
    "For instance, free parks offer opportunities to exercise and meet neighbours. "
    "If entrance fees were introduced, some families might stop visiting, even though "
    "they would benefit most from those facilities.",
    "Local authorities could consult residents before changing public facilities. "
    "Older people may need shaded benches, while students might prefer safe cycling "
    "routes. A combination of surveys and small community meetings would help "
    "planners understand these different priorities.",
    "Compared with the past, people have more entertainment choices at home. "
    "However, online activities cannot completely replace face-to-face contact. "
    "Neighbourhood events could encourage younger residents to spend more time "
    "outside and develop stronger relationships with people living nearby.",
    "In the future I expect cities to invest more in green spaces because heat "
    "and air pollution are becoming serious problems. Nevertheless, maintenance "
    "needs reliable funding. Universities and local businesses could support "
    "community gardens, provided that public access remains a priority.",
]


def main():
    started = time.time()
    clock_offset = [0]
    service = SpeakingService(UITModel(Settings.load()), clock=lambda: time.time() + clock_offset[0])

    def progress(event):
        if event["event"] in {"model_completed", "tool_completed", "schema_repair", "run_failed"}:
            print(json.dumps(event, ensure_ascii=True), flush=True)

    session = service.start("sp-riverside", progress)
    print("Synthetic live smoke: preparation clock accelerated by 61s; UI enforces real 60s.")
    for i, answer in enumerate(ANSWERS):
        if session.part == "part2_prepare":
            clock_offset[0] += 61
            session = service.begin_part2(session.session_id)
        print(f"Answer {i+1}/9, part={session.part}", flush=True)
        session = service.answer(session.session_id, answer, progress)
    assert session.part == "completed", session.part
    assert len(session.followups) == 4
    assert session.assessment["criteria"][-1]["status"] == "not_assessed"
    transcript = session.assessment["transcript"]
    for criterion in session.assessment["criteria"][:3]:
        for e in criterion["evidence"]:
            assert transcript[e["start_char"]:e["end_char"]] == e["quote"]
    output = ROOT / "runtime" / "live-demo.json"
    output.write_text(session.model_dump_json(indent=2), encoding="utf-8")
    print(f"LIVE PASS: session={session.session_id}; duration={time.time()-started:.1f}s")
    print(f"Result: {output}; pronunciation=not_assessed; no accuracy claim.")


if __name__ == "__main__":
    main()
