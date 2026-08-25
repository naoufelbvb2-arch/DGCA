# DGCA Phase 2.5 — Real-Data Trial 01 Specification v1.0

## Natural-Text Knowledge Acquisition on Simple English Wikipedia

### Frozen-Architecture One-Pass Empirical Baseline

**Project:** DGCA — Dynamic Graph Cognitive Architecture  
**Stage:** Phase 2.5 — Post-Phase-II Empirical Validation  
**Document type:** Experimental specification / empirical protocol  
**Version:** 1.0  
**Status:** **PROTOCOL FROZEN — EXECUTION PENDING**  
**Phase-II status:** **IMPLEMENTED / VERIFIED / CLOSED / FROZEN**  
**Architecture changes authorized by this document:** **0**  
**New normative laws:** **0**  
**Primary outcome:** **Reality, not PASS optimization**

---

# Document map

- **Part I — Sections 0–3:** Scientific purpose, governance, and dataset identity.
- **Part II — Sections 4–8:** Deterministic split/order and Article-to-DGCA ingestion semantics.
- **Part III — Sections 9–13:** Pilot, main ladder, evaluation isolation, probe bank, and raw outputs.
- **Part IV — Sections 14–22:** Runtime, graph, learning, retention, reasoning, generation, and held-out evaluation.
- **Part V — Sections 23–31:** Failure taxonomy, stop rules, checkpoint contract, longitudinal curves, and scaling.
- **Part VI — Sections 32–33:** Evidence-driven Phase III interpretation and deferred curriculum Trial 02.
- **Part VII — Sections 34–36:** Frozen experimental invariants, pilot gates, and checkpoint protocol.
- **Part VIII — Sections 37–41:** Deliverables, final questions, interpretation discipline, and frozen status.

## 0. Executive statement

DGCA Phase II established a verified sparse cognitive architecture capable of local learning, structural adaptation, sparse distributed representation, pattern completion and separation, reasoning/prediction, hierarchical language realization, recurrent generation, external-feedback handling, multi-root orchestration, and lawful quiescence. Phase 2.5 does **not** extend that architecture.

Real-Data Trial 01 asks a different question:

\[
\boxed{\text{What can the frozen Phase-II DGCA actually learn from natural real-world text?}}
\]

The trial exposes an unchanged DGCA system to a fixed snapshot of Simple English Wikipedia, measures acquisition, retention, reasoning, generation, sparsity, resource use, and failure modes, and then evaluates the resulting model with pre-registered prompts that are never allowed to alter the training instance.

The experiment is intentionally diagnostic. Poor language, low acquisition yield, graph growth, retrieval failures, reasoning failures, or inability to ingest natural text are all valid scientific outcomes. No architectural mechanism may be added or repaired during the main run merely to improve the result.

\[
\boxed{\text{Failures are measured, not repaired.}}
\]

---

# 1. Scientific purpose

The trial is designed to answer, with real data rather than synthetic fixtures, at least the following questions:

1. Can DGCA acquire useful persistent knowledge from natural text through its existing encoder, evidence, and local-learning paths?
2. How quickly can it ingest natural documents?
3. How much CPU time, RAM, storage, and graph growth does that acquisition require?
4. Does the graph remain sparse as knowledge increases?
5. Does previously learned knowledge survive later exposure without global retraining?
6. Can learned knowledge be retrieved from non-identical cues?
7. Can DGCA combine separately acquired relations in reasoning tasks?
8. Can RFC-14/RFC-15 express acquired knowledge in natural-language responses?
9. Does generation improve as linguistic exposure increases?
10. Which observed failures belong to encoding, evidence formation, representation, retrieval, reasoning, structural scaling, generation, or runtime/resource constraints?
11. Does the evidence firewall remain valid under a natural corpus?
12. What empirical evidence should determine the actual scope of Phase III?

The trial does **not** assume that DGCA succeeds. Its purpose is to replace architectural speculation with measured evidence.

---

# 2. Governance and phase boundary

## 2.1 Phase 2.5 is not Phase III

Phase 2.5 is an empirical validation stage between the closed Phase II architecture and any future Phase III design.

\[
\boxed{\text{Phase 2.5 observes Phase II; it does not reopen Phase II.}}
\]

No RFC-11..RFC-16 law, primitive, ownership boundary, or frozen signature may be changed to make Trial 01 perform better.

## 2.2 No new cognitive authority

Trial infrastructure may add only experimental/runtime support such as:

- dataset download and verification;
- deterministic manifests;
- article/segment operational identifiers;
- telemetry collectors;
- checkpoint serialization wrappers;
- read-only evaluation clones;
- benchmark/evaluation scripts;
- logs and reports.

These additions must remain noncognitive and nonnormative.

Forbidden during Trial 01:

- new learning laws;
- new cognitive primitives;
- new persistent learned fields;
- new semantic thresholds;
- new global controller or planner;
- new source-trust/reputation score;
- new persistent dialogue memory;
- new text-to-fact semantic preprocessor;
- changes to encoder semantics;
- changes to RFC-13, RFC-14, RFC-15, or RFC-16 behavior;
- changes to Edge Law merely to improve real-data performance.

## 2.3 Baseline signatures

The main run must begin only after the following frozen signatures match:

