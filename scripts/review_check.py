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

--release follows PRD §12.8 for the languages in release_languages.
English is required. Japanese is re-added when the ai_verified ja
copy lands; until then it may be absent and those pages are excluded.
en passes as ai_reviewed by the author-rule reviewer, or
human_verified. ja passes as ai_reviewed by ai-ja-reviewer when
needs_native_check is false. When that flag is true, ja passes only
as ai_verified by ai-ja-reviewer with reviewed_at set, or
human_verified. Unreviewed, flagged, and stale-hash pages in a
release language fail. Excluded locales are reported, not failed.

--release also requires Gabriel's Final Review OK and site.effective_date
(an ISO date, the day the site goes public) in release/checklist.json.
A missing OK or a missing date fails. That sign-off is the human gate
for the legal pages. Per-page human_verified is optional. The same
command fails while a launch page still contains the postal-address
placeholder, the unpublished telephone line, the governing-law
sentence, or the retention-confirmation note. When both checklist
fields are set, the built pages must no longer carry the draft banner
and must show that effective date. Until then the draft banners stay.

reviewer == author fails, except PRD §12.8 exception (b): a ja page
authored by ai-ja-reviewer, first passed as ai_reviewed by
ai-product-lead, then ai_verified by ai-ja-reviewer in a later
session. That case needs allow_ja_self_verified, a matching
release/ja-review-log.json entry, and the path listed in
site.self_verified. The flag is "confirm at Final Review". If it is
false or absent, self_verified true still fails.

--write refreshes source_hash. A changed hash resets that page to
unreviewed. A missing record is added as unreviewed.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from site_map import DRAFT_MARK, LOCALE_CODES, PAGE_IDS  # noqa: E402

ROOT = SCRIPT_DIR.parent
REVIEW_PATH = ROOT / "review.json"
CHECKLIST_PATH = ROOT / "release" / "checklist.json"
JA_LOG_PATH = ROOT / "release" / "ja-review-log.json"
REVIEW_VERSION = 1
# ja is re-added to release_languages when the ai_verified ja copy lands.
DEFAULT_RELEASE_LANGUAGES = ["en"]
FINAL_REVIEW_BY = "human:gabriel"
# allow_ja_self_verified: confirm at Final Review. §12.8 exception (b) only.
CHECKLIST_SITE_KEYS = frozenset({"final_review_ok", "effective_date", "self_verified"})
PRESERVED_REVIEW_KEYS = (
    "release_languages_note",
    "allow_ja_self_verified",
    "allow_ja_self_verified_note",
)
RELEASE_BLOCKERS = (
    "{{POSTAL_ADDRESS_IF_REQUIRED}}",
    "Not published in this draft",
    "Governing law and venue are not chosen",
    "retention period pending Gabriel's confirmation",
)
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

AI_AUTHORS = frozenset(
    {"ai-product-lead", "ai-ja-reviewer", "ai-qa", "ai-designer"}
)
STATUSES = frozenset(
    {"unreviewed", "ai_reviewed", "flagged", "ai_verified", "human_verified"}
)
HUMAN_IDENTITY = re.compile(r"^human:\S(?:.*\S)?$")
HASH_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
REVIEWED_AT = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
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
    # ja is re-added when the ai_verified ja copy lands.
    if "en" not in raw:
        errors.append("review.json: release_languages must include en")
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


def parse_iso_date(value: object) -> str | None:
    if not isinstance(value, str) or ISO_DATE.fullmatch(value) is None:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    if parsed.isoformat() != value:
        return None
    return value


def format_public_date(iso: str) -> str:
    parsed = date.fromisoformat(iso)
    return f"{parsed.day} {MONTHS[parsed.month - 1]} {parsed.year}"


def load_ja_log(path: Path) -> tuple[list, list[str]]:
    if not path.is_file():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"release/ja-review-log.json: invalid JSON ({exc})"]
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return [], ["release/ja-review-log.json: entries must be an array"]
    return entries, []


def _log_pass(block: object, reviewer: str) -> bool:
    return isinstance(block, dict) and block.get("reviewer") == reviewer


