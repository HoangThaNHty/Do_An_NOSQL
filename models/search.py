"""Tìm gần đúng tiếng Việt cho tập bài nhỏ, không cần dịch vụ bên ngoài."""
import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache


@lru_cache(maxsize=4096)
def normalize(text):
    text = unicodedata.normalize("NFD", str(text).casefold().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


STOP_WORDS = set("va ve cua cho tai mot nhung cach de gi la trong voi nhu the nao cac tim bai viet toi muon xem".split())
# Các nhóm nghĩa có giới hạn, không phải tìm kiếm ngữ nghĩa bằng AI.
CONCEPTS = [
    ("container", "logistics", "van chuyen", "van tai", "hang hoa", "cang bien", "tau bien", "chuoi cung ung"),
    ("thien van", "vu tru", "tinh van", "thien ha", "ngam sao", "kinh thien van"),
    ("may chu", "trung tam du lieu", "phong may", "server"),
    ("lap trinh", "ma nguon", "javascript", "phan mem", "ung dung web"),
    ("bo nho dem", "cache", "redis", "cache aside"),
    ("nau an", "vao bep", "bua an", "am thuc", "che bien"),
    ("san van dong", "san dau", "khan dai", "bong da", "bong bau duc"),
]


def contains_phrase(text, phrase):
    return f" {phrase} " in f" {text} "


@lru_cache(maxsize=32768)
def similarity(token, word):
    if token == word:
        return 1.0
    if len(token) >= 3 and word.startswith(token):
        return 0.9
    if min(len(token), len(word)) < 4 or abs(len(token) - len(word)) > 2:
        return 0.0
    ratio = SequenceMatcher(None, token, word).ratio()
    return ratio if ratio >= 0.78 else 0.0


def relevance(doc, keyword):
    query = normalize(keyword[:120])
    tokens = list(dict.fromkeys(t for t in query.split() if t not in STOP_WORDS))[:12]
    if not tokens:
        return 0
    tags = doc.get("tags") or []
    fields = [(normalize(doc.get("title", "")), 6),
              (normalize(" ".join(tags) if isinstance(tags, list) else tags), 4),
              (normalize(doc.get("summary", "")), 3),
              (normalize(doc.get("content", "")), 1)]
    score, covered = 0.0, 0
    for token in tokens:
        matches = [max((similarity(token, word) for word in set(text.split())), default=0) * weight
                   for text, weight in fields]
        best = max(matches)
        covered += best > 0
        score += best
    direct = covered == len(tokens)
    related = 0
    requested_concept = False
    prominent = " ".join(text for text, weight in fields if weight >= 3)
    raw_prominent = re.sub(r"[^\w]+", " ", unicodedata.normalize("NFC", " ".join(
        str(doc.get(k, "")) for k in ("title", "summary", "tags"))).casefold())
    for group in CONCEPTS:
        if any(contains_phrase(query, alias) for alias in group):
            requested_concept = True
            for alias in group:
                if alias == "van tai":
                    related += contains_phrase(raw_prominent, "vận tải") or contains_phrase(raw_prominent, "van tai")
                else:
                    related += contains_phrase(prominent, alias)
    # Ví dụ "vận tải" không nên khớp bài thiên "văn" chỉ vì cũng có chữ "tại".
    if requested_concept and not related:
        return 0
    if not direct and not related:
        return 0
    if contains_phrase(fields[0][0], query):
        score += 40
    return score + (20 if direct else 0) + min(related, 4) * 2
