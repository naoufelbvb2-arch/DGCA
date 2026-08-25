"""
مُرمِّز الحواس الرمزية: اللغة الطبيعية، الأرقام، والكود البرمجي (RFC-04: The Symbolic Sensory Encoder).

المبدأ الحاكم:
«المُرمِّز حاسّة مُصممة لا شبكة مُدربة؛ يُصنِّف ولا يُدرِّب، ويستخرج البنية ولا يُدخل الانتشار الخلفي من الباب الخلفي».
"""
import ast
import math
from dataclasses import dataclass, field
from typing import ClassVar, Literal

TEXT = "text"
QUANTITY = "quantity"

_MAX_SIGNIFICANT = 4
_SYMBOLIC_MAX = 2
MAX_SEQUENCE_STEPS = 16

_OPS = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
    ast.Mod: "%", ast.Pow: "**", ast.LShift: "<<", ast.RShift: ">>", ast.BitOr: "|",
    ast.BitXor: "^", ast.BitAnd: "&", ast.MatMult: "@",
    ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">",
    ast.GtE: ">=", ast.Is: "is", ast.IsNot: "is not", ast.In: "in", ast.NotIn: "not in",
    ast.And: "and", ast.Or: "or", ast.Not: "not",
    ast.UAdd: "+", ast.USub: "-", ast.Invert: "~",
}

_STMT_KEYWORDS = {
    ast.Return: "return", ast.If: "if", ast.For: "for", ast.AsyncFor: "for",
    ast.While: "while", ast.With: "with", ast.AsyncWith: "with", ast.Try: "try",
    ast.Raise: "raise", ast.Assert: "assert", ast.Import: "import",
    ast.ImportFrom: "import", ast.Global: "global", ast.Nonlocal: "nonlocal",
    ast.Pass: "pass", ast.Break: "break", ast.Continue: "continue",
    ast.Delete: "del", ast.Match: "match",
}
_ASSIGNMENTS = (ast.Assign, ast.AugAssign, ast.AnnAssign)
_BODY_FIELDS = ("body", "orelse", "finalbody", "handlers", "cases")

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "been", "being", "am",
    "of", "that", "this", "these", "those",
}

LABEL_PREFIXES = {
    "flight", "flight_", "error", "line", "v", "version", "port",
    "iphone", "gate", "room", "model", "step", "page", "route", "ch", "app", "code",
}


# ─────────────────────────────────────────────────── تصنيف الأرقام
def _significant(value: float) -> int:
    digits = repr(abs(value)).split("e")[0].replace(".", "")
    return len(digits.strip("0"))