def ja_log_errors(path: str, entries: list) -> list[str]:
    matches = [
        entry for entry in entries if isinstance(entry, dict) and entry.get("path") == path
    ]
    if len(matches) != 1:
        return [f"{path}: self_verified requires one matching JA Review Log entry"]
    entry = matches[0]
    errors: list[str] = []
    if entry.get("author") != "ai-ja-reviewer":
        errors.append(f"{path}: JA Review Log author must be ai-ja-reviewer")
    reviewed = entry.get("ai_reviewed")
    verified = entry.get("ai_verified")
    if not _log_pass(reviewed, "ai-product-lead"):
        errors.append(f"{path}: JA Review Log ai_reviewed reviewer must be ai-product-lead")
    if not _log_pass(verified, "ai-ja-reviewer"):
        errors.append(f"{path}: JA Review Log ai_verified reviewer must be ai-ja-reviewer")
    for name, block in (("ai_reviewed", reviewed), ("ai_verified", verified)):
        if isinstance(block, dict):
            logged = block.get("date")
            if not isinstance(logged, str) or REVIEWED_AT.fullmatch(logged) is None:
                errors.append(f"{path}: JA Review Log {name} date must be an ISO date")
    reviewed_session = reviewed.get("session") if isinstance(reviewed, dict) else None
    verified_session = verified.get("session") if isinstance(verified, dict) else None
    if (
        not isinstance(reviewed_session, str)
        or not reviewed_session.strip()
        or not isinstance(verified_session, str)
        or not verified_session.strip()
        or reviewed_session == verified_session
    ):
        errors.append(f"{path}: JA Review Log sessions must differ")
    return errors


def ja_self_verified_exception(
    record: dict[str, object],
    *,
    allowed: bool,
    log_entries: list,
    listed: set[str],
) -> tuple[bool, list[str]]:
    """PRD §12.8 exception (b). Returns (reviewer may equal author, errors)."""
    if record.get("self_verified") is not True:
        return False, []
    label = str(record.get("path") or "record")
    if not allowed:
        return False, [
            f"{label}: self_verified is not accepted; reviewer must not be the author"
        ]
    errors: list[str] = []
    if record.get("locale") != "ja" or record.get("author") != "ai-ja-reviewer":
        errors.append(
            f"{label}: self_verified exception is only for a ja page authored by ai-ja-reviewer"
        )
    if record.get("review_status") != "ai_verified" or record.get("reviewer") != "ai-ja-reviewer":
        errors.append(
            f"{label}: self_verified exception requires a later ai_verified pass by ai-ja-reviewer"
        )
    errors.extend(ja_log_errors(label, log_entries))
    if label not in listed:
        errors.append(
            f"{label}: self_verified must be listed under Final Review in release/checklist.json"
        )
    return (not errors), errors


