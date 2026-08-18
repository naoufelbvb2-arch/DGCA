# DGCA — RFC-11 v1.0

## Local Assemblies: Emergent Local Structural Organization
### التجمعات المحلية: النشوء والتنظيم البنيوي المحلي

**المشروع:** DGCA — Dynamic Graph Cognitive Architecture  
**المرحلة:** Phase II — Generative Cognitive Architecture  
**الوثيقة:** RFC-11  
**الحالة المعمارية:** **ARCHITECTURALLY CLOSED / FROZEN**  
**Law 14:** **SEMANTICALLY FROZEN — IMPLEMENTATION & CALIBRATION PENDING**  
**التاريخ:** 2026-08-18  
**صيغة الوثيقة:** Markdown / Implementation-Ready Specification

---

## سجل الحالة

| البند | الحالة |
|---|---|
| التعريف المعماري لـLocal Assembly | FROZEN |
| Data Model البنيوي | FROZEN |
| Formation / Activation / Competition | FROZEN |
| Growth / Sanitation / Split / Merge / Retirement | FROZEN |
| التكامل مع Laws 1–13 | FROZEN |
| Law 14 Semantics | FROZEN |
| Complexity & Safety Semantics | FROZEN |
| Acceptance Contract | FROZEN |
| التنفيذ البرمجي | PENDING |
| Empirical Verification | PENDING |
| Numeric Policy Calibration | PENDING |

> **قاعدة الإغلاق:** تجميد المعمارية لا يعني الادعاء بأنها نُفذت أو اختُبرت. التنفيذ، القياس، والمعايرة خطوات لاحقة يجب أن تنتج أدلتها التجريبية بصورة مستقلة.

---

# 0. الملخص التنفيذي

أنهت Phase I من DGCA بناء النواة المعرفية التي تتعلم محلياً من دون Backpropagation، مع مبدأ دستوري مركزي: **المعرفة طويلة الأمد في الروابط (Edges)، لا في العقد (Nodes)**. غير أن الانتقال إلى Phase II — Generative Cognition — يتطلب طبقة تنظيم محلية تسمح للنظام بتمثيل المعرفة المترابطة كوحدات موزعة قابلة لإعادة التنشيط، من دون نسخ المعرفة إلى Supernodes أو إنشاء ذاكرة معرفية ثانية.

يُدخل RFC-11 Primitive بنيوياً جديداً هو **Local Assembly**. الـAssembly ليست Concept Hub، وليست Event، وليست Node مركزية، وليست مخزن belief جماعي. إنها **Subgraph محلية محدودة، Edge-centric، تنشأ من الاستخدام الخارجي الصحيح والمتكرر والمستقل لمجموعة مترابطة من الروابط الدائمة**. تحفظ الـAssembly مراجع العضوية، الهوية، النسخة، وبنية lineage فقط. أما weights، salience، context، causality، prediction، evidence، وغيرها من cognition فتبقى ملكاً للـEdges تحت Laws 1–13.

يفصل RFC-11 بين:

- **Structural Assembly:** بنية طويلة العمر نسبياً، versioned، immutable بعد النشر.
- **Active Assembly:** حالة تشغيلية مؤقتة مرتبطة بنسخة بنيوية محددة، تحمل seeds/participants/frontier/budget/status فقط.

تسمح Assemblies بالتداخل والعضوية المتعددة المحدودة، لكن التداخل لا يعني Merge، والعضوية لا تعني truth أو salience أو resource ownership. يتم اختيار Active Assemblies محلياً عبر **Cue Coverage + Seed-Normalized Conductance + Local Dominance** من دون Softmax عالمي أو winner-take-all مركزي. كما تحافظ Poly-membership على الطاقة عبر deduplication للانتقال الفيزيائي لنفس Edge.

يبرهن RFC-11 كذلك على وجود **ضرورة فريدة لقانون جديد** لا تغطيها Laws 1–13، ومن ثم يضيف:

> **Law 14 — Local Assembly Emergence & Structural Organization**

وهو قانون تنظيم بنيوي فقط، لا قانون تعلم معرفي جديد. القانون 14 لا يغيّر W أوSalience أوCausal Strength أوContext Belief، ولا يسمح للنشاط الداخلي، الاسترجاع، التوقع، Pattern Completion أوالنص المولّد المعاد ترميزه بأن يصبح Structural Evidence.

تتضمن الوثيقة أيضاً نموذجاً رياضياً مضغوطاً، سجل Parameters، حدود تعقيد، مراجعة عدائية، 96 Acceptance Scenarios، 10 Property Families، و18 Benchmark Families، إضافة إلى عقد تنفيذ واضح لـAntigravity.

---

# 1. موضع RFC-11 داخل خارطة DGCA

## 1.1 Phase I — Cognitive Core

الحالة: **CLOSED / FROZEN**.

تشمل النواة الحالية، ضمن وثائقها الأصلية، الرسم البياني الديناميكي، Encoder، القوانين 1–13، التعلم المحلي، الرنين، السياق والكبح، المفاهيم، الأحداث، الأرقام، السببية، الرؤية، الصوت، القياس التشبيهي، وGraph-to-Sequence الحالي.

## 1.2 Phase II — Generative Cognitive Architecture

الهدف العام:

> تحويل المعرفة المتناثرة داخل DGCA إلى حالة فكرية موزعة تستطيع الاستمرار زمنياً والتحول إلى لغة طويلة ومتماسكة من دون Transformer أوBackpropagation.

البنية المتفق عليها لPhase II:

1. **Local Assemblies** — substrate التنظيم المحلي.  
2. **Sparse Distributed Representation** — RFC-12.  
3. **Pattern Completion / Separation** — RFC-13.  
4. **Hierarchical Generative Dynamics** — RFC-14.  
5. **Predictive Recurrence** — RFC-15.  
6. **Unified Generative Loop** — RFC-16.

RFC-11 هو الركيزة البنيوية التي ستبني فوقها RFCs اللاحقة.

---

# 2. المرجعيات المعمارية والحدود

## 2.1 المرجعيات الداخلية

اشتُق RFC-11 بما يحافظ على مبادئ:

- **DGCA 3.0 — Dynamic Graph Cognitive Architecture**: Knowledge in Edges، Nodes transient، graph sparse/local/deterministic.
- **DGCA 3.0 — Formal Lawbook**: Laws 1–13 وسلطاتها الحالية.
- **RFC-03**: Deep Resonant Reasoning، `theta_active`، energy/loop semantics.
- **RFC-04 / RFC-06**: Encoder وMicro-Episode isolation.
- **Architectural Gaps Registry**: انتقال Phase II إلى Generative Fluency وSparse Distributed Representations.
- خبرة ELT/ELT FLASH السابقة في فصل Assembly structural memory عن activation working state، والعضوية غير الحصرية، وconservative split/merge؛ وقد أُعيد اشتقاق هذه المبادئ وفق دستور DGCA ولم تُنسخ كسلطات خارجية.

## 2.2 Non-Goals

RFC-11 لا يحاول حل:

- Pattern Completion نفسه؛ هذا RFC-13.
- Sparse Distributed Representation النهائي؛ هذا RFC-12.
- Syntax أوHierarchical Generation؛ هذا RFC-14.
- Predictive Recurrence؛ هذا RFC-15.
- Truth verification للبيانات الخارجية الرديئة.
- Data curriculum أوtraining interface؛ هذه Phase III.
- تعلم Persistent Node Excitability.

---

# 3. المبادئ الدستورية

## 3.1 طبقات الملكية

\[
\boxed{Node = Transient\ Operational\ Unit}
\]

\[
\boxed{Edge = Persistent\ Cognitive\ Memory\ Owner}
\]

\[
\boxed{Assembly = Persistent\ Structural\ Organization\ Owner}
\]

\[
\boxed{ActiveAssembly = Transient\ Working\ Organization}
\]

وبالتالي:

\[
\boxed{KnowledgeOwner = Edge}
\]

\[
\boxed{StructuralOrganizationOwner = Assembly}
\]

## 3.2 القاعدة الأعلى

\[
\boxed{Structural\ Organization \neq Cognitive\ Duplication}
\]

أي أن إضافة Assembly إلى DGCA لا تنشئ مكاناً ثانياً لتخزين المعنى نفسه.

## 3.3 No New Primitive Without Unique Necessity

أي state أوscore أوthreshold جديد يجب أن يملك ضرورة فريدة لا يمكن اشتقاقها من state موجودة. لذلك يرفض RFC-11 Persistent Assembly Strength/Confidence/Salience/Context Belief، ويرفض global clustering/global optimizer/global popularity.

---

# 4. التعريف الرسمي لـLocal Assembly

## 4.1 Structural Definition

تعرف Local Assembly بالإصدار البنيوي:

\[
\boxed{
\mathcal A^{(v)}=
\langle
AID,
v,
E_A,
O_A,
Pred_A,
Parents_A
\rangle
}
\]

حيث:

- \(AID\): Logical Assembly Identity.
- \(v\): immutable structural version.
- \(E_A\subseteq E\): Member Edge references.
- \(O_A\): origin signature / founding provenance fingerprint.
- \(Pred_A\): predecessor version reference عند التطور الطبيعي.
- \(Parents_A\): lineage parents عند Split/Merge.

العقد ليست membership مستقلة، بل:

\[
\boxed{V_A = Endpoints(E_A)}
\]

## 4.2 ما لا تملكه Assembly

يُحظر في canonical persistent assembly record امتلاك:

- `weight`
- `confidence`
- `salience`
- `context_belief`
- `causal_strength`
- `prediction_memory`
- `evidence`
- `learned_excitability`
- `activation_strength`
- `winner_count`
- `loss_count`
- `global_importance`

وبالتالي:

\[
\boxed{PersistentCognition(A)=\varnothing}
\]

## 4.3 Assembly ليست Hub

\[
\boxed{Assembly \neq ConceptHub}
\]