- **Phase-I / Laws 1–13:** `c4b2549940a49789`
- **RFC-11 / Law 14:** `412730689a2befa5`
- **RFC-12:** `f121b698e6d97292`
- **RFC-13 / Law 15:** `8652eb05126afa8c`
- **RFC-14 / Law 16:** `46213188cdb02ee8`
- **RFC-15 / Law 17:** `92c6ba731b372f10`
- **RFC-16:** `cc9363dc6394a7cf`

Any unexplained signature drift before the main run is a blocker.

---

# 3. Dataset contract

## 3.1 Canonical corpus target

Trial 01 uses:

- **Repository:** `wikimedia/wikipedia`
- **Configuration:** `20231101.simple`
- **Language:** Simple English
- **Format:** Parquet
- **Expected fields:** `id`, `url`, `title`, `text`
- **Expected published scale:** approximately 242k rows
- **Published data file size:** approximately 157 MB
- **Published Parquet SHA256 at protocol freeze:** `31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0`

The source is the cleaned Wikimedia Wikipedia dataset distributed through Hugging Face. The published dataset card states that each example corresponds to one cleaned full article and that unwanted MediaWiki sections such as references are stripped during dataset construction.

## 3.2 Execution-time identity

Before any pilot or training exposure, the executor must record:

- resolved repository revision;
- exact downloaded file name(s);
- local file size;
- locally computed SHA256;
- exact row count;
- field schema;
- download timestamp;
- dataset license metadata.

If the downloaded artifact does not match the frozen expected file hash, execution must not silently continue. The mismatch must be reported and either the frozen artifact must be obtained or this specification must be explicitly revised before execution.

## 3.3 Plain-text scope only

Trial 01 uses only natural plain text plus article title/context.

Excluded from the learning stream:

\[
Images=OFF
\]

\[
Audio=OFF
\]

\[
Tables=OFF
\]

\[
InfoboxStructuredKnowledge=OFF
\]

\[
ExternalWebLinks=OFF
\]

\[
LLMAugmentation=OFF
\]

The URL may be retained in provenance/audit logs but is not treated as cognitive content unless the pre-existing encoder already explicitly owns such semantics.

---

# 4. Deterministic split and exposure order

## 4.1 Train / held-out split

The single Wikipedia split is partitioned deterministically into:

\[
90\%\ Train
\]

\[
10\%\ HeldOut
\]

The partition must be based on a stable cryptographic hash of the article ID, not a language/runtime `hash()` function.

Canonical rule:

`h_i = SHA256("RDT01-SPLIT-v1\\0" || ArticleID_i)`

Let \(u_i\) be the unsigned integer represented by the first eight digest bytes.

\[
HeldOut(i) \iff u_i \bmod 10 = 0
\]

All other rows belong to Train.

The complete partition manifest must be frozen before training.

## 4.2 Deterministic training order

Training articles must not follow source-file order. They are assigned a stable order key:

`o_i = SHA256("RDT01-ORDER-v1\\0" || ArticleID_i)`

Train articles are processed in ascending lexicographic order of \(o_i\), with ArticleID only as a serialization tie-break if ever required.

This provides deterministic pseudo-randomized exposure without relying on implementation-specific RNG behavior.

## 4.3 Sentence order is never shuffled

Within an article:

\[
Shuffle(Articles)=YES
\]

but:

\[
Shuffle(SentencesWithinArticle)=NO
\]

Original document order is preserved because context, coreference, temporal relations, definitions, and local causal flow may depend on sequence.

---

# 5. Article-to-DGCA Experience Protocol v1

This section is the central ingestion contract.

## 5.1 One article = one external causal root episode

Each Wikipedia article is treated as one externally caused experience episode:

\[
\boxed{OneWikipediaArticle=OneRootExternalEpisode}
\]

A stable operational root identifier is derived from the frozen dataset identity and article ID:

\[
RootExternalEpisodeID_i = SHA256(DatasetSnapshotID \Vert ArticleID_i)
\]

All title/paragraph/sentence events originating from that article share the same root external episode identity.

Therefore:

\[
ManySegments\neq ManyIndependentEvidenceSources
\]

Repeated statements inside one article do not automatically become independent evidence episodes merely because the representation is repeated.

## 5.2 Article segmentation is operational, not epistemic

The article is not fed as one unbounded event. It is exposed as an ordered stream of bounded segments:

\[
Article
\rightarrow
RootExternalEpisode
\rightarrow
Segment_1,Segment_2,\ldots,Segment_n
\]

Segmentation must prefer natural paragraph and sentence boundaries already present in the text. It may obey pre-existing encoder/runtime size limits, but Trial 01 may not introduce a new semantic chunking threshold.

\[
\boxed{NoNewSemanticChunkThreshold}
\]

## 5.3 Segment identity

Each segment must receive deterministic operational identity:

\[
SegmentEventID_j=
SHA256(RootExternalEpisodeID\Vert SegmentIndex\Vert SegmentTextHash)
\]

A crash/restart that replays the same segment must reproduce the same identity.

\[
Retry\neq NewExperience
\]

## 5.4 Title handling

The article title belongs to the same root episode and may serve as a natural contextual anchor. It must not be counted as independent external evidence.

## 5.5 Existing encoder only

Natural text enters the current DGCA encoder unchanged except for allowed mechanical normalization.

Forbidden learning-path shortcuts:

\[
Text\not\rightarrow EdgeMutation
\]

