DGCA

English Encoder v2

Specification v1.0

Deterministic English Linguistic Front-End for Natural-Text Acquisition

Project

DGCA — Dynamic Graph Cognitive Architecture

Component

English Encoder v2

Status

Architecture & Test Specification — Candidate for Freeze

Scope

English text only

Law 3

Unchanged / out of path during Encoder validation

Core target: Raw English → structurally faithful DGCA SensoryEpisodes

0. Executive Statement

Real-Data Trial 01 demonstrated that the frozen Phase-II DGCA could process a large real corpus at high throughput while acquiring almost no durable natural-language knowledge. The final graph after 217,503 Simple English Wikipedia training articles contained only 22 nodes and 44 edges, with zero assemblies and near-zero ingestion yield. Subsequent code review identified the current English encoder as a primary failure candidate: it relies on narrow regular-expression patterns, handwritten open-class verb lists, unsafe suffix stripping, and flat positional fallbacks that do not reliably preserve the semantic-syntactic structure of natural English.

English Encoder v2 is therefore defined as a pure, deterministic, graph-free linguistic compiler whose job is to preserve the explicit linguistic structure of English input and emit the existing DGCA SensoryEpisode contract without adding cognitive primitives, learned state, world knowledge, semantic scoring, or graph-dependent behavior.

RawEnglish → CorrectStructuralEpisodes

This specification deliberately supports English only. Audio, vision, multilingual support, long-range discourse, and advanced coreference are deferred until the English pathway succeeds on real natural text.

1. Problem Statement

The current encoder is insufficient for natural text because it can:

corrupt lexical identity through naive suffix stripping;

lose subject-predicate-object structure;

flatten unrelated words into simultaneous co-occurrence;

mishandle explicit negation;

discard relational prepositions that carry semantic structure;

fail to preserve proper-name and compound spans;

depend on a finite handwritten open-class verb vocabulary;

fall back to positional heuristics such as first-word/last-word heads;

silently discard content when no narrow rule matches;

mix analysis and graph publication too closely for isolated diagnosis.

Examples observed during diagnostic review include Mars becoming mar, The Earth orbits the Sun losing subject-predicate-object structure, No bird is a mammal failing to preserve contradiction, and multi-clause natural sentences collapsing into flat associations.

The corrective objective is not a full general-purpose NLP system. It is the minimum sufficient English structural front-end required for DGCA to receive lawful, deterministic, low-error natural-language experience.

2. Constitutional Position

EncoderState ≠ CognitiveState

EncoderAnalysis ≠ Learning

EncoderRule ≠ DGCA Law

ClauseFrame ≠ CognitivePrimitive

The encoder MUST NOT own:

persistent learned state

evidence confidence

learned semantic weights

world-knowledge facts

graph authority

memory consolidation

pruning authority

long-term discourse memory

planning authority

All cognitive ownership remains with the frozen DGCA architecture.

3. Scope

3.1 In Scope

1. adjective + noun

2. copular nominal definition

3. copular property

4. active subject-verb-object

5. passive voice with explicit agent

6. possession / have constructions

7. prepositional relations

8. explicit negation

9. safe coordination with and/or/but

10. quantities

11. simple proper-name and compound spans

12. simple subject relative clauses with that/which/who

13. simple predicate + prepositional complement

14. simple predicate + object + prepositional complement

15. safe partial extraction

3.2 Explicitly Deferred

non-English languages and multilingual morphology

audio and vision

deep coreference and discourse pronoun resolution

arbitrarily nested relative clauses

ellipsis and idioms

metaphor interpretation

indirect speech

sophisticated modality

external trained semantic role models

pretrained entity linking and knowledge bases

Transformer parsing and LLM preprocessing

4. Top-Level Contract

RawEnglish → Normalization → Tokenization → Morphology → SpanProtection → ClauseSegmentation → SyntacticRoleParsing → RelationBindingResolution → EpisodeEmission

The public analysis path SHALL be conceptually equivalent to:

analysis = english_encoder.analyze(text, source_ref)

The analysis result contains normalized text, tokens, protected spans, clauses, clause frames, emitted SensoryEpisodes, diagnostics, and rule provenance. It MUST NOT mutate a DGCA graph.

