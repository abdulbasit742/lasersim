"""Validate the report generator."""
from report import build_html
from full_system import run_full_system


def test_html_contains_key_sections():
    html = build_html(run_full_system())
    assert "<table" in html
    assert "Abstract" in html
    assert "B-integral" in html
    assert "1280 mJ" in html


def test_html_is_nontrivial():
    html = build_html(run_full_system())
    assert len(html) > 1500
