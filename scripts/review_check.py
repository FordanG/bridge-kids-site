#!/usr/bin/env python3
"""Review records for the Bridge Kids locale pages.

review.json has one record per page and locale, plus release_languages.
source_hash is "sha256:" plus the hex SHA-256 of that page's visible
text after NFC normalization, newline conversion to LF, and a trim.

Visible text is the body's text nodes. Script, style, and head content
are left out. HTML comments are not text. No other whitespace is
collapsed, so the hash tracks the published wording.

The default run recomputes every hash. It fails on a missing author, a
reviewer who is the same identity as the author, a reviewer outside
ai-product-lead | ai-ja-reviewer | ai-qa | ai-designer | human:<name>,
a human_verified record whose reviewer is not human:<name>, a bad
author/reviewer pairing, a bad hash, or a record outside the locale ×
page matrix. Unreviewed pages in a release language are reported and
do not fail this mode. Locales outside release_languages are reported
as excluded and do not fail.

--release follows PRD §12.8 for the languages in release_languages
(en and ja at launch). en passes as ai_reviewed by the author-rule
reviewer, or human_verified. ja passes as ai_reviewed by
ai-ja-reviewer when needs_native_check is false. When that flag is
true, ja passes only as ai_verified by ai-ja-reviewer with reviewed_at
set, or human_verified. Unreviewed, flagged, and stale-hash pages in
a release language fail. Excluded locales are reported, not failed.
Gabriel's Final Review OK in release/checklist.json is required;
a missing OK fails. That sign-off is the human gate for the legal
pages. Per-page human_verified is optional.

reviewer == author always fails. --write refreshes source_hash and
adds a missing record as unreviewed. It does not change an existing
review.
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

from site_map import LOCALE_CODES, PAGE_IDS  # noqa: E402

ROOT = SCRIPT_DIR.parent
REVIEW_PATH = ROOT / "review.json"
CHECKLIST_PATH = ROOT / "release" / "checklist.json"
REVIEW_VERSION = 1
DEFAULT_RELEASE_LANGUAGES = ["en", "ja"]
FINAL_REVIEW_BY = "human:gabriel"

AI_AUTHORS = frozenset(
    {"ai-product-lead", "ai-ja-reviewer", "ai-qa", "ai-designer"}
)
STATUSES = frozenset(
    {"unreviewed", "ai_reviewed", "flagged", "ai_verified", "human_verified"}
)
HUMAN_IDENTITY = re.compile(r"^human:\S(?:.*\S)?$")
HASH_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
REVIEWED_AT = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$")
ATTR_URL = re.compile(r"""(?:href|src|action)\s*=\s*["']([^"']+)["']""", re.I)
HREFLANG_ATTR = re.compile(r"""hreflang\s*=\s*["']([^"']+)["']""", re.I)

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


def parse_release_languages(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [], ["review.json: expected an object"]
    raw = data.get("release_languages")
    if not isinstance(raw, list) or not raw or any(not isinstance(code, str) for code in raw):
        return [], ["review.json: release_languages must be a list of locale codes"]
    if len(set(raw)) != len(raw):
        errors.append("review.json: release_languages has a duplicate")
    unknown = [code for code in raw if code not in LOCALE_CODES]
    if unknown:
        errors.append(
            "review.json: release_languages has unknown locale " + ", ".join(unknown)
        )
    for required in ("en", "ja"):
        if required not in raw:
            errors.append(f"review.json: release_languages must include {required}")
    return list(raw), errors


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
    if isinstance(data, dict):
        _languages, language_errors = parse_release_languages(data)
        errors.extend(language_errors)
    return data, errors


def en_reviewer_ok(author: object, reviewer: object) -> bool:
    """Author rule for English: product-lead text is reviewed by ja or qa."""
    if not is_identity(author) or not is_identity(reviewer) or author == reviewer:
        return False
    if is_human(reviewer):
        return True
    if author == "ai-product-lead":
        return reviewer in {"ai-ja-reviewer", "ai-qa"}
    return reviewer == "ai-product-lead"


def ja_reviewer_ok(author: object, reviewer: object) -> bool:
    """First-pass Japanese reviewer. A fix the JA reviewer wrote is reviewed by the product lead."""
    if not is_identity(author) or not is_identity(reviewer) or author == reviewer:
        return False
    if is_human(reviewer):
        return True
    if author == "ai-ja-reviewer":
        return reviewer == "ai-product-lead"
    return reviewer == "ai-ja-reviewer"


def pairing_error(locale: object, author: object, reviewer: object) -> str | None:
    if not is_identity(author) or not is_identity(reviewer):
        return None
    if author == reviewer:
        return "reviewer must not be the author"
    if locale == "en" and not en_reviewer_ok(author, reviewer):
        if author == "ai-product-lead":
            return (
                "en author ai-product-lead requires reviewer "
                "ai-ja-reviewer, ai-qa, or human:*"
            )
        return "en author requires reviewer ai-product-lead or human:*"
    if locale == "ja" and not ja_reviewer_ok(author, reviewer):
        if author == "ai-ja-reviewer":
            return "ja author ai-ja-reviewer requires reviewer ai-product-lead or human:*"
        return "ja requires reviewer ai-ja-reviewer or human:*"
    if locale not in {"en", "ja"} and not is_human(reviewer) and reviewer not in AI_AUTHORS:
        return "reviewer is not an allowed identity"
    return None


def release_status_error(record: dict[str, object]) -> str | None:
    """PRD §12.8 pass rule for one page in a release language."""
    label = str(record.get("path") or "record")
    status = record.get("review_status")
    locale = record.get("locale")
    author = record.get("author")
    reviewer = record.get("reviewer")
    reviewed_at = record.get("reviewed_at")
    if status == "unreviewed":
        return f"{label}: unreviewed pages fail release mode"
    if status == "flagged":
        return f"{label}: flagged pages fail release mode"
    dated = isinstance(reviewed_at, str) and REVIEWED_AT.fullmatch(reviewed_at) is not None
    human_ok = status == "human_verified" and is_human(reviewer)
    verified_ok = (
        status == "ai_verified"
        and locale == "ja"
        and reviewer == "ai-ja-reviewer"
        and dated
    )
    if record.get("needs_native_check") is True:
        if human_ok or verified_ok:
            return None
        return (
            f"{label}: needs_native_check requires ai_verified by ai-ja-reviewer "
            "with reviewed_at, or human_verified"
        )
    if locale == "en":
        if (status == "ai_reviewed" and en_reviewer_ok(author, reviewer)) or human_ok:
            return None
        return (
            f"{label}: en release requires ai_reviewed by the author-rule reviewer, "
            "or human_verified"
        )
    if locale == "ja":
        if (status == "ai_reviewed" and ja_reviewer_ok(author, reviewer)) or human_ok or verified_ok:
            return None
        return (
            f"{label}: ja release requires ai_reviewed by ai-ja-reviewer, "
            "or human_verified"
        )
    return f"{label}: no release rule for locale {locale}"


def check_record(
    record: object,
    *,
    html: str | None,
    release: bool,
    in_release: bool,
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
    elif reviewer is None:
        if status != "unreviewed":
            errors.append(f"{label}: reviewer is required once a page is reviewed")
    elif not is_identity(reviewer):
        errors.append(
            f"{label}: reviewer is not an allowed identity "
            "(ai-product-lead | ai-ja-reviewer | ai-qa | ai-designer | human:<name>)"
        )
    if is_identity(author) and author == reviewer:
        errors.append(f"{label}: reviewer must not be the author")
    elif reviewer is not None and is_identity(reviewer):
        pairing = pairing_error(record.get("locale"), author, reviewer)
        if pairing is not None:
            errors.append(f"{label}: {pairing}")
    if status not in STATUSES:
        errors.append(f"{label}: review_status is not allowed")
    if status == "human_verified" and not is_human(reviewer):
        errors.append(f"{label}: human_verified without human:* reviewer")
    if status == "ai_verified" and (
        record.get("locale") != "ja"
        or reviewer != "ai-ja-reviewer"
        or not isinstance(record["reviewed_at"], str)
        or REVIEWED_AT.fullmatch(record["reviewed_at"]) is None
    ):
        errors.append(
            f"{label}: ai_verified requires ja, reviewer ai-ja-reviewer, and reviewed_at"
        )
    if not isinstance(record["needs_native_check"], bool):
        errors.append(f"{label}: needs_native_check must be true or false")
    if record["self_verified"] is not False:
        if record["self_verified"] is True:
            errors.append(
                f"{label}: self_verified is not accepted; reviewer must not be the author"
            )
        else:
            errors.append(f"{label}: self_verified must be true or false")
    if not isinstance(record["notes"], str):
        errors.append(f"{label}: notes must be a string")
    reviewed_at = record["reviewed_at"]
    if reviewed_at is not None and (
        not isinstance(reviewed_at, str) or REVIEWED_AT.fullmatch(reviewed_at) is None
    ):
        errors.append(f"{label}: reviewed_at must be null or an ISO date")
    if status != "unreviewed" and reviewed_at is None:
        errors.append(f"{label}: reviewed_at is required once a page is reviewed")
    stated = record["source_hash"]
    if not isinstance(stated, str) or HASH_VALUE.fullmatch(stated) is None:
        errors.append(f"{label}: source_hash must be sha256: and 64 hex digits")
    elif html is not None:
        actual = source_hash(html)
        if stated != actual:
            errors.append(f"{label}: source_hash is {stated}, recomputed {actual}")
    if not in_release:
        notices.append(f"{label}: excluded")
        return errors, notices
    if status == "unreviewed" and not release:
        notices.append(f"{label}: unreviewed")
    if release:
        status_error = release_status_error(record)
        if status_error is not None:
            errors.append(status_error)
    return errors, notices


def launch_pages(root: Path, release_languages: list[str]) -> list[Path]:
    pages = [root / "index.html", root / "404.html"]
    for locale in release_languages:
        for page_id in PAGE_IDS:
            pages.append(root / locale / f"{page_id}.html")
    return pages


def url_mentions_locale(url: str, code: str) -> bool:
    path = url.split("#", 1)[0].split("?", 1)[0]
    if "://" in path or path.startswith("mailto:"):
        return False
    parts = [part for part in path.split("/") if part not in {"", ".", ".."}]
    return code in parts


def excluded_link_errors(root: Path, release_languages: list[str]) -> list[str]:
    """Launch pages must not link or advertise a locale left out of the release."""
    excluded = [code for code in LOCALE_CODES if code not in release_languages]
    errors: list[str] = []
    for path in launch_pages(root, release_languages):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        label = path.relative_to(root).as_posix()
        for url in ATTR_URL.findall(text):
            for code in excluded:
                if url_mentions_locale(url, code):
                    errors.append(f"{label}: links excluded locale {code} ({url})")
        for language in HREFLANG_ATTR.findall(text):
            if language in excluded:
                errors.append(f"{label}: hreflang lists excluded locale {language}")
    return errors


def check_final_review(
    checklist_file: Path,
    release_languages: list[str],
    *,
    release: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notices: list[str] = []
    if not checklist_file.is_file():
        message = "release/checklist.json: missing Gabriel's Final Review OK"
        if release:
            errors.append(message)
        else:
            notices.append(f"{message} (not a failure outside --release)")
        return errors, notices
    try:
        data = json.loads(checklist_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"release/checklist.json: invalid JSON ({exc})"], notices
    site = data.get("site") if isinstance(data, dict) else None
    if not isinstance(site, dict) or set(site) - {"final_review_ok"}:
        return [
            "release/checklist.json: expected site.final_review_ok and no other site fields"
        ], notices
    ok = site.get("final_review_ok", None)
    if ok is None:
        message = "release/checklist.json: Final Review OK is not recorded"
        if release:
            errors.append(message)
        else:
            notices.append(f"{message} (not a failure outside --release)")
        return errors, notices
    if not isinstance(ok, dict):
        return ["release/checklist.json: final_review_ok must be an object or null"], notices
    unknown = set(ok) - {"by", "date", "languages"}
    for key in sorted(unknown):
        errors.append(f"release/checklist.json: unknown final_review_ok field {key}")
    for key in ("by", "date", "languages"):
        if key not in ok:
            errors.append(f"release/checklist.json: final_review_ok missing {key}")
    if errors:
        return errors, notices
    if ok.get("by") != FINAL_REVIEW_BY:
        errors.append(
            "release/checklist.json: final_review_ok.by must be human:gabriel"
        )
    date = ok.get("date")
    if not isinstance(date, str) or REVIEWED_AT.fullmatch(date) is None:
        errors.append("release/checklist.json: final_review_ok.date must be an ISO date")
    languages = ok.get("languages")
    if (
        not isinstance(languages, list)
        or any(not isinstance(code, str) for code in languages)
        or set(languages) != set(release_languages)
        or len(languages) != len(set(languages))
    ):
        errors.append(
            "release/checklist.json: final_review_ok.languages must match release_languages"
        )
    return errors, notices


def check_tree(
    root: Path,
    review_file: Path,
    *,
    release: bool,
    checklist_file: Path | None = None,
) -> tuple[list[str], list[str]]:
    data, errors = load_review(review_file)
    notices: list[str] = []
    if data is None or not isinstance(data, dict):
        return errors, notices
    languages, _language_errors = parse_release_languages(data)
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

    release_set = set(languages)
    for locale, page_id, relative in expected_pairs():
        record = by_key.pop((locale, page_id), None)
        target = root / relative
        html = target.read_text(encoding="utf-8") if target.is_file() else None
        if html is None:
            errors.append(f"{relative}: page file is missing")
        if record is None:
            errors.append(f"{relative}: missing review record")
            continue
        record_errors, record_notices = check_record(
            record,
            html=html,
            release=release,
            in_release=locale in release_set,
        )
        errors.extend(record_errors)
        notices.extend(record_notices)
    for locale, page_id in sorted(by_key):
        errors.append(f"{locale}/{page_id}: review record is not a locale page")
    if languages:
        errors.extend(excluded_link_errors(root, languages))
        checklist_errors, checklist_notices = check_final_review(
            checklist_file or (root / "release" / "checklist.json"),
            languages,
            release=release,
        )
        errors.extend(checklist_errors)
        notices.extend(checklist_notices)
    return errors, notices


def write_review(root: Path, review_file: Path) -> None:
    """Refresh hashes. Existing review fields stay. New pages start unreviewed."""
    existing: dict[tuple[str, str], dict[str, object]] = {}
    languages = list(DEFAULT_RELEASE_LANGUAGES)
    if review_file.is_file():
        data, errors = load_review(review_file)
        if errors and data is None:
            raise SystemExit("\n".join(errors))
        if isinstance(data, dict):
            parsed, _language_errors = parse_release_languages(data)
            if parsed:
                languages = parsed
            if isinstance(data.get("records"), list):
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
    payload = {
        "version": REVIEW_VERSION,
        "release_languages": languages,
        "records": records,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    review_file.write_text(text, encoding="utf-8")


def self_test() -> list[str]:
    failures: list[str] = []

    def run(
        html: str,
        record: dict[str, object],
        release: bool = False,
        in_release: bool = True,
    ) -> tuple[list[str], list[str]]:
        return check_record(record, html=html, release=release, in_release=in_release)

    base_html = "<html><body><p>Cafe\u0301</p></body></html>"
    composed = "<html><body><p>Caf\u00e9</p>\r\n</body></html>"
    if source_hash(base_html) != source_hash(composed):
        failures.append("NFC and LF did not produce one hash")
    if source_hash("<html><head><title>Secret</title></head><body><p>Shown</p></body></html>") == source_hash(
        "<html><body><p>Shown</p><p>Secret</p></body></html>"
    ):
        failures.append("head text was treated as visible")
    hello = "<html><body><p>Hello</p></body></html>"
    digest = source_hash(hello)
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
    errors, notices = run(hello, good)
    if errors or not notices:
        failures.append(f"unreviewed record should only be reported, got {errors} {notices}")
    errors, _notices = run(hello, good, release=True)
    if not any("unreviewed" in item and "release" in item for item in errors):
        failures.append(f"release mode should fail unreviewed, got {errors}")
    missing = dict(good)
    missing["author"] = ""
    errors, _notices = run(hello, missing)
    if not any("missing author" in item for item in errors):
        failures.append(f"missing author should fail, got {errors}")
    same = dict(good)
    same["author"] = "ai-qa"
    same["reviewer"] = "ai-qa"
    same["review_status"] = "ai_reviewed"
    same["reviewed_at"] = "2026-10-23"
    errors, _notices = run(hello, same)
    if not any("reviewer must not be the author" in item for item in errors):
        failures.append(f"self-review should fail, got {errors}")
    machine = dict(good)
    machine["reviewer"] = "ai-qa"
    machine["review_status"] = "human_verified"
    machine["reviewed_at"] = "2026-10-23"
    errors, _notices = run(hello, machine)
    if not any("human_verified without human:*" in item for item in errors):
        failures.append(f"human_verified without human:* should fail, got {errors}")
    bad_reviewer = dict(good)
    bad_reviewer["reviewer"] = "native-speaker"
    bad_reviewer["review_status"] = "ai_reviewed"
    bad_reviewer["reviewed_at"] = "2026-10-23"
    errors, _notices = run(hello, bad_reviewer)
    if not any("not an allowed identity" in item for item in errors):
        failures.append(f"unknown reviewer should fail, got {errors}")
    en_ok = dict(good)
    en_ok["reviewer"] = "ai-ja-reviewer"
    en_ok["review_status"] = "ai_reviewed"
    en_ok["reviewed_at"] = "2026-10-23"
    errors, notices = run(hello, en_ok, release=True)
    if errors or notices:
        failures.append(f"en ai_reviewed by ai-ja-reviewer should pass, got {errors} {notices}")
    en_fallback = dict(en_ok)
    en_fallback["reviewer"] = "ai-qa"
    errors, notices = run(hello, en_fallback, release=True)
    if errors or notices:
        failures.append(f"en ai_qa fallback should pass, got {errors} {notices}")
    en_other = dict(en_ok)
    en_other["author"] = "ai-designer"
    en_other["reviewer"] = "ai-product-lead"
    errors, notices = run(hello, en_other, release=True)
    if errors or notices:
        failures.append(f"en written by another author should pass with ai-product-lead, got {errors} {notices}")
    wrong_en = dict(en_ok)
    wrong_en["reviewer"] = "ai-designer"
    errors, _notices = run(hello, wrong_en, release=True)
    if not any("ai-ja-reviewer, ai-qa, or human:*" in item for item in errors):
        failures.append(f"wrong en reviewer should fail, got {errors}")
    ja = dict(good)
    ja["locale"] = "ja"
    ja["path"] = "ja/privacy.html"
    ja["needs_native_check"] = True
    ja["reviewer"] = "ai-ja-reviewer"
    ja["review_status"] = "ai_reviewed"
    ja["reviewed_at"] = "2026-10-23"
    errors, _notices = run(hello, ja, release=True)
    if not any("needs_native_check" in item for item in errors):
        failures.append(f"ja ai_reviewed with needs_native_check should fail release, got {errors}")
    ja_verified = dict(ja)
    ja_verified["review_status"] = "ai_verified"
    errors, notices = run(hello, ja_verified, release=True)
    if errors or notices:
        failures.append(f"ja ai_verified by ai-ja-reviewer should pass, got {errors} {notices}")
    ja_undated = dict(ja_verified)
    ja_undated["reviewed_at"] = None
    errors, _notices = run(hello, ja_undated, release=True)
    if not any("reviewed_at" in item for item in errors):
        failures.append(f"ja ai_verified without reviewed_at should fail, got {errors}")
    held = dict(good)
    held["locale"] = "vi"
    held["path"] = "vi/privacy.html"
    held["needs_native_check"] = True
    errors, notices = run(hello, held, release=True, in_release=False)
    if errors or not any(item.endswith(": excluded") for item in notices):
        failures.append(f"excluded unreviewed page should be reported, not failed, got {errors} {notices}")
    human = dict(good)
    human["reviewer"] = "human:Gabriel John Fordan"
    human["review_status"] = "human_verified"
    human["reviewed_at"] = "2026-10-23"
    errors, notices = run(hello, human, release=True)
    if errors or notices:
        failures.append(f"human verification should pass the page rule, got {errors} {notices}")
    stale = dict(good)
    stale["source_hash"] = "sha256:" + ("ab" * 32)
    errors, _notices = run(hello, stale)
    if not any("source_hash" in item for item in errors):
        failures.append(f"hash mismatch should fail, got {errors}")
    flagged = dict(en_ok)
    flagged["review_status"] = "flagged"
    errors, _notices = run(hello, flagged, release=True)
    if not any("flagged" in item and "release" in item for item in errors):
        failures.append(f"flagged page should fail release, got {errors}")

    failures.extend(fixture_release_gate(hello, digest))
    return failures


def fixture_release_gate(html: str, digest: str) -> list[str]:
    """A full locale matrix: excluded pages stay out, and Final Review OK is required."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        records: list[dict[str, object]] = []
        for locale, page_id, relative in expected_pairs():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            record = blank_record(locale, page_id, relative, html)
            record["source_hash"] = digest
            if locale == "en":
                record["reviewer"] = "ai-ja-reviewer"
                record["review_status"] = "ai_reviewed"
                record["reviewed_at"] = "2026-10-23"
                record["needs_native_check"] = False
            elif locale == "ja":
                record["reviewer"] = "ai-ja-reviewer"
                record["review_status"] = "ai_verified"
                record["reviewed_at"] = "2026-10-23"
                record["needs_native_check"] = True
            records.append(record)
        review_file = root / "review.json"
        review_file.write_text(
            json.dumps(
                {
                    "version": REVIEW_VERSION,
                    "release_languages": ["en", "ja"],
                    "records": records,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "index.html").write_text(
            '<html><body><p><a href="en/index.html">English</a> '
            '<a href="ja/index.html">Japanese</a></p></body></html>',
            encoding="utf-8",
        )
        (root / "404.html").write_text(
            "<html><body><p>Missing</p></body></html>",
            encoding="utf-8",
        )
        checklist = root / "release" / "checklist.json"
        errors, notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        if any("excluded" in item and "fail" in item for item in errors):
            failures.append(f"excluded locales should not fail release, got {errors}")
        if not any(item.endswith(": excluded") for item in notices):
            failures.append(f"excluded locales should be reported, got {notices}")
        if not any("Final Review OK" in item for item in errors):
            failures.append(f"missing Final Review OK should fail release, got {errors}")
        if any("unreviewed" in item for item in errors):
            failures.append(f"ready en/ja pages should not be unreviewed failures, got {errors}")
        checklist.parent.mkdir(parents=True)
        checklist.write_text(
            json.dumps(
                {
                    "site": {
                        "final_review_ok": {
                            "by": "human:gabriel",
                            "date": "2026-10-23",
                            "languages": ["en", "ja"],
                        }
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        errors, notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        if errors:
            failures.append(f"ready release with Final Review OK should pass, got {errors}")
        if sum(item.endswith(": excluded") for item in notices) != 25:
            failures.append(f"expected 25 excluded notices, got {notices}")
        (root / "index.html").write_text(
            '<html><body><p><a href="zh-Hans/index.html">Chinese</a></p></body></html>',
            encoding="utf-8",
        )
        errors, _notices = check_tree(root, review_file, release=False, checklist_file=checklist)
        if not any("links excluded locale zh-Hans" in item for item in errors):
            failures.append(f"a launch link to an excluded locale should fail, got {errors}")
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
    excluded = [notice for notice in notices if notice.endswith(": excluded")]
    unreviewed = [notice for notice in notices if notice.endswith(": unreviewed")]
    other = [notice for notice in notices if notice not in excluded and notice not in unreviewed]
    if excluded:
        print(f"Excluded pages: {len(excluded)} (not a release failure)")
        for notice in excluded:
            print(f"  {notice}")
    if unreviewed:
        print(f"Unreviewed pages: {len(unreviewed)} (not a failure outside --release)")
        for notice in unreviewed:
            print(f"  {notice}")
    for notice in other:
        print(notice)
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