Graph publication is a separate adapter boundary:

publish_to_graph(graph, analysis.episodes)

Analyze ≠ Learn

SameSentence + SameSource + SameConfig ⇒ SameEncoderOutput

5. Encoder-Local Intermediate Representation

The encoder MAY use local transient programming structures such as ClauseFrame. A minimal conceptual form is:

ClauseFrame

  subject

  predicate

  object

  subject_modifiers

  object_modifiers

  prepositional_relations

  quantity_bindings

  negated

  voice

  inherited_subject_ref

  dependent_clauses

  provenance

ClauseFrame is transient, deterministic, graph-free, non-cognitive, non-learning, and forbidden from becoming a canonical DGCA cognitive primitive.

6. Layer Architecture

6.1 Layer 1 — Normalization

Input: raw Unicode English text. Output: normalized text with source offsets preserved or reconstructable. Allowed operations are Unicode normalization, whitespace normalization, canonical quote/apostrophe handling, punctuation normalization, and sentence-boundary preservation. Semantic interpretation, world-knowledge lookup, premature identity-destroying lowercasing, relation extraction, and graph access are forbidden.

6.2 Layer 2 — Tokenization

The tokenizer produces deterministic tokens with surface form, normalized surface, start/end offsets, token kind, and clitic information. It must preserve contractions, possessives, decimal numbers, common initialisms where unambiguous, and source offsets.

6.3 Layer 3 — Morphology

Morphology derives conservative lemmas and grammatical features. Uncertain forms preserve original identity. Suffix-only plural stripping and finite handwritten open-class verb vocabularies are forbidden. A small closed-class grammar lexicon is permitted for English mechanics.

6.4 Layer 4 — Span Protection

Span protection prevents high-confidence lexical units from being destroyed before syntax analysis. Proper-name and compound spans are detected through deterministic linguistic/orthographic rules, not external NER or world-knowledge systems.

6.5 Layer 5 — Clause Segmentation

Clause segmentation operates on typed normalized tokens and protected spans. It distinguishes coordinated predicates from coordinated noun phrases and may carry inherited subject references as encoder-local bookkeeping.

6.6 Layer 6 — Syntactic Role Parsing

The parser is template-bounded and extracts supported subjects, predicates, objects, noun-phrase heads, modifiers, prepositional complements, passive roles, explicit negation, coordination boundaries, and simple relative antecedents. Unsupported structures do not trigger positional semantic fallbacks.

6.7 Layer 7 — Relation & Binding Resolution

Relational prepositions are preserved as explicit linguistic relation symbols when they carry structure. The encoder does not invent semantic labels or world facts. Deterministic local instance binding is allowed only when needed to avoid identity collapse, such as quantity binding or repeated same-head roles.

6.8 Layer 8 — Episode Emitter

The emitter performs only EncoderLocalIR → ExistingSensoryEpisode. It is graph-free and performs no parsing, learning, morphology, confidence scoring, or world-knowledge augmentation.

Representative morphology safety examples:

birds    -> bird

animals  -> animal

chased   -> chase

freezes  -> freeze

Mars     -> mars

physics  -> physics

species  -> species

news     -> news

UncertainLemma ⇒ PreserveOriginalIdentity

Representative protected spans:

New York City          -> new_york_city

United States          -> united_states

Alexander Graham Bell  -> alexander_graham_bell

7. Existing SensoryEpisode Mapping

7.1 Attribute / Co-Property

simultaneous

  apple

  red

7.2 Event Sequence

sequence

  cat

  chase

  mouse

7.3 Prepositional Relation

sequence

  apple

  rel:on

  table

7.4 Passive Normalization

sequence

  cat

  chase

  mouse

7.5 Explicit Contradiction

Mars is not a star MUST NOT emit a positive mars + star association and later negate it. It SHALL use the existing contradiction mechanism directly where the current contract supports it.

8. Fail-Closed Parsing Semantics

IfStructureIsNotSafe ⇒ DoNotInventRelation

COMPLETE: The supported structure is deterministically parsed.

SAFE_PARTIAL: A subset is certain and may be emitted without inventing unsupported relations.

UNSUPPORTED: No safe structural episode is emitted.

