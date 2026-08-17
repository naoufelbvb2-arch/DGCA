"""
اختبارات الخطوة 11 — مُرمِّز الكود.
هذه الاختبارات جزء من المواصفة. لا تُعدَّل لتمرير الكود.
"""
import pytest

from dgca.encoder import QUANTITY, TEXT, CodeEncoder, encode_number, feed

SAMPLE = '''
def parse_config(path, strict=False):
    if not path:
        return None
    return load(path, timeout=30)
'''


def _enc(src, module="m"):
    return CodeEncoder(module).encode(src)


class FakeGraph:
    """شبكة صورية — تلتقط ما يصلها بلا منطق."""

    def __init__(self):
        self.simultaneous = []
        self.sequences = []

    def observe(self, signals, context=None):
        self.simultaneous.append((signals, context))

    def observe_sequence(self, steps, context=None):
        self.sequences.append((steps, context))


# ─────────────────── الأرقام — ثلاث فئات
def test_symbolic_numbers_stay_text():
    for v in (0, 1, 2, -1, -2):
        assert encode_number(v) == (TEXT, str(v)), v


def test_quantities_become_logarithmic_buckets():
    assert encode_number(3) == (QUANTITY, "1e0")
    assert encode_number(30) == (QUANTITY, "1e1")
    assert encode_number(255) == (QUANTITY, "1e2")
    assert encode_number(1024) == (QUANTITY, "1e3")
    assert encode_number(0.001) == (QUANTITY, "1e-3")


def test_neighbouring_magnitudes_share_a_bucket():
    """1024 و2048 في المجال نفسه ⟹ جوار مشترك ⟹ ق9 تعمل عليهما."""
    assert encode_number(1024) == encode_number(2048)
    assert encode_number(100) != encode_number(1000)


def test_incidental_numbers_are_dropped():
    assert encode_number(0.7853981633974483) is None
    assert encode_number(3.14159265) is None


def test_booleans_are_not_numbers():
    assert encode_number(True) is None
    assert encode_number(False) is None


# ─────────────────── الرمز إلى حلقات
def test_definition_is_simultaneous_with_name_as_head():
    eps = _enc(SAMPLE)
    first = eps[0]
    assert first.kind == "simultaneous"
    assert first.signals[0] == (TEXT, "parse_config"), "اسم الدالة هو الرأس"
    assert first.context == "parse_config"


def test_parameters_become_attributes():
    signals = _enc(SAMPLE)[0].signals
    syms = [s for _, s in signals]
    assert "parse_config.path" in syms
    assert "parse_config.strict" in syms


def test_statements_become_sequences():
    eps = _enc(SAMPLE)
    assert [e.kind for e in eps[1:]] == ["sequence", "sequence", "sequence"]


def test_statement_order_is_preserved():
    ret = _enc(SAMPLE)[-1]
    flat = [s for step in ret.steps for _, s in step]
    assert flat == ["kw.return", "load", "parse_config.path", "timeout", "1e1"]


def test_each_step_holds_exactly_one_signal():
    for ep in _enc(SAMPLE):
        if ep.kind == "sequence":
            assert all(len(step) == 1 for step in ep.steps)


# ─────────────────── النطاق — علاج جزئي لربط المتغيرات
def test_locals_are_scoped_by_function():
    src = '''
def a(x):
    return x
def b(x):
    return x
'''
    eps = _enc(src)
    syms = {s for e in eps for step in e.steps for _, s in step}
    assert "a.x" in syms and "b.x" in syms


def test_globals_stay_unscoped():
    src = '''
def a(x):
    return helper(x)
'''
    syms = {s for e in _enc(src) for step in e.steps for _, s in step}
    assert "helper" in syms, "الاسم غير المحلي يبقى عامّياً"
    assert "a.helper" not in syms


def test_loop_target_is_local():
    src = '''
def a(items):
    for item in items:
        use(item)
'''
    syms = {s for e in _enc(src) for step in e.steps for _, s in step}
    assert "a.item" in syms


# ─────────────────── السياق
def test_context_is_the_enclosing_function():
    src = '''
def outer(a):
    return a
def other(b):
    return b
'''
    contexts = {e.context for e in _enc(src)}
    assert contexts == {"outer", "other"}


def test_module_level_uses_module_context():
    assert _enc("x = load()", module="mymod")[0].context == "mymod"


# ─────────────────── ما يُطرح
def test_string_literals_are_dropped():
    syms = {s for e in _enc('def f():\n    log("connection failed")\n')
            for step in e.steps for _, s in step}
    assert not any("connection" in s or "failed" in s for s in syms)


def test_structural_punctuation_never_becomes_a_node():
    syms = {s for e in _enc(SAMPLE)
            for step in (e.steps or [])
            for _, s in step} | {s for e in _enc(SAMPLE) for _, s in (e.signals or [])}
    for junk in ("(", ")", ":", ",", "{", "}"):
        assert junk not in syms


def test_keywords_are_prefixed():
    syms = {s for e in _enc(SAMPLE) for step in e.steps for _, s in step}
    assert "kw.if" in syms and "kw.return" in syms


def test_operators_are_prefixed():
    syms = {s for e in _enc("def f(a, b):\n    return a + b\n")
            for step in e.steps for _, s in step}
    assert "op.+" in syms


# ─────────────────── التغذية
def test_feed_routes_to_the_right_channel():
    g = FakeGraph()
    sent = feed(g, SAMPLE, "m")
    assert sent == len(g.simultaneous) + len(g.sequences)
    assert len(g.simultaneous) == 1
    assert len(g.sequences) == 3


def test_feed_never_sends_a_single_step_sequence():
    g = FakeGraph()
    feed(g, SAMPLE, "m")
    assert all(len(steps) >= 2 for steps, _ in g.sequences)


def test_encoder_is_deterministic():
    a = _enc(SAMPLE)
    b = _enc(SAMPLE)
    assert [(e.kind, e.context, e.signals, e.steps) for e in a] == \
           [(e.kind, e.context, e.signals, e.steps) for e in b]


def test_encoder_handles_real_source_without_crashing():
    import pathlib
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    eps = _enc(src, "self")
    assert len(eps) > 20
    assert all(e.kind in ("simultaneous", "sequence") for e in eps)


def test_syntax_error_is_reported_not_swallowed():
    with pytest.raises(SyntaxError):
        _enc("def broken(:\n")
