# SHIKSHASETU — ADDITIONAL DATASETS TO OPTIMIZE THE RAG SYSTEM
Companion to the original 13-dataset collection. Follows the same classification rules:
A = Structured (MongoDB) · B = RAG Knowledge · C = Hybrid · D = External Live Source
official_status ∈ {VERIFIED_OFFICIAL, DERIVED_FROM_OFFICIAL, INTERNAL_PROTOTYPE, UNKNOWN}

These datasets are missing from the original plan not because they're "extra content," but
because **your current 13 only cover what goes IN the RAG — nothing covers whether the RAG
is actually retrieving well, whether it's safe, or whether it understands Indian statistical
terminology/language variance.** That's the gap this document closes.

---

## DATASET 14 — RETRIEVAL EVALUATION SET (GOLDEN Q&A)
**Class: A (Structured) — used offline for evaluation, not served at runtime**

Without this, you cannot measure whether your reranker/hybrid search is actually working.
This is the single highest-leverage dataset for a hackathon demo because judges will ask
"how do you know your RAG doesn't hallucinate?" — this is your answer.

Fields:
```
eval_id
query
query_type          (factual / navigational / comparative / ambiguous / out_of_scope)
expected_chunk_ids  (list)
expected_answer_summary
acceptable_sources
difficulty
created_by
created_at
last_run_at
last_run_score
notes
```
Build this by hand-writing 40–100 realistic queries per persona (Statistical Officer, Survey
Officer, etc.) and manually identifying which chunks *should* be retrieved. This becomes your
regression suite — run it every time you change chunking, embeddings, or reranking.

Priority: **P0** — you cannot claim "grounded" without this.

---

## DATASET 15 — SYNONYM / ACRONYM / ALIAS DICTIONARY
**Class: C (Hybrid) — used for query rewriting + BM25/keyword expansion**

Official statistics is acronym-dense (PLFS, CPI, IIP, ASI, NAS, SDG, MoSPI, NSSTA, TPAC, CBC).
Users will type "PLFS" or "employment survey" or "labour force survey" interchangeably. Pure
vector search handles some of this; keyword/BM25 legs of hybrid search won't, unless you
expand the query first.

Fields:
```
term_id
canonical_term
aliases            (list)
acronym_of
domain
language
definition
source
official_status
last_verified_at
```
Priority: **P0** — directly improves recall on the keyword half of your hybrid retriever, which
is otherwise your weakest link on abbreviation-heavy queries.

---

## DATASET 16 — GLOSSARY OF OFFICIAL STATISTICAL CONCEPTS
**Class: B (RAG) — small, high-value grounding corpus**

Distinct from Dataset 9 (documents) — this is atomic, one-concept-per-chunk definitional
content (e.g. "Worker Population Ratio", "Usual Status", "Base Year", "Chain Linking").
Concept lookups are extremely common in a competency-learning tool and deserve their own
tightly-scoped, high-precision index rather than being buried inside long PDFs.

Fields:
```
concept_id
term
definition
domain
source_document
source_url
source_page
publication_date
retrieval_date
official_status
```
Priority: **P0** — cheap to build (small chunks, high precision), disproportionately improves
answer quality for "what is X" queries, which will be common in a training/competency tool.

---

## DATASET 17 — MULTILINGUAL TERMINOLOGY MAPPING (HINDI–ENGLISH)
**Class: C (Hybrid)**

Given the domain (Government of India, MoSPI, NSSTA), Hindi query variants and Hindi-language
official documents are realistic. Even if the MVP is English-only, mapping this now avoids a
retrieval blind spot and is a strong differentiator in a SIH evaluation.

Fields:
```
mapping_id
term_en
term_hi
transliteration
domain
source
official_status
last_verified_at
```
Priority: **P1** for Round 1 demo, **P0** if any judge/user testing will happen in Hindi.

---

## DATASET 18 — CHUNK QUALITY / RETRIEVAL FEEDBACK LOG
**Class: A (Structured), append-only**

Captures real usage so retrieval improves over time — this is what turns your RAG from a
static demo into a system that gets better. Also doubles as your hallucination safety net.

Fields:
```
feedback_id
query
retrieved_chunk_ids
final_answer
user_rating          (thumbs up/down or 1-5)
flagged_hallucination (bool)
flagged_reason
session_id
timestamp
resolved
resolution_notes
```
Priority: **P1** for Round 1, **P0** for any post-Round-1/production narrative — judges like
seeing a feedback loop even if it's not fully wired up yet.