The lawful route remains:

\[
Text
\rightarrow
AuthorizedExternalIngress
\rightarrow
ExistingEncoder
\rightarrow
CurrentSparseRepresentation
\rightarrow
ExistingEvidenceEligibility/Validation
\rightarrow
ExistingLearningOwner
\rightarrow
LocalMutation
\]

If the current DGCA system cannot transform natural text into useful lawful learning effects, that is a Trial 01 result, not permission to invent a bridge during the main run.

---

# 6. Preprocessing contract

## 6.1 Allowed preprocessing

Only mechanical transformations are permitted, such as:

- Unicode normalization where required by the existing text pipeline;
- line-ending normalization;
- whitespace normalization;
- removal of empty records/segments;
- deterministic paragraph/sentence segmentation;
- preservation of original article order within each article;
- deterministic operational IDs.

## 6.2 Forbidden semantic preprocessing

Trial 01 forbids external semantic assistance:

\[
\boxed{NoLLMFactExtraction}
\]

\[
\boxed{NoLLMSummarization}
\]

\[
\boxed{NoLLMEntityLinking}
\]

\[
\boxed{NoLLMRelationExtraction}
\]

Also forbidden unless already part of the frozen DGCA encoder:

- automatic semantic rewriting;
- simplification beyond the source corpus itself;
- generated knowledge augmentation;
- generated training Q&A;
- external embeddings used to route cognition;
- source-trust scoring.

Trial 01 must test DGCA, not an external semantic solver placed in front of it.

---

# 7. Article context and boundary semantics

## 7.1 Context persists naturally within an article

Trial infrastructure must not artificially reset transient cognition between every sentence.

Conceptually:

\[
S_1\rightarrow R_1
\]

\[
S_2+R_1\rightarrow R_2
\]

subject only to the already frozen DGCA runtime and authority rules.

No new `ArticleMemory` primitive is introduced.

## 7.2 Article boundary must settle

At the end of each article, DGCA must reach its existing lawful settling/quiescence boundary before the next article begins:

\[
ArticleEnd
\rightarrow
ExistingSettling
\rightarrow
Quiescence
\rightarrow
NextArticle
\]

This protects the baseline from artificial adjacency associations between unrelated documents.

Persistent knowledge survives; article-local transient activity must not be artificially carried into the next independent document.

## 7.3 No training-mode cognitive override

Trial 01 must not introduce a global mode that disables or enables cognitive subsystems for convenience.

\[
ExistingAuthorityDecides
\]

Pattern Completion, reasoning, prediction, RFC-14, and RFC-15 run only if their already frozen authorities permit them. A Wikipedia article is not automatically an expressive request, so generation must not occur merely because text was ingested.

---

# 8. Evidence independence and one-pass rule

## 8.1 One-pass baseline

Trial 01 uses exactly one intentional corpus pass:

\[
\boxed{ExposurePasses=1}
\]

This avoids conflating repeated exposure with independent evidence.

## 8.2 Re-reading is not automatically new evidence

A future repetition experiment may distinguish:

\[
ExposureRepetition
\]

from:

\[
EvidenceIndependence
\]

but Trial 01 does not perform that experiment.

## 8.3 Different articles may be different external episodes

Two different Wikipedia articles are different root external episodes. Whether their statements lawfully reinforce the same cognition is determined only by existing evidence/learning laws. Trial 01 does not introduce a universal Wikipedia trust score.

Contradictory claims are not cleaned away merely to improve accuracy; they are allowed to exercise current ambiguity, context, evidence, and refutation semantics.

---

# 9. Pilot stage — harness validation only

Before the main trial, execute a disposable pilot on 100 deterministic Train articles selected by:

`p_i = SHA256("RDT01-PILOT-v1\\0" || ArticleID_i)`

and taking the first 100 eligible Train rows by \(p_i\).

The pilot exists only to validate experimental infrastructure.

Allowed pilot fixes:

- dataset loader bugs;
- logging bugs;
- telemetry bugs;
- serialization bugs;
- deterministic-ID bugs;
- harness crashes that do not require changing DGCA semantics.

Forbidden pilot fixes:

- new cognitive state;
- learning-law changes;
- encoder semantic changes;
- new thresholds intended to improve performance;
- altered RFC behavior.

After the pilot:

\[
\boxed{PilotModel=DISCARDED}
\]

The main training run must start from a clean verified \(M_0\), not from the pilot state.

## 9.1 Pilot entry/exit gates

The pilot must demonstrate:

1. dataset hash/schema verification;
2. deterministic split/order manifests;
3. deterministic article/segment IDs;
4. restart/retry deduplication;
5. article-end quiescence;
6. complete telemetry capture;
7. checkpoint save/restore round-trip;
8. evaluation clone isolation;
9. no held-out leakage;
10. no new cognitive primitive/law;
11. all Phase-II frozen signatures unchanged;
12. pilot state discarded before main run.

If any gate fails, the main run does not start.

---

# 10. Main training ladder

The verified clean model \(M_0\) is exposed cumulatively:

\[
M_0
\rightarrow
M_{1k}
\rightarrow
M_{10k}
\rightarrow
M_{50k}
\rightarrow
M_{100k}
\rightarrow
M_{full}
\]

Checkpoints:

