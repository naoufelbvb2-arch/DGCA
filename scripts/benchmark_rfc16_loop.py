"""
DGCA — RFC-16 v1.0 Authoritative Benchmark Suite (RFC16-B01 .. RFC16-B12).
Executes all 12 frozen benchmark families with high-resolution monotonic timing,
min, median, p95, max, mean, stdev, operation counters, and 30 repeated trials.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.audit_rfc16_benchmarks import (
    run_comprehensive_audit,
)

if __name__ == "__main__":
    run_comprehensive_audit()
