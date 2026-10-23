#!/usr/bin/env python3
"""Checks for the Bridge Kids static site.

Fails if any HTML or SVG file contains a script, if a stylesheet or
document loads a third-party URL, if an href or src leaves the site
for anything other than an Apple app-store link or the approved
mailto address, if HTML links or fragments are broken, or if the
locale contract is wrong.

Valid HTML is checked separately with the Nu Html Checker in CI.

`python3 scripts/check_site.py --release` also fails when visible page
text, the title, or the meta description still contains draft, TODO,
placeholder, not finished, or "question for counsel", or when a meta
description still starts with "Draft ". The default run does not.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from site_map import (  # noqa: E402
    CONTACT_ADDRESS,
    CONTACT_MAILTO,
    DRAFT_MARK,
    EMAIL_RETENTION_LINE,
    EMAIL_RETENTION_NOTE,
    LEGAL_PAGE_IDS,
    LOCALE_CODES,
    PAGE_IDS,
    PENDING_MARK,
    POSTAL_ADDRESS,
    ROOT_HTML,
)

ROOT = SCRIPT_DIR.parent

ALLOWED_STORE_HOSTS = frozenset({"apps.apple.com", "itunes.apple.com"})
FORBIDDEN_PHRASES = (
    "subscription",
    "in-app purchase",
    "android",
    "google play",
    "google",
    "english-learning",
    "about 3",
    "7 languages",
)
BANNED_TAGS = frozenset(
    {"script", "iframe", "object", "embed", "applet", "base", "form"}
)
URL_ATTRS = ("href", "src", "action", "data", "poster", "srcset")

# Required phrases for locales that are actually launched.
# Japanese phrases are added when the product lead's ja copy lands.
# Excluded locales are skipped. English phrases are never required
# on a non-English page.
LOCALE_PHRASES: dict[str, tuple[tuple[str, frozenset[str]], ...]] = {
    "en": (
        ("children aged 3–10", frozenset({"index", "privacy", "children", "support", "terms"})),
        (EMAIL_RETENTION_LINE, LEGAL_PAGE_IDS),
        ("IP address", frozenset({"privacy"})),
        ("user agent", frozenset({"privacy"})),
    ),
}


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[tuple[str, int]] = []
        self.urls: list[tuple[str, str, int]] = []
        self.bad_tags: list[tuple[str, int]] = []
        self.refreshes: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line, _column = self.getpos()
        attr = {key.lower(): value for key, value in attrs}
        if tag in BANNED_TAGS:
            self.bad_tags.append((tag, line))
        if "id" in attr and attr["id"] is not None:
            self.ids.append((attr["id"], line))
        for key in URL_ATTRS:
            if key not in attr or attr[key] is None:
                continue
            if key == "srcset":
                for candidate in attr[key].split(","):
                    piece = candidate.strip().split()
                    if piece:
                        self.urls.append((key, piece[0], line))
                continue
            self.urls.append((key, attr[key], line))
        if tag == "meta" and (attr.get("http-equiv") or "").lower() == "refresh":
            self.refreshes.append(line)


def classify(url: str) -> str:
    """Return 'internal', 'store', 'mailto', or a short reason the URL is rejected."""
    raw = url.strip()
    if not raw:
        return "empty URL"
    lowered = raw.lower()
    if lowered == CONTACT_MAILTO:
        return "mailto"
    if lowered.startswith(("javascript:", "vbscript:", "data:", "mailto:")):
        return "disallowed URL scheme"
    if raw.startswith("//"):
        return "protocol-relative URL"
    parts = urlsplit(raw)
    if parts.scheme == "" and parts.netloc == "":
        if "\\" in raw:
            return "backslash in URL"
        return "internal"
    host = (parts.hostname or "").lower().rstrip(".")
    if (
        parts.scheme == "https"
        and host in ALLOWED_STORE_HOSTS
        and parts.username is None
        and parts.password is None
        and parts.port in (None, 443)
    ):
        return "store"
    return "external URL is not an app-store link"


def css_references(text: str) -> list[str]:
    import re

    refs: list[str] = []
    for match in re.finditer(r"url\(\s*([^)]+?)\s*\)", text, re.IGNORECASE):
        value = match.group(1).strip().strip("\"'")
        if value and not value.lower().startswith("data:"):
            # data: is rejected by classify; keep it so the caller reports it.
            refs.append(match.group(1).strip().strip("\"'"))
        elif value:
            refs.append(value)
    for match in re.finditer(
        r"@import\s+(?:url\(\s*)?['\"]([^'\"]+)['\"]", text, re.IGNORECASE
    ):
        refs.append(match.group(1))
    return refs


def html_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.html") if ".git" not in path.parts)


def text_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(f"*{suffix}")
        if ".git" not in path.parts and "scripts" not in path.parts
    )


def parse_html(path: Path, text: str) -> Collector:
    collector = Collector()
    collector.feed(text)
    collector.close()
    return collector


def resolve_internal(page: Path, url: str, root: Path) -> tuple[Path, str] | str:
    parts = urlsplit(url.strip())
    fragment = parts.fragment
    path = unquote(parts.path)
    if path.startswith("/"):
        return "site-absolute links are not allowed"
    if not path:
        return page, fragment
    target = (page.parent / path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return "link escapes the site directory"
    if target.is_dir():
        target = target / "index.html"
    return target, fragment


def check_documents(root: Path) -> list[str]:
    import re

    errors: list[str] = []
    pages = html_files(root)
    parsed: dict[Path, Collector] = {}
    ids_by_file: dict[Path, set[str]] = {}

    script_re = re.compile(r"<\s*/?\s*script\b", re.IGNORECASE)
    handler_re = re.compile(r"(?i)(?:^|[\s<])on[a-z]+\s*=")

    for path in pages:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append(f"{relative}: not valid UTF-8 ({exc})")
            continue
        if script_re.search(text):
            errors.append(f"{relative}: contains a script tag")
        if re.search(r"(?i)javascript\s*:", text):
            errors.append(f"{relative}: contains a javascript URL")
        if handler_re.search(text):
            errors.append(f"{relative}: contains an inline event handler")
        collector = parse_html(path, text)
        parsed[path] = collector
        seen: dict[str, int] = {}
        for element_id, line in collector.ids:
            if element_id in seen:
                errors.append(
                    f"{relative}:{line}: duplicate id {element_id!r} "
                    f"(also on line {seen[element_id]})"
                )
            else:
                seen[element_id] = line
        ids_by_file[path] = set(seen)
        for tag, line in collector.bad_tags:
            errors.append(f"{relative}:{line}: disallowed <{tag}> tag")
        for line in collector.refreshes:
            errors.append(f"{relative}:{line}: meta refresh is not allowed")

    for path, collector in parsed.items():
        relative = path.relative_to(root).as_posix()
        for attr, url, line in collector.urls:
            kind = classify(url)
            if kind in {"store", "mailto"}:
                continue
            if kind != "internal":
                errors.append(f"{relative}:{line}: {attr} {url!r} is not allowed ({kind})")
                continue
            resolved = resolve_internal(path, url, root)
            if isinstance(resolved, str):
                errors.append(f"{relative}:{line}: {url!r} {resolved}")
                continue
            target, fragment = resolved
            if not target.is_file():
                errors.append(f"{relative}:{line}: broken link {url!r}")
                continue
            if not fragment:
                continue
            if target.suffix.lower() != ".html":
                errors.append(
                    f"{relative}:{line}: fragment on a non-HTML file {url!r}"
                )
                continue
            known = ids_by_file.get(target)
            if known is None:
                # Linked HTML that was not parsed (outside the tree) cannot happen
                # after the escape check. Parse it if a link points at a file
                # the walk skipped.
                known = set()
            if fragment not in known:
                errors.append(
                    f"{relative}:{line}: broken fragment {url!r} "
                    f"(no id {fragment!r} in {target.relative_to(root).as_posix()})"
                )

    for path in text_files(root, ".css") + text_files(root, ".svg"):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if script_re.search(text) or re.search(r"(?i)javascript\s*:", text):
            errors.append(f"{relative}: contains script or a javascript URL")
        if path.suffix == ".css" and re.search(r"(?i)expression\s*\(", text):
            errors.append(f"{relative}: contains a CSS expression()")
        for url in css_references(text):
            kind = classify(url)
            if kind == "store":
                errors.append(
                    f"{relative}: stylesheet must not load an app-store URL ({url})"
                )
                continue
            if kind != "internal":
                errors.append(f"{relative}: disallowed CSS reference {url!r} ({kind})")
                continue
            resolved = resolve_internal(path, url, root)
            if isinstance(resolved, str):
                errors.append(f"{relative}: {url!r} {resolved}")
                continue
            target, _fragment = resolved
            if not target.is_file():
                errors.append(f"{relative}: broken CSS reference {url!r}")

    return errors


def launch_locales(root: Path) -> set[str]:
    review = root / "review.json"
    if not review.is_file():
        return {"en"}
    try:
        data = json.loads(review.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"en"}
    from review_check import parse_release_languages

    languages, errors = parse_release_languages(data if isinstance(data, dict) else {})
    if errors or not languages:
        return {"en"}
    return set(languages)


def drafts_are_required(root: Path, launch: set[str]) -> bool:
    from review_check import publication_stamp

    return publication_stamp(root / "release" / "checklist.json", sorted(launch)) is None


def required_phrase_errors(relative: str, text: str, launch: set[str]) -> list[str]:
    """Phrases for one page. Excluded locales and unknown locale tables are skipped."""
    parts = Path(relative).parts
    page_id = Path(relative).stem
    if len(parts) == 2 and parts[0] in LOCALE_CODES:
        phrase_locale: str | None = parts[0]
        in_locale_folder = True
    elif relative in ROOT_HTML:
        phrase_locale = "en"
        in_locale_folder = False
    else:
        return []
    if phrase_locale not in launch:
        return []
    errors: list[str] = []
    for phrase, pages in LOCALE_PHRASES.get(phrase_locale, ()):
        if page_id not in pages:
            continue
        present = phrase in text or (
            phrase == "children aged 3–10" and "children aged 3-10" in text
        )
        if not present:
            errors.append(f"{relative}: missing required phrase {phrase!r}")
    if phrase_locale != "en":
        return errors
    if in_locale_folder and page_id in LEGAL_PAGE_IDS:
        for token in (POSTAL_ADDRESS, "TODO", CONTACT_MAILTO, CONTACT_ADDRESS):
            if token not in text:
                errors.append(f"{relative}: missing {token}")
        if f"<!-- {EMAIL_RETENTION_NOTE} -->" not in text:
            errors.append(f"{relative}: missing the email-retention confirmation comment")
    if in_locale_folder and page_id == "privacy":
        if "do not use them for tracking" not in text:
            errors.append(f"{relative}: missing the host-log disclosure")
    return errors


def locale_of(relative: str) -> str | None:
    parts = Path(relative).parts
    if len(parts) == 2 and parts[0] in LOCALE_CODES:
        return parts[0]
    return None


def pending_banner_errors(relative: str, text: str) -> list[str]:
    """Non-English pages need the translation banner. Japanese is authored, so it does not."""
    locale = locale_of(relative)
    if locale is not None and locale not in {"en", "ja"}:
        if PENDING_MARK not in text:
            return [f"{relative}: missing the {PENDING_MARK} banner"]
        return []
    if PENDING_MARK in text:
        who = "Japanese" if locale == "ja" else "English"
        return [f"{relative}: {who} page must not say {PENDING_MARK}"]
    return []


def check_contract(root: Path) -> list[str]:
    errors: list[str] = []
    found = {path.relative_to(root).as_posix() for path in html_files(root)}
    expected = set(ROOT_HTML)
    for code in LOCALE_CODES:
        for page_id in PAGE_IDS:
            expected.add(f"{code}/{page_id}.html")
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    for relative in missing:
        errors.append(f"missing {relative}")
    for relative in extra:
        errors.append(f"unexpected HTML file {relative}")

    launch = launch_locales(root)
    drafts_required = drafts_are_required(root, launch)
    for path in html_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if drafts_required:
            if DRAFT_MARK not in text:
                errors.append(f"{relative}: missing the draft mark in an HTML comment")
            if f"<!-- {DRAFT_MARK} -->" not in text:
                errors.append(f"{relative}: draft mark must appear as an HTML comment")
        elif locale_of(relative) not in launch and locale_of(relative) is not None:
            if "Effective date:" in text or "施行日：" in text:
                errors.append(f"{relative}: a held language must not show the effective date")
            draft_line = "付の下書きです" if locale_of(relative) == "ja" else "Draft dated"
            if draft_line not in text:
                errors.append(f"{relative}: a held language must keep the draft date line")
        elif DRAFT_MARK in text:
            errors.append(f"{relative}: draft mark must be removed once the effective date is set")
        errors.extend(pending_banner_errors(relative, text))
        if locale_of(relative) != "ja" and (
            "fordang.github.io" in text or "hosted by GitHub Pages" in text
        ):
            errors.append(
                f"{relative}: names a site host that deploy config does not set"
            )
        if "{{CONTACT_EMAIL}}" in text:
            errors.append(f"{relative}: still contains the contact-email placeholder")
        if "{{EMAIL_RETENTION_PERIOD}}" in text:
            errors.append(f"{relative}: still contains the email-retention placeholder")
        lowered = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered:
                errors.append(f"{relative}: contains {phrase!r}")
        errors.extend(required_phrase_errors(relative, text, launch))
    return errors


def check_tree(root: Path, *, contract: bool) -> list[str]:
    errors = check_documents(root)
    if contract:
        errors.extend(check_contract(root))
    return errors


# Japanese counterparts of draft, placeholder, and not finished. TODO stays Latin.
# These phrases live here so scripts/content_ja.py can stay the product lead's text.
RELEASE_BANNED_PHRASES_JA: tuple[str, ...] = (
    "下書き",
    "仮の表示",
    "まだ確定していません",
)

# Word matches, not raw substrings: "today" is not a TODO.
RELEASE_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("draft", re.compile(r"(?<![A-Za-z])draft(?![A-Za-z])", re.I)),
    ("todo", re.compile(r"(?<![A-Za-z])todo(?![A-Za-z])", re.I)),
    ("placeholder", re.compile(r"(?<![A-Za-z])placeholder(?![A-Za-z])", re.I)),
    ("not finished", re.compile(r"(?<![A-Za-z])not finished(?![A-Za-z])", re.I)),
    ("question for counsel", re.compile(r"(?<![A-Za-z])question for counsel(?![A-Za-z])", re.I)),
    *(
        (phrase, re.compile(re.escape(phrase)))
        for phrase in RELEASE_BANNED_PHRASES_JA
    ),
)
GATED_MARKER_REPLACEMENTS = (
    ("{{POSTAL_ADDRESS_IF_REQUIRED}}", "POSTAL_RESOLVED"),
    ("Not published in this draft", "Telephone omitted"),
    ("Governing law and venue are not chosen", "Governing law and venue remain unset"),
    (
        "retention period pending Gabriel's confirmation",
        "retention period pending confirmation",
    ),
)


class ReleaseSurfaceParser(HTMLParser):
    """Body text, title text, and meta descriptions. Comments and attributes are out."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_parts: list[str] = []
        self.title_parts: list[str] = []
        self.descriptions: list[str] = []
        self.in_body = False
        self.in_title = False
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body":
            self.in_body = True
        if tag in {"script", "style"}:
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            named = {key.lower(): value or "" for key, value in attrs}
            if named.get("name", "").lower() == "description":
                self.descriptions.append(named.get("content", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
        if tag == "body":
            self.in_body = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_body and self.skip == 0:
            self.body_parts.append(data)


def release_surface(html: str) -> tuple[str, list[str]]:
    parser = ReleaseSurfaceParser()
    parser.feed(html)
    parser.close()
    title = "".join(parser.title_parts)
    body = "".join(parser.body_parts)
    surface = "\n".join([title, *parser.descriptions, body])
    return surface, parser.descriptions


def release_scan_paths(root: Path) -> list[Path]:
    """Released languages, plus the root pages. A held language's draft line stays."""
    review = root / "review.json"
    languages: list[str] | None = None
    if review.is_file():
        try:
            data = json.loads(review.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = None
        raw = data.get("release_languages") if isinstance(data, dict) else None
        if isinstance(raw, list) and raw and all(isinstance(code, str) for code in raw):
            languages = raw
    if languages is None:
        return html_files(root)
    paths: list[Path] = []
    for name in ("index.html", "404.html"):
        candidate = root / name
        if candidate.is_file():
            paths.append(candidate)
    for code in languages:
        folder = root / code
        if folder.is_dir():
            paths.extend(sorted(folder.glob("*.html")))
    return paths


def release_text_errors(root: Path) -> list[str]:
    """Case-insensitive draft words in visible text, title, and meta description."""
    errors: list[str] = []
    for path in release_scan_paths(root):
        html = path.read_text(encoding="utf-8")
        surface, descriptions = release_surface(html)
        label = path.relative_to(root).as_posix()
        for token, pattern in RELEASE_TEXT_PATTERNS:
            if pattern.search(surface):
                errors.append(
                    f"{label}: release blocked by {token!r} in visible text, title, or meta description"
                )
        for description in descriptions:
            if description.startswith("Draft "):
                errors.append(f"{label}: meta description still starts with 'Draft '")
    return errors


def scrub_release_words(html: str) -> str:
    """Replace gated words in text nodes, titles, and meta descriptions."""

    def scrub_piece(piece: str) -> str:
        for _token, pattern in RELEASE_TEXT_PATTERNS:
            piece = pattern.sub("ok", piece)
        return piece

    def scrub_tag(tag: str) -> str:
        if not tag.lower().startswith("<meta") or "description" not in tag.lower():
            return tag

        def repl(match: re.Match[str]) -> str:
            return match.group(1) + scrub_piece(match.group(2)) + match.group(3)

        return re.sub(r'(content=")(.*?)(")', repl, tag, count=1, flags=re.S)

    parts = re.split(r"(<!--.*?-->|<[^>]*>)", html, flags=re.S)
    cleaned: list[str] = []
    for part in parts:
        if part.startswith("<!--"):
            cleaned.append(part)
        elif part.startswith("<"):
            cleaned.append(scrub_tag(part))
        else:
            cleaned.append(scrub_piece(part))
    return "".join(cleaned)


def _launch_html_paths(root: Path) -> list[Path]:
    paths = [root / "index.html", root / "404.html"]
    english = root / "en"
    if english.is_dir():
        paths.extend(sorted(english.glob("*.html")))
    return [path for path in paths if path.is_file()]


def _copy_html_tree(source: Path, dest: Path) -> None:
    for path in html_files(source):
        target = dest / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    review = source / "review.json"
    if review.is_file():
        shutil.copyfile(review, dest / "review.json")


def _stage_marker_replaced_copy(source: Path, dest: Path) -> None:
    """QA's simulation: Final Review OK, a date, and the four gated markers replaced."""
    _copy_html_tree(source, dest)
    for path in html_files(dest):
        text = path.read_text(encoding="utf-8")
        for old, new in GATED_MARKER_REPLACEMENTS:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
    effective = "<p>Effective date: 23 October 2026. Last updated: 23 October 2026.</p>\n"
    for path in _launch_html_paths(dest):
        text = path.read_text(encoding="utf-8")
        text = text.replace(DRAFT_MARK, "")
        if "Effective date:" not in text:
            text = text.replace("</body>", effective + "</body>", 1)
        path.write_text(text, encoding="utf-8")
    _refresh_simulated_review(dest)


def _refresh_simulated_review(dest: Path) -> None:
    import review_check

    review_file = dest / "review.json"
    data = json.loads(review_file.read_text(encoding="utf-8"))
    for record in data["records"]:
        html = (dest / record["path"]).read_text(encoding="utf-8")
        record["source_hash"] = review_check.source_hash(html)
        if record.get("locale") == "en":
            record["author"] = "ai-product-lead"
            record["reviewer"] = "ai-ja-reviewer"
            record["review_status"] = "ai_reviewed"
            record["reviewed_at"] = "2026-10-23"
            record["needs_native_check"] = False
            record["self_verified"] = False
    listed_blocks: list[str] = []
    for block in data.get("self_verified_blocks") or []:
        if not isinstance(block, dict):
            continue
        relative = block.get("path")
        block_id = block.get("block_id")
        if not isinstance(relative, str) or not isinstance(block_id, str):
            continue
        html_path = dest / relative
        if html_path.is_file():
            refreshed = review_check.block_source_hash(
                html_path.read_text(encoding="utf-8"),
                block_id,
            )
            if refreshed is not None:
                block["source_hash"] = refreshed
        listed_blocks.append(f"{relative}#{block_id}")
    review_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    languages = data.get("release_languages")
    checklist = dest / "release" / "checklist.json"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text(
        json.dumps(
            {
                "site": {
                    "final_review_ok": {
                        "by": "human:gabriel",
                        "date": "2026-10-23",
                        "languages": languages,
                    },
                    "effective_date": "2026-10-23",
                    "self_verified": [],
                    "self_verified_blocks": listed_blocks,
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _release_check(dest: Path) -> tuple[list[str], list[str]]:
    import review_check

    return review_check.check_tree(
        dest,
        dest / "review.json",
        release=True,
        checklist_file=dest / "release" / "checklist.json",
        ja_log_file=dest / "release" / "ja-review-log.json",
    )


def test_ja_release_banned_phrases() -> list[str]:
    """Japanese draft words fail --release, and ja does not need the translation banner."""
    failures: list[str] = []
    if pending_banner_errors("ja/privacy.html", "<html><body><p>本文</p></body></html>"):
        failures.append("an authored ja page should not need the translation-pending banner")
    ja_banner = pending_banner_errors(
        "ja/privacy.html",
        f"<html><body><p>{PENDING_MARK}</p></body></html>",
    )
    if not ja_banner:
        failures.append("ja must not show the translation-pending banner")
    held = pending_banner_errors("zh-Hans/privacy.html", "<html><body><p>English draft</p></body></html>")
    if not any(PENDING_MARK in item for item in held):
        failures.append("a non-ja excluded locale should still require the translation banner")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        page = root / "sample.html"
        page.write_text(
            "<!DOCTYPE html><html lang=\"ja\"><head><title>確認</title>"
            '<meta name="description" content="確認ページです。"></head>'
            "<body><p>本日の利用時間です。</p></body></html>",
            encoding="utf-8",
        )
        if release_text_errors(root):
            failures.append("ordinary Japanese text should pass the release word scan")
        for phrase in RELEASE_BANNED_PHRASES_JA:
            page.write_text(
                f"<!DOCTYPE html><html><body><p>{phrase}</p></body></html>",
                encoding="utf-8",
            )
            errors = release_text_errors(root)
            if not any(phrase in item for item in errors):
                failures.append(f"release scan should report {phrase!r}, got {errors}")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        held = root / "ja"
        held.mkdir()
        (held / "privacy.html").write_text(
            "<!DOCTYPE html><html lang=\"ja\"><head><title>確認</title></head>"
            "<body><p>2026年10月23日付の下書きです。</p></body></html>",
            encoding="utf-8",
        )
        (root / "review.json").write_text(
            json.dumps({"version": 1, "release_languages": ["en"], "records": []}),
            encoding="utf-8",
        )
        if release_text_errors(root):
            failures.append("a held language's draft date line should not fail --release")
        data = json.loads((root / "review.json").read_text(encoding="utf-8"))
        data["release_languages"] = ["en", "ja"]
        (root / "review.json").write_text(json.dumps(data), encoding="utf-8")
        released = release_text_errors(root)
        if not any("下書き" in item for item in released):
            failures.append(f"ja draft wording should fail once ja is released, got {released}")
    return failures


def test_ja_dates() -> list[str]:
    """Japanese dates are unpadded, and a held language keeps the draft date line."""
    failures: list[str] = []
    import build_site
    import content_ja as content

    if content.ja_date_label("2026-01-05") != "2026年1月5日":
        failures.append(
            f"2026-01-05 should be 2026年1月5日, got {content.ja_date_label('2026-01-05')}"
        )
    if content.ja_date_label("2026-11-01") != "2026年11月1日":
        failures.append(
            f"2026-11-01 should be 2026年11月1日, got {content.ja_date_label('2026-11-01')}"
        )
    if content.ja_date_label("2026-10-23") != "2026年10月23日":
        failures.append(
            f"2026-10-23 should keep both digits, got {content.ja_date_label('2026-10-23')}"
        )
    common = dict(
        title="T",
        description="D",
        heading="H",
        body="<p>本文</p>",
        css_href="../css/site.css",
        icon_prefix="../",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
    )
    published = build_site.page(
        **common,
        published=("2026-01-05", "5 January 2026"),
        lang="ja",
        released=True,
    )
    expected = (
        "施行日：<time datetime=\"2026-01-05\">2026年1月5日</time>"
        "　最終更新日：<time datetime=\"2026-01-05\">2026年1月5日</time>"
    )
    if expected not in published:
        failures.append("published ja dates should be unpadded and separated by a full-width space")
    if "2026年01月" in published or "月05日" in published:
        failures.append("published ja dates must not zero-pad the month or day")
    english = build_site.page(
        **common,
        published=("2026-01-05", "5 January 2026"),
        lang="en",
        released=True,
    )
    if "Effective date:" not in english or "5 January 2026" not in english:
        failures.append("the English effective date should stay in the English format")
    if "年" in english:
        failures.append("the English page should not use the Japanese date format")
    held = build_site.page(
        **common,
        published=("2026-11-01", "1 November 2026"),
        lang="ja",
        released=False,
    )
    if "付の下書きです" not in held:
        failures.append("a held language should keep the draft date line after Final Review OK")
    if "施行日" in held:
        failures.append("a held language should not show the effective date")
    return failures


def test_r2_markers_replaced_still_blocks_release_words() -> list[str]:
    """After the four gated markers are gone, draft words still fail --release."""
    failures: list[str] = []
    expected = {
        "en/privacy.html": (
            "are not finished",
            "Name the site host when a deploy target is configured.",
        ),
        "en/children.html": (
            "are not finished",
            "Please read it as a draft",
            "question for counsel",
        ),
        "en/terms.html": (
            "These are draft terms for the Bridge Kids app.",
            "This draft does not name",
            "TODO:",
            "included here as a draft",
            "This section is a draft",
            "This draft does not choose",
            "still a placeholder",
        ),
        "en/support.html": ("TODO:", "Leave the placeholder"),
        "en/index.html": ("still a placeholder",),
        "index.html": ("still a placeholder",),
    }
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        _stage_marker_replaced_copy(ROOT, dest)
        for relative, phrases in expected.items():
            surface, _descriptions = release_surface(
                (dest / relative).read_text(encoding="utf-8")
            )
            for phrase in phrases:
                if phrase not in surface:
                    failures.append(f"{relative}: simulation dropped {phrase!r}")
        for path in html_files(dest):
            text = path.read_text(encoding="utf-8")
            for old, _new in GATED_MARKER_REPLACEMENTS:
                if old in text:
                    failures.append(f"{path.name}: gated marker {old!r} was not replaced")
        word_errors = release_text_errors(dest)
        joined = "\n".join(word_errors)
        for token in ("draft", "todo", "placeholder", "not finished", "question for counsel"):
            if f"release blocked by {token!r}" not in joined:
                failures.append(f"release scan should report {token!r}, got {word_errors}")
        if "meta description still starts with 'Draft '" not in joined:
            failures.append(f"Draft meta prefix should fail --release, got {word_errors}")
        for relative in expected:
            if not any(item.startswith(f"{relative}:") for item in word_errors):
                failures.append(f"{relative} should still fail the release word scan")
        errors, _notices = _release_check(dest)
        other = [
            item
            for item in errors
            if "release blocked by" not in item and "meta description still starts" not in item
        ]
        if other:
            failures.append(
                "expected only release-word failures after the four markers were replaced, "
                f"got {other}"
            )
        if not any("release blocked by" in item for item in errors):
            failures.append(f"--release should still fail, got {errors}")
        draft_errors, _draft_notices = _release_check_mode(dest, release=False)
        if any("release blocked by" in item or "Draft '" in item for item in draft_errors):
            failures.append(f"draft mode should ignore the word scan, got {draft_errors}")
    return failures


def _release_check_mode(dest: Path, *, release: bool) -> tuple[list[str], list[str]]:
    import review_check

    return review_check.check_tree(
        dest,
        dest / "review.json",
        release=release,
        checklist_file=dest / "release" / "checklist.json",
        ja_log_file=dest / "release" / "ja-review-log.json",
    )


def test_r2_clean_pages_pass_release_word_scan() -> list[str]:
    """A copy with the gated words removed can pass --release."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        sample = dest / "sample.html"
        sample.write_text(
            "<!DOCTYPE html><html><head><title>Ready</title>"
            '<meta name="description" content="Ready page."></head>'
            '<body><p class="draft">today\'s play time</p>'
            "<!-- English draft TODO placeholder not finished --></body></html>",
            encoding="utf-8",
        )
        if release_text_errors(dest):
            failures.append("today, class=draft, and comments must not fail the release scan")
        sample.unlink()
        _stage_marker_replaced_copy(ROOT, dest)
        for path in html_files(dest):
            path.write_text(scrub_release_words(path.read_text(encoding="utf-8")), encoding="utf-8")
        _refresh_simulated_review(dest)
        privacy = (dest / "en" / "privacy.html").read_text(encoding="utf-8")
        surface, _descriptions = release_surface(privacy)
        if "today" not in surface:
            failures.append("the clean scan should still allow today's play time")
        if 'class="draft"' not in privacy:
            failures.append("class=draft should remain an attribute and not be part of the scan")
        comment = (dest / "zh-Hans" / "privacy.html").read_text(encoding="utf-8")
        if "English draft" not in comment:
            failures.append("an HTML comment may still say draft without failing --release")
        word_errors = release_text_errors(dest)
        if word_errors:
            failures.append(f"clean pages should pass the release word scan, got {word_errors}")
        errors, _notices = _release_check(dest)
        if errors:
            failures.append(f"clean pages should pass --release, got {errors}")
    return failures


def write_page(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def self_test() -> list[str]:
    """Run the document checks against tiny fixtures. Returns failures."""
    failures: list[str] = []

    def expect(label: str, html_text: str, must_contain: str | None, css: str | None = None) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_page(root, "index.html", html_text)
            if css is not None:
                write_page(root, "site.css", css)
            errors = check_documents(root)
            blob = "\n".join(errors)
            if must_contain is None:
                if errors:
                    failures.append(f"{label}: expected no errors, got {errors}")
            elif must_contain not in blob:
                failures.append(f"{label}: expected {must_contain!r} in {errors}")

    good = """<!DOCTYPE html>
<html><head><title>Ok</title><link rel="stylesheet" href="site.css"></head>
<body><p id="ok">Hi</p><a href="#ok">Here</a>
<a href="https://apps.apple.com/account/subscriptions">Apple</a>
<a href="mailto:gabrieljohnfordan@gmail.com">gabrieljohnfordan@gmail.com</a>
</body></html>
"""
    expect("clean page", good, None, css="body { color: #111; }\n")
    expect(
        "script tag",
        "<!DOCTYPE html><html><body><script>bad()</script></body></html>",
        "script tag",
    )
    expect(
        "google play link",
        '<!DOCTYPE html><html><body><a href="https://play.google.com/store/apps">x</a></body></html>',
        "not an app-store link",
    )
    expect(
        "other mailto",
        '<!DOCTYPE html><html><body><a href="mailto:other@example.com">x</a></body></html>',
        "disallowed URL scheme",
    )
    expect(
        "external link",
        '<!DOCTYPE html><html><body><a href="https://example.com/">x</a></body></html>',
        "not an app-store link",
    )
    expect(
        "javascript url",
        '<!DOCTYPE html><html><body><a href="javascript:alert(1)">x</a></body></html>',
        "javascript",
    )
    expect(
        "event handler",
        '<!DOCTYPE html><html><body><a href="#a" id="a" onclick="bad()">x</a></body></html>',
        "event handler",
    )
    expect(
        "broken link",
        '<!DOCTYPE html><html><body><a href="missing.html">x</a></body></html>',
        "broken link",
    )
    expect(
        "broken fragment",
        '<!DOCTYPE html><html><body><a href="#missing">x</a></body></html>',
        "broken fragment",
    )
    expect(
        "protocol relative",
        '<!DOCTYPE html><html><body><a href="//example.com/a">x</a></body></html>',
        "protocol-relative",
    )
    expect(
        "spoofed store host",
        '<!DOCTYPE html><html><body><a href="https://apps.apple.com.evil.com/">x</a></body></html>',
        "not an app-store link",
    )
    expect(
        "http store link",
        '<!DOCTYPE html><html><body><a href="http://apps.apple.com/app">x</a></body></html>',
        "not an app-store link",
    )
    expect(
        "remote css",
        "<!DOCTYPE html><html><head><link rel=\"stylesheet\" href=\"site.css\"></head><body></body></html>",
        "disallowed CSS",
        css='@import "https://example.com/font.css";\n',
    )
    ja_text = "<html><body><p>これは下書きです。</p></body></html>"
    if required_phrase_errors("ja/privacy.html", ja_text, {"en"}):
        failures.append("excluded ja pages should skip English phrase checks")
    if required_phrase_errors("ja/privacy.html", ja_text, {"en", "ja"}):
        failures.append("ja must not be checked for English phrases before its own table exists")
    en_errors = required_phrase_errors("en/privacy.html", "<html><body><p>Hello</p></body></html>", {"en"})
    for phrase in ("children aged 3–10", EMAIL_RETENTION_LINE, "IP address", "user agent"):
        if not any(phrase in item for item in en_errors):
            failures.append(f"en privacy should require {phrase!r}, got {en_errors}")
    held = required_phrase_errors(
        "zh-Hans/terms.html",
        "<html><body><p>Hello</p></body></html>",
        {"en"},
    )
    if held:
        failures.append(f"an excluded locale should skip phrase checks, got {held}")
    if any("GitHub Pages" in item for item in en_errors):
        failures.append("en privacy should not require a guessed GitHub Pages host")
    failures.extend(test_ja_release_banned_phrases())
    failures.extend(test_ja_dates())
    failures.extend(test_r2_markers_replaced_still_blocks_release_words())
    failures.extend(test_r2_clean_pages_pass_release_word_scan())
    import review_check

    failures.extend(review_check.fixture_self_verified_blocks())
    return failures


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    release = "--release" in args
    unknown = [arg for arg in args if arg != "--release"]
    if unknown:
        print("Usage: python3 scripts/check_site.py [--release]", file=sys.stderr)
        return 2
    failures = self_test()
    if failures:
        print("Checker self-test failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    errors = check_tree(ROOT, contract=True)
    import review_check

    review_data, review_errors = review_check.load_review(ROOT / "review.json")
    errors.extend(review_errors)
    if isinstance(review_data, dict):
        errors.extend(
            review_check.self_verified_block_errors(
                ROOT,
                review_data,
                release=release,
                allow_ja_self_verified=review_data.get("allow_ja_self_verified") is True,
                release_languages=sorted(launch_locales(ROOT)),
            )
        )
    if release:
        errors.extend(release_text_errors(ROOT))
    if errors:
        print(f"{len(errors)} site check(s) failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    count = len(html_files(ROOT))
    print(
        f"OK: {count} HTML files, no script tags, no disallowed external URLs, "
        "no broken internal links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