- **`M0`:** 0 cumulative Train articles processed.
- **`M1K`:** 1,000 cumulative Train articles processed.
- **`M10K`:** 10,000 cumulative Train articles processed.
- **`M50K`:** 50,000 cumulative Train articles processed.
- **`M100K`:** 100,000 cumulative Train articles processed.
- **`MFULL`:** all remaining Train partition articles, if no legitimate stop condition occurs.

The model is **not** reset between main-run checkpoints.

Each checkpoint must record a reproducible state digest and be independently restorable.

---

# 11. Evaluation isolation

## 11.1 Never evaluate on the mutable training instance

At every checkpoint:

\[
Checkpoint
\rightarrow
BitExactClone
\rightarrow
ReadOnlyEvaluation
\rightarrow
DiscardClone
\]

The original training instance resumes from its untouched checkpoint state.

Evaluation prompts must not become training episodes and must not alter persistent cognition.

## 11.2 Held-out partition isolation

Held-out articles never enter the training instance. They may be read only by the evaluation harness for pre-registered evaluation construction and scoring.

---

# 12. Pre-registered Evaluation Bank

Before the main run begins, freeze exactly 420 evaluation probes:

- **Bank A — Learned Fact Recall (100):** Can knowledge seen in Train be retrieved?
- **Bank B — Paraphrased Recall (100):** Can the same knowledge be retrieved from a non-identical cue?
- **Bank C — Compositional Reasoning (100):** Can separately learned relations be combined without exact-string memorization?
- **Bank D — Held-Out Behavior (100):** How does the system behave when relevant source knowledge was not trained?
- **Bank E — Free Generation (20):** What does the real model actually say from learned cognition?
- **Total:** 420 frozen probes.

## 12.1 Bank construction integrity

The bank must be frozen before training and stored with:

- probe ID;
- prompt text;
- source article IDs where applicable;
- source segment citations/anchors;
- expected semantic anchors or answer conditions;
- bank category;
- Train/HeldOut provenance;
- grading rule.

External LLMs may not create or validate the ground-truth semantics. If deterministic/mechanical construction is insufficient for a reliable item, that item must be manually curated/reviewed before the main run or excluded and replaced before freeze.

## 12.2 Same probes at every checkpoint

The same 420 frozen probes are run against:

\[
M_0,M_{1k},M_{10k},M_{50k},M_{100k},M_{full}
\]

subject to the experiment reaching each checkpoint.

This produces longitudinal capability curves rather than isolated scores.

---

# 13. Raw response capture

For every natural-language probe, retain the exact model output.

At minimum:

```text
PROBE_ID:
CHECKPOINT:
PROMPT:
RAW_DGCA_RESPONSE:
CLOSURE_REASON:
LATENCY:
RELEVANT_KNOWLEDGE_REFS:
REASONING/GENERATION TRACE REFS:
SUPPORTED_ANCHORS:
UNSUPPORTED_CLAIMS:
```

The report must never replace raw outputs with summaries only.

The 20 Free Generation prompts are especially important and must be presented longitudinally so that human reviewers can compare the model before training and after each checkpoint.

---

# 14. Runtime and resource telemetry

For every checkpoint interval record at least:

- wall-clock acquisition time;
- CPU time;
- current RAM;
- peak RAM;
- storage used by persistent model state;
- checkpoint size;
- articles/second;
- segments/second;
- words/second where deterministically measurable;
- external episodes/second;
- learning transactions/second;
- min/median/p95 processing latency for relevant stages;
- encoding time;
- evidence/validation time;
- local-learning time;
- structural-adaptation time;
- quiescence/settling time.

Fixture/download/checkpoint-copy time must be separated from cognitive processing time.

---

# 15. Graph and structural evolution telemetry

At \(M_0\) and every checkpoint record:

\[
|Nodes|,
|Edges|,
|Assemblies|
\]

plus at minimum:

- live edges;
- pruned/retired edges where represented;
- average degree;
- maximum degree;
- graph density;
- new edges per interval;
- reused edges per interval;
- structural mutation count;
- growth/prune/split/merge counts where applicable;
- evidence-record counts;
- context/profile growth where measurable without global semantic scans.

Graph density is diagnostic:

\[
Density=\frac{|E|}{|V|(|V|-1)}
\]

The experiment does not define a success threshold for density. The observed curve is evidence for Phase III.

---

# 16. Knowledge-storage efficiency telemetry

Experimental diagnostics include:

\[
EdgesPerArticle
\]

\[
NodesPerArticle
\]

\[
AssembliesPer1000Articles
\]

\[
BytesPerStoredEdge
\]

and, where a defensible denominator exists:

\[
BytesPerAcquiredFact
\]

These are telemetry metrics only. They do not influence cognition or learning decisions.

---

# 17. Learning-health telemetry

For every interval record at least:

- segments seen;
- representations created;
- evidence candidates created;
- validated evidence;
- rejected evidence;
- duplicate root episodes/events;
- positive local updates;
- negative/refutation updates;
- no-op learning transactions;
- new edges;
- existing edges updated;
- conflicts;
- ambiguities;
- budget-blocked work;
- segments with no lawful learning effect.

## 17.1 Ingestion Yield

Define diagnostic:

\[
IngestionYield=
\frac{SegmentsProducingAtLeastOneLawfulLearningEffect}
{TotalValidSegments}
\]