Hub هي Node تجريدية تحت Law 10، بينما Assembly هي subgraph موزعة. يمكن لHub أن تشارك في Assemblies متعددة، ويمكن لAssembly أن توجد بلا Hub.

## 4.4 Assembly ليست Event أوInstance

\[
Assembly\neq ev:* ,\qquad Assembly\neq inst:*
\]

الكيانات transient/hypothetical لا تصبح أعضاء دائمة في Structural Assembly v1.

---

# 5. Structural Data Model

## 5.1 Canonical Record

العقد التنفيذي الأدنى:

```python
StructuralAssembly(
    assembly_id,
    version,
    member_edges,
    origin_signature,
    predecessor_version,
    parent_assemblies,
)
```

هذه صيغة معمارية وليست إلزاماً بلغة Python أوبنية memory محددة، ما دامت semantics ثابتة.

## 5.2 Versioning

كل تغيير عضوية مادي ينتج نسخة جديدة:

\[
A^{(v)}\rightarrow A^{(v+1)}
\]

النسخة المنشورة immutable. لا silent patch ولا in-place historical rewrite.

## 5.3 Derived Views

تُشتق ولا تُخزن كمعرفة canonical:

- Member Nodes.
- Boundary Nodes/Edges.
- Overlap.
- Containment.
- Assembly-to-Assembly connection views.

يجوز caching لأسباب الأداء بشرط:

\[
\boxed{Delete(Cache)\Rightarrow Reconstructible}
\]

## 5.4 Origin Signature

الغرض منها الهوية التشغيلية، reproducibility ومنع duplicates، لا تخزين اعتقاد سياقي.

هوية الميلاد المفضلة:

\[
\boxed{AssemblyID_{birth}=H("DGCA\_ASM",CanonicalEdgeSet(S))}
\]

والـOrigin Signature يمكن أن تضم founding edge set + context signature + policy/version metadata اللازمة للمراجعة.

Hash equality لا تكفي لإثبات structural identity؛ يجب التحقق من canonical member set عند collision.

---

# 6. Emergent Assembly Formation

## 6.1 المبدأ

\[
\boxed{
Independent\ Validated\ External\ Local\ CoUse
\rightarrow
Structural\ Assembly
}
\]

التكوين ليس نتيجة activation واحدة، ولا similarity، ولا graph clustering.

## 6.2 Edge Adjacency

\[
Adj(e_i,e_j)=1
\iff
Endpoints(e_i)\cap Endpoints(e_j)\neq\varnothing
\]

ومجموعة \(S\) تعتبر Local فقط إذا:

\[
\boxed{Connected(S)=1}
\]

## 6.3 Assembly Eligibility

مبدئياً:

\[
AssemblyEligible(e)=
Canonical(e)\land Live(e)\land\neg Transient(e)\land\neg Hypothetical(e)
\]

لا يضيف RFC-11 threshold جديداً على Weight لتحديد العضوية.

## 6.4 Participation Receipt

لكل Root External Experience صحيحة:

\[
\mathcal P_r(c)=
\{e\in E:\ Participated(e,r,c)=1\land AssemblyEligible(e)\}
\]

`Participated` لا يعني بالضرورة أن Weight تغيرت؛ Locked edges أوintrinsic structure قد تشارك دون \(\Delta W\).

## 6.5 Canonical Formation Extraction

من Participation Graph المحلية تُستخرج فقط Connected Components canonical:

\[
CC(\mathcal P_r)=\{S_1,\dots,S_k\}
\]

ويُحظر:

\[
\boxed{EnumerateConnectedSubsets(S_i)}
\]

وبالتالي لا يوجد subset mining أو \(2^q\) combinatorial search.

## 6.6 Root Episode Deduplication

كل Micro-Episodes أوModalities الناتجة من تجربة خارجية واحدة تشترك في:

`RootExternalEpisodeID`

والتصويت البنيوي يستعمل:

\[
VoteKey=(CandidateSignature,RootExternalEpisodeID)
\]

إذن:

\[
\boxed{OneRootExternalExperience\le OneStructuralVotePerCandidate}
\]

## 6.7 Self-Derived Provenance Firewall

يُحفظ lineage داخلي بحيث:

\[
SelfDerived(x)=1\Rightarrow SelfDerived(descendant(x))=1
\]

ويكون:

\[
ValidStructuralOrigin(r)=ValidOrigin(r)\land\neg SelfDerived(r)
\]

وبالتالي Recall/Simulation/Prediction/Pattern Completion/Generation/internal re-encoding لا تنتج Structural Evidence.

## 6.8 Structural Confirmation Count

\[
\boxed{
N_{str}(X,c)=
\left|
\left\{
r:
ValidStructuralOrigin(r)
\land UniqueRootExternalEpisode(r)
\land ObservationSupports(X,c,r)
\right\}
\right|
}
\]

هذا عداد إثبات بنيوي bounded وليس Weight أوConfidence.

## 6.9 Formation Eligibility

\[
\boxed{
FormEligible(S,c)
}
\]

إذا وفقط إذا:

\[
N_{str}(S,c)\ge N_{ASM}^{confirm}
\]

\[
Connected(S)=1
\]

\[
K_{ASM}^{min}\le |S|\le K_{ASM}^{mem}
\]

\[
\forall e\in S:\ AssemblyEligible(e)
\]

\[
CapacityValid(S)
\]

\[
\neg ExactAssemblyExists(S)
\]

وعند Commit:

\[
A^{(1)}=Create(S)
\]

مع:

\[
\boxed{\Delta CognitiveState_{Formation}=0}
\]

## 6.10 Oversized Components

إذا:

\[
|S|>K_{ASM}^{mem}
\]

فالنتيجة:

\[
\boxed{NO\ DIRECT\ FORMATION}
\]

ولا truncation أوrandom subset أوfirst-N.

---

# 7. Active Assembly & Activation Dynamics

## 7.1 تعريف Active Assembly

\[
\boxed{\alpha=Activation(A^{(v)},C,t)}
\]

هي transient operational state مرتبطة بنسخة Structural Assembly محددة.

## 7.2 Membership ≠ Participation

\[
P_\alpha(t)\subseteq V_A
\]

ولا يلزم:

\[
P_\alpha(t)=V_A
\]

## 7.3 Version Pinning

\[
\boxed{PinnedVersion(\alpha)=A^{(v)}}
\]

طوال حياة Activation. نشر \(A^{(v+1)}\) لا يهاجر بالActivation المفتوحة.

## 7.4 Lawful Origins for Activation

على خلاف Formation، يمكن Activation أن تبدأ من External أوRecall أوReasoning أوSimulation أوGeneration أوPrediction، لكن internal activation لا تنتج Law-14 evidence.

## 7.5 Candidate Lookup

لCue محلية:

\[
E_{cue}=
\{e:\ endpoint(e)\in C_t\land Live(e)\land GateOpen(e,c)\}
\]

ثم:

\[
\boxed{
CandidateAssemblies(C_t)=
\bigcup_{e\in E_{cue}}Membership(e)
}
\]

لا global Assembly scan.

## 7.6 Seeds

بعد Law 4:

\[
\boxed{
S_A^\star(t)=
\{u\in C_t\cap V_A:A_u^\star(t)\ge\theta_{active}\}
}
\]

إذا:

\[
S_A^\star=\varnothing
\]

فلا Activation.

## 7.7 No Duplicate Node Activation

Node activation تبقى Node-owned transient state. لا توجد نسخة per-Assembly من activation الفيزيائية نفسها.

## 7.8 Propagation

RFC-11 لا يعيد تعريف propagation physics؛ Law 4 وLaw 7 تظلان صاحبتَي السلطة. الانتشار الداخلي المقيد بAssembly يستعمل Member Edges المثبتة في النسخة الحالية، ولا يعطي Assembly قوة propagation خاصة.

## 7.9 Lifecycle

الحالات الدنيا:

`INITIATED -> ACTIVE -> CLOSED`

الإغلاق لا يكتب في cognition ولا membership.

---

# 8. Boundary, Overlap & Poly-membership

## 8.1 Boundary

\[
\partial V_A=
\{u\in V_A:\exists e\notin E_A,\ u\in Endpoints(e)\}
\]

\[
\partial E_A=
\{e\in E\setminus E_A:\ Endpoints(e)\cap V_A\neq\varnothing\}
\]

Boundary مشتقة من النسخة البنيوية + live graph.

## 8.2 Overlap

\[
O_E(A,B)=E_A\cap E_B
\]

\[
O_V(A,B)=V_A\cap V_B
\]

لكن:

\[
\boxed{Overlap\neq Merge}
\]

\[
\boxed{Overlap\neq ActivationInheritance}
\]

## 8.3 Poly-membership

\[
M(e)=\{AID:e\in E_A\}
\]

وبالتالي:

\[
\boxed{|M(e)|\le A_{max}}
\]

Historical versions لنفس Logical Assembly لا تضاعف هذا العدد.

## 8.4 Containment

\[
Contained(A,B)\iff E_A\subset E_B
\]

Containment علاقة بنيوية مشتقة ولا تنقل authority أوactivation.

## 8.5 Connection

Assembly-to-Assembly connection لا تُخزن كEdge معرفية جديدة؛ هي view مشتقة من underlying graph إذا ربطت Edge أعضاء A بأعضاء B.

## 8.6 Boundary Crossing

عبور النشاط Boundary Edge لا يضيفها تلقائياً إلى membership، لكنه قد يولد Cue محلية تجعل Assembly أخرى Candidate في Selection Epoch لاحقة.

---

# 9. Compute & Energy Conservation under Overlap

إذا كانت Edge واحدة عضواً في Assemblies متعددة، يجب ألا تنفذ propagation الفيزيائية عدة مرات بسبب metadata.

\[
TransmissionKey=
(ParentCycleID,MicroTick,EdgeID,ContextBinding)
\]

ويجب:

\[
\boxed{CountPhysicalTransmission(TransmissionKey)\le1}
\]

إذن:

