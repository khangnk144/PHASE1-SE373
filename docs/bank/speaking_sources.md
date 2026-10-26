# Speaking Bank — Research Sources and Editorial Principles

**Project:** IELTS Learning Agent / UC03 — nhóm 38
**Research and access date:** 2026-10-26 (Asia/Bangkok)
**Status:** Principles researched; the original bank remains an **AI-assisted draft pending human review**.

## Scope and intellectual-property boundaries

The pages and PDF below were opened and read to understand **test format, task purpose and principles of speaking practice**, not to collect, remix or republish source questions. All English practice questions in `speaking.draft.json` were authored anew for this assignment. No cue card, commercial-book question, copyrighted sample prompt, recall/leaked item, answer transcript, or source passage is included. **The original sources are not redistributed with this package.**

The value `license: "CC-BY-4.0"` is intended **only for the 10 original AI-assisted draft question sets** in this deliverable, subject to the team's rights/attribution review. It does **not** state or imply that any material owned by IELTS.org, British Council or IDP is licensed under Creative Commons. No conclusion about third-party permission to redistribute was inferred from the fact that content was publicly accessible. This compilation does not claim official IELTS endorsement, examiner authorship or authenticated past-paper status.

## Official references actually accessed

### IELTS-01 — IELTS.org: IELTS Academic: Speaking test format
- **Organisation:** IELTS.org
- **URL:** https://www.ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-speaking
- **Accessed:** 2026-10-26
- **Read:** Introduction and interview (familiar topics, everyday experiences), individual long turn (task card with content points and preparation time), and Part 3 (general/abstract discussion related to the Part 2 topic).
- **Editorial application:** Part 1 asks one accessible, personal question at a time; Part 2 provides an open cue card for sustained speech; each Part 3 group moves beyond the speaker's anecdote.
- **Note:** Timing of the actual exam was used only to understand task purpose; the demo's fixed 4 questions per Part 1 and 4 Part 3 pool questions are local product constraints.

### BC-01 — British Council: IELTS Speaking Test: How it Works
- **Organisation:** British Council / Take IELTS
- **URL:** https://takeielts.britishcouncil.org/what-is-ielts/how-it-works/test-format/speaking
- **Accessed:** 2026-10-26
- **Read:** Questions about familiar topics are straightforward and conversational; the Part 2 task card supports a sustained talk; Part 3 discusses the related topic more analytically.
- **Editorial application:** Avoid jargon and multi-part questions in Part 1; build specific, natural paths from cue cards into a discussion of wider issues.

### BC-02 — British Council: IELTS Speaking Fluency & Coherence Tips
- **Organisation:** British Council / Take IELTS
- **URL:** https://takeielts.britishcouncil.org/prepare/ielts-academic/speaking/tips-fluency-coherence
- **Accessed:** 2026-10-26
- **Read:** Extending Part 1 responses with details, using cue-card points to organise a long turn, and developing Part 3 through reasons, effects and comparisons.
- **Editorial application:** Construct prompts that allow real examples and explanations instead of one-word responses; ensure that Part 3 questions test distinct reasoning functions, not variations of the same question.

### BC-03 — British Council: IELTS Academic Speaking Preparation
- **Organisation:** British Council / Take IELTS
- **URL:** https://takeielts.britishcouncil.org/prepare/ielts-academic/speaking
- **Accessed:** 2026-10-26
- **Read:** Part 1 familiarity, Part 2 task cards, Part 3 more abstract questions, and advice to add a reason/example, compare situations and discuss different perspectives; opinions are not scored as right/wrong.
- **Editorial application:** Do not require privileged travel, money or specialist facts; make prompts open to multiple valid viewpoints; do not supply memorisable answers.

### IDP-01 — IDP IELTS: *IELTS Focus: Speaking* (Student Book, PDF)
- **Organisation:** IDP IELTS Middle East; the PDF identifies © IDP Education 2020 (this is an imprint in the document, not an independently verified web-page update date).
- **URL:** https://info.ielts.idp.com/rs/561-EIU-022/images/IELTS%20Focus%20-%20Speaking%20-%20Student%20-%20Updated.pdf
- **Accessed:** 2026-10-26
- **Read:** PDF pages **7 and 36** (PDF page indices **6 and 35**): overview of three speaking parts and the progression from personal content in Parts 1–2 to broader, more abstract discussion in Part 3. Also considered the document's notes on developing answers rather than just stating an opinion. Page 2 explicitly restricts reproduction without permission.
- **Editorial application:** Each Part 3 question is a generalisable question about people, society, changes or choices; no prewritten personal follow-up like “You mentioned...” appears without a candidate response.
- **Copyright:** This PDF clearly forbids reproduction of all or part without IDP's permission; it has **not** been copied or included in the ZIP.

## How the principles map to the JSON fields

| Field | Purpose | Reference logic |
|---|---|---|
| `part1` | Exactly four short, familiar questions per demo test | IELTS-01, BC-01, BC-03 |
| `cue_card.prompt` / `cue_card.bullets` | One broad long-turn task with four complementary prompts | IELTS-01, BC-02, IDP-01 |
| `part3_topics` | Four distinct editorial directions linked to the cue-card theme | IELTS-01, IDP-01 |
| `part3_question_pool` | Four corresponding, general, analytical questions for the agent to select/adapt | BC-02, BC-03, IDP-01 |
| `reference_ids` | Traceable sources of **design principles**, not provenance of question text | This reference register |

The existing ID values were retained from the user's `speaking.json`; that file was inspected only to preserve interface compatibility, **not** as a model of question quality. The accompanying requirements document determined the UC03 stateful conversational flow and the need for human verification.

## Intended use and review gate

- This set is a **draft** (`source: llm_generated`, `verification.status: pending_human_review`), not a benchmark, speaking transcript, or confirmed official item bank.
- The team should have at least one member read each question aloud and check accessibility, clarity, grammar, depth and duplication before determining whether to approve it.
- The application should support response-aware Part 3 follow-ups using `candidate_points` and `asked_questions`; four pool items are not a substitute for that behaviour.
- The application must not silently treat a draft item as `self_written` or `llm_generated_verified` merely because it parses successfully.
- The licensing metadata for new question text must be checked separately from the copyright and terms of the official sources; source-site material is never licensed onward by this project.