These dispositions are diagnostics only and MUST NOT become DGCA cognitive lifecycle states. Semantic confidence scores and new numeric semantic thresholds are forbidden.

9. No-Silent-Loss Contract

EveryContentToken → Emitted OR ConsumedWithExplicitReason OR UnsupportedWithExplicitReason

The       -> CONSUMED_DETERMINER

red       -> EMITTED_MODIFIER(apple)

apple     -> EMITTED_HEAD

is        -> CONSUMED_COPULA

on        -> EMITTED_RELATION_OPERATOR

wooden    -> EMITTED_MODIFIER(table)

table     -> EMITTED_HEAD

10. Rule Provenance

Every structural decision MUST expose deterministic rule provenance. Illustrative rule identifiers include:

ENC2-R-COPULA-NOMINAL

ENC2-R-COPULA-ADJECTIVE

ENC2-R-ACTIVE-SVO

ENC2-R-PASSIVE-BY

ENC2-R-COORD-PRED

ENC2-R-COORD-NP

ENC2-R-RELATIVE-SUBJECT

ENC2-R-PP-RELATION

ENC2-R-QUANTITY-BIND

ENC2-R-PROPER-SPAN

11. Canonical Acceptance Sentences

ENC2-C01 — Copular Nominal

Input: A falcon is a bird.

simultaneous

  falcon

  bird

No is node.

ENC2-C02 — Copular Nominal + Of Complement

Input: A falcon is a bird of prey.

simultaneous

  falcon

  bird

 

sequence

  bird

  rel:of

  prey

ENC2-C03 — Active SVO + Modifier

Input: Falcons hunt small animals.

simultaneous

  animal

  small

 

sequence

  falcon

  hunt

  animal

ENC2-C04 — Possession

Input: Birds have feathers.

sequence

  bird

  have

  feather

ENC2-C05 — Coordinated Predicates

Input: Birds have feathers and lay eggs.

sequence

  bird

  have

  feather

 

sequence

  bird

  lay

  egg

No flat clique and no and cognitive node.

ENC2-C06 — Natural SVO

Input: The Earth orbits the Sun.

sequence

  earth

  orbit

  sun

ENC2-C07 — Proper Identity + Quantity

Input: Mars has two moons.

simultaneous

  inst:moon:<deterministic-id>

  moon

  quantity:2

 

sequence

  mars

  have

  inst:moon:<deterministic-id>

Mars MUST NOT become mar; quantity binds to moon.

ENC2-C08 — Explicit Negation

Input: Mars is not a star.

existing contradiction mechanism:

  text:mars

  text:star

No positive mars + star learning episode; not is not a cognitive node.

ENC2-C09 — Modifiers + Spatial Relation

Input: The red apple is on the wooden table.

simultaneous

  apple

  red

 

simultaneous

  table

  wooden

 

sequence

  apple

  rel:on

  table

ENC2-C10 — Passive Voice

Input: The mouse was chased by the black cat.

simultaneous

  cat

  black

 

sequence

  cat

  chase

  mouse

ENC2-C11 — Same-Head Multi-Role Binding

Input: Photosynthesis converts light energy into chemical energy.

simultaneous

  inst:energy:A

  energy

  light

 

simultaneous

  inst:energy:B

  energy

  chemical

 

sequence

  photosynthesis

  convert

  inst:energy:A

  rel:into

  inst:energy:B

Actual IDs must be deterministic, not literal A/B.

ENC2-C12 — Proper-Name Relation

Input: New York City is in the United States.

sequence

  new_york_city

  rel:in

  united_states

No destructive decomposition into unrelated lexical concepts.

ENC2-C13 — Proper-Name Subject + Past Verb

Input: Alexander Graham Bell invented the telephone.

sequence

  alexander_graham_bell

  invent

  telephone

ENC2-C14 — Event + Numeric Condition

Input: Water freezes at zero degrees Celsius.

simultaneous

  inst:degree:<deterministic-id>

  degree

  celsius

  quantity:0

 

sequence

  water

  freeze

  rel:at

  inst:degree:<deterministic-id>

The encoder MUST NOT invent an unstated concept such as temperature.

ENC2-C15 — Relative Clause

Input: A lion is a large cat that lives in Africa.