\[
\boxed{AssemblyMultiplicity\not\Rightarrow EnergyMultiplicity}
\]

وتبقى Working States لكل Active Assembly منفصلة حتى لو شاركت أعضاء فيزيائيين.

---

# 10. Assembly Competition, Selection & Local Inhibition

## 10.1 المبدأ

\[
Cue\rightarrow LocalCandidates\rightarrow DerivedSupport\rightarrow LocalDominance\rightarrow BoundedActiveSet
\]

المنافسة تختار computation ولا تنشئ Knowledge.

## 10.2 Post-Law-4 State

RFC-11 يستهلك \(A_u^\star\) بعد تطبيق context gating/inhibition الموجودة في Law 4؛ لا يعيد تعريفها.

## 10.3 Cue Coverage

\[
M_C=\sum_{u\in C_t}A_u^\star
\]

\[
\boxed{
Cov(A|C)=
\frac{\sum_{u\in S_A^\star}A_u^\star}{M_C}
}
\]

إذا \(M_C=0\) فلا Competition.

## 10.4 Seed-Normalized Conductance

لمنع تحيز Assemblies الكبيرة، لكل Seed:

\[
\boxed{
g_A(u)=
\max_{e:LawfulFrom(u,e,c)\land e\in E_A}W_e
}
\]

وإن لم توجد Edge قانونية: \(g_A(u)=0\).

ثم:

\[
\boxed{
Cond(A|C)=
\frac{
\sum_{u\in S_A^\star}
A_u^\star\sigma(g_A(u))
}{
\sum_{u\in S_A^\star}A_u^\star
}
}
\]

حيث:

\[
\sigma(x)=1-e^{-x}
\]

## 10.5 Assembly Cue Support

\[
\boxed{Q_A=Cov(A|C)\cdot Cond(A|C)}
\]

ومن ثم:

\[
0\le Q_A<1
\]

لكن \(Q_A\) Derived/Transient/Read-Only ولا تُخزن ولا تُتعلم.

## 10.6 Local Dominance

\[
B\triangleright A
\]

إذا:

\[
S_A^\star\subseteq S_B^\star
\]

و:

\[
Q_B\ge Q_A
\]

مع تفوق صارم واحد على الأقل في seed coverage أوQ.

ثم:

\[
\boxed{
\mathcal N_t=
\{A:\nexists B,\ B\triangleright A\}
}
\]

هي Non-Dominated Set.

## 10.7 Ambiguity

إذا كانت Candidates متعادلة معرفياً فلا يحسم AssemblyID المعنى. إذا لم تكفِ الموارد لقبول Tie Group كاملة:

\[
\boxed{DEFERRED\_AMBIGUOUS}
\]

## 10.8 Capacity

\[
\boxed{|ActiveAssemblies|\le K_{ASM}^{active}}
\]

وهو ceiling لا target.

## 10.9 Inhibition

Assembly inhibition في v1 هي **Admission Inhibition فقط**؛ لا تخفض Node activation ولا W ولاSalience ولاحقيقة المنافس.

## 10.10 Competition Is Read-Only

\[
Win(A)\not\Rightarrow Evidence
\]

\[
Loss(A)\not\Rightarrow NegativeEvidence
\]

ولا winner bonus أوloser penalty أوSoftmax/global normalization.

---

# 11. Structural Evolution

## 11.1 General Rule

كل Mutation بنيوية:

\[
LocalCondition\rightarrow Proposal\rightarrow Validation\rightarrow AtomicCommit
\]

وتحقق:

\[
\boxed{Local+Persistent+Bounded+Versioned+Atomic}
\]

## 11.2 Structural Arbitration

الترتيب القانوني عند تعارض Proposals:

\[
\boxed{SANITIZE > REUSE > GROW > MERGE > FORM}
\]

الغرض هو أقل تغيير بنيوي قانوني، وليس ترتيب قيمة معرفية. بعد كل Commit تعاد validation لبقية Proposals.

---

# 12. Growth

Growth تضيف Edge موجودة أصلاً في graph إلى Assembly؛ لا تنشئ Edge جديدة.

شرط locality:

\[
e\in\partial E_A
\]

وتحتاج repeated independent validated external co-use:

\[
N_{str}(A,e,c)\ge N_{ASM}^{confirm}
\]

ثم:

\[
E_A^{v+1}=E_A^v\cup\{e\}
\]

وفي v1:

\[
\boxed{OneGrowthCommit\le OneNewMemberEdge}
\]

Growth لا تغير cognition للEdge.

---

# 13. Weakening & Sanitation

لا يوجد Assembly weakness scalar ولاmembership strength.

\[
Inactivity\not\Rightarrow Detachment
\]

\[
LowSelectionFrequency\not\Rightarrow Detachment
\]

\[
WeightReductionAlone\not\Rightarrow Detachment
\]

إذا أصبحت Edge نفسها غير قانونية للعضوية بسبب lifecycle/identity/validity، تنشأ Sanitation Proposal versioned:

\[
E_A^{v+1}=E_A^v\setminus\{e\}
\]

Law 14 لا تحذف Edge من graph؛ Law 3 تملك Edge death.

---

# 14. Split

Split في v1 ليست clustering. تأتي من disconnection بنيوية قانونية، غالباً بعد Sanitation.