def check_record(
    record: object,
    *,
    html: str | None,
    release: bool,
    in_release: bool,
    allow_ja_self_verified: bool = False,
    ja_log: list | None = None,
    self_verified_paths: set[str] | None = None,
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
    exception_ok = False
    if record["self_verified"] is True:
        exception_ok, exception_errors = ja_self_verified_exception(
            record,
            allowed=allow_ja_self_verified,
            log_entries=ja_log or [],
            listed=self_verified_paths or set(),
        )
        errors.extend(exception_errors)
    elif record["self_verified"] is not False:
        errors.append(f"{label}: self_verified must be true or false")
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
    if is_identity(author) and author == reviewer and not exception_ok:
        errors.append(f"{label}: reviewer must not be the author")
    elif reviewer is not None and is_identity(reviewer) and not exception_ok:
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


def checklist_state(
    checklist_file: Path,
    release_languages: list[str],
    *,
    release: bool,
) -> tuple[list[str], list[str], set[str], str | None]:
    """Return errors, notices, self_verified paths, and the effective ISO date."""
    errors: list[str] = []
    notices: list[str] = []
    listed: set[str] = set()
    ok_missing = "release/checklist.json: missing Gabriel's Final Review OK"
    date_missing = "release/checklist.json: site.effective_date is not set"
    if not checklist_file.is_file():
        if release:
            return [ok_missing, date_missing], notices, listed, None
        return (
            [],
            [
                f"{ok_missing} (not a failure outside --release)",
                f"{date_missing} (not a failure outside --release)",
            ],
            listed,
            None,
        )
    try:
        data = json.loads(checklist_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"release/checklist.json: invalid JSON ({exc})"], notices, listed, None
    site = data.get("site") if isinstance(data, dict) else None
    if not isinstance(site, dict):
        return ["release/checklist.json: expected a site object"], notices, listed, None
    unknown = set(site) - CHECKLIST_SITE_KEYS
    for key in sorted(unknown):
        errors.append(f"release/checklist.json: unknown site field {key}")
    for key in ("final_review_ok", "effective_date", "self_verified"):
        if key not in site:
            errors.append(f"release/checklist.json: missing site.{key}")
    if errors:
        return errors, notices, listed, None

    raw_listed = site.get("self_verified")
    if not isinstance(raw_listed, list) or any(not isinstance(item, str) for item in raw_listed):
        errors.append("release/checklist.json: site.self_verified must be an array of paths")
    else:
        listed = set(raw_listed)

    ok = site.get("final_review_ok")
    if ok is None:
        message = "release/checklist.json: Final Review OK is not recorded"
        if release:
            errors.append(message)
        else:
            notices.append(f"{message} (not a failure outside --release)")
    elif not isinstance(ok, dict):
        errors.append("release/checklist.json: final_review_ok must be an object or null")
    else:
        unknown_ok = set(ok) - {"by", "date", "languages"}
        for key in sorted(unknown_ok):
            errors.append(f"release/checklist.json: unknown final_review_ok field {key}")
        for key in ("by", "date", "languages"):
            if key not in ok:
                errors.append(f"release/checklist.json: final_review_ok missing {key}")
        if "by" in ok and ok.get("by") != FINAL_REVIEW_BY:
            errors.append("release/checklist.json: final_review_ok.by must be human:gabriel")
        signed = ok.get("date")
        if "date" in ok and (
            not isinstance(signed, str) or REVIEWED_AT.fullmatch(signed) is None
        ):
            errors.append("release/checklist.json: final_review_ok.date must be an ISO date")
        languages = ok.get("languages")
        if "languages" in ok and (
            not isinstance(languages, list)
            or any(not isinstance(code, str) for code in languages)
            or set(languages) != set(release_languages)
            or len(languages) != len(set(languages))
        ):
            errors.append(
                "release/checklist.json: final_review_ok.languages must match release_languages"
            )

    effective = site.get("effective_date")
    iso: str | None = None
    if effective is None:
        message = "release/checklist.json: site.effective_date is not set"
        if release:
            errors.append(message)
        else:
            notices.append(f"{message} (not a failure outside --release)")
    else:
        iso = parse_iso_date(effective)
        if iso is None:
            errors.append("release/checklist.json: site.effective_date must be an ISO date")
    return errors, notices, listed, iso if not errors else None


def publication_stamp(
    checklist_file: Path,
    release_languages: list[str],
) -> tuple[str, str] | None:
    """(iso, public label) once Final Review OK and effective_date are both valid."""
    errors, _notices, _listed, iso = checklist_state(
        checklist_file,
        release_languages,
        release=True,
    )
    if errors or iso is None:
        return None
    return iso, format_public_date(iso)


def launch_release_errors(
    root: Path,
    release_languages: list[str],
    checklist_file: Path,
    *,
    release: bool,
) -> list[str]:
    """Placeholders and draft banners block --release. Draft mode leaves them."""
    if not release:
        return []
    errors: list[str] = []
    stamp = publication_stamp(checklist_file, release_languages)
    for path in launch_pages(root, release_languages):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        label = path.relative_to(root).as_posix()
        for marker in RELEASE_BLOCKERS:
            if marker in text:
                errors.append(f"{label}: release blocked while {marker!r} remains")
        if stamp is None:
            if DRAFT_MARK not in text:
                errors.append(
                    f"{label}: draft banner must stay until Final Review OK and effective_date are set"
                )
        else:
            _iso, pretty = stamp
            if DRAFT_MARK in text:
                errors.append(
                    f"{label}: draft banner must be removed once Final Review OK and effective_date are set"
                )
            if "Effective date:" not in text or pretty not in text:
                errors.append(
                    f"{label}: effective date must be filled from site.effective_date ({pretty})"
                )
    return errors


def check_tree(
    root: Path,
    review_file: Path,
    *,
    release: bool,
    checklist_file: Path | None = None,
    ja_log_file: Path | None = None,
) -> tuple[list[str], list[str]]:
    data, errors = load_review(review_file)
    notices: list[str] = []
    if data is None or not isinstance(data, dict):
        return errors, notices
    languages, _language_errors = parse_release_languages(data)
    records = data.get("records")
    if not isinstance(records, list):
        return errors, notices
    log_entries, log_errors = load_ja_log(ja_log_file or (root / "release" / "ja-review-log.json"))
    errors.extend(log_errors)
    allow_self = data.get("allow_ja_self_verified") is True
    checklist = checklist_file or (root / "release" / "checklist.json")
    checklist_errors, checklist_notices, listed, _iso = checklist_state(
        checklist,
        languages,
        release=release,
    )

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
            allow_ja_self_verified=allow_self,
            ja_log=log_entries,
            self_verified_paths=listed,
        )
        errors.extend(record_errors)
        notices.extend(record_notices)
    for locale, page_id in sorted(by_key):
        errors.append(f"{locale}/{page_id}: review record is not a locale page")
    if languages:
        errors.extend(excluded_link_errors(root, languages))
        errors.extend(checklist_errors)
        notices.extend(checklist_notices)
        errors.extend(
            launch_release_errors(
                root,
                languages,
                checklist,
                release=release,
            )
        )
    return errors, notices


