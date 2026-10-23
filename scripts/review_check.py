#!/usr/bin/env python3
"""Review records for the Bridge Kids locale pages.

review.json has one record per page and locale. source_hash is
"sha256:" plus the hex SHA-256 of that page's visible text after NFC
normalization, newline conversion to LF, and a trim of the ends.

Visible text is the body's text nodes. Script, style, and head content
are left out. HTML comments are not text. No other whitespace is
collapsed, so the hash tracks the published wording rather than a
renderer's layout.

The default run recomputes every hash. It fails on a missing author,
a reviewer who is the same identity as the author, a human_verified
record whose reviewer is not human:<name>, a bad hash, or a record
that is not in the locale × page matrix. Unreviewed pages are
reported and do not fail this mode.

--release is the later gate. It also fails unreviewed and flagged
pages. Legal pages (privacy, children, support, terms) pass only as
human_verified, so legal text is never machine-only for release.
--write refreshes source_hash and adds any missing record as
unreviewed. It does not change an existing review.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from site_map import LEGAL_PAGE_IDS, LOCALE_CODES, PAGE_IDS  # noqa: E402

ROOT = SCRIPT_DIR.parent
REVIEW_PATH = ROOT / "review.json"
REVIEW_VERSION = 1

AI_AUTHORS = frozenset(
    {"ai-product-lead", "ai-ja-reviewer", "ai-qa", "ai-designer"}
)
STATUSES = frozenset(
    {"unreviewed", "ai_reviewed", "flagged", "ai_verified", "human_verified"}
)
HUMAN_IDENTITY = re.compile(r"^human:\S(?:.*\S)?$")
HASH_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
REVIEWED_AT = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$")

RECORD_KEYS = (
    "locale",
    "page",
    "path",
    "author",
    "reviewer",
    "reviewed_at",
    "notes",
    "review_status",
    "needs_native_check",
    "self_verified",
    "source_hash",
)

INITIAL_AUTHOR = "ai-product-lead"


class VisibleText(HTMLParser):
    """Collect text nodes that are inside body and outside script or style."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.in_body = False
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body":
            self.in_body = True
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
        if tag == "body":
            self.in_body = False

    def handle_data(self, data: str) -> None:
        if self.in_body and self.skip == 0:
            self.parts.append(data)


