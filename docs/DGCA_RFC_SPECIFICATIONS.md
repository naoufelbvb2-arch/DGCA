# DGCA Master Architectural Specifications & RFC Compendium
### *Dynamic Graph Cognitive Architecture (RFC-01 through RFC-11)*

**Author & System Architect:** Naoufel & DGCA Core Contributors  
**Status:** Approved & Implemented in Production  
**License:** MIT  
**Target Engine:** 100% Deterministic Multimodal Cognitive Graph Engine (Zero External Dependencies)

---

## 📑 Table of Contents

1. [Executive Summary & Core Mathematical Principles](#1-executive-summary--core-mathematical-principles)
2. [The 13 Governing Cognitive Laws](#2-the-13-governing-cognitive-laws)
3. [RFC-01: Numbers, Quantities & Relational Arithmetic](#3-rfc-01-numbers-quantities--relational-arithmetic)
4. [RFC-02: Structural Causality & Dynamic Path Analysis](#4-rfc-02-structural-causality--dynamic-path-analysis)
5. [RFC-03: Deep Resonant Reasoning & Transitive Composition](#5-rfc-03-deep-resonant-reasoning--transitive-composition)
6. [RFC-04: Master Symbolic Multimodal Encoder (Text & AST)](#6-rfc-04-master-symbolic-multimodal-encoder-text--ast)
7. [RFC-05: Graph-to-Sequence Linearization & Action Loop](#7-rfc-05-graph-to-sequence-linearization--action-loop)
8. [RFC-06: Vision Modality & Multimodal Spatial Grounding](#8-rfc-06-vision-modality--multimodal-spatial-grounding)
9. [RFC-07: Analogical Reasoning & Cross-Domain Knowledge Transfer](#9-rfc-07-analogical-reasoning--cross-domain-knowledge-transfer)
10. [RFC-08: Biomimetic Auditory Pipeline & Lean CAR-FAC Grounding](#10-rfc-08-biomimetic-auditory-pipeline--lean-car-fac-grounding)
11. [RFC-09: Interactive Multimodal Agent REPL Runtime](#11-rfc-09-interactive-multimodal-agent-repl-runtime)
12. [RFC-11: Curated Knowledge Training & Graph Persistence](#12-rfc-11-curated-knowledge-training--graph-persistence)
13. [Verification & Deterministic Signature Guarantee](#13-verification--deterministic-signature-guarantee)

---

## 1. Executive Summary & Core Mathematical Principles

DGCA (Dynamic Graph Cognitive Architecture) is a biologically inspired, fully deterministic alternative to opaque backpropagation-trained deep neural networks and stochastic Large Language Models.

### Core Postulates:
1. **Relational Substrate**: Knowledge is not stored in static, opaque floating-point matrix weights. Knowledge resides in explicit, typed, and weighted topological relations between symbols.
2. **Emergent Inference**: Reasoning is an active, directed wave of spreading activation ($E(h)$) traversing associative and causal pathways.
3. **Biological Life-Cycle & Apoptosis**: Memory undergoes Hebbian reinforcement upon repeated co-occurrence, exponential decay during idle periods, structural locking upon deep multi-context validation, and cellular pruning (garbage collection) for transient sensory instances.
4. **Tri-Modal Sensory Convergence**: Textual language, visual scenes, and acoustic waveforms map directly into unified concept hubs without machine translation models or statistical alignment dictionaries.

---

## 2. The 13 Governing Cognitive Laws

The cognitive engine executes 13 fundamental mathematical laws on every simulation tick $t$:

$$\begin{aligned}
\text{Law 1 (Emergence):} \quad & W_0 = M_0 \cdot \theta_{\text{create}} \cdot \delta_{\text{gen}} \\
\text{Law 2 (Hebbian Reinforcement):} \quad & \Delta W = \eta \cdot A_i(t) \cdot A_j(t) \cdot (1 - W) \cdot P_{ij} \\
\text{Law 3 (Exponential Decay & GC):} \quad & W(t+1) = \max(W_{\text{floor}}, W(t) \cdot (1 - \lambda)) \\
\text{Law 4 (Contradiction & Rivalry):} \quad & \forall j \in X(i): \quad \text{Inhibition}(j) = \beta \cdot A_i(t) \\
\text{Law 5 (Structural Solidification):} \quad & \text{Lock}(e) \iff W \ge \theta_{\text{solid}} \land n \ge n_{\min} \land (|C| \ge \kappa \lor g \neq \emptyset) \\
\text{Law 6 (Source Tagging):} \quad & \text{Origin}(e) = O_i \to O_j \\
\text{Law 7 (Spreading Activation):} \quad & A_j(t+1) = \sigma\left( \sum_i A_i(t) \cdot W_{ij} \cdot e_{\text{decay}} - \beta \sum_{k \in X(j)} A_k \right) \\
\text{Law 8 (Salience & Protection):} \quad & S(t) = \max(M_k) \cdot e^{-\lambda_s \cdot \Delta t}, \quad W_{\text{floor}} = \theta_{\text{protect}} \cdot S \\
\text{Law 9 (Context Gating):} \quad & \text{Conductance}(e) = W_{ij} \cdot \mathbf{1}\{g = \emptyset \lor g = \text{context}\} \\
\text{Law 10 (Concept Generalization):} \quad & \text{Merge}(u, v) \to \text{Concept}(c) \iff \text{Jaccard}(\text{Adj}(u), \text{Adj}(v)) \ge \theta_{\text{concept}} \\
\text{Law 11 (Positional Lag):} \quad & \text{Lag}_{ij} = (1 - \alpha)\text{Lag}_{ij} + \alpha(pos_j - pos_i) \\
\text{Law 12 (Drive & Valence):} \quad & V_i = \text{Valence}(i), \quad \Delta \text{Drive} = f(\text{Outcome}) \\
\text{Law 13 (Predictive Anticipation):} \quad & \text{Score}(ev | \text{prefix}) = \frac{\sum_k W(ev, h_k)\mathbf{1}\{\text{role}_k\} + W(ev, h_{\text{next}})}{|\text{prefix}| + 1}
\end{aligned}$$

---

## 3. RFC-01: Numbers, Quantities & Relational Arithmetic

### 1. Architectural Scope
Provides an intrinsic, non-symbolic, grounded quantitative backbone directly in the graph topology (`quantity:0` through `quantity:9`) enabling exact ordinal and quantitative comparisons in $O(1)$ without calling external calculators.

### 2. Topological Foundation
* **Intrinsic Nodes**: `quantity:0` .. `quantity:9` with `is_intrinsic=True` (exempt from pruning).
* **Successor & Predecessor Links**:
  $$quantity:n \xrightarrow[\text{succ}]{W=1.0} quantity:n+1, \quad quantity:n+1 \xrightarrow[\text{pred}]{W=1.0} quantity:n$$
* **Topological Proximity**:
  $$W_{\text{sim}}(n, m) = \exp(-0.35 \cdot |n - m|)$$

### 3. Comparison Algorithm (`compare_quantities`)
1. If $n = m \implies 0$.
2. Traverse direct `succ` edges: if $m$ reachable from $n \implies +1$ ($n > m$).
3. Traverse direct `pred` edges: if $m$ reachable from $n \implies -1$ ($n < m$).

---

## 4. RFC-02: Structural Causality & Dynamic Path Analysis

### 1. Architectural Scope
Distinguishes bidirectional symmetric associations (`kind="assoc"`) from true directed, asymmetric causal relations (`kind="causes"`, `kind="role:*"`).

### 2. Mathematical Definition of Causal Strength
The causal strength $C(u \to v)$ integrates forward edge weight, repetition count, multi-context validation, and temporal lag:

$$C(u \to v) = W_{uv} \cdot \left(1 - e^{-\kappa \cdot n_{uv}}\right) \cdot \left(1 + \gamma \cdot \frac{\min(|C_{uv}|, 5)}{5}\right) \cdot \mathbf{1}\{ \text{Lag}_{uv} \ge 0 \lor \text{kind} = \text{"causes"} \}$$

### 3. Multi-Cause Credit Assignment
When an effect $E$ is preceded by multiple potential causes $\{C_1, C_2, \dots, C_k\}$, the engine assigns credit proportionally:
$$\text{Credit}(C_i) = \frac{C(C_i \to E)}{\sum_{j=1}^k C(C_j \to E)}$$

---

## 5. RFC-03: Deep Resonant Reasoning & Transitive Composition

### 1. Architectural Scope
Solves the classical graph search explosion and the 5-hop search barrier through energy decay with concept hub recharging and target conductance boosting.

### 2. Algorithmic Formulation (`deep_infer`)
1. **Exponential Energy Decay**:
   $$E(h+1) = E(h) \cdot (1 - \gamma_{\text{decay}}) \cdot W_{\text{eff}}, \quad \gamma_{\text{decay}} = 0.12$$
2. **Concept Recharging Boost**:
   When an energy wave reaches a consolidated concept node ($c \in \text{concepts} \lor \text{nid} \in \{\text{hub:*}, \text{cat:*}\}$) with $E_{\text{in}} \ge 0.25$:
   $$E_{\text{out}} = \min(1.0, E_{\text{in}} + 0.45), \quad \text{recharges} \le 3$$
3. **Target Conductance Field**:
   $$W_{\text{effective}}(i \to \text{target}) = \min(1.0, W \cdot 1.40)$$
4. **Simulation Mode (`mode="simulation"`)**:
   Guarantees 100% read-only purity without mutating any graph nodes, edges, or timestamps.

### 3. Transitive Relation Composition (`compose_relations`)
Automatically derives higher-order genealogical and mathematical structures:
* $(\text{parent}, \text{parent}) \implies \text{grandparent}$
* $(\text{part\_of}, \text{part\_of}) \implies \text{part\_of}$
* $(\text{succ}, \text{succ}) \implies \text{greater}$

---

## 6. RFC-04: Master Symbolic Multimodal Encoder (Text & AST)

### 1. Architectural Scope
Unifies natural language text and Python code AST parsing into standardized `SensoryEpisode` micro-episodes.

### 2. Episodic Contract Specifications
* **Head-First Rule**: The first element `signals[0]` must be the anchor identifier (`ev:*` or `inst:*`).
* **Sensory Budget Ceiling**: Maximum 5 signals per micro-episode to prevent combinatorial explosion.
* **Role Slots**:
  * For events: `ev:verb -> role0:subj, role1:obj, role2:target`
  * For Python AST: `ev:func -> role0:kw.def, role1:param:x, role2:op.*, role3:param:y`

---

## 7. RFC-05: Graph-to-Sequence Linearization & Action Loop

### 1. Architectural Scope
Linearizes multidimensional graph walks and resonant activation states into coherent text, executable Python code, or robotic actions.

### 2. Dynamic Competitive Queue & Inhibition of Return (IOR)
Prevents repetitive cycles during generation by dynamically suppressing visited nodes:
$$\text{NextWinner} = \arg\max_{v \notin \text{Suppressed}} \left( E(v) \cdot W_{\text{curr} \to v} \right)$$
$$\text{Suppressed} \leftarrow \text{Suppressed} \cup \{\text{NextWinner}\}$$

### 3. Surface Realization Templates
* **Event Nodes (`ev:*`)**: Extracted by sequential role edge order (`role0`, `role1`, `role2`).
* **Copular Statements**: `[Entity] is [Attribute]`
* **Procedural Code**: `out = func(arg1, arg2)`
* **Action Payloads**: `{"action": action_name, "target": target_name, "args": [...]}`

---

## 8. RFC-06: Vision Modality & Multimodal Spatial Grounding

### 1. Architectural Scope
Deconstructs visual scenes into a **Ventral Pathway** (identity, color, shape, size) and a **Dorsal Pathway** (spatial topology, containment, contact trees).

### 2. Visual Primitives
* **HSV Color Quantization**: 8 spectral sectors (Red, Orange, Yellow, Green, Cyan, Blue, Purple, Magenta) + Grayscale (White, Gray, Black).
* **Geometric Shape Classification**:
  * Circularity $\ge 0.82 \implies \text{vis:shp:circle}$
  * $N_{\text{vertices}} = 3 \implies \text{vis:shp:triangle}$
  * Convexity $\ge 0.90 \land 0.85 \le \text{Aspect Ratio} \le 1.15 \implies \text{vis:shp:square}$
  * Convexity $\ge 0.90 \implies \text{vis:shp:rectangle}$
* **Spatial Contact Tree ($O(N)$)**:
  * $\text{inside}(A, B) \iff BBox_A \subseteq BBox_B$
  * $\text{on\_top}(A, B) \iff y_{\max}(A) \approx y_{\min}(B) \land |\text{center}_x(A) - \text{center}_x(B)| < \epsilon$
  * $\text{left\_of} / \text{right\_of} / \text{above} / \text{below}$

---

## 9. RFC-07: Analogical Reasoning & Cross-Domain Knowledge Transfer

### 1. Architectural Scope
Implements deep structure-mapping for proportional analogy ($A : B :: C : D$) based on relational topology rather than superficial surface similarity.

### 2. Structural Depth Index (SDI)
Measures the ratio of deep causal and structural alignments relative to total matched paths:

$$\text{SDI} = \frac{\sum_{r \in \text{matched}} \omega(r) \cdot W_{\text{eff}}(r)}{\sum_{r \in \text{matched}} 4.0 \cdot W_{\text{eff}}(r)}$$

**Hierarchical Relational Weights:**
* $\omega_{\text{causal}} = 4.0$: Causal, functional, transformative, and symmetry relations (`causes`, `transforms_to`, `mirror`, `symmetry`, `opposite_of`).
* $\omega_{\text{ordinal}} = 2.0$: Hierarchical and quantitative relations (`succ`, `pred`, `is_a`, `part_of`).
* $\omega_{\text{spatial}} = 0.25$: Superficial associative or spatial relations (`assoc`, `sim`, `left_of`).

### 3. Pre-Projection Contradiction Check (Law 4)
Before projecting an inference $B \xrightarrow{R} X$ onto candidate target $D$, the engine checks whether $X \in \text{Rivals}(D)$. If contradiction is detected, the inference is blocked (`status = BLOCKED_BY_CONTRADICTION`).

---

## 10. RFC-08: Biomimetic Auditory Pipeline & Lean CAR-FAC Grounding

### 1. Architectural Scope
Models the biophysical fluid mechanics of the human cochlea using a 16-channel Greenwood filterbank with nonlinear compression and formant extraction.

### 2. Biophysical Pipeline Stages
1. **Greenwood Characteristic Frequency Distribution ($100\text{ Hz} - 4000\text{ Hz}$)**:
   $$f_c(k) = 165.4 \cdot \left(10^{1.40 \cdot \frac{15-k}{15}} - 0.88\right), \quad k \in [0, 15]$$
2. **2-Pole Digital IIR Resonators**: Models asymmetric resonant basilar membrane deflection.
3. **Inner Hair Cell (IHC) Rectification**: Cubic half-wave velocity-to-neural transduction:
   $$y(t) = \max(0, x(t))^3$$
4. **Two-Stage Multi-Rate Dynamic Compression (AGC)**: Fast-acting biological gain control.
5. **Feature Vector Extraction**:
   * $\text{fmt1\_band} \in [8, 15]$ (Formant 1, $300\text{ Hz} - 1000\text{ Hz}$)
   * $\text{fmt2\_band} \in [2, 7]$ (Formant 2, $1000\text{ Hz} - 3000\text{ Hz}$)
   * $\text{is\_voiced} \in \{\text{True}, \text{False}\}$ (Autocorrelation pitch detection at $80\text{ Hz} - 400\text{ Hz}$)
   * $\text{has\_onset} \in \{\text{True}, \text{False}\}$ (Sharp burst attack detection)

---

## 11. RFC-09: Interactive Multimodal Agent REPL Runtime

### 1. Architectural Scope
Provides the high-level `CognitiveAgent` orchestrator and interactive terminal REPL CLI for conversational reasoning, life-cycle stepping, and graph inspection.

### 2. Interface Command Reference
* `/learn <text>`: Ingest natural language proposition.
* `/ask <query>`: Resonant inquiry and linearized response generation.
* `/code <code>`: Python snippet AST ingestion.
* `/analogy <a> <b> <c>`: Solve proportional analogy ($a : b :: c : ?$).
* `/compare <n1> <n2>`: Native quantitative comparison.
* `/inspect <nid>`: Deep node inspection (activations, in/out edges, rivalry sets).
* `/tick [n]`: Step simulation clock for biological decay and cellular pruning.
* `/save [path]` & `/load [path]`: JSON brain state persistence.
* `/stats`: Live memory metrics (nodes, edges, concepts, hypotheses).
* `/demo`: Automated multi-step demonstration.

---

## 12. RFC-11: Curated Knowledge Training & Graph Persistence

### 1. Curated Training Curriculum (176 Structured Propositions)
1. **Ontological & Taxonomic Knowledge**: Biological taxonomy, physical materials, celestial astronomy, mechanical tools.
2. **Physical & Causal Dynamics**: Thermodynamics (evaporation, freezing, condensation), electrical circuits, ecological cycles, cardiovascular biology.
3. **Cross-Lingual Arabic-English Grounding**: Paired semantic nouns and perceptual sensory attributes.
4. **Procedural Code AST Knowledge**: Standard mathematical and utility Python functions.

### 2. Periodic Consolidation & Sleep Ticks
The curriculum executes in batches of 20 propositions with structural weight $0.80$, followed by `step_time(ticks=2)` consolidation cycles:
* Decays transient noise.
* Solidifies multi-context connections into locked status (Law 5).
* Merges overlapping concepts (Law 10).
* Persists consolidated brain to `data/brain_curated.json` (435 nodes, 2673 edges).

---

## 13. Verification & Deterministic Signature Guarantee

Every build and modification of DGCA is validated against a bit-exact behavioral signature generated from the reference graph state:

```python
from dgca.signature import behavioral_signature, build_reference_graph

reference_graph = build_reference_graph()
signature = behavioral_signature(reference_graph)
assert signature == "c4b2549940a49789", f"Determinism violated: {signature}"
```

* **Baseline Signature**: `c4b2549940a49789`
* **Test Suite Status**: **273/273 Unit Tests Passing (100% Green)**
* **Linter & Code Hygiene**: **100% Clean (`ruff check .`)**
* **External Dependencies**: **0 (Standard Library Only)**
