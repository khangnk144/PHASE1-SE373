# Speaking Bank — Editorial Review for UC03

**Draft date:** 2026-10-26
**Scope:** 10 original AI-assisted Speaking practice sets, one array in `speaking.draft.json`
**Verification status:** Pending human review; no item approved by a human and no benchmark labels created.

## 1. Content-by-content assessment (AI self-review, not human approval)

| Item ID | Cue-card task type | Strength of this draft | What a human should verify |
|---|---|---|---|
| `sp-riverside` | Place | Quiet spot can be indoors or outdoors; no city/park ownership assumption. | Check whether “green areas” feels sufficiently related if the learner chooses an indoor location. |
| `sp-transport` | Unexpected experience | Journey can be on foot or by any means; four directions cover emotion, planning, consequences and policy. | Check that “unreliable transport in smaller communities” remains accessible to learners with limited travel experience. |
| `sp-learning` | Person | One identifiable person and a teachable experience; social, educational and cross-generational angles. | Check the line between “teaching methods” and “learning from people versus online” is clear. |
| `sp-food` | Shared experience | Ordinary meal is affordable; topics connect food, culture, skill and waste without a restaurant requirement. | Check that the fourth question does not demand specialised food-waste knowledge. |
| `sp-technology` | Object | Allows paper, simple non-digital tools or devices; four distinct consumer/design questions. | Check whether topic label needs to be “Everyday Tools” in UI to avoid implying a digital product. |
| `sp-community` | Observed/experienced event | Does not force candidate to have volunteered; trust, online coordination and community support. | Check if the act was witnessed rather than received, and that user can still build a sustained answer. |
| `sp-books` | Story/media | Accepts oral story, book, film or video; does not assume paid media or habitual book reading. | Check that students understand “stayed in your mind” as “memorable” without extra coaching. |
| `sp-exercise` | Activity | Any accessible movement activity qualifies; barriers, group settings, schools and public space are distinct. | Check that learners with disabilities can select an appropriate physical activity without exclusion. |
| `sp-environment` | Habit change | A failed or partial attempt is permitted; no expensive environmental purchases expected. | Check that the source bank has not inadvertently biased learner answers toward “recycling” only. |
| `sp-travel` | Decision | The free afternoon can be spent near home with minimal cost; social, geographical and policy extension. | Check the cue card still gives enough event detail for a 1–2 minute monologue. |

## 2. Part 2 → Part 3 thematic progression (human spot-check)

| ID | Part 2 anchor | Four distinct Part 3 directions |
|---|---|---|
| `sp-riverside` | Describe a place you can visit when you want some peace and quiet. | Availability of quiet public spaces in different communities / Different needs of children and older adults in shared spaces / Choosing between green areas and other public facilities / The future use of public spaces as daily routines change |
| `sp-transport` | Describe a journey you took that did not go as you expected. | Sources of stress and enjoyment during everyday travel / Differences between planning short trips and long journeys / Consequences of unreliable transport in smaller communities / Local priorities for making everyday travel more dependable |
| `sp-learning` | Describe someone who showed you how to do something useful. | Qualities of people who teach practical skills effectively / Learning from people compared with online instructions / The place of everyday skills in formal education / Learning opportunities between younger and older generations |
| `sp-food` | Describe a meal you shared with other people that you remember clearly. | Social importance of eating together / Changes in eating habits caused by convenient food options / Teaching basic food preparation to children / Reducing food waste at home and in restaurants |
| `sp-technology` | Describe an everyday object that makes a task easier for you. | Simple product design compared with feature-heavy products / The influence of price on access to useful equipment / Reasons people replace rather than repair working objects / Manufacturers’ responsibility for repairable products |
| `sp-community` | Describe a small act of kindness you witnessed or experienced. | Reasons people help or hesitate to help strangers / How small acts of kindness affect trust in communities / The role of online groups in organising local support / Responsibilities of local organisations during times of need |
| `sp-books` | Describe a story that stayed in your mind after you heard, read or watched it. | Reasons stories are sometimes easier to remember than facts / Storytelling as a way to preserve community traditions / Changes in how children encounter stories across generations / The balance between local and international stories in schools |
| `sp-exercise` | Describe a physical activity you tried for the first time. | Barriers that stop people from being physically active / Different benefits of exercising alone and with others / Schools’ role in encouraging enjoyable physical activity / Access to low-cost exercise opportunities in public spaces |
| `sp-environment` | Describe a small habit you changed, or tried to change, to avoid wasting something. | Why wasteful habits persist despite awareness of consequences / The relative impact of households and businesses on waste / How schools can build respect for everyday resources / Local infrastructure that makes reuse and recycling easier |
| `sp-travel` | Describe a decision you made about where to go during a free afternoon. | Factors that influence local leisure destinations / Differences in leisure choices between towns and cities / Effects of sudden popularity on quiet local attractions / Public funding for free or low-cost recreation spaces |