simultaneous

  cat

  large

 

simultaneous

  lion

  cat

 

sequence

  cat

  live

  rel:in

  africa

Relative antecedent is grammatical cat, not an inferred lion shortcut.

12. Canonical Invariants

EN2-INV-01 — English Only: v2.0 supports English text only.

EN2-INV-02 — No Learned Parser: No trainable parser is introduced.

EN2-INV-03 — No LLM / Transformer: No LLM, Transformer, or pretrained semantic parser is used.

EN2-INV-04 — Analyze Is Pure: Analysis is graph-free and does not learn.

EN2-INV-05 — Existing SensoryEpisode Contract Preserved: No new cognitive episode primitive is introduced.

EN2-INV-06 — No Positional Semantic Fallback: No first-word/last-word semantic fallback.

EN2-INV-07 — No Finite Open-Class Verb Vocabulary: Open-class verbs are not restricted to a handwritten finite list.

EN2-INV-08 — Conservative Morphology: Uncertain forms preserve original identity.

EN2-INV-09 — Proper-Name Identity Protected: Protected spans are not destructively re-tokenized or stemmed.

EN2-INV-10 — Relational Prepositions Preserved: Semantic prepositions are retained as relation operators.

EN2-INV-11 — Clause-Local Structure Required: Relation emission is based on supported clause structure.

EN2-INV-12 — No Whole-Sentence Flat Co-occurrence: Natural sentences may not collapse into false simultaneous cliques.

EN2-INV-13 — Passive Agent Normalization: Supported passive clauses preserve agent/patient order.

EN2-INV-14 — Coordination Safety: Coordination may not create false cross-clause associations.

EN2-INV-15 — Quantity Binding: Quantities bind deterministically to the intended noun phrase.

EN2-INV-16 — Same-Head Multi-Role Binding: Repeated same-head role instances are separated where required.

EN2-INV-17 — No Invented World Semantics: No facts or semantic labels are added beyond input/authorized contract.

EN2-INV-18 — No Silent Content-Token Loss: Every content token is emitted, explicitly consumed, or explicitly unsupported.

EN2-INV-19 — Unsupported Syntax Fails Closed: Unsupported structure does not produce guessed semantic relations.

EN2-INV-20 — Deterministic Output: Same input/source/config yields the same output.

EN2-INV-21 — Rule Provenance Available: Every parse/emission decision is traceable to deterministic rules.

EN2-INV-22 — No Cognitive Persistence in Encoder: Encoder-local state is transient/non-cognitive.

EN2-INV-23 — No Graph-Dependent Parsing: Graph contents cannot alter the parse.

EN2-INV-24 — Law 3 Untouched During Validation: Law 3 is excluded from E2A-E2H and must not be modified.

EN2-INV-01..24 = 24/24

13. Negative Contract

suffix-only plural stripping

handwritten finite open-class verb list

last-word-is-head fallback

first-word-is-head copula fallback

flat whole-sentence co-occurrence

dropping all prepositions as stopwords

external world knowledge

LLM preprocessing

Transformer parser

pretrained semantic parser

persistent learned encoder state

graph mutation during analysis

graph-dependent parsing

semantic confidence threshold

best-parse score / beam search as semantic authority

global mutable instance counter

silent token deletion

14. Implementation Module Boundary

dgca/

  encoding/

    english/

      __init__.py

      types.py

      normalize.py

      tokenize.py

      morphology.py

      spans.py

      clauses.py

      noun_phrases.py

      predicates.py

      relations.py

      emitter.py

      diagnostics.py

      encoder.py

The existing top-level dgca/encoder.py MAY remain as a compatibility facade. Audio and vision remain unchanged. The goal is modular responsibility, not file-count growth; adjacent modules may be combined if boundaries remain testable.

15. Validation Stages

E2A — Normalization & Tokenization

Verify source offsets, contractions, possessives, punctuation, decimal numbers, initialisms, deterministic tokenization, and absence of lexical corruption.

E2B — Morphology & Span Protection

Verify plural/singular handling, common irregulars, conservative fallback, proper-name integrity, compound span protection, and no Mars→mar class failures.

E2C — Clause & Noun-Phrase Parsing