def write_review(root: Path, review_file: Path) -> None:
    """Refresh hashes. A changed hash returns that page to unreviewed."""
    existing: dict[tuple[str, str], dict[str, object]] = {}
    languages = list(DEFAULT_RELEASE_LANGUAGES)
    extras: dict[str, object] = {}
    if review_file.is_file():
        data, errors = load_review(review_file)
        if errors and data is None:
            raise SystemExit("\n".join(errors))
        if isinstance(data, dict):
            parsed, _language_errors = parse_release_languages(data)
            if parsed and not _language_errors:
                languages = parsed
            for key in PRESERVED_REVIEW_KEYS:
                if key in data:
                    extras[key] = data[key]
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
        new_hash = source_hash(html)
        if updated.get("source_hash") != new_hash:
            updated["review_status"] = "unreviewed"
            updated["reviewer"] = None
            updated["reviewed_at"] = None
            updated["self_verified"] = False
        updated["source_hash"] = new_hash
        records.append(updated)
    payload: dict[str, object] = {
        "version": REVIEW_VERSION,
        "release_languages": languages,
    }
    for key in PRESERVED_REVIEW_KEYS:
        if key in extras:
            payload[key] = extras[key]
    payload["records"] = records
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

    only_en, only_en_errors = parse_release_languages({"release_languages": ["en"]})
    if only_en_errors or only_en != ["en"]:
        failures.append(f"en-only release_languages should pass, got {only_en_errors}")
    _ja_only, ja_only_errors = parse_release_languages({"release_languages": ["ja"]})
    if not any("must include en" in item for item in ja_only_errors):
        failures.append(f"release_languages without en should fail, got {ja_only_errors}")
    failures.extend(fixture_self_verified(hello))
    failures.extend(fixture_publication_banner())
    failures.extend(fixture_hash_reset())
    failures.extend(fixture_release_gate(hello, digest))
    return failures


