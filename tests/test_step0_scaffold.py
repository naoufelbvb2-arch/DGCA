"""اختبارات الخطوة ٠ — تأسيس المستودع."""
import importlib


def test_package_and_config_import():
    assert importlib.import_module("dgca") is not None
    assert importlib.import_module("dgca.config") is not None


def test_regions_has_four_entries():
    from dgca.config import REGIONS
    assert len(REGIONS) == 4


def test_law_c_max():
    from dgca.config import Law
    assert Law.C_MAX == 1.0
