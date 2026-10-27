"""Ngăn benchmark ghi nhận payload rỗng, HTTP sai nguồn hoặc tính cả prepare."""
import sys
from pathlib import Path

import pytest
import requests
from bson import ObjectId
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import benchmark
from services.cache_service import CacheService


def test_prepare_and_validation_are_not_timed(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(benchmark.time, "perf_counter", lambda: clock[0])
    def prepare():
        clock[0] += 5
    def read():
        clock[0] += .003
        return {"items": [1, 2, 3]}
    def validate(value):
        clock[0] += 7
        return value
    stats, samples = benchmark._paired({"mongodb": read, "redis": read}, {"items": [1, 2, 3]}, 3, 1,
                                       {"mongodb": prepare, "redis": prepare},
                                       {"mongodb": validate, "redis": validate})
    assert stats["mongodb"]["count"] == stats["redis"]["count"] == 3
    assert all(value == pytest.approx(3) for values in samples.values() for value in values)


def test_different_payload_aborts_measurement():
    with pytest.raises(benchmark.BenchmarkError, match="Payload"):
        benchmark._paired({"mongodb": lambda: {"items": [1]}, "redis": lambda: {"items": []}},
                          {"items": [1]}, 1, 0)


def test_p95_uses_nearest_rank():
    assert benchmark._stats([1, 2, 3, 4, 5, 6, 7])["p95"] == 7


def test_native_mongo_and_hash_decode_produce_identical_dto():
    doc = {"_id": ObjectId(), "author": ObjectId(), "title": "Bài tiếng Việt", "tags": ["dữ liệu"],
           "created_at": datetime.now(timezone.utc), "seed_version": 3}
    mapping = CacheService._article_mapping(str(doc["_id"]), doc)
    decoded = benchmark.article_model.to_dict(CacheService._decode_hash(mapping))
    assert benchmark._article_payload(doc) == decoded


class Response:
    def __init__(self, source="cache", status=200):
        self.source, self.status = source, status
    def raise_for_status(self):
        if self.status != 200:
            raise requests.HTTPError("HTTP error")


@pytest.mark.parametrize("source,status", [("database", 200), ("cache", 500)])
def test_http_invalid_source_or_status_is_rejected(source, status):
    with pytest.raises((benchmark.BenchmarkError, requests.HTTPError)):
        benchmark._validate_http((Response(source, status), {"success": True, "source": source, "data": {}}), "cache")
