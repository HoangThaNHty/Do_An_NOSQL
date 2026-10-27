"""Hành vi xếp hạng gần đúng; không phụ thuộc DB hay dịch vụ tìm kiếm ngoài."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.search import normalize, relevance

CONTAINER = {"title": "Hành trình container từ cảng biển đến kho hàng", "summary": "Tìm hiểu vận chuyển hàng hóa và logistics.",
             "content": "Tàu đưa container tới cảng rồi chuyển lên xe.", "tags": ["container", "logistics"]}


@pytest.mark.parametrize("query", ["Container", "contaner", "CONTAINR", "cang bien", "biển cảng", "vận tải", "hàng hóa", "van chuyen"])
def test_vietnamese_partial_typo_and_topic_queries(query):
    assert relevance(CONTAINER, query) > 0


def test_irrelevant_and_punctuation_do_not_match_everything():
    for query in ("zz_no_result_qa", ".*", "[", "nấu ăn"):
        assert relevance(CONTAINER, query) == 0


def test_title_matches_rank_above_body_only():
    other = {"title": "Nhật ký công việc", "content": "container", "summary": "", "tags": []}
    assert relevance(CONTAINER, "container") > relevance(other, "container")


def test_normalize_combining_vietnamese_and_whitespace():
    assert normalize("  ĐIỆN   THOẠI ") == "dien thoai"


def test_concept_avoids_short_vietnamese_word_collisions():
    astronomy = {"title": "Quan sát thiên văn tại một ngôi nhà", "content": "Ngắm sao trong đêm.", "tags": []}
    assert relevance(astronomy, "vận tải") == 0
