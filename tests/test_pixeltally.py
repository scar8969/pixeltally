"""B11 privacy-analytics — tests. Run: pytest test_pixeltally.py"""
import sys, os

import pytest
flask_ok = True
try:
    import flask_sqlalchemy
except ImportError:
    flask_ok = False

def test_ip_hash_deterministic():
    from privacy_analytics.analytics.tracker import ip_hash
    assert ip_hash("1.2.3.4") == ip_hash("1.2.3.4")
    assert ip_hash("1.2.3.4") != ip_hash("5.6.7.8")

def test_ip_hash_no_raw():
    from privacy_analytics.analytics.tracker import ip_hash
    assert "1.2.3.4" not in ip_hash("1.2.3.4")

def test_geo_unknown():
    from privacy_analytics.analytics.geo import country
    assert country("1.2.3.4") == "unknown"  # no mmdb installed

@pytest.mark.skipif(not flask_ok, reason="flask-sqlalchemy not installed")
def test_rollup_empty():
    from privacy_analytics.analytics.agg import rollup
    assert rollup(999, 7) == []