## 3. Automated validation performed

- Re-read `speaking.draft.json` as UTF-8 JSON after writing; confirmed the parsed value equals the constructed objects.
- Verified **exactly 10 array objects**, all 10 IDs are unique and preserve the order/values of the attached `speaking.json`.
- Verified exact required top-level fields; `cue_card` has only `prompt` and `bullets`.
- Per item: **4** Part 1 questions, **1** cue-card prompt with **4** bullets, **4** Part 3 directions and **4** Part 3 reference questions.
- Verified fixed metadata (`skill`, `question_type`, `target_band`, `source`, `license`, `author`, `created_at`) and `reference_ids` from the research register.
- Verified `verification.status = pending_human_review`, `reviewer = null` and `reviewed_at = null` in all 10 cases.
- Checked there are no exact case-/space-insensitive duplicate strings among all question texts, cues, bullets and labels.
- Checked that all Part 1 and Part 3 strings terminate with a question mark, cue cards start with “Describe”, and none contain `...`, `…` or “You mentioned”.
- Simple near-duplicate *screening* (difflib, threshold 0.78) flagged **0** pairs of questions to inspect; this is a surface-level heuristic, not a semantic review.

### Near-duplicate heuristic findings

None above the specified text-similarity threshold. This **does not** prove there are no paraphrases or conceptual overlaps.

## 4. Editorial evaluation by the drafting assistant (not independently verified)

| Criterion | Self-review result | Limits |
|---|---|---|
| English grammar/naturalness | All questions were read and manually edited for everyday spoken English. | No external human or IELTS examiner has signed off. |
| Part 1 accessibility | Two familiar micro-themes per set, with simple single-focus questions. | A minority of questions are yes/no openings; agent should encourage natural extension, not supply answers. |
| Cue-card breadth | Types include place, unexpected event, person, shared meal, object, kindness event, story, physical activity, habit change and decision. | Human should try 1–2 minute mock responses from differing backgrounds. |
| Part 3 linkage | Each set broadens its Part 2 theme into four distinct reasons, comparisons, effects or policy angles. | Actual personalised probing must still be dynamically generated from the candidate response. |
| Inclusion | No implied motorcycle, overseas trip, high income or city residence. | A human should run a separate disability and regional-accessibility review. |
| Copyright | New questions were composed without copying external prompts. | Independent originality search/licence/legal assessment was not performed. |

## 5. Human approval checklist (team-owned)

- [ ] Allocate named reviewer(s) and date(s); review every item and record any change in a separate approval log.
- [ ] Read all 40 Part 1 and 40 Part 3 questions aloud; simplify any awkward or multi-focus wording.
- [ ] Have at least two people with different backgrounds try each cue card for a 1–2 minute response without special facts or purchases.
- [ ] Verify topic diversity and that cue-card guidance has four complementary points, not repeated prompts.
- [ ] Confirm Part 3 moves from personal narrative to a general question and that all four directions differ in purpose.
- [ ] Run a human semantic-duplicate review across the full 10-set bank, not just exact-text/code checks.
- [ ] Review for implicit financial, transport, gender, physical ability, geographical or family assumptions.
- [ ] Review and document authorship/licence for the newly generated questions; do not reuse or redistribute IELTS.org, British Council or IDP questions or pages.
- [ ] Keep unapproved items out of the **production** question bank. Do not promote `llm_generated` to `self_written` or `llm_generated_verified` without an explicit, documented team process.
- [ ] Test the agent with a short answer, an off-topic answer, an empty answer and an injection attempt; ensure `asked_questions` prevents repetition.
- [ ] Confirm Part 3 produces at least two meaningful response-aware follow-ups using `candidate_points`, not merely four static pool items.
- [ ] For text-only sessions mark Pronunciation as `not_assessed`, do not invent pronunciation evidence or scores.
- [ ] After actual approval, update verification fields through a human-controlled workflow and preserve an audit trail before import.

## 6. Integration notes for group 38

The assignment document specifies **4–6** Part 1 questions and **4–6** Part 3 discussion questions for UC03; the draft here deliberately contains **four** in each relevant field to match the current demo constraints. The agent still must run a Part 2 preparation stage, retain part/state/elapsed time, and ask personalised Part 3 follow-up questions based on the learner’s answers. This bank is not a Speaking benchmark, and it includes no model answers or band labels.

Suggested safe gating before import: reject any item whose `verification.status` is not an approved status defined by your team; do not infer approval from `license` or `source`. Treat external-source `reference_ids` as an editorial audit trail, not licence grants.

**Review outcome:** Suitable for structured **human review and demo prototyping**; **not** certified as accepted content for the official project bank.