def fixture_self_verified(html: str) -> list[str]:
    """§12.8 exception (b) is the only reviewer==author case, and only when it matches."""
    failures: list[str] = []
    base = {
        "locale": "ja",
        "page": "privacy",
        "path": "ja/privacy.html",
        "author": "ai-ja-reviewer",
        "reviewer": "ai-ja-reviewer",
        "reviewed_at": "2026-10-23",
        "notes": "",
        "review_status": "ai_verified",
        "needs_native_check": True,
        "self_verified": True,
        "source_hash": source_hash(html),
    }
    log = [
        {
            "path": "ja/privacy.html",
            "author": "ai-ja-reviewer",
            "ai_reviewed": {
                "reviewer": "ai-product-lead",
                "date": "2026-10-20",
                "session": "first-pass",
            },
            "ai_verified": {
                "reviewer": "ai-ja-reviewer",
                "date": "2026-10-23",
                "session": "later-pass",
            },
        }
    ]
    listed = {"ja/privacy.html"}

    def check(record: dict[str, object], **kwargs: object) -> list[str]:
        errors, _notices = check_record(
            record,
            html=html,
            release=True,
            in_release=True,
            allow_ja_self_verified=bool(kwargs.get("allowed", True)),
            ja_log=kwargs.get("log", log),  # type: ignore[arg-type]
            self_verified_paths=kwargs.get("listed", listed),  # type: ignore[arg-type]
        )
        return errors

    if not any("self_verified is not accepted" in item for item in check(base, allowed=False)):
        failures.append("self_verified should fail when the flag is off")
    english = dict(base)
    english["locale"] = "en"
    english["path"] = "en/privacy.html"
    if not any("only for a ja page" in item for item in check(english)):
        failures.append("self_verified should fail for en")
    wrong_author = dict(base)
    wrong_author["author"] = "ai-product-lead"
    if not any("authored by ai-ja-reviewer" in item for item in check(wrong_author)):
        failures.append("self_verified should fail for the wrong author")
    early = dict(base)
    early["review_status"] = "ai_reviewed"
    if not any("later ai_verified pass" in item for item in check(early)):
        failures.append("self_verified should fail on the first ai_reviewed pass")
    if not any("JA Review Log" in item for item in check(base, log=[])):
        failures.append("self_verified should fail when the JA Review Log entry is missing")
    same_session = json.loads(json.dumps(log))
    same_session[0]["ai_verified"]["session"] = "first-pass"
    if not any("sessions must differ" in item for item in check(base, log=same_session)):
        failures.append("self_verified should fail when both passes share a session")
    if not any("listed under Final Review" in item for item in check(base, listed=set())):
        failures.append("self_verified should fail when the checklist list omits the path")
    errors = check(base)
    if errors:
        failures.append(f"matching later-session self_verified ja page should pass, got {errors}")
    if not any(item == "ai-ja-reviewer" for item in (base["author"], base["reviewer"])):
        failures.append("the passing self_verified case must be reviewer==author")
    return failures


def fixture_publication_banner() -> list[str]:
    failures: list[str] = []
    import build_site

    draft = build_site.page(
        title="T",
        description="D",
        heading="H",
        body="<p>Body</p>",
        css_href="css/site.css",
        icon_prefix="",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
    )
    if DRAFT_MARK not in draft or "Draft dated" not in draft:
        failures.append("draft build should keep the banner and the dated line")
    live = build_site.page(
        title="T",
        description="D",
        heading="H",
        body="<p>Body</p>",
        css_href="css/site.css",
        icon_prefix="",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
        published=("2026-10-23", "23 October 2026"),
    )
    if DRAFT_MARK in live or "Draft dated" in live or "Effective date:" not in live:
        failures.append("published build should strip the banner and fill the effective date")
    if live.count("23 October 2026") < 2:
        failures.append("published build should use the effective date for both dates")
    return failures