This is a measurement, not a semantic threshold or policy score.

## 17.2 Learning Density

Define:

\[
LearningEffectsPer1000Words
\]

using a clearly documented counting rule. Again, this is reporting only.

---

# 18. Acquisition decomposition

For pre-registered Train facts/probes, distinguish three levels:

### Level 1 — Stored

Does the relevant learned relation/state exist in persistent cognition?

### Level 2 — Retrievable

Can the current cue lawfully recover/activate the relevant cognition?

### Level 3 — Expressible

Can RFC-14/RFC-15 produce a response that expresses the required supported semantic anchors?

This permits diagnoses such as:

\[
Stored=YES,\ Retrievable=NO
\Rightarrow RetrievalLimitation
\]

\[
Stored=YES,\ Retrievable=YES,\ Expressible=NO
\Rightarrow GenerativeLimitation
\]

A final answer score alone is insufficient for failure localization.

---

# 19. Retention protocol

At `M1K`, freeze a retention cohort \(K_1\) drawn from knowledge demonstrably acquired during the first 1,000 articles.

Re-evaluate the same cohort after:

\[
M_{10k},M_{50k},M_{100k},M_{full}
\]

Record at least:

- stored retention;
- retrievable retention;
- expressible retention;
- exact state changes for sampled relations;
- whether failure is deletion, weakening, contextual exclusion, retrieval failure, or generation failure.

No arbitrary catastrophic-forgetting threshold is imposed in Trial 01; the measured curve is the result.

---

# 20. Reasoning evaluation

Reasoning probes must not be exact copies of training sentences.

Prefer cases where separate acquired relations support a conclusion such as:

\[
A\rightarrow B
\]

\[
B\rightarrow C
\]

and the probe asks for a lawful implication involving \(A\) and \(C\).

The report must distinguish:

- direct stored answer;
- retrieved multi-relation support;
- actual reasoning traversal/inference;
- unsupported answer/hallucination;
- ambiguity/blockage.

---

# 21. Generation evaluation

DGCA is not evaluated primarily by Transformer language-model metrics such as perplexity.

At minimum record:

1. **Semantic correctness:** Are required supported semantic anchors expressed?
2. **Unsupported claims:** Does the response introduce claims not supported by current lawful cognition?
3. **Coverage:**

\[
Coverage=
\frac{CorrectRequiredAnchorsExpressed}
{RequiredAnchors}
\]

4. **Repetition:** Did recurrent generation repeat covered obligations without lawful repetition authority?
5. **Closure reason:** `COMPLETE`, ambiguity, conflict, no-progress, budget, or other lawful upstream reason.
6. **Response latency.**
7. **Exact raw response for human inspection.**

No automatic fluency score may replace direct inspection of the raw response in Trial 01.

---

# 22. Held-out behavior

Held-out probes are not expected to be answered magically. They measure behavior under missing direct training exposure.

The evaluator should classify outcomes such as:

- correct inference from related learned knowledge;
- explicit ambiguity/insufficient support;
- irrelevant retrieval;
- unsupported generation;
- accidental overlap with Train knowledge;
- genuine transfer/generalization where demonstrable.

Held-out accuracy must not be conflated with Train acquisition accuracy.

---

# 23. Article-level outcome taxonomy

Experimental article-processing status may be reported as:

- **`LEARNED`:** At least one lawful persistent learning effect occurred.
- **`PROCESSED_NO_LEARNING`:** Article processed but no persistent learning effect.
- **`ENCODER_EMPTY`:** No useful current representation produced.
- **`EVIDENCE_REJECTED`:** Candidate evidence appeared but existing validation rejected it.
- **`AMBIGUOUS`:** Lawful unresolved ambiguity remained material.
- **`BUDGET_BLOCKED`:** Existing runtime bounds prevented completion.
- **`INVARIANT_FAILURE`:** Frozen architectural invariant was violated.
- **`RESOURCE_FAILURE`:** Host resource limitation stopped processing.
- **`CRASHED`:** Unexpected software failure.

These are experiment/report labels only. They are not new DGCA lifecycle states.

---

# 24. Failure localization taxonomy

Every material failure should be assigned, where evidence permits, to one or more categories:

- `DATASET/LOADER`
- `SEGMENTATION`
- `ENCODER`
- `EXTERNAL_INGRESS/PROVENANCE`
- `EVIDENCE_FORMATION`
- `EVIDENCE_VALIDATION`
- `LOCAL_LEARNING`
- `STRUCTURAL_GROWTH`
- `REPRESENTATION`
- `PATTERN_COMPLETION/RECALL`
- `REASONING/PREDICTION`
- `RFC14_REALIZATION`
- `RFC15_CONTINUATION`
- `RFC16_ORCHESTRATION`
- `SERIALIZATION/RECOVERY`
- `PERFORMANCE/RESOURCE`
- `UNKNOWN`

The goal is not to force a category when evidence is insufficient; `UNKNOWN` is preferable to a fabricated diagnosis.

---

# 25. Failure log

A machine-readable failure stream must record at least:

```text
article_id
root_external_episode_id
segment_id / segment_index
checkpoint interval
stage
failure category
invariant or authority involved, if any
graph/state size
state digest
exception/traceback where applicable
recoverable flag
resource snapshot
```

The recommended format is JSONL so failures can be aggregated without losing individual evidence.

---