---

## DATASET 19 — ENTITY / ORGANIZATION REGISTRY
**Class: C (Hybrid) — supports entity linking and disambiguation**

Prevents the LLM from conflating similarly-named bodies (NSSTA vs NSSO vs NSC vs MoSPI vs
CBC vs Karmayogi Bharat) and gives the router a clean lookup when a query names an org.

Fields:
```
entity_id
entity_name
entity_type       (ministry / institute / scheme / platform / committee)
full_name
parent_organization
description
official_url
official_status
last_verified_at
```
Priority: **P1**.

---

## DATASET 20 — RERANKER TRAINING/CALIBRATION PAIRS
**Class: A (Structured) — offline ML asset, not served at runtime**

If you're using a cross-encoder reranker (even an off-the-shelf one), you need labeled
(query, chunk, relevance) triples to sanity-check or fine-tune it. This can be bootstrapped
directly from Dataset 14 plus manual negative sampling — no separate collection effort needed.

Fields:
```
pair_id
query
chunk_id
relevance_label     (0-3 graded relevance)
source              (manual / derived_from_eval_set / user_feedback)
created_at
```
Priority: **P2** unless you have time to fine-tune a reranker; otherwise use it just for
calibration/threshold-setting on the off-the-shelf reranker's scores.

---

## DATASET 21 — OUT-OF-SCOPE / REFUSAL TEST SET
**Class: A (Structured) — evaluation asset**

A RAG system's failure mode isn't just wrong answers — it's confidently answering questions
it has no grounding for (e.g. real-time data it should route to MoSPI MCP, or genuinely
unknown info). This set tests that the Intent Router correctly declines or redirects instead
of fabricating.

Fields:
```
test_id
query
expected_behavior     (route_to_mcp / decline / ask_clarification / route_to_rag)
expected_response_pattern
last_run_at
last_run_result
```
Priority: **P0** — directly demonstrates the "grounded, not hallucinating" claim that's core
to your architecture's value proposition, and is cheap to build (20–30 adversarial queries).

---

## UPDATED DATA_ARCHITECTURE_MATRIX ADDITIONS

| dataset | storage | RAG_indexed | structured_query | dynamic | priority |
|---|---|---|---|---|---|
| Retrieval eval set (14) | MongoDB | No | Yes (test runner) | Yes (grows) | P0 |
| Synonym/acronym dictionary (15) | MongoDB | Used in query rewrite | Yes | Occasional | P0 |
| Statistical glossary (16) | MongoDB + vector | Yes | No | Occasional | P0 |
| Hindi–English mapping (17) | MongoDB | Used in query rewrite | Yes | Occasional | P1 |
| Retrieval feedback log (18) | MongoDB | No | Yes | Yes (continuous) | P1 |
| Entity registry (19) | MongoDB | Optional metadata | Yes | Occasional | P1 |
| Reranker calibration pairs (20) | MongoDB | No | Offline only | Occasional | P2 |
| Out-of-scope test set (21) | MongoDB | No | Yes (test runner) | Occasional | P0 |

---

## WHY THESE MATTER MORE THAN MORE CONTENT

Your original plan is heavily weighted toward **acquiring more source content** (courses,
programmes, documents). That's necessary but not sufficient. The datasets above address the
three things that actually separate a working RAG demo from a fragile one:

1. **You can't improve what you don't measure** — Datasets 14 and 21 give you a repeatable
   way to prove retrieval quality and grounding to judges, and to catch regressions when you
   change chunking or embeddings the night before a demo.
2. **Retrieval fails silently on vocabulary mismatch** — Datasets 15, 16, 17 close the gap
   between how officials write ("Worker Population Ratio," "PLFS") and how users ask
   ("employment rate," "job survey").
3. **A feedback loop is a stronger P0-adjacent story than more records** — Dataset 18 is small
   to build and lets you honestly say "the system improves with use" rather than "we scraped
   more PDFs."

None of these require additional web scraping of iGOT/NSSTA/MoSPI sources — they're built
from your own team's domain knowledge plus small amounts of manual curation, which keeps them
squarely INTERNAL_PROTOTYPE or DERIVED_FROM_OFFICIAL and avoids any fabrication risk under
your existing integrity rules.