def fixture_hash_reset() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        original = "<html><body><p>Hello</p></body></html>"
        records: list[dict[str, object]] = []
        for locale, page_id, relative in expected_pairs():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(original, encoding="utf-8")
            record = blank_record(locale, page_id, relative, original)
            if locale == "en" and page_id == "privacy":
                record["reviewer"] = "ai-ja-reviewer"
                record["review_status"] = "ai_reviewed"
                record["reviewed_at"] = "2026-10-23"
            if locale == "en" and page_id == "index":
                record["reviewer"] = "ai-qa"
                record["review_status"] = "ai_reviewed"
                record["reviewed_at"] = "2026-10-23"
            records.append(record)
        review_file = root / "review.json"
        review_file.write_text(
            json.dumps(
                {
                    "version": REVIEW_VERSION,
                    "release_languages": ["en"],
                    "release_languages_note": "ja is re-added when the ai_verified ja copy lands",
                    "allow_ja_self_verified": True,
                    "allow_ja_self_verified_note": "confirm at Final Review",
                    "records": records,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "en" / "privacy.html").write_text(
            "<html><body><p>Changed</p></body></html>",
            encoding="utf-8",
        )
        write_review(root, review_file)
        data = json.loads(review_file.read_text(encoding="utf-8"))
        if data.get("allow_ja_self_verified") is not True:
            failures.append("write should keep allow_ja_self_verified")
        if data.get("release_languages") != ["en"]:
            failures.append("write should keep an en-only release_languages list")
        privacy = next(item for item in data["records"] if item["path"] == "en/privacy.html")
        if privacy["review_status"] != "unreviewed" or privacy["reviewer"] is not None:
            failures.append(f"a changed hash should reset the review, got {privacy}")
        unchanged = next(item for item in data["records"] if item["path"] == "en/index.html")
        if unchanged["review_status"] != "ai_reviewed" or unchanged["reviewer"] != "ai-qa":
            failures.append(f"an unchanged hash should keep the review, got {unchanged}")
    return failures


def fixture_release_gate(html: str, digest: str) -> list[str]:
    """A full locale matrix: excluded pages stay out, and Final Review OK is required."""
    failures: list[str] = []
    del html, digest
    page_html = (
        "<html><body><p>Effective date: 23 October 2026. "
        "Last updated: 23 October 2026.</p></body></html>"
    )
    page_digest = source_hash(page_html)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        records: list[dict[str, object]] = []
        for locale, page_id, relative in expected_pairs():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page_html, encoding="utf-8")
            record = blank_record(locale, page_id, relative, page_html)
            record["source_hash"] = page_digest
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
        dated = (
            "<html><body><p>Effective date: 23 October 2026. "
            "Last updated: 23 October 2026.</p>"
        )
        (root / "index.html").write_text(
            dated
            + '<p><a href="en/index.html">English</a> '
            + '<a href="ja/index.html">Japanese</a></p></body></html>',
            encoding="utf-8",
        )
        (root / "404.html").write_text(dated + "</body></html>", encoding="utf-8")
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
        ready = {
            "site": {
                "final_review_ok": {
                    "by": "human:gabriel",
                    "date": "2026-10-23",
                    "languages": ["en", "ja"],
                },
                "effective_date": "2026-10-23",
                "self_verified": [],
            }
        }
        checklist.write_text(json.dumps(ready) + "\n", encoding="utf-8")
        errors, notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        if errors:
            failures.append(f"ready release with Final Review OK should pass, got {errors}")
        if sum(item.endswith(": excluded") for item in notices) != 25:
            failures.append(f"expected 25 excluded notices, got {notices}")
        missing_date = json.loads(json.dumps(ready))
        missing_date["site"]["effective_date"] = None
        checklist.write_text(json.dumps(missing_date) + "\n", encoding="utf-8")
        errors, _notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        if not any("effective_date is not set" in item for item in errors):
            failures.append(f"missing effective_date should fail release, got {errors}")
        errors, _notices = check_tree(root, review_file, release=False, checklist_file=checklist)
        if any("effective_date" in item for item in errors):
            failures.append(f"missing effective_date should not fail draft mode, got {errors}")
        checklist.write_text(json.dumps(ready) + "\n", encoding="utf-8")
        (root / "index.html").write_text(
            dated + "<p>{{POSTAL_ADDRESS_IF_REQUIRED}}</p></body></html>",
            encoding="utf-8",
        )
        errors, _notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        if not any("POSTAL_ADDRESS_IF_REQUIRED" in item for item in errors):
            failures.append(f"a postal placeholder should fail release, got {errors}")
        errors, _notices = check_tree(root, review_file, release=False, checklist_file=checklist)
        if any("POSTAL_ADDRESS_IF_REQUIRED" in item for item in errors):
            failures.append(f"a postal placeholder should not fail draft mode, got {errors}")
        (root / "en" / "terms.html").write_text(
            page_html.replace(
                "</p>",
                "</p><p>Governing law and venue are not chosen. Not published in this draft. "
                "retention period pending Gabriel's confirmation.</p>",
            ),
            encoding="utf-8",
        )
        errors, _notices = check_tree(root, review_file, release=True, checklist_file=checklist)
        for marker in (
            "Governing law and venue are not chosen",
            "Not published in this draft",
            "retention period pending Gabriel's confirmation",
        ):
            if not any(marker in item for item in errors):
                failures.append(f"{marker} should fail release, got {errors}")
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