# 26. Stop conditions

The main run may stop before `MFULL` only for legitimate reasons, including:

- invariant violation;
- illegal persistent ownership mutation;
- corrupted or non-restorable state;
- deterministic replay/recovery failure that threatens evidence integrity;
- imminent out-of-memory condition;
- disk exhaustion;
- unrecoverable crash;
- host/runtime failure;
- inability to continue without changing the frozen architecture.

Host safety limits may be configured before execution as operational limits, but they must never be presented as cognitive correctness thresholds.

A poor evaluation score is **not** a reason to stop or modify the architecture.

---

# 27. No mid-run repair rule

Once the main run begins:

\[
\boxed{ArchitectureChangesDuringMainTrial=0}
\]

If the model exhibits a limitation, record it.

If a frozen invariant is violated, stop and report it.

Do not patch and resume the same scientific run as if it were unchanged.

Any semantic model fix requires a new experiment version/run identity beginning again from a clean baseline.

---

# 28. Experimental success vs model success

Two verdicts must remain separate.

## 28.1 Protocol integrity verdict

Did the experiment execute according to this frozen specification with reproducible data, isolation, telemetry, and no architecture modification?

Possible examples:

- `PROTOCOL_PASS`
- `PROTOCOL_PARTIAL_RESOURCE_STOP`
- `PROTOCOL_FAIL`
- `ARCHITECTURAL_BLOCKER`

## 28.2 Model capability outcome

What did the unchanged DGCA actually achieve?

This may be excellent, mediocre, poor, or surprising without changing the protocol verdict.

\[
\boxed{A scientifically successful trial may reveal a weak model.}
\]

That distinction is mandatory.

---

# 29. Checkpoint artifact contract

Each checkpoint must retain:

- serialized model state;
- state digest;
- Node/Edge/Assembly counts;
- persistent cognition inventory summary;
- acquisition telemetry since previous checkpoint;
- cumulative telemetry;
- dataset cursor / next ArticleID;
- partition/order manifest identity;
- source-code revision;
- configuration manifest;
- resource telemetry;
- evaluation-clone results;
- raw responses;
- failure log segment;
- frozen upstream/RFC signatures where feasible.

Checkpoint restoration must be tested before continuing beyond the pilot and at least once during the main ladder.

---

# 30. Main longitudinal plots/tables

The final report should provide at least the following curves/tables:

1. Articles processed vs wall-clock time.
2. Articles processed vs peak/current RAM.
3. Articles processed vs persistent storage.
4. Articles processed vs Nodes.
5. Articles processed vs Edges.
6. Articles processed vs Assemblies.
7. Articles processed vs average/max degree.
8. Articles processed vs graph density.
9. Articles processed vs Ingestion Yield.
10. Articles processed vs learning effects per 1,000 words.
11. Checkpoint vs Fact Recall.
12. Checkpoint vs Paraphrased Recall.
13. Checkpoint vs Reasoning performance.
14. Checkpoint vs Held-Out behavior.
15. Checkpoint vs retention cohort performance.
16. Checkpoint vs free-generation qualitative progression.

No curve should be extrapolated beyond measured ranges without being clearly labeled as a projection.

---

# 31. Scaling projection

After measured checkpoints, the report may estimate cost toward larger corpora such as one million articles, but must distinguish:

\[
Measured
\]

from:

\[
Projected
\]

Projection assumptions must be explicit and must use measured graph/resource curves rather than nominal complexity alone.

---

# 32. Phase-III interpretation rule

Trial 01 exists to determine what Phase III actually needs.

Examples of evidence-driven implications:

- **If text processes but little lawful learning occurs:** ask whether a natural-language-to-evidence bridge is missing or too restrictive.
- **If knowledge is stored but not retrievable:** ask whether retrieval/activation is insufficient at realistic scale.
- **If knowledge is retrievable but not expressible:** ask whether generative realization requires richer learned linguistic structure.
- **If old knowledge degrades during later exposure:** identify which local interference mechanism is responsible.
- **If the graph grows too rapidly:** identify which structural/sparsity assumptions fail under natural corpora.
- **If generation repeats or stalls:** distinguish knowledge-structure, obligation-derivation, and recurrence causes.
- **If a later curriculum trial outperforms random exposure:** test whether DGCA requires developmental knowledge acquisition.

Trial 01 must not implement these solutions. It produces the evidence used to decide whether any of them deserve Phase III architectural work.

---

# 33. Deferred Trial 02 — developmental curriculum hypothesis

The following hypothesis is explicitly deferred:

\[
\boxed{DoesDGCARequireDevelopmentalEducation?}
\]

If Trial 01 establishes a stable real-data baseline, a later Trial 02 may compare identical data budgets under:

\[
RandomExposure
\]

vs.

\[
Simple\rightarrow Complex
\]

vs.

\[
Complex\rightarrow Simple
\]

Trial 01 itself must not mix these conditions.

---

# 34. Experimental integrity invariants

The following invariants are frozen for Real-Data Trial 01.

### RDT01-INV-001 — Frozen architecture
No Phase-II cognitive law, primitive, learned field, semantic threshold, or ownership boundary is changed during the main trial.

### RDT01-INV-002 — Fixed corpus
The main run uses only the verified frozen `wikimedia/wikipedia` `20231101.simple` artifact identified by the accepted local SHA256.

