import pytest

from app.services.document_extractor import extract_text, is_supported, parse_header


SAMPLE = """document_id: spacex-dragon-001
title: Dragon Spacecraft Overview
category: vehicle
vehicle: Dragon

Dragon is a SpaceX spacecraft family: cargo and crew.
"""


def test_parse_header_reads_block_until_blank_line():
    assert parse_header(SAMPLE) == {
        "document_id": "spacex-dragon-001",
        "title": "Dragon Spacecraft Overview",
        "category": "vehicle",
        "vehicle": "Dragon",
    }


def test_parse_header_without_header_returns_empty():
    assert parse_header("Just body text.\n\nMore text: with a colon.") == {}


def test_parse_header_ignores_colons_in_body():
    assert "Dragon is a SpaceX spacecraft family" not in parse_header(SAMPLE)


def test_is_supported():
    assert is_supported("a.txt")
    assert is_supported("B.MD")
    assert not is_supported("spacex_rag_demo_docs.zip")


def test_extract_text_strips_bom():
    assert extract_text("a.txt", "﻿hello".encode("utf-8")) == "hello"


def test_extract_text_rejects_unsupported():
    with pytest.raises(ValueError):
        extract_text("docs.zip", b"PK")