def encode_number(value):
    """تصنيف الأرقام المتوافق مع Step 11: رمز اصطلاحي، كمّية لوغاريتمية، أو عارضٌ يُطرح."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        if _significant(value) > _MAX_SIGNIFICANT:
            return None
    if float(value).is_integer() and abs(value) <= _SYMBOLIC_MAX:
        return TEXT, str(int(value))
    return QUANTITY, f"1e{math.floor(math.log10(abs(value)))}"


# ─────────────────────────────────────────────────── كائن الحلقة المعيارية
@dataclass
class SensoryEpisode:
    """حلقة إدراكية معيارية جاهزة للاستهلاك المباشر من نواة DGCA."""

    kind: Literal["simultaneous", "sequence"]
    context: str | None = None
    signals: list[tuple[str, str]] = field(default_factory=list)
    steps: list[list[tuple[str, str]]] = field(default_factory=list)
    structural_weight: float = 0.0
    valence: float = 0.0
    contradictions: list[tuple[str, str]] = field(default_factory=list)


Episode = SensoryEpisode


# ─────────────────────────────────────────────────── خط معالجة المقادير والأعداد (RFC-01 & RFC-04)
class QuantityNormalizer:
    """فرز الأرقام وتوجيهها: عزل الأرقام الاسمية في text وربط الكميات الفطرية 0..9 في quantity."""

    _uid_counters: ClassVar[dict[str, int]] = {}

    @classmethod
    def get_instance_id(cls, entity: str) -> str:
        cls._uid_counters[entity] = cls._uid_counters.get(entity, 0) + 1
        return f"inst:{entity}_{cls._uid_counters[entity]}"

    @classmethod
    def reset_uids(cls) -> None:
        cls._uid_counters.clear()

    @staticmethod
    def is_label(word: str, prev_word: str | None = None) -> bool:
        w_lower = word.lower()
        if prev_word and prev_word.lower() in LABEL_PREFIXES:
            return True
        for prefix in LABEL_PREFIXES:
            if w_lower.startswith(prefix) and len(w_lower) > len(prefix):
                rest = w_lower[len(prefix):].lstrip("-_")
                if rest.isdigit():
                    return True
        return False

    @classmethod
    def normalize(cls, token: str, prev_token: str | None = None) -> tuple[str, str] | None:
        token_clean = token.strip().replace(",", "")
        if cls.is_label(token_clean, prev_token):
            if prev_token and prev_token.lower() in LABEL_PREFIXES:
                return TEXT, f"{prev_token.lower()}_{token_clean.lower()}"
            return TEXT, token_clean.lower()

        if token_clean.isdigit():
            val = int(token_clean)
            if 0 <= val <= 9:
                return QUANTITY, str(val)
            return TEXT, str(val)

        try:
            val_f = float(token_clean)
            if val_f.is_integer() and 0 <= int(val_f) <= 9:
                return QUANTITY, str(int(val_f))
            return TEXT, str(token_clean)
        except ValueError:
            return None


# ─────────────────────────────────────────────────── خط معالجة النصوص الطبيعية (EnglishTextPipeline)
class EnglishTextPipeline:
    """خط معالجة النصوص الطبيعية الإنجليزية وفق معمارية English Encoder v2."""

    def __init__(self):
        from dgca.encoding.english import EnglishEncoderV2
        self._v2_encoder = EnglishEncoderV2()
        self.normalizer = QuantityNormalizer()

    def process(self, text: str, context: str | None = None) -> list[SensoryEpisode]:
        cleaned = text.strip()
        if not cleaned:
            return []

        res = self._v2_encoder.analyze(cleaned, source_ref=context or "")
        if res.episodes:
            return list(res.episodes)

        # Standalone descriptive noun phrase fallback (e.g. "The small black dog")
        from dgca.encoding.english.emitter import _emit_np_episodes
        from dgca.encoding.english.noun_phrases import parse_noun_phrase
        from dgca.encoding.english.tokenize import tokenize

        toks = tokenize(cleaned)
        np_view, _ = parse_noun_phrase(toks)
        if np_view is not None:
            eps = _emit_np_episodes(np_view, context=context)
            if eps:
                return eps
            return [SensoryEpisode(kind="simultaneous", context=context, signals=[(TEXT, np_view.head_lemma)])]

        return []


# ─────────────────────────────────────────────────── خط معالجة الكود الهرمي (CodeSensoryPipeline)
class CodeSensoryPipeline:
    """خط معالجة الكود البرمجي وفق قواعد RFC-04:
    - الترميز بالأدوار البنيوية (param:pos_k).
    - تكييف الكلمات المفتاحية ومنع تضخم المركز.
    - حقن البروز البنيوي الفطري (structural_weight = 0.80) لتعريفات الدوال والفئات.
    - حارس طول التتابع (MAX_SEQUENCE_STEPS = 16).
    """

    def __init__(self, use_structural_roles: bool = True):
        self.use_structural_roles = use_structural_roles

    def process(self, source_code: str, module: str = "module") -> list[SensoryEpisode]:
        tree = ast.parse(source_code)
        episodes: list[SensoryEpisode] = []
        self._walk_node(tree.body, None, module, episodes)
        return episodes

    def _walk_node(self, body, scope, module: str, out: list[SensoryEpisode]) -> None:
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self._handle_definition(stmt, scope, module, out)
                continue
            self._handle_statement(stmt, scope, module, out)

    def _handle_definition(self, stmt, scope, module: str, out: list[SensoryEpisode]) -> None:
        name = stmt.name
        if isinstance(stmt, ast.ClassDef):
            inner = (name, set())
            signals = [(TEXT, name)]
            for base in stmt.bases:
                signals += self._atoms(base, scope)
            out.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=name,
                    signals=signals,
                    structural_weight=0.80,
                )
            )
            self._walk_node(stmt.body, inner, module, out)
        else:
            args = self._all_args(stmt.args)
            if self.use_structural_roles:
                signals = [(TEXT, name)] + [
                    (TEXT, f"param:pos_{idx}") for idx in range(len(args))
                ]
            else:
                inner_scope = (name, self._locals_of(stmt))
                signals = [(TEXT, name)] + [
                    (TEXT, f"{name}.{a.arg}") for a in args
                ]
            out.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=name,
                    signals=signals,
                    structural_weight=0.80,
                )
            )
            inner_scope = (name, self._locals_of(stmt))
            self._walk_node(stmt.body, inner_scope, module, out)

    def _handle_statement(self, stmt, scope, module: str, out: list[SensoryEpisode]) -> None:
        context = scope[0] if scope else module
        atoms = self._statement_atoms(stmt, scope)
        if not atoms:
            return

        # حارس طول التتابع MAX_SEQUENCE_STEPS = 16
        if len(atoms) > MAX_SEQUENCE_STEPS:
            atoms = atoms[:MAX_SEQUENCE_STEPS]

        if len(atoms) >= 2:
            out.append(
                SensoryEpisode(
                    kind="sequence",
                    context=context,
                    steps=[[a] for a in atoms],
                )
            )
        elif atoms:
            out.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=context,
                    signals=list(atoms),
                )
            )

        for name in _BODY_FIELDS:
            nested = getattr(stmt, name, None)
            if isinstance(nested, list):
                inner = [s for s in nested if isinstance(s, ast.stmt)]
                self._walk_node(inner, scope, module, out)
                for handler in (n for n in nested if not isinstance(n, ast.stmt)):
                    self._walk_node(getattr(handler, "body", []), scope, module, out)

    def _statement_atoms(self, stmt, scope) -> list:
        head = _STMT_KEYWORDS.get(type(stmt))
        own = []
        for name, value in ast.iter_fields(stmt):
            if name in _BODY_FIELDS:
                continue
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, ast.AST):
                    own += self._atoms(item, scope)
        if isinstance(stmt, _ASSIGNMENTS):
            targets = getattr(stmt, "targets", None) or [stmt.target]
            lhs = [a for t in targets for a in self._atoms(t, scope)]
            return lhs + own[len(lhs):]
        return ([(TEXT, f"kw.{head}")] if head else []) + own

    def _atoms(self, node, scope) -> list:
        if node is None:
            return []
        if isinstance(node, ast.Name):
            if self.use_structural_roles and scope and node.id in scope[1]:
                # تعيين موضع بنيوي للمعاملات أو الهدف
                return [(TEXT, f"param:{node.id}")]
            if scope and node.id in scope[1]:
                return [(TEXT, f"{scope[0]}.{node.id}")]
            return [(TEXT, node.id)]
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, bytes)):
                return []
            if node.value is None or isinstance(node.value, bool):
                return [(TEXT, str(node.value))]
            norm = QuantityNormalizer.normalize(str(node.value))
            if norm:
                return [norm]
            got = encode_number(node.value)
            return [got] if got else []
        if isinstance(node, ast.Attribute):
            return self._atoms(node.value, scope) + [(TEXT, node.attr)]
        if isinstance(node, ast.Call):
            out = self._atoms(node.func, scope)
            for arg in node.args:
                out += self._atoms(arg, scope)
            for kw in node.keywords:
                if kw.arg:
                    out.append((TEXT, kw.arg))
                out += self._atoms(kw.value, scope)
            return out
        if isinstance(node, ast.BinOp):
            return self._atoms(node.left, scope) + self._op(node.op) + self._atoms(node.right, scope)
        if isinstance(node, ast.UnaryOp):
            return self._op(node.op) + self._atoms(node.operand, scope)
        if isinstance(node, ast.BoolOp):
            out = self._atoms(node.values[0], scope)
            for value in node.values[1:]:
                out += self._op(node.op) + self._atoms(value, scope)
            return out
        if isinstance(node, ast.Compare):
            out = self._atoms(node.left, scope)
            for op, right in zip(node.ops, node.comparators, strict=False):
                out += self._op(op) + self._atoms(right, scope)
            return out
        if isinstance(node, ast.alias):
            return [(TEXT, node.asname or node.name.split(".")[0])]
        out = []
        for child in ast.iter_child_nodes(node):
            out += self._atoms(child, scope)
        return out

    @staticmethod
    def _op(op) -> list:
        symbol = _OPS.get(type(op))
        return [(TEXT, f"op.{symbol}")] if symbol else []

    @staticmethod
    def _locals_of(fn) -> set[str]:
        names = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                names.add(node.name)
        return names

    @staticmethod
    def _all_args(args) -> list:
        got = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        return got + [a for a in (args.vararg, args.kwarg) if a is not None]


# ─────────────────────────────────────────────────── المُنسق العام (MasterSymbolicEncoder)
class MasterSymbolicEncoder:
    """المُنسق العام للحواس الرمزية في معمارية DGCA."""

    def __init__(self):
        self.text_pipeline = EnglishTextPipeline()
        self.code_pipeline = CodeSensoryPipeline()
        self.quantity_normalizer = QuantityNormalizer()
        self._audio_pipeline = None

    @property
    def audio_pipeline(self):
        if self._audio_pipeline is None:
            from .audio import AudioSensoryPipeline

            self._audio_pipeline = AudioSensoryPipeline()
        return self._audio_pipeline

    def encode_text(self, text: str, context: str | None = None) -> list[SensoryEpisode]:
        """معالجة النصوص الطبيعية الإنجليزية وتحويلها لحلقات معيارية."""
        return self.text_pipeline.process(text, context)

    def encode_code(self, source_code: str, module: str = "module") -> list[SensoryEpisode]:
        """معالجة كود بايثون القياسي واستخراج الهرمية والأدوار البنيوية."""
        return self.code_pipeline.process(source_code, module)

    def encode_audio(
        self,
        waveform: list[float],
        paired_text: str | None = None,
        context: str | None = None,
        sample_rate: int = 8000,
    ) -> list[SensoryEpisode]:
        """معالجة الإشارات والموجات الصوتية واستخراج البصمات الرنينية والجهر (RFC-08)."""
        return self.audio_pipeline.process_audio(
            waveform, paired_text=paired_text, context=context, sample_rate=sample_rate
        )

    def feed_to_graph(self, graph, episodes: list[SensoryEpisode]) -> int:
        """تغذية الحلقات إلى محرك الرسم البياني مع تسجيل التناقضات والبروز."""
        for ep in episodes:
            for src, dst in ep.contradictions:
                graph._link_contradiction(src, dst)

            if ep.kind == "simultaneous":
                if ep.signals:
                    graph.observe(
                        ep.signals,
                        context=ep.context,
                        valence=ep.valence,
                        structural_weight=ep.structural_weight,
                    )
            else:
                if ep.steps:
                    graph.observe_sequence(
                        ep.steps,
                        context=ep.context,
                        valence=ep.valence,
                        structural_weight=ep.structural_weight,
                    )
        return len(episodes)


# ─────────────────────────────────────────────────── مُرمِّز الكود القديم للتوافقية مع Step 11
class CodeEncoder:
    """يحوّل مصدر بايثون إلى حلقات إدراكية. متوافق 100% مع اختبارات Step 11."""

    def __init__(self, module: str = "module"):
        self.module = module

    @staticmethod
    def _locals_of(fn) -> set[str]:
        names = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                names.add(node.name)
        return names

    def _name(self, ident: str, scope) -> tuple:
        if scope and ident in scope[1]:
            return TEXT, f"{scope[0]}.{ident}"
        return TEXT, ident

    def _atoms(self, node, scope) -> list:
        if node is None:
            return []
        if isinstance(node, ast.Name):
            return [self._name(node.id, scope)]
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, bytes)):
                return []
            if node.value is None or isinstance(node.value, bool):
                return [(TEXT, str(node.value))]
            got = encode_number(node.value)
            return [got] if got else []
        if isinstance(node, ast.Attribute):
            return self._atoms(node.value, scope) + [(TEXT, node.attr)]
        if isinstance(node, ast.Call):
            out = self._atoms(node.func, scope)
            for arg in node.args:
                out += self._atoms(arg, scope)
            for kw in node.keywords:
                if kw.arg:
                    out.append((TEXT, kw.arg))
                out += self._atoms(kw.value, scope)
            return out
        if isinstance(node, ast.BinOp):
            return self._atoms(node.left, scope) + self._op(node.op) + self._atoms(node.right, scope)
        if isinstance(node, ast.UnaryOp):
            return self._op(node.op) + self._atoms(node.operand, scope)
        if isinstance(node, ast.BoolOp):
            out = self._atoms(node.values[0], scope)
            for value in node.values[1:]:
                out += self._op(node.op) + self._atoms(value, scope)
            return out
        if isinstance(node, ast.Compare):
            out = self._atoms(node.left, scope)
            for op, right in zip(node.ops, node.comparators, strict=False):
                out += self._op(op) + self._atoms(right, scope)
            return out
        if isinstance(node, ast.alias):
            return [(TEXT, node.asname or node.name.split(".")[0])]
        out = []
        for child in ast.iter_child_nodes(node):
            out += self._atoms(child, scope)
        return out

    @staticmethod
    def _op(op) -> list:
        symbol = _OPS.get(type(op))
        return [(TEXT, f"op.{symbol}")] if symbol else []

    def _statement_atoms(self, stmt, scope) -> list:
        head = _STMT_KEYWORDS.get(type(stmt))
        own = []
        for name, value in ast.iter_fields(stmt):
            if name in _BODY_FIELDS:
                continue
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, ast.AST):
                    own += self._atoms(item, scope)
        if isinstance(stmt, _ASSIGNMENTS):
            targets = getattr(stmt, "targets", None) or [stmt.target]
            lhs = [a for t in targets for a in self._atoms(t, scope)]
            return lhs + [(TEXT, "kw.assign")] + own[len(lhs):]
        return ([(TEXT, f"kw.{head}")] if head else []) + own

    def _emit(self, atoms, context, out) -> None:
        if len(atoms) >= 2:
            out.append(SensoryEpisode("sequence", context, steps=[[a] for a in atoms]))
        elif atoms:
            out.append(SensoryEpisode("simultaneous", context, signals=list(atoms)))

    def _walk(self, body, scope, out) -> None:
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self._definition(stmt, scope, out)
                continue
            self._emit(self._statement_atoms(stmt, scope), self._context(scope), out)
            for name in _BODY_FIELDS:
                nested = getattr(stmt, name, None)
                if isinstance(nested, list):
                    inner = [s for s in nested if isinstance(s, ast.stmt)]
                    self._walk(inner, scope, out)
                    for handler in (n for n in nested if not isinstance(n, ast.stmt)):
                        self._walk(getattr(handler, "body", []), scope, out)

    def _definition(self, stmt, scope, out) -> None:
        name = stmt.name
        if isinstance(stmt, ast.ClassDef):
            inner, signals = scope, [(TEXT, name)]
            for base in stmt.bases:
                signals += self._atoms(base, scope)
        else:
            inner = (name, self._locals_of(stmt))
            signals = [(TEXT, name)] + [
                self._name(a.arg, inner) for a in self._all_args(stmt.args)
            ]
        out.append(SensoryEpisode("simultaneous", name, signals=signals))
        self._walk(stmt.body, inner, out)

    @staticmethod
    def _all_args(args) -> list:
        got = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        return got + [a for a in (args.vararg, args.kwarg) if a is not None]

    def _context(self, scope) -> str:
        return scope[0] if scope else self.module

    def encode(self, source: str) -> list[SensoryEpisode]:
        episodes: list[SensoryEpisode] = []
        self._walk(ast.parse(source).body, None, episodes)
        return episodes


def feed(graph, source: str, module: str = "module") -> int:
    episodes = CodeEncoder(module).encode(source)
    for ep in episodes:
        if ep.kind == "simultaneous":
            graph.observe(ep.signals, context=ep.context)
        else:
            graph.observe_sequence(ep.steps, context=ep.context)
    return len(episodes)