### RDT01-INV-003 — Deterministic split
Train/HeldOut membership is reconstructible from the canonical cryptographic split rule.

### RDT01-INV-004 — Deterministic order
Training order is reconstructible from the canonical article order hash.

### RDT01-INV-005 — Held-out isolation
No HeldOut article becomes a training exposure.

### RDT01-INV-006 — One article, one causal root
All segments of one article share one `RootExternalEpisodeID`.

### RDT01-INV-007 — Segment multiplicity is not evidence independence
Article segmentation cannot multiply independent evidence authority merely by producing multiple events.

### RDT01-INV-008 — Retry deduplication
Replaying the same segment after retry/recovery does not create a new learning episode.

### RDT01-INV-009 — Existing encoder only
No external semantic solver, LLM fact extractor, relation extractor, embedding router, or hidden knowledge preprocessor is inserted before DGCA cognition.

### RDT01-INV-010 — Mechanical preprocessing only
Preprocessing cannot rewrite semantic content.

### RDT01-INV-011 — Original intra-article order
Paragraph/sentence order within an article remains source-ordered.

### RDT01-INV-012 — Article boundary settling
The next independent article cannot begin while prior article-local transient work remains unlawfully active.

### RDT01-INV-013 — No artificial sentence reset
Transient cognition is not forcibly erased between every sentence solely for experiment convenience.

### RDT01-INV-014 — No expressive auto-authority
Wikipedia exposure alone cannot create a universal request to generate a response.

### RDT01-INV-015 — Existing authority only
Recall, completion, reasoning, prediction, generation, and continuation run only under existing frozen authorities.

### RDT01-INV-016 — Existing learning ownership
Any persistent cognitive mutation is attributable to an existing frozen learning owner.

### RDT01-INV-017 — One-pass baseline
The main corpus is intentionally exposed once; retry is not counted as a new pass.

### RDT01-INV-018 — Evaluation isolation
Evaluation occurs on a read-only/disposable clone, never on the mutable training instance.

### RDT01-INV-019 — Evaluation cannot learn
Evaluation probes produce zero persistent mutation to the main training model.

### RDT01-INV-020 — Bank pre-registration
The 420 evaluation probes and grading rules are frozen before the main run.

### RDT01-INV-021 — Raw response preservation
Natural-language responses are retained exactly, not only summarized.

### RDT01-INV-022 — Pilot disposal
The 100-article pilot state is discarded before the main run.

### RDT01-INV-023 — Harness-only pilot fixes
Pilot fixes cannot modify DGCA cognitive semantics.

### RDT01-INV-024 — Clean M0
The main run begins from a clean model whose Phase-II signatures match the frozen registry.

### RDT01-INV-025 — Cumulative checkpoints
`M1K`, `M10K`, `M50K`, `M100K`, and `MFULL` are successive states of the same main run unless a legitimate stop occurs.

### RDT01-INV-026 — Checkpoint restorability
Checkpoint state must be reconstructible and state-digest stable under save/restore.

### RDT01-INV-027 — Separate setup timing
Download, fixture construction, evaluation cloning, and checkpoint copying cannot be misreported as cognitive acquisition time.

### RDT01-INV-028 — Resource truthfulness
All resource and throughput claims use actual measured data; no unexecuted scale may be reported as empirical.

### RDT01-INV-029 — No performance-driven repair
Low performance cannot trigger a semantic architecture patch inside the same main run.

### RDT01-INV-030 — Failure evidence preservation
Every invariant/crash/resource failure retains enough evidence for forensic localization.

### RDT01-INV-031 — Protocol verdict != capability verdict
Experiment integrity and model quality are reported independently.

### RDT01-INV-032 — Phase III is evidence-driven
No Phase-III mechanism is adopted solely because Trial 01 was expected to need it; observed evidence must justify future architecture.

---

# 35. Pilot release gates

The main run is authorized only if all 12 pilot gates pass:

- **P-G01:** Dataset artifact identity and local SHA256 verified.
- **P-G02:** Schema and exact row count recorded.
- **P-G03:** Deterministic Train/HeldOut manifest frozen.
- **P-G04:** Deterministic training-order manifest frozen.
- **P-G05:** 100-article pilot processes with article-root/segment lineage intact.
- **P-G06:** Retry/recovery does not duplicate learning episodes.
- **P-G07:** Article-end settling/quiescence works without cross-article transient leakage.
- **P-G08:** Telemetry and failure logging are complete.
- **P-G09:** Checkpoint save/restore returns identical state digest.
- **P-G10:** Evaluation clone produces zero mutation to main/pilot source state.
- **P-G11:** Phase-II signatures remain unchanged and no new cognitive primitive/law is found.
- **P-G12:** Pilot model is discarded and clean `M0` is established.

\[
\boxed{PilotRelease=12/12\ PASS}
\]

is required before main training.

---

# 36. Main-run checkpoint contract

At every reached checkpoint, the executor must:

1. stop new article ingress at a lawful article/quiescence boundary;
2. finalize interval telemetry;
3. serialize the checkpoint;
4. compute state digest;
5. create a read-only/disposable evaluation clone;
6. run the same frozen 420-probe bank;
7. capture raw responses and traces;
8. destroy the evaluation clone;
9. verify that the training checkpoint digest is unchanged by evaluation;
10. resume from the original training state.