def visible_text(html: str) -> str:
    """Return visible text after NFC, LF newlines, and a trim."""
    parser = VisibleText()
    parser.feed(html)
    parser.close()
    text = unicodedata.normalize("NFC", "".join(parser.parts))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def source_hash(html: str) -> str:
    digest = hashlib.sha256(visible_text(html).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def is_human(value: object) -> bool:
    return isinstance(value, str) and HUMAN_IDENTITY.fullmatch(value) is not None


def is_identity(value: object) -> bool:
    return (isinstance(value, str) and value in AI_AUTHORS) or is_human(value)


def expected_pairs() -> list[tuple[str, str, str]]:
    pairs: list[tuple[str, str, str]] = []
    for locale in LOCALE_CODES:
        for page_id in PAGE_IDS:
            pairs.append((locale, page_id, f"{locale}/{page_id}.html"))
    return pairs


def blank_record(locale: str, page_id: str, path: str, html: str) -> dict[str, object]:
    return {
        "locale": locale,
        "page": page_id,
        "path": path,
        "author": INITIAL_AUTHOR,
        "reviewer": None,
        "reviewed_at": None,
        "notes": "",
        "review_status": "unreviewed",
        "needs_native_check": locale != "en",
        "self_verified": False,
        "source_hash": source_hash(html),
    }


def load_review(path: Path) -> tuple[object, list[str]]:
    errors: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, [f"missing {path.name}"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"{path.name}: invalid JSON ({exc})"]
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        errors.append(f"{path.name}: expected an object with a records array")
    if isinstance(data, dict) and data.get("version") != REVIEW_VERSION:
        errors.append(f"{path.name}: version must be {REVIEW_VERSION}")
    return data, errors


def check_record(
    record: object,
    *,
    html: str | None,
    release: bool,
) -> tuple[list[str], list[str]]:
    """Return (errors, notices) for one record."""
    errors: list[str] = []
    notices: list[str] = []
    if not isinstance(record, dict):
        return ["a review record is not an object"], notices
    label = str(record.get("path") or record.get("page") or "record")
    unknown = set(record) - set(RECORD_KEYS)
    for key in sorted(unknown):
        errors.append(f"{label}: unknown field {key}")
    for key in RECORD_KEYS:
        if key not in record:
            errors.append(f"{label}: missing {key}")
    if errors:
        return errors, notices

    author = record["author"]
    reviewer = record["reviewer"]
    status = record["review_status"]
    if not is_identity(author):
        errors.append(f"{label}: missing author")
    elif not is_identity(reviewer) and reviewer is not None:
        errors.append(f"{label}: reviewer is not an allowed identity")
    if is_identity(author) and author == reviewer:
        errors.append(f"{label}: reviewer must not be the author")
    if status not in STATUSES:
        errors.append(f"{label}: review_status is not allowed")
    if status == "human_verified" and not is_human(reviewer):
        errors.append(f"{label}: human_verified without human:* reviewer")
    if not isinstance(record["needs_native_check"], bool):
        errors.append(f"{label}: needs_native_check must be true or false")
    if not isinstance(record["self_verified"], bool):
        errors.append(f"{label}: self_verified must be true or false")
    if not isinstance(record["notes"], str):
        errors.append(f"{label}: notes must be a string")
    reviewed_at = record["reviewed_at"]
    if reviewed_at is not None and (
        not isinstance(reviewed_at, str) or REVIEWED_AT.fullmatch(reviewed_at) is None
    ):
        errors.append(f"{label}: reviewed_at must be null or an ISO date")
    stated = record["source_hash"]
    if not isinstance(stated, str) or HASH_VALUE.fullmatch(stated) is None:
        errors.append(f"{label}: source_hash must be sha256: and 64 hex digits")
    elif html is not None:
        actual = source_hash(html)
        if stated != actual:
            errors.append(f"{label}: source_hash is {stated}, recomputed {actual}")
    if status == "unreviewed":
        notices.append(f"{label}: unreviewed")
    if release:
        if status == "unreviewed":
            errors.append(f"{label}: unreviewed pages fail release mode")
        elif status == "flagged":
            errors.append(f"{label}: flagged pages fail release mode")
        if record.get("page") in LEGAL_PAGE_IDS and status in {"ai_reviewed", "ai_verified"}:
            errors.append(
                f"{label}: legal text is machine-only ({status}); "
                "release requires human_verified"
            )
    return errors, notices


def check_tree(root: Path, review_file: Path, *, release: bool) -> tuple[list[str], list[str]]:
    data, errors = load_review(review_file)
    notices: list[str] = []
    if data is None or not isinstance(data, dict):
        return errors, notices
    records = data.get("records")
    if not isinstance(records, list):
        return errors, notices

    by_key: dict[tuple[str, str], object] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append("a review record is not an object")
            continue
        locale = record.get("locale")
        page_id = record.get("page")
        path = record.get("path")
        key = (locale, page_id) if isinstance(locale, str) and isinstance(page_id, str) else None
        if key is None:
            errors.append(f"{path or 'record'}: locale and page must be strings")
            continue
        if key in by_key:
            errors.append(f"{locale}/{page_id}: duplicate review record")
            continue
        by_key[key] = record
        if path != f"{locale}/{page_id}.html":
            errors.append(f"{path}: path must be {locale}/{page_id}.html")

    for locale, page_id, relative in expected_pairs():
        record = by_key.pop((locale, page_id), None)
        target = root / relative
        html = target.read_text(encoding="utf-8") if target.is_file() else None
        if html is None:
            errors.append(f"{relative}: page file is missing")
        if record is None:
            errors.append(f"{relative}: missing review record")
            continue
        record_errors, record_notices = check_record(record, html=html, release=release)
        errors.extend(record_errors)
        notices.extend(record_notices)
    for locale, page_id in sorted(by_key):
        errors.append(f"{locale}/{page_id}: review record is not a locale page")
    return errors, notices


def write_review(root: Path, review_file: Path) -> None:
    """Refresh hashes. Existing review fields stay. New pages start unreviewed."""
    existing: dict[tuple[str, str], dict[str, object]] = {}
    if review_file.is_file():
        data, errors = load_review(review_file)
        if errors and data is None:
            raise SystemExit("\n".join(errors))
        if isinstance(data, dict) and isinstance(data.get("records"), list):
            for record in data["records"]:
                if isinstance(record, dict) and isinstance(record.get("locale"), str):
                    existing[(record["locale"], str(record.get("page")))] = record
    records: list[dict[str, object]] = []
    for locale, page_id, relative in expected_pairs():
        html = (root / relative).read_text(encoding="utf-8")
        current = existing.get((locale, page_id))
        if current is None:
            records.append(blank_record(locale, page_id, relative, html))
            continue
        updated = dict(current)
        updated["path"] = relative
        updated["source_hash"] = source_hash(html)
        records.append(updated)
    payload = {"version": REVIEW_VERSION, "records": records}
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    review_file.write_text(text, encoding="utf-8")


def self_test() -> list[str]:
    failures: list[str] = []

    def run(html: str, record: dict[str, object], release: bool = False) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "en" / "privacy.html"
            target.parent.mkdir(parents=True)
            target.write_text(html, encoding="utf-8")
            # The checker expects the full matrix. This fixture only plants
            # one page, so call check_record directly for rule tests.
            return check_record(record, html=html, release=release)

    base_html = "<html><body><p>Cafe\u0301</p></body></html>"
    composed = "<html><body><p>Caf\u00e9</p>\r\n</body></html>"
    if source_hash(base_html) != source_hash(composed):
        failures.append("NFC and LF did not produce one hash")
    if source_hash("<html><head><title>Secret</title></head><body><p>Shown</p></body></html>") == source_hash(
        "<html><body><p>Shown</p><p>Secret</p></body></html>"
    ):
        failures.append("head text was treated as visible")
    digest = source_hash("<html><body><p>Hello</p></body></html>")
    good = {
        "locale": "en",
        "page": "privacy",
        "path": "en/privacy.html",
        "author": "ai-product-lead",
        "reviewer": None,
        "reviewed_at": None,
        "notes": "",
        "review_status": "unreviewed",
        "needs_native_check": False,
        "self_verified": False,
        "source_hash": digest,
    }
    errors, notices = run("<html><body><p>Hello</p></body></html>", good)
    if errors or not notices:
        failures.append(f"unreviewed record should only be reported, got {errors} {notices}")
    errors, _notices = run("<html><body><p>Hello</p></body></html>", good, release=True)
    if not any("unreviewed" in item and "release" in item for item in errors):
        failures.append(f"release mode should fail unreviewed, got {errors}")
    missing = dict(good)
    missing["author"] = ""
    errors, _notices = run("<html><body><p>Hello</p></body></html>", missing)
    if not any("missing author" in item for item in errors):
        failures.append(f"missing author should fail, got {errors}")
    same = dict(good)
    same["author"] = "ai-qa"
    same["reviewer"] = "ai-qa"
    same["review_status"] = "ai_reviewed"
    errors, _notices = run("<html><body><p>Hello</p></body></html>", same)
    if not any("reviewer must not be the author" in item for item in errors):
        failures.append(f"self-review should fail, got {errors}")
    machine = dict(good)
    machine["reviewer"] = "ai-qa"
    machine["review_status"] = "human_verified"
    machine["reviewed_at"] = "2026-10-23"
    errors, _notices = run("<html><body><p>Hello</p></body></html>", machine)
    if not any("human_verified without human:*" in item for item in errors):
        failures.append(f"human_verified without human:* should fail, got {errors}")
    legal = dict(good)
    legal["reviewer"] = "ai-qa"
    legal["review_status"] = "ai_verified"
    legal["reviewed_at"] = "2026-10-23"
    errors, _notices = run("<html><body><p>Hello</p></body></html>", legal, release=True)
    if not any("machine-only" in item for item in errors):
        failures.append(f"release mode should reject machine-only legal text, got {errors}")
    human = dict(good)
    human["reviewer"] = "human:Gabriel John Fordan"
    human["review_status"] = "human_verified"
    human["reviewed_at"] = "2026-10-23"
    errors, notices = run("<html><body><p>Hello</p></body></html>", human, release=True)
    if errors or notices:
        failures.append(f"human verification should pass release, got {errors} {notices}")
    stale = dict(good)
    stale["source_hash"] = "sha256:" + ("ab" * 32)
    errors, _notices = run("<html><body><p>Hello</p></body></html>", stale)
    if not any("source_hash" in item for item in errors):
        failures.append(f"hash mismatch should fail, got {errors}")
    return failures


def main(argv: list[str]) -> int:
    release = "--release" in argv
    write = "--write" in argv
    unknown = [arg for arg in argv if arg not in {"--release", "--write"}]
    if unknown:
        print("Usage: python3 scripts/review_check.py [--release] [--write]", file=sys.stderr)
        return 2
    failures = self_test()
    if failures:
        print("Review checker self-test failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    if write:
        write_review(ROOT, REVIEW_PATH)
        print(f"Wrote {REVIEW_PATH.relative_to(ROOT)}")
    errors, notices = check_tree(ROOT, REVIEW_PATH, release=release)
    if notices:
        print(f"Unreviewed pages: {len(notices)} (not a failure outside --release)")
        for notice in notices:
            print(f"  {notice}")
    if errors:
        print(f"{len(errors)} review check(s) failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    mode = "release" if release else "draft"
    print(f"OK: review records ({mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