Verify noun-phrase heads, modifiers, coordinations, clause boundaries, inherited subjects, safe partial parses, and no flat fallback.

E2D — Predicate & Relation Resolution

Verify active SVO, possession, copula, prepositional relations, passive normalization, explicit negation, relative clauses, quantity binding, and same-head role binding.

E2E — Episode Emitter

Verify ClauseFrame→SensoryEpisode determinism and graph isolation.

E2F — Canonical Acceptance Set

Run ENC2-C01..C15; required result 15/15 PASS.

E2G — 100 Natural English Sentences

Evaluate bounded natural English not written only to fit implementation. Record structural accuracy and false-association diagnostics.

E2H — 100–500 Simple Wikipedia Sentences

Evaluate real Simple Wikipedia sentences with GraphLearning=OFF and Law3 out of path. Preserve raw analysis/episode archives.

E2A → E2B → E2C → E2D → E2E → E2F → E2G → E2H

16. Evaluation Metrics

CompleteParseRate

SafePartialRate

UnsupportedRate

HeadAccuracy

SubjectAccuracy

PredicateAccuracy

ObjectAccuracy

ModifierBindingAccuracy

NegationAccuracy

ProperSpanIntegrity

QuantityBindingAccuracy

RelativeAntecedentAccuracy

FalseAssociationRate

SilentLossRate

DeterministicReplayConsistency

FalseLearningRisk > Coverage

A safe unsupported result is preferable to a false semantic relation in a continual-learning graph.

17. Release Gates

EN2-G01 — Constitutional Boundary: No new cognitive primitive, learned parser state, law, world-knowledge dependency, or graph authority.

EN2-G02 — Determinism: Same input/source/config returns identical tokenization, parse, bindings, episodes, and diagnostics.

EN2-G03 — Morphological Safety: No known lexical-identity corruption in the frozen morphology suite.

EN2-G04 — No-Guess Safety: Unsupported syntax fails closed without positional semantic fallback.

EN2-G05 — Token Accounting: No silent content-token loss.

EN2-G06 — Canonical Acceptance: ENC2-C01..C15 = 15/15 PASS.

EN2-G07 — Invariant Registry: EN2-INV-01..24 = 24/24 PASS.

EN2-G08 — Natural-English Evaluation: E2G completed with full diagnostics and no unresolved high-severity false-association mechanism.

EN2-G09 — Wikipedia Evaluation: E2H completed with graph learning disabled and raw parse/episode archive preserved.

EN2-G10 — Graph Isolation: Analysis proved graph-free; Law 3 unchanged.

EN2-G01..G10 = 10/10 PASS

18. Post-Encoder Forensic Handoff

If English Encoder v2 passes all release gates, the next experiment is a controlled graph-learning forensic run rather than an immediate large Wikipedia retraining. It measures cumulative node/edge creation, reinforcement, edge lifetime, Law 3 pruning, orphan-node deletion, deletion cause, inter-exposure intervals, and survival under repeated independent exposure.

CorrectEpisodes → GraphPersistence

This isolates Law 3 for independent review without contaminating the Encoder diagnosis.

19. Non-Goals

human-level language understanding

open-domain semantic disambiguation

discourse comprehension

multilingual competence

long-term memory

language generation quality

world-knowledge acquisition

Law 3 correctness

curriculum necessity

The specification proves only that the English sensory front-end can translate bounded natural English into structurally faithful, deterministic DGCA episodes at low false-association risk.

20. Final Design Summary

EnglishEncoderV2 = DeterministicStructuralCompiler

EnglishOnly = TRUE

LearnedParser = FALSE

LLM/Transformer = FALSE

GraphDependentParsing = FALSE

NewCognitivePrimitive = 0

NewNormativeLaw = 0

PersistentEncoderCognition = 0

ExistingSensoryEpisodeContract = PRESERVED

Law3DuringEncoderValidation = UNCHANGED / OUT OF PATH

21. Approval / Freeze Record

Current document state: Candidate for Freeze.

Implementation state: Not started under this specification.

Law 3: Unchanged.

Multilingual work: Deferred.

Audio/Vision work: Unchanged and out of scope.

Upon explicit project approval, this document becomes the authoritative English Encoder v2 implementation and validation specification.