---

# 37. Final deliverables

Execution must produce at least:

1. `DGCA-REAL-DATA-TRIAL-01-REPORT.md`
2. dataset identity/checksum manifest;
3. Train/HeldOut partition manifest;
4. deterministic training-order manifest;
5. frozen 420-probe evaluation bank;
6. pilot report;
7. checkpoint inventory and state digests;
8. telemetry tables/CSV or equivalent machine-readable data;
9. failure JSONL;
10. raw response archive organized by checkpoint/probe;
11. retention cohort evidence;
12. graph/resource evolution data;
13. final protocol-integrity verdict;
14. final model-capability assessment;
15. evidence-backed Phase-III questions — **not implementations**.

---

# 38. Required final report questions

The final report must explicitly answer:

1. How many articles/segments/words were actually processed?
2. How long did acquisition take at each interval?
3. What resources were consumed?
4. How did Nodes, Edges, Assemblies, degree, density, and storage evolve?
5. What proportion of natural text produced lawful learning effects?
6. What proportion of acquired knowledge was stored, retrievable, and expressible?
7. How did retention change as later data accumulated?
8. Could DGCA perform reasoning over separately learned relations?
9. How did the 20 fixed free-generation responses change across checkpoints?
10. How often did unsupported claims appear?
11. What were the dominant failure categories?
12. Did the evidence/learning firewall remain constitutionally intact?
13. Did any Phase-II invariant/signature drift?
14. What empirical bottleneck dominates at realistic scale?
15. What does the evidence imply Phase III should investigate first?
16. Is the system ready for a curriculum comparison Trial 02?

---

# 39. Interpretation discipline

The final report must use literal language.

Forbidden forms of overclaiming include:

- “DGCA scales to millions of articles” when only 100k were measured;
- “O(1)” based on one timing point without operation-counter evidence;
- “no catastrophic forgetting” based only on final accuracy without retention cohorts;
- “understands Wikipedia” merely because articles were processed;
- “reasons” when the answer was directly stored;
- “generates natural language” without preserving and inspecting raw responses;
- “Phase III needs X” without measured evidence connecting the failure to X.

---

# 40. Frozen protocol summary

Real-Data Trial 01 is frozen around the following experimental contract:

\[
\boxed{Dataset=SimpleEnglishWikipedia(20231101.simple)}
\]

\[
\boxed{Train/HeldOut=90/10\ deterministic}
\]

\[
\boxed{Exposure=OnePass\ deterministic\ article\ order}
\]

\[
\boxed{OneArticle=OneRootExternalEpisode}
\]

\[
\boxed{Segments=OrderedExternalEventsUnderSameRoot}
\]

\[
\boxed{ExistingEncoderOnly}
\]

\[
\boxed{NoExternalSemanticPreprocessing}
\]

\[
\boxed{ExistingEvidenceAndLearningLawsOnly}
\]

\[
\boxed{ArticleEnd\rightarrow Quiescence}
\]

\[
\boxed{Pilot=100\ Articles\ And\ Disposable}
\]

\[
\boxed{MainCheckpoints=0\rightarrow1k\rightarrow10k\rightarrow50k\rightarrow100k\rightarrow Full}
\]

\[
\boxed{EvaluationBank=420\ Frozen\ Probes}
\]

\[
\boxed{Evaluation=ReadOnlyDisposableClone}
\]

\[
\boxed{ArchitectureChangesDuringMainTrial=0}
\]

\[
\boxed{PrimaryOutcome=MeasuredReality}
\]

---

# 41. Final status

With this document adopted:

\[
\boxed{\textbf{DGCA Phase 2.5 — Real-Data Trial 01 Protocol v1.0 — FROZEN}}
\]

Execution remains:

\[
\boxed{\textbf{PENDING}}
\]

No conclusion about real-world DGCA capability may be drawn from this specification alone. Capability claims begin only after the pilot and main empirical run produce measured evidence.

The next artifact after this specification is the **Real-Data Trial 01 Master Execution Prompt for Antigravity**, which must implement the experimental harness and execute the pilot/main ladder without modifying the frozen Phase-II cognitive architecture.

---

# Appendix A — Frozen dataset source record

At protocol freeze, the Hugging Face `wikimedia/wikipedia` dataset card describes the corpus as cleaned Wikipedia articles with fields `id`, `url`, `title`, and `text`. The `20231101.simple` viewer reports approximately 242k rows. The published configuration contains a single Parquet file of approximately 157 MB. The published file metadata reports SHA256:

`31bded16768a47c286becd292079122f5d7d4397a17b87d4250a00ccd581e6f0`

Execution must independently verify the locally downloaded bytes before exposure begins.

---

# Appendix B — Experimental accounting

- **New DGCA cognitive primitives:** 0.
- **New persistent learned fields:** 0.
- **New normative laws:** 0.
- **New semantic thresholds:** 0.
- **External LLM semantic preprocessing:** 0.
- **Main corpus passes:** 1.
- **Pilot articles:** 100.
- **Main checkpoints:** 6 including `M0`.
- **Pre-registered evaluation probes:** 420.
- **Experimental integrity invariants:** 32.
- **Pilot release gates:** 12.
- **Phase-II architecture modifications authorized:** 0.

---

**End of DGCA Phase 2.5 — Real-Data Trial 01 Specification v1.0**