\[
CC(E_A')=\{C_1,\dots,C_k\}
\]

إذا \(k>1\)، تنشأ Child Assemblies لكل Component صالح:

\[
|C_i|\ge K_{ASM}^{min}
\]

مع conservation:

\[
E_A=D\uplus C_1\uplus\dots\uplus C_k
\]

حيث \(D\) أعضاء أزيلوا صراحة وبشكل قانوني.

Split ينشئ Logical IDs جديدة، يحفظ lineage، ولا ينسخ Edge cognition. Parent تصبح Retired بعد Commit ناجح.

---

# 15. Merge

Merge لا تعتمد على similarity أوoverlap threshold.

في DGCA v1 يجب أن يكون:

\[
\boxed{CanonicalParticipationComponent=E_A\cup E_B}
\]

في repeated independent validated external observations.

يُحظر pair mining من Component أكبر مثل \(A+B+C\).

ثم:

\[
E_M=E_A\cup E_B
\]

\[
Parents(M)=\{A,B\}
\]

وMerge **Non-Destructive** في v1:

\[
A\ survives,\qquad B\ survives
\]

ولا collective belief أوweight averaging.

---

# 16. Retirement & Reclamation

Retirement لا تعني forgetting:

\[
Retire(A)\not\Rightarrow DeleteKnowledge
\]

أسبابها القانونية تشمل: below-minimum بعد sanitation، successful split parent، structural invalidity، exact duplicate recovery case، أوexplicit lawful replacement.

Lifecycle مقترح:

`ACTIVE -> RETIRE_CANDIDATE -> RETIRED -> RECLAIMABLE -> PHYSICALLY_RECLAIMED`

Assembly المتقاعدة لا تقبل Activations جديدة، لكن Activations المفتوحة على نسخة محمية تكمل عملها.

\[
ProtectedReferences(A:v)>0\Rightarrow NoGC(A:v)
\]

---

# 17. Integration with Laws 1–13

| القانون | سلطة القانون الأصلية | علاقة Law 14 |
|---|---|---|
| Law 1 | Edge creation | Law 14 لا تنشئ semantic Edges؛ تنظّم الموجودة فقط |
| Law 2 | Edge reinforcement/context learning | نفس external episode قد تغذي Law 2 وstructural vote، لكن لا double learning |
| Law 2-b | direction/role asymmetry | membership لا تعيد كتابة direction/roles |
| Law 3 | decay/pruning/cellular death | Law 14 تستجيب بنيوياً لموت Edge ولا تملك سلطة موتها |
| Law 4 | energy/gating/inhibition | Law 14 تستهلك post-gating state ولا تتجاوز gates |
| Law 5 | Edge consolidation/locking | لا Assembly-lock persistent scalar في v1 |
| Law 6 | provenance/timestamp/episode isolation | السلطة الأساسية لإثبات Structural Evidence |
| Law 7 | resonant propagation physics | Active Assembly تنظّم النطاق ولا تستبدل propagation law |
| Law 8 | salience | membership/wins لا تزيد salience |
| Law 9 | similarity/generalization | similarity لا تسبب formation أوmerge مباشرة |
| Law 10 | concept hubs | Hub وAssembly primitives مختلفان |
| Law 11 | sequence/events/roles | Assemblies يمكنها تنظيم هذه Edges دون إعادة كتابة role/lag |
| Law 12 | drives/valence | قد تؤثر في activation الحالي، لا في structural evidence بذاتها |
| Law 13 | prediction/causality/disappointment | prediction/internal outcome لا يصوت لـLaw 14 بلا external validated root experience |

---

# 18. Law 14 — النص الرسمي

## 18.1 الاسم

**Law 14 — Local Assembly Emergence & Structural Organization**  
**القانون 14 — قانون نشوء التجمعات المحلية والتنظيم البنيوي**

## 18.2 النص المعياري

> **Independent, validated external co-use of a bounded connected set of persistent edges may establish a Local Assembly that records structural membership only. Subsequent structural adaptation may grow, sanitize, split, merge, or retire such assemblies only through local, bounded, versioned, deterministic, and atomic operations. Law 14 shall not create, duplicate, average, reinforce, suppress, or otherwise mutate the cognitive state owned by member edges. Internally generated activity, recall, simulation, prediction, pattern completion, or re-encoded self-derived output shall not constitute structural evidence.**

الصياغة العربية المعيارية:

> **يجوز للاستخدام الخارجي الصحيح، المستقل والمتكرر لمجموعة محدودة ومتصلة من الروابط الدائمة أن ينشئ Local Assembly تحفظ العضوية والتنظيم البنيوي فقط. ولا يجوز لأي تكيف بنيوي لاحق — نمو، تنظيف، انقسام، دمج أوتقاعد — إلا أن يتم محلياً، بحدود صلبة، وبنسخ بنيوية معلومة، وبحتمية وذرية. لا يملك القانون 14 سلطة إنشاء أو نسخ أو دمج أو تقوية أو إضعاف أو تعديل الحالة المعرفية المملوكة للروابط الأعضاء. ولا يعد النشاط المولّد داخلياً، أو الاسترجاع، أو المحاكاة، أو التوقع، أو Pattern Completion، أو المخرجات الذاتية المعاد ترميزها، دليلاً بنيوياً صالحاً.**

## 18.3 القلب الرياضي

\[
\boxed{
N_{str}(S,c)\ge N_{ASM}^{confirm}
\land Connected(S)
\land CapacityValid(S)
\Rightarrow StructuralOrganization(S)
}
\]

تحت شروط eligibility والهوية والمصدر والحدود.

وقانون الحفظ الأعلى:

\[
\boxed{\Delta CognitiveState_{Law14}=0}
\]

أي، بسبب Law 14 نفسها:

\[
\Delta W=0
\]

\[
\Delta Salience=0
\]

\[
\Delta CausalStrength=0
\]

\[
\Delta ContextBelief=0
\]

\[
\Delta PredictionMemory=0
\]

---

# 19. Mathematical Core & Parameter Registry

## 19.1 Existing Quantities Reused

| الكمية | المصدر | استعمال RFC-11 |
|---|---|---|
| \(A_u(t)\) | DGCA Core | transient node activation |
| \(W_e(t)\) | Laws 1–3 | seed conductance/read-only support |
| `ValidOrigin` | Law 6 | provenance validation |
| `GateOpen` | Law 4 | contextual eligibility |
| \(\sigma(x)=1-e^{-x}\) | Law 4 family | conductance saturation |
| \(\theta_{active}\) | RFC-03 | seed/participant eligibility |
| Edge lifecycle | Law 3 | sanitation |
| Edge context | Laws 2/4 | gating |

لا يُعاد تعريف هذه الكميات داخل Law 14.

## 19.2 New Policy Parameters

| الرمز | المعنى | النوع |
|---|---|---|
| \(K_{ASM}^{min}\) | أقل Member Edges لAssembly قانونية | Structural bound |
| \(N_{ASM}^{confirm}\) | عدد Root External Experiences المستقلة لتأكيد structural mutation إيجابية | Structural persistence |
| \(A_{max}\) | أقصى Logical Assemblies لكل Edge | Membership bound |
| \(K_{ASM}^{mem}\) | أقصى Member Edges داخل Assembly | Structural/resource bound |
| \(K_{ASM}^{active}\) | أقصى Active Assemblies المتزامنة في Parent Cycle | Runtime sparsity bound |
| \(K_{struct}^{pending}\) | أقصى pending structural candidates لكل Anchor | Runtime/storage bound |

## 19.3 Provisional Starting Profile

استناداً إلى prior هندسي سابق فقط، لا إلى DGCA calibration نهائية:

\[
K_{ASM}^{min}=3
\]

\[
N_{ASM}^{confirm}=5
\]

\[
A_{max}=4
\]

الحالة:

**PROVISIONAL STARTING PROFILE — NOT FROZEN AS EMPIRICALLY OPTIMAL**.

أما \(K_{ASM}^{mem}\)، \(K_{ASM}^{active}\)، \(K_{struct}^{pending}\) فتحتاج Calibration Benchmarks.

## 19.4 Parameters Rejected in v1

لا نضيف:

- independent `k_form_max`
- separate `n_grow`
- separate `n_merge`
- `theta_assembly`
- Assembly strength/confidence/salience
- Assembly context threshold
- Assembly similarity threshold
- split/merge similarity threshold
- global popularity score

## 19.5 Policy Versioning

أي تغيير في Policy Parameters المعتمدة ينتج:

\[
\Theta_{14}^{v}\rightarrow\Theta_{14}^{v+1}
\]

ولا يعيد تفسير التاريخ بأثر رجعي.

---

# 20. Complexity & Resource Bounds

نعرف:

\[
N=|V|,\quad M=|E|,\quad L=|\mathbb A|
\]

\[
a=A_{max},\quad m=K_{ASM}^{mem},\quad k=K_{ASM}^{active},\quad p=K_{struct}^{pending}
\]

## 20.1 Total Membership Bound

\[
R=\sum_{A\in\mathbb A}|E_A|
=
\sum_{e\in E}|Membership(e)|
\]

وبالتالي:

\[
\boxed{R\le M\cdot a}
\]

ومع \(a\) ثابت:

\[
\boxed{Memory_{membership}=O(M)}
\]

## 20.2 Live Assembly Count Bound

بما أن:

\[
|E_A|\ge K_{ASM}^{min}
\]

فإن:

\[
\boxed{
L\le \frac{M A_{max}}{K_{ASM}^{min}}
}
\]

## 20.3 Formation

لا subset enumeration. Connected-component extraction محلية وتكلفتها مرتبطة بحجم current participation region، لا graph الكاملة.

## 20.4 Growth/Split/Merge

مع \(|E_A|\le m\):

- Growth validation: \(O(m)\).
- Split connectivity: \(O(|V_A|+|E_A|)\), bounded محلياً.
- Merge union/validation: \(O(m)\) تقريباً تحت bound.

## 20.5 Candidate Lookup

إذا كان عدد Cue-local edges هو \(q_C\):

\[
|CandidateAssemblies|\le q_C A_{max}
\]

قبل deduplication.

Candidate scoring:

\[
O(q_C A_{max} K_{ASM}^{mem})
\]

Local dominance قد يكون تربيعياً داخل **candidate set المحلية فقط**، وليس \(O(L^2)\) عالمياً.

## 20.6 No Global Operations

يحظر:

- global assembly scan for cue.
- all-pairs assembly merge search.
- global overlap matrix.
- global clustering/community detection.
- global optimizer.

## 20.7 Active Working Memory

\[
\boxed{Space_{active}=O(K_{ASM}^{active}\cdot K_{ASM}^{mem})}
\]

لكل Parent Cycle، إضافة إلى transient node state الموجودة أصلاً.

## 20.8 Hot Runtime vs Audit Archive

Historical audit growth قد يعتمد على عدد commits عبر الزمن، لذلك يفصل:

\[
HotRuntimeState\neq AuditArchive
\]

ولا تجعل retention policy جزءاً من cognition أوLaw 14 نفسها.

---

# 21. Security & Adversarial Review

## 21.1 الثغرات التي أغلقت معمارياً

1. **Micro-Episode Vote Inflation** — RootExternalEpisode deduplication.
2. **Cross-Modal Vote Inflation** — modalities من نفس root تصوت مرة واحدة.
3. **Self-Generated Provenance Laundering** — transitive SelfDerived firewall.
4. **Large-Assembly Selection Bias** — Seed-Normalized Conductance.
5. **Concurrent Proposal Race** — deterministic structural arbitration + revalidation.
6. **Merge Storm / Pair Mining** — exact canonical union observation.
7. **Formation Subset Explosion** — no connected-subset enumeration.
8. **Membership Explosion** — \(A_{max}\) hard bound.
9. **Overlap Energy Multiplication** — transmission deduplication.
10. **Shared-Node Destructive Suppression** — admission-only inhibition.
11. **Winner Self-Reinforcement** — no winner bonus / loser penalty.
12. **Stale Version Mutation** — base-version revalidation.
13. **GC Race** — protected references.
14. **Hash Collision Overwrite** — canonical member-set identity verification.
15. **Lineage Cycle** — lineage DAG requirement.
16. **Structural Oscillation** — conservative detachment semantics.
17. **Mega-Assembly Direct Formation** — oversize fail-closed.
18. **Merge Parent Destruction** — non-destructive merge v1.
19. **Prediction/Completion Self-Reinforcement** — internal origin cannot vote.
20. **Cache as Authority** — derived indexes are rebuildable and non-canonical.

## 21.2 Empirical Risks Remaining

تحتاج Benchmark لا redesign مسبق:

- \(A_{max}\) saturation.
- \(K_{ASM}^{mem}\) calibration.
- \(K_{ASM}^{active}\) calibration.
- \(K_{struct}^{pending}\) pressure.
- high-degree hubs.
- local dominance runtime.
- version-storm hot memory.
- million-edge scaling.
- exact-context fragmentation.
- long-running pending candidate pressure.

## 21.3 Upstream Trust Boundary

Law 14 لا تستطيع بنفسها إثبات صحة العالم الخارجي. بيانات خارجية مضللة ومتكررة قد تنتج cognition/structure مضللة وفق القوانين نفسها. إدارة provenance/source quality/curriculum هي مسؤولية Phase III.

---

# 22. Determinism & Atomicity

## 22.1 Canonical Arithmetic

يجب جمع/ترتيب member edges بمعرفات canonical ثابتة عند الحاجة لضمان deterministic replay.

## 22.2 Identity

Hash collision لا يساوي identity. يجب التحقق من canonical edge set.

## 22.3 Structural Proposal Key

يمكن ترتيب same-class proposals بمفتاح deterministic من نوع:

`(mutation_priority, base_assembly_id, canonical_edge_ids, context_signature)`

للتنفيذ، مع revalidation بعد كل Commit.

## 22.4 Atomic Publication

أي mutation:

\[
\boxed{COMMIT\quad or\quad NO\ VISIBLE\ CHANGE}
\]

ولا partial membership/index state.

---

# 23. Architecture / Policy Separation

يعتمد RFC-11 فصل نسختين:

```text
RFC-11 Architecture:     v1.0 — FROZEN
Law-14 Semantics:        v1.0 — FROZEN
Law-14 Policy Profile:   provisional / calibrated separately
```

تغيير \(A_{max}\) مثلاً بعد Benchmark لا يعيد فتح المعمارية إذا بقيت semantics نفسها.

---

# 24. Acceptance & Verification Philosophy

كل implementation يجب أن يثبت:

- Constitution compliance.
- Functional correctness.
- Adversarial resistance.
- Deterministic replay.
- Integration with Laws 1–13.
- Scaling/locality.
- Cognitive conservation.
- Phase-I regression safety.

لا يُقبل implementation بسبب demo ناجح أوفقرة لغوية جيدة فقط.

---

# 25. Canonical Invariant Registry

هذا السجل هو المرجع التنفيذي المرقم. أي Implementation يجب أن يربط الاختبارات الحرجة بهذه الـIDs.

| ID | Invariant |
|---|---|
| RFC11-INV-001 | Edge Cognitive Ownership — Assembly membership never duplicates or owns member-edge cognitive state. |
| RFC11-INV-002 | No Global Assembly Discovery — assembly formation is local; no global clustering scan. |
| RFC11-INV-003 | Non-Exclusive Membership — an Edge may belong to multiple bounded Logical Assemblies. |
| RFC11-INV-004 | No Assembly Controller — no master node/router owns or centrally controls an Assembly. |
| RFC11-INV-005 | MemberNodes(A) = Endpoints(MemberEdges(A)); no independent persistent node membership in v1. |
| RFC11-INV-006 | AssemblyMembership = ReferencesOnly; membership does not copy member state. |
| RFC11-INV-007 | MaterialMembershipChange => NewStructuralVersion. |
| RFC11-INV-008 | ActiveAssembly pins an exact StructuralAssemblyVersion. |
| RFC11-INV-009 | Boundary, Overlap and NodeSet are derived structural views. |
| RFC11-INV-010 | Assembly owns no persistent Strength, Confidence, Salience or ContextBelief. |
| RFC11-INV-011 | Derived caches and indexes must be reconstructible. |
| RFC11-INV-012 | Structural lineage is not cognitive inheritance. |
| RFC11-INV-013 | Internal activation does not create Formation Evidence. |
| RFC11-INV-014 | One Root External Episode contributes at most one structural vote per candidate. |
| RFC11-INV-015 | Formation requires repeated validated external local co-use. |
| RFC11-INV-016 | FormationCandidate != StructuralAssembly. |
| RFC11-INV-017 | Exact duplicate formation => reuse existing logical structure. |
| RFC11-INV-018 | Partial overlap does not imply duplicate identity. |
| RFC11-INV-019 | Formation commit does not mutate Edge cognition. |
| RFC11-INV-020 | Transient or hypothetical Edges cannot become persistent StructuralAssembly members in v1. |
| RFC11-INV-021 | Formation detection must remain local and bounded. |
| RFC11-INV-022 | Poly-membership overflow => fail closed; no hidden eviction. |
| RFC11-INV-023 | StructuralAssembly != ActiveAssembly. |
| RFC11-INV-024 | Membership != Participation. |
| RFC11-INV-025 | ActiveAssembly pins exact structural version. |
| RFC11-INV-026 | No mid-flight version migration. |
| RFC11-INV-027 | Activation working state is transient only. |
| RFC11-INV-028 | No lawful Seed => no Activation. |
| RFC11-INV-029 | Internal Activation is allowed while internal Formation voting remains forbidden. |
| RFC11-INV-030 | Assembly Activation does not own duplicate Node activation state. |
| RFC11-INV-031 | Internal Assembly propagation uses pinned member edges only. |
| RFC11-INV-032 | Boundary traversal does not imply membership growth. |
| RFC11-INV-033 | Activation creates no persistent cognition. |
| RFC11-INV-034 | ActiveAssembly != PatternCompletion. |
| RFC11-INV-035 | Closed Activation cannot be reopened as the same operational instance. |
| RFC11-INV-036 | Pinned structural version cannot be collected while referenced. |
| RFC11-INV-037 | Boundary is derived from member set and live graph. |
| RFC11-INV-038 | Boundary change alone does not imply membership change. |
| RFC11-INV-039 | Overlap != Merge. |
| RFC11-INV-040 | Shared membership does not duplicate underlying Edge/Node state. |
| RFC11-INV-041 | Poly-membership is bounded per Logical Assembly identity. |
| RFC11-INV-042 | Historical versions do not multiply membership count. |
| RFC11-INV-043 | Assembly connection is derived from the underlying graph. |
| RFC11-INV-044 | Shared member activation does not automatically activate every Assembly containing it. |
| RFC11-INV-045 | Assembly multiplicity does not imply energy multiplicity. |
| RFC11-INV-046 | One underlying Edge performs at most one physical propagation per lawful micro-interaction key. |
| RFC11-INV-047 | A shared Node has one underlying transient activation state. |
| RFC11-INV-048 | Shared members do not merge ActiveAssembly working states. |
| RFC11-INV-049 | Structural containment does not imply authority inheritance. |
| RFC11-INV-050 | No global overlap matrix and no writable flattened super-Assembly view. |
| RFC11-INV-051 | Membership count carries no truth, confidence or salience meaning. |
| RFC11-INV-052 | Structural membership does not reserve runtime resources. |
| RFC11-INV-053 | Assembly membership cannot override Edge/Node context gating. |
| RFC11-INV-054 | Competition is read-only with respect to persistent cognition. |
| RFC11-INV-055 | Win does not create Evidence or Formation votes. |
| RFC11-INV-056 | Loss does not create Negative Evidence or decay. |
| RFC11-INV-057 | Assembly Cue Support Q is derived transient state. |
| RFC11-INV-058 | No persistent Assembly Strength or Confidence. |
| RFC11-INV-059 | Competition consumes post-Law-4 state. |
| RFC11-INV-060 | No Softmax or global candidate normalization. |
| RFC11-INV-061 | Selection uses local dominance, not global winner-take-all. |
| RFC11-INV-062 | Non-dominated Assemblies may coactivate when resources allow. |
| RFC11-INV-063 | Exact cognitive ambiguity must not be broken by numeric identity. |
| RFC11-INV-064 | Tie group larger than remaining capacity => deferred ambiguity. |
| RFC11-INV-065 | Simultaneous ActiveAssemblies <= K_ASM^active. |
| RFC11-INV-066 | Capacity is a ceiling, not a target to fill. |
| RFC11-INV-067 | Assembly inhibition is transient admission inhibition only. |
| RFC11-INV-068 | Assembly competition cannot directly suppress shared Node activation. |
| RFC11-INV-069 | No persistent Assembly-to-Assembly inhibitory edges in v1. |
| RFC11-INV-070 | No winner incumbency bonus. |
| RFC11-INV-071 | No persistent loser penalty. |
| RFC11-INV-072 | Reselection occurs only at meaningful Selection Epochs. |
| RFC11-INV-073 | Assembly competition cannot override existing context gates. |
| RFC11-INV-074 | Operational selection failure != cognitive failure. |
| RFC11-INV-075 | Structural evolution requires Proposal -> Validation -> Atomic Commit. |
| RFC11-INV-076 | Growth adds structural membership, not knowledge. |
| RFC11-INV-077 | Growth requires repeated validated external local co-use. |
| RFC11-INV-078 | Growth is boundary-local. |
| RFC11-INV-079 | Assembly membership size is bounded by K_ASM^mem. |
| RFC11-INV-080 | One Growth commit adds at most one member Edge in v1. |
| RFC11-INV-081 | Assembly weakening has no persistent scalar. |
| RFC11-INV-082 | Inactivity or competition loss cannot detach membership. |
| RFC11-INV-083 | Edge weight reduction alone cannot detach membership. |
| RFC11-INV-084 | Invalid membership requires versioned sanitation. |
| RFC11-INV-085 | Lawful disconnection may trigger local Split. |
| RFC11-INV-086 | Split discovery uses no global clustering metric. |
| RFC11-INV-087 | Split explicitly accounts for every former member. |
| RFC11-INV-088 | Split creates new Logical Assembly identities. |
| RFC11-INV-089 | Split does not clone Edge cognition. |
| RFC11-INV-090 | Merge requires repeated validated external co-use and local connectivity. |
| RFC11-INV-091 | Merge is non-destructive to parents in DGCA v1. |
| RFC11-INV-092 | Merged Assembly owns no merged belief state. |
| RFC11-INV-093 | Merge must respect poly-membership and Assembly capacity bounds. |
| RFC11-INV-094 | Assembly inactivity alone cannot cause retirement. |
| RFC11-INV-095 | Retirement does not delete underlying knowledge. |
| RFC11-INV-096 | Merge does not automatically retire parents. |
| RFC11-INV-097 | Retired Assembly cannot admit new Activations. |
| RFC11-INV-098 | Protected references delay physical reclamation. |
| RFC11-INV-099 | Published structural versions are immutable. |
| RFC11-INV-100 | Stale structural Proposal must revalidate or fail. |
| RFC11-INV-101 | Structural Commit creates no cognitive Evidence. |
| RFC11-INV-102 | Structural evolution remains local, event-driven and bounded. |
| RFC11-INV-103 | Law 14 owns persistent Assembly structural organization only. |
| RFC11-INV-104 | Law 14 cannot create or mutate semantic Edge knowledge. |
| RFC11-INV-105 | Law-6-valid provenance is required for Law-14 structural evidence. |
| RFC11-INV-106 | Law 3 owns Edge death; Law 14 owns only structural response. |
| RFC11-INV-107 | Law 4 owns physical gating and Node inhibition. |
| RFC11-INV-108 | Law 7 owns propagation physics. |
| RFC11-INV-109 | Law 9 similarity cannot directly cause Assembly formation or merge. |
| RFC11-INV-110 | ConceptHub and Assembly remain distinct primitives. |
| RFC11-INV-111 | Prediction or internal simulation cannot validate Law-14 structure. |
| RFC11-INV-112 | Law-14 structural mutation conserves Edge identity and cognition. |
| RFC11-INV-113 | No existing Law 1–13 is silently reinterpreted as Assembly authority. |
| RFC11-INV-114 | Law 14 introduces no persistent learned scalar. |
| RFC11-INV-115 | Existing DGCA quantities are reused rather than redefined when semantics match. |
| RFC11-INV-116 | Formation, Growth and Merge share one structural persistence parameter in v1. |
| RFC11-INV-117 | No independent formation maximum beyond the Assembly membership bound. |
| RFC11-INV-118 | Assembly Cue Support Q is derived, read-only and bounded. |
| RFC11-INV-119 | No Assembly support threshold is required in v1. |
| RFC11-INV-120 | All Law-14 policy parameters are finite, versioned and non-learned. |
| RFC11-INV-121 | Silent policy-parameter mutation is forbidden. |
| RFC11-INV-122 | Canonical arithmetic/ordering is required for deterministic replay. |
| RFC11-INV-123 | Law-14 numeric calibration cannot be claimed before dedicated DGCA Assembly benchmarks. |
| RFC11-INV-124 | Total live Assembly membership references <= M * A_max. |
| RFC11-INV-125 | Live Assembly count <= M*A_max/K_ASM^min. |
| RFC11-INV-126 | Formation must never enumerate connected subsets. |
| RFC11-INV-127 | Formation candidates are extracted from canonical local participation components. |
| RFC11-INV-128 | Oversized formation component => no direct formation. |
| RFC11-INV-129 | No global Assembly pair enumeration for Merge. |
| RFC11-INV-130 | Merge candidates originate from current local validated co-use. |
| RFC11-INV-131 | Candidate Assembly discovery uses Edge membership indexes, not global Assembly search. |
| RFC11-INV-132 | Pairwise dominance may operate only on the current local candidate set. |
| RFC11-INV-133 | ActiveAssembly working state is bounded by K_ASM^active * K_ASM^mem. |
| RFC11-INV-134 | Runtime structural state and historical audit archive are distinct. |
| RFC11-INV-135 | Unprotected historical full versions need not remain in hot runtime memory. |
| RFC11-INV-136 | Remote graph growth must not cause global Assembly scanning for an unchanged local cue. |
| RFC11-INV-137 | Law 14 makes no empirical large-scale claim before measured scaling benchmarks. |
| RFC11-INV-138 | Structural votes are deduplicated by RootExternalEpisodeID. |
| RFC11-INV-139 | Micro-Episode multiplicity cannot increase structural confirmation count. |
| RFC11-INV-140 | Cross-modal observations from one root experience cannot inflate structural votes. |
| RFC11-INV-141 | SelfDerived provenance propagates transitively through internal re-encoding. |
| RFC11-INV-142 | Self-derived content cannot become Law-14 evidence by serialization/re-encoding alone. |
| RFC11-INV-143 | Assembly Conductance is seed-normalized. |
| RFC11-INV-144 | Dormant member count cannot increase Assembly Cue Support. |
| RFC11-INV-145 | Positive structural mutation uses canonical minimal-change precedence. |
| RFC11-INV-146 | Concurrent structural Proposals are deterministically ordered and revalidated. |
| RFC11-INV-147 | Merge requires exact canonical union observation in v1. |
| RFC11-INV-148 | Larger participation components cannot be mined into pairwise Merge subsets. |
| RFC11-INV-149 | Assembly identity hash equality does not override structural identity verification. |
| RFC11-INV-150 | Assembly lineage must remain acyclic. |
| RFC11-INV-151 | Corrupted derived indexes cannot become canonical structural authority. |
| RFC11-INV-152 | Ambiguity/resource failure must fail conservatively without cognitive mutation. |
| RFC11-INV-153 | Every critical architectural invariant must have executable acceptance coverage. |
| RFC11-INV-154 | Law 14 cannot be released with known failing mandatory tests. |
| RFC11-INV-155 | Phase-I regression pass is mandatory for Law-14 release. |
| RFC11-INV-156 | Deterministic replay is a release requirement. |
| RFC11-INV-157 | Empirical scalability claims require measured scaling evidence. |
| RFC11-INV-158 | Diagnostic observability cannot feed back into cognition. |
| RFC11-INV-159 | Policy calibration is separated from architectural correctness. |
| RFC11-INV-160 | Structural-only execution must preserve the Edge Cognitive Digest. |

# 26. Acceptance Test Matrix — RFC11-T001..T096

| Test | الهدف | معيار PASS المختصر |
|---|---|---|
| RFC11-T001 — Edge-Centric Membership | Edge-Centric Membership | Member nodes derived only from member-edge endpoints. |
| RFC11-T002 — No Cognitive Duplication | No Cognitive Duplication | Formation leaves member-edge cognition unchanged by Law 14. |
| RFC11-T003 — No Assembly Cognitive State | No Assembly Cognitive State | Canonical Assembly record contains no forbidden learned cognitive scalar. |
| RFC11-T004 — Version Immutability | Version Immutability | Published old version remains unchanged after a new version is published. |
| RFC11-T005 — Derived Boundary | Derived Boundary | Boundary cache rebuild exactly matches derived boundary. |
| RFC11-T006 — Reconstructible Reverse Index | Reconstructible Reverse Index | edge_to_assemblies can be deleted and rebuilt deterministically. |
| RFC11-T007 — Historical Version Membership | Historical Version Membership | Multiple versions of one logical Assembly count as one membership. |
| RFC11-T008 — Lineage ≠ Cognition | Lineage ≠ Cognition | Split/Merge lineage changes no Edge cognition. |
| RFC11-T009 — No Formation from One Observation | No Formation from One Observation | Single root experience does not form an Assembly. |
| RFC11-T010 — Formation at Confirmation Count | Formation at Confirmation Count | Formation occurs exactly when confirmation policy is met. |
| RFC11-T011 — Duplicate Callback Dedup | Duplicate Callback Dedup | Repeated callback for same root contributes one vote. |
| RFC11-T012 — Micro-Episode Inflation Attack | Micro-Episode Inflation Attack | Many micros from one root contribute one vote. |
| RFC11-T013 — Cross-Modal Inflation Attack | Cross-Modal Inflation Attack | Vision/audio/text descendants of one root contribute one vote. |
| RFC11-T014 — Independent Experiences | Independent Experiences | Distinct valid root experiences count independently. |
| RFC11-T015 — Recall Gives Zero Votes | Recall Gives Zero Votes | Repeated internal recall cannot increase N_str. |
| RFC11-T016 — Generation/Re-encoding Gives Zero Votes | Generation/Re-encoding Gives Zero Votes | Self-derived output remains structurally non-evidentiary. |
| RFC11-T017 — Pattern-Completion Future-Proof | Pattern-Completion Future-Proof | Internal completion-like activation contributes no vote. |
| RFC11-T018 — Formation Connectivity | Formation Connectivity | Disconnected edge set never forms one Assembly. |
| RFC11-T019 — Minimum Size | Minimum Size | Below K_ASM^min never forms. |
| RFC11-T020 — Oversized Component | Oversized Component | Above K_ASM^mem yields no direct formation/truncation. |
| RFC11-T021 — Exact Duplicate Reuse | Exact Duplicate Reuse | Exact existing member set reuses existing logical Assembly. |
| RFC11-T022 — Partial Overlap Allowed | Partial Overlap Allowed | Partial overlap alone does not imply duplicate identity. |
| RFC11-T023 — No Subset Enumeration | No Subset Enumeration | Instrumentation confirms no combinatorial connected-subset mining. |
| RFC11-T024 — No Seed No Activation | No Seed No Activation | Empty lawful seed set prevents Activation. |
| RFC11-T025 — Multiple Seeds | Multiple Seeds | Multiple lawful seeds are preserved without synthetic seed creation. |
| RFC11-T026 — Membership ≠ Participation | Membership ≠ Participation | Activation starts with actual participants, not all members. |
| RFC11-T027 — Exact Version Pinning | Exact Version Pinning | ActiveAssembly remains pinned to starting version. |
| RFC11-T028 — No Mid-Flight Migration | No Mid-Flight Migration | Runtime cannot migrate open Activation to a newer version. |
| RFC11-T029 — Closure Non-Cognitive | Closure Non-Cognitive | Closing Activation mutates no persistent cognition/membership. |
| RFC11-T030 — Internal Activation Allowed | Internal Activation Allowed | Internal cue may activate, but structural vote remains zero. |
| RFC11-T031 — Shared Edge Is One Edge | Shared Edge Is One Edge | One underlying Edge state is seen by all Assemblies referencing it. |
| RFC11-T032 — Shared Node One Activation | Shared Node One Activation | Shared Node has one underlying transient activation state. |
| RFC11-T033 — Poly-Membership Limit | Poly-Membership Limit | Fifth membership fails if A_max=4. |
| RFC11-T034 — No Hidden Eviction | No Hidden Eviction | Capacity failure does not evict older Assemblies automatically. |
| RFC11-T035 — Overlap Does Not Merge | Overlap Does Not Merge | Overlap alone never causes merge. |
| RFC11-T036 — Containment No Authority | Containment No Authority | Containing Assembly cannot control contained Assembly. |
| RFC11-T037 — Connection Is Derived | Connection Is Derived | Connection view rebuilds from graph. |
| RFC11-T038 — Boundary Crossing No Growth | Boundary Crossing No Growth | Runtime boundary traversal alone never grows membership. |
| RFC11-T039 — Support Is Derived | Support Is Derived | Q_A never appears in persistent serialized Assembly state. |
| RFC11-T040 — Seed-Normalized Conductance | Seed-Normalized Conductance | Adding dormant member edges does not raise Q_A. |
| RFC11-T041 — Coverage Advantage | Coverage Advantage | Superset seed coverage with no worse Q locally dominates subset candidate. |
| RFC11-T042 — Non-Dominated Coactivation | Non-Dominated Coactivation | Different valid aspects can coactivate when capacity allows. |
| RFC11-T043 — Exact Ambiguity Preservation | Exact Ambiguity Preservation | Identity does not break true semantic tie. |
| RFC11-T044 — Tie Group > Capacity | Tie Group > Capacity | Returns deferred ambiguity instead of arbitrary member selection. |
| RFC11-T045 — No Winner Bonus | No Winner Bonus | Previous win does not increase future support. |
| RFC11-T046 — No Loser Penalty | No Loser Penalty | Previous loss changes no cognition or persistent Assembly state. |
| RFC11-T047 — Admission-Only Suppression | Admission-Only Suppression | Suppressing Assembly does not zero a shared Node. |
| RFC11-T048 — No Assembly Softmax | No Assembly Softmax | Static/behavioral guard rejects global candidate normalization. |
| RFC11-T049 — Shared Edge Transmits Once | Shared Edge Transmits Once | One physical transmission per lawful key despite multiple active memberships. |
| RFC11-T050 — Membership Multiplicity Energy Invariance | Membership Multiplicity Energy Invariance | Physical energy does not increase with membership count alone. |
| RFC11-T051 — Growth Requires External Repetition | Growth Requires External Repetition | Internal repetition never qualifies growth; independent external repetition can. |
| RFC11-T052 — One Edge Per Growth Commit | One Edge Per Growth Commit | At most one new member edge per growth commit in v1. |
| RFC11-T053 — Growth New Version | Growth New Version | Growth preserves logical ID and publishes new version. |
| RFC11-T054 — Low Use No Detach | Low Use No Detach | Inactivity alone keeps membership. |
| RFC11-T055 — Weight Reduction No Detach | Weight Reduction No Detach | Lower W alone keeps membership while Edge remains live. |
| RFC11-T056 — Dead Edge Sanitation | Dead Edge Sanitation | Law-3 death triggers versioned sanitation, no ghost reference. |
| RFC11-T057 — Connected Sanitation | Connected Sanitation | If still connected, same logical ID publishes sanitized version. |
| RFC11-T058 — Disconnection Split | Disconnection Split | Lawful disconnection yields legal child Assemblies. |
| RFC11-T059 — Split Conservation | Split Conservation | Every former member is explicitly assigned or lawfully detached. |
| RFC11-T060 — Split No Clone | Split No Clone | Edge identity/cognition preserved exactly. |
| RFC11-T061 — Small Fragment No Knowledge Loss | Small Fragment No Knowledge Loss | Sub-min fragment creates no Assembly but underlying Edges persist. |
| RFC11-T062 — Mere Co-occurrence No Merge | Mere Co-occurrence No Merge | A and B inside larger event do not merge automatically. |
| RFC11-T063 — Canonical Union Requirement | Canonical Union Requirement | Merge only on exact canonical participation union in v1. |
| RFC11-T064 — No Pair Mining | No Pair Mining | A+B+C observation does not emit AB/AC/BC merges. |
| RFC11-T065 — Merge Non-Destructive | Merge Non-Destructive | Parents remain after merged Assembly creation. |
| RFC11-T066 — Merge Union by Identity | Merge Union by Identity | Union deduplicates only true Edge identity. |
| RFC11-T067 — Merge No Cognition Averaging | Merge No Cognition Averaging | No merged W/confidence/belief is created. |
| RFC11-T068 — Merge Capacity Atomic Failure | Merge Capacity Atomic Failure | Any membership overflow rejects entire merge. |
| RFC11-T069 — Inactivity No Retirement | Inactivity No Retirement | Unused Assembly remains structurally live. |
| RFC11-T070 — Below-Min Retirement | Below-Min Retirement | Sanitized structure below minimum retires if no legal child remains. |
| RFC11-T071 — Split Retires Parent | Split Retires Parent | Successful split retires parent for new activations. |
| RFC11-T072 — Merge Does Not Retire Parents | Merge Does Not Retire Parents | Non-destructive v1 semantics preserved. |
| RFC11-T073 — Open Activation Survives Retirement | Open Activation Survives Retirement | Pinned Activation can complete after structural retirement. |
| RFC11-T074 — Protected Version No GC | Protected Version No GC | Protected references block reclamation. |
| RFC11-T075 — Sanitize Precedence | Sanitize Precedence | Safety sanitation precedes positive mutation on conflicting structure. |
| RFC11-T076 — Reuse Precedence | Reuse Precedence | Existing exact structure prevents redundant mutation. |
| RFC11-T077 — Grow Before Form | Grow Before Form | Exact one-edge extension uses growth, not duplicate formation. |
| RFC11-T078 — Merge Before Novel Form | Merge Before Novel Form | Exact legal union uses merge semantics before novel form. |
| RFC11-T079 — Same-Class Determinism | Same-Class Determinism | Equivalent proposal arrival orders yield same final structural digest. |
| RFC11-T080 — Stale Proposal Revalidation | Stale Proposal Revalidation | Stale base version cannot overwrite current state. |
| RFC11-T081 — Failure Atomicity | Failure Atomicity | Injected commit failure leaves pre-commit visible state. |
| RFC11-T082 — Unknown Origin Rejected | Unknown Origin Rejected | Missing/uncertain provenance yields zero structural vote. |
| RFC11-T083 — Self-Derived Transitivity | Self-Derived Transitivity | Generated->encoded->transformed descendants remain self-derived. |
| RFC11-T084 — Hash Collision Protection | Hash Collision Protection | Forced ID collision fails closed without overwrite. |
| RFC11-T085 — Lineage Cycle Rejection | Lineage Cycle Rejection | Attempted ancestry cycle is rejected. |
| RFC11-T086 — Corrupt Reverse Index | Corrupt Reverse Index | Verifier detects mismatch and rebuilds/fails closed. |
| RFC11-T087 — Law 1 Owns Edge Creation | Law 1 Owns Edge Creation | Law 14 cannot grow with a nonexistent semantic Edge. |
| RFC11-T088 — Law 2 Sole Reinforcement Authority | Law 2 Sole Reinforcement Authority | Formation introduces no extra W reinforcement. |
| RFC11-T089 — Law 3 Owns Edge Death | Law 3 Owns Edge Death | Assembly cannot delete live Edge for structural convenience. |
| RFC11-T090 — Law 4 Gate Authority | Law 4 Gate Authority | EXCLUDED member Edge cannot be forced open by Assembly. |
| RFC11-T091 — Law 7 Propagation Authority | Law 7 Propagation Authority | No Assembly-specific alternate propagation law appears. |
| RFC11-T092 — Law 8 Salience Independence | Law 8 Salience Independence | Membership count does not increase Edge salience. |
| RFC11-T093 — Law 9 Similarity No Merge | Law 9 Similarity No Merge | Similarity alone never merges Assemblies. |
| RFC11-T094 — Law 10 Hub Independence | Law 10 Hub Independence | Hub lifecycle does not redefine Assembly identity semantics. |
| RFC11-T095 — Law 11 Role Preservation | Law 11 Role Preservation | Assembly membership does not rewrite role_k/lag. |
| RFC11-T096 — Law 13 Prediction No Vote | Law 13 Prediction No Vote | Prediction/internal success gives no structural vote without valid external root. |

# 27. Property-Based Test Families

| ID | Property | PASS condition |
|---|---|---|
| RFC11-P01 | Membership Bound | For all generated graphs: |M(e)| <= A_max. |
| RFC11-P02 | Assembly Size Bound | Every live Assembly respects K_ASM^min <= |E_A| <= K_ASM^mem. |
| RFC11-P03 | Membership Reference Bound | sum_A |E_A| <= M*A_max always. |
| RFC11-P04 | Cognitive Conservation | Random structural mutation sequences preserve Edge cognitive digest when Laws 1–13 learning is absent. |
| RFC11-P05 | Deterministic Replay | Same initial state + ordered events + policy version => identical digest. |
| RFC11-P06 | Equivalent Proposal Order | Canonical arbitration makes semantically equivalent concurrent ordering converge. |
| RFC11-P07 | Internal Activity No N_str Growth | Thousands of internal events never increase structural confirmation counts. |
| RFC11-P08 | Poly-Membership Compute Conservation | Increasing memberships alone never increases physical transmission count. |
| RFC11-P09 | No Global Assembly Scan | Instrumentation shows unreachable Assemblies are not visited for local cue. |
| RFC11-P10 | No Hidden Persistent Score | Long selection runs leave no persistent win/loss/support state in Assemblies. |

# 28. Benchmark Families

| ID | Benchmark | المطلوب |
|---|---|---|
| RFC11-B01 | Baseline Correctness | Hand-auditable graph covering formation, activation, competition, overlap, growth, merge, split and retirement. |
| RFC11-B02 | Formation Noise | Random non-repeating patterns produce zero false Assemblies under policy. |
| RFC11-B03 | Repeated Pattern Recovery | Deterministic formation occurs exactly at confirmation count. |
| RFC11-B04 | Context Separation | Different exact ContextSignatures do not pool confirmation votes. |
| RFC11-B05 | N_ASM^confirm Sweep | Measure false/missed formation, latency and pending pressure. |
| RFC11-B06 | A_max Sweep | Measure valid-formation rejection, membership memory, lookup pressure and overlap coverage. |
| RFC11-B07 | K_ASM^mem Calibration | Measure fragmentation, activation cost and mega-assembly tendency. |
| RFC11-B08 | K_ASM^active Calibration | Measure lost valid aspects, runtime and ambiguity pressure. |
| RFC11-B09 | K_struct^pending Pressure | Measure pending peak, eviction and valid-pattern loss. |
| RFC11-B10 | Scale Independence | 10^3..10^6 remote-edge growth must not induce remote Assembly scanning for fixed local cue. |
| RFC11-B11 | High-Degree Hub | Degree 10..10^4+; measure lookup/candidates/scoring/dominance. |
| RFC11-B12 | Overlap Stress | Increase overlap to A_max while proving zero energy duplication. |
| RFC11-B13 | Merge Storm Attack | Verify no O(L^2) pair discovery and only canonical local merges. |
| RFC11-B14 | Version Storm | Stress growth/sanitize/split/merge; measure hot/protected/history memory and GC correctness. |
| RFC11-B15 | Structural Mutation Throughput | Engineering metric only; commits/sec without changing semantics. |
| RFC11-B16 | Law-14 Behavioral Signature | Canonical end-to-end scenario yields stable deterministic digest. |
| RFC11-B17 | Phase-I Regression | All pre-Law-14 DGCA regression tests remain green unless a separately approved architecture change exists. |
| RFC11-B18 | Law-14 Disabled Equivalence | When Law 14 is disabled/no Assemblies exist, Phase-I behavior remains reference-equivalent. |


---

# 29. Required Observability

يجوز للتنفيذ توفير counters تشخيصية غير معرفية مثل:

```text
assembly_candidates_examined
edges_examined_for_assembly
structural_votes_accepted
structural_votes_rejected
duplicate_root_votes
self_derived_votes_rejected
assemblies_formed
growth_commits
sanitize_commits
split_commits
merge_commits
retirement_commits
stale_proposals_rejected
membership_capacity_rejections
assembly_capacity_rejections
physical_edge_transmissions
deduplicated_transmissions
active_assemblies_peak
pending_candidates_peak
versions_hot
versions_protected
```

شرط دستوري:

\[
\boxed{Observability\not\Rightarrow CognitiveInput}
\]

أي لا يجوز استعمال counters السابقة في learning/selection إلا إذا فُتح RFC مستقل يثبت ضرورة ذلك.

---

# 30. Reference Fixtures

يفضل أن تنشئ implementation suite Fixtures ثابتة:

1. **F1 — Simple Triangle**: Formation أساسية.
2. **F2 — Two Contexts**: `bank-money` و`bank-river`.
3. **F3 — Overlap**: Shared Edge.
4. **F4 — Boundary Growth**: Assembly + external boundary edge.
5. **F5 — Broken Bridge**: Sanitation -> Split.
6. **F6 — Merge Pair**: Exact canonical union.
7. **F7 — Large Dormant Assembly**: seed-normalized selection bias guard.
8. **F8 — Provenance Loop**: generated -> encoded -> generated.
9. **F9 — High-Degree Hub**: locality stress.
10. **F10 — Million-Edge Remote Noise**: fixed local region plus remote graph growth.

---

# 31. Release Gates

يجب اجتياز جميع الـGates التالية قبل وصف Law 14 بأنها `IMPLEMENTED / VERIFIED`:

1. **Constitutional Gate** — no cognitive ownership violation.
2. **Functional Gate** — RFC11-T001..T096 mandatory PASS.
3. **Property Gate** — P01..P10 على seeds متعددة.
4. **Adversarial Gate** — provenance, vote inflation, merge storm, bias, race, collision, GC attacks PASS.
5. **Determinism Gate** — stable behavioral digest under same environment/profile.
6. **Phase-I Regression Gate** — existing DGCA suite PASS.
7. **Locality Gate** — remote graph growth cannot trigger remote Assembly scanning.
8. **Structural Bounds Gate** — membership/member/active/pending bounds never violated.
9. **Cognitive Conservation Gate** — structural-only run preserves Edge cognitive digest.
10. **Calibration Evidence Gate** — frozen numeric profile claims require benchmark evidence.

نتائج verification المسموح بها:

- `PASS`
- `CONDITIONAL PASS` — semantics صحيحة لكن calibration/performance تحتاج profile tuning.
- `FAIL` — architecture/implementation violation requires reopening the responsible RFC section.

---

# 32. Complexity & Scaling Verification Contract

يجب أن تجمع B10/B11 على الأقل:

- `EdgesInspected`
- `AssembliesInspected`
- `CandidateCount`
- `Runtime`
- `MemoryDelta`
- `LocalDegree`
- `PhysicalTransmissionCount`

الادعاء الصحيح قبل benchmark:

> **RFC-11 establishes analytical locality and bounded structural-memory semantics. It does not claim empirically verified million-edge scalability until measured.**

---

# 33. Implementation Contract for Antigravity

## 33.1 سلطة الوثيقة

هذه الوثيقة هي **Specification** وليست اقتراحاً. عند التنفيذ:

> **Implement the RFC; do not redesign the architecture.**

## 33.2 ممنوعات التنفيذ

لا يجوز لـAntigravity من تلقاء نفسه:

- إضافة persistent Assembly score.
- إضافة learned parameter.
- إضافة global scan أوglobal optimizer.
- تغيير Law 1–13 semantics لحل مشكلة محلية.
- إدخال Softmax/global normalization.
- جعل internal activity structural evidence.
- حذف Parent Assemblies عند Merge v1.
- إضافة automatic eviction لتجاوز capacity.
- تغيير merge/split rules بناء على similarity heuristic.
- تحويل caches إلى source of truth.
- تغيير policy values بصمت.

## 33.3 إذا وجد تناقضاً

لا يبتكر workaround معماري. يجب أن ينتج Blocker من الشكل:

```text
RFC_BLOCKER
section: RFC-11.x
invariant: RFC11-INV-xxx
problem: ...
why implementation is impossible/ambiguous: ...
minimal reproduction: ...
```

ثم يعاد القرار إلى المراجعة المعمارية.

## 33.4 ترتيب التنفيذ الموصى به

1. Immutable StructuralAssembly records + IDs/versioning.
2. Reconstructible indexes.
3. Provenance/RootExternalEpisode structural-vote intake.
4. Formation candidates + confirmation.
5. Formation commit + duplicate protection.
6. ActiveAssembly working state + pinning.
7. Candidate lookup + support calculation.
8. Local dominance + ambiguity/capacity semantics.
9. Energy/physical-transmission dedup integration.
10. Growth + sanitation.
11. Split.
12. Merge.
13. Retirement + protected-version GC.
14. Structural arbitration + failure atomicity.
15. Static guards / forbidden state checks.
16. Acceptance tests T001..T096.
17. Property tests P01..P10.
18. Benchmarks B01..B18.
19. Phase-I full regression.
20. Release report + behavioral digest.

## 33.5 Delivery Artifacts

Antigravity يجب أن يعيد على الأقل:

- قائمة الملفات created/modified.
- mapping بين modules وRFC sections.
- mapping بين tests وTest IDs.
- results T001..T096.
- property-test results.
- benchmark tables.
- Phase-I regression result.
- deterministic digest.
- selected Law-14 policy profile مع evidence.
- أي deviations أوblocked tests.

---

# 34. Formal Closure Verdict

بعد المراجعة التكاملية:

| البند | الحكم |
|---|---|
| Architectural consistency | PASS |
| Compatibility with Laws 1–13 | PASS |
| Unique necessity of Law 14 | PASS |
| Edge cognitive ownership | PASS |
| New learned persistent scalar | NONE |
| Backpropagation introduced | NO |
| Global optimizer introduced | NO |
| Hidden Assembly belief | NO |
| Analytical locality | PASS BY DESIGN |
| Structural memory boundedness | PASS BY DESIGN |
| Adversarial architecture review | PASS |
| Executable acceptance specification | COMPLETE |
| Empirical implementation verification | PENDING |
| Numeric policy calibration | PENDING |

وعليه:

\[
\boxed{RFC\text{-}11\ — ARCHITECTURALLY\ CLOSED/FROZEN}
\]

\[
\boxed{LAW\ 14\ v1.0\ — SEMANTICALLY\ FROZEN}
\]

\[
\boxed{IMPLEMENTATION\ \&\ CALIBRATION\ — PENDING}
\]

---

# 35. Frozen vs Provisional Registry

## 35.1 FROZEN

- Local Assembly كPrimitive بنيوي.
- Edge-centric membership.
- StructuralAssembly / ActiveAssembly separation.
- Knowledge remains Edge-owned.
- bounded poly-membership.
- no global clustering/subset enumeration/global Assembly scan.
- provenance firewall + RootExternalEpisode dedup.
- overlap/containment semantics.
- energy deduplication.
- seed-normalized support.
- local dominance + ambiguity preservation.
- read-only competition.
- growth/sanitation/split/merge/retirement semantics.
- non-destructive Merge v1.
- deterministic arbitration.
- immutable versions + atomic commit.
- complexity/locality contracts.
- Law 14 normative semantics.
- invariant/test/benchmark contract.

## 35.2 PROVISIONAL / CALIBRATION

- `K_ASM^min = 3`
- `N_ASM^confirm = 5`
- `A_max = 4`
- value of `K_ASM^mem`
- value of `K_ASM^active`
- value of `K_struct^pending`
- runtime optimizations and archival retention policy.

---

# 36. Transition to RFC-12

RFC-11 يوفر الآن substrate رسمي:

```text
Long-Term DGCA Edge Memory
        ↓
Structural Local Assemblies
        ↓
Cue + Context
        ↓
Bounded Active Assemblies
        ↓
Sparse current participants
        ↓
[ RFC-12 ] Sparse Distributed Cognitive Representation
```

السؤال الذي يتركه RFC-11 عمداً لRFC-12:

> **كيف تصبح عدة Active Assemblies، مع النشاط المتناثر داخلها، تمثيلاً معرفياً موزعاً واحداً لمفهوم أوحدث أوحالة، من دون العودة إلى Node واحدة = Concept ومن دون Dense Embeddings؟**

---

# 37. الخلاصة

يضيف RFC-11 إلى DGCA طبقة تنظيم بنيوي محلية يمكنها تجميع العلاقات المستخدمة معاً بصورة متكررة من دون نقل المعرفة من الـEdges. هذه الطبقة versioned، محدودة، قابلة للتداخل، ومتوافقة مع التعلم المحلي والحتمية. أهم حماية في التصميم هي الفصل الصارم بين:

\[
Cognition\ in\ Edges
\]

و:

\[
Organization\ in\ Assemblies
\]

و:

\[
Working\ Activation\ in\ ActiveAssemblies
\]

وبذلك يمكن لPhase II الانتقال إلى التمثيل الموزع وPattern Completion والتوليد الهرمي من substrate أوضح وأكثر قرباً من التنظيم الشبكي الذي نريد محاكاته، من دون إدخال Backpropagation أوDense Embeddings أوذاكرة جماعية مركزية.

**End of RFC-11 v1.0.**
