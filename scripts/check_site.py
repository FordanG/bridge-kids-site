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
placeholder, not finished, "question for counsel", "counsel still has to",
"still has to review", or "TBD before store release", or when a meta
description still starts with "Draft ". That scan covers index.html,
404.html, and the locales named in review.json. The default run does not.
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
    SITE_URL,
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
    canonical_host = (urlsplit(SITE_URL).hostname or "").lower().rstrip(".")
    if (
        parts.scheme == "https"
        and host == canonical_host
        and parts.username is None
        and parts.password is None
        and parts.port in (None, 443)
    ):
        return "canonical"
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
            if kind in {"store", "mailto", "canonical"}:
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


def required_phrase_errors(
    relative: str,
    text: str,
    launch: set[str],
    *,
    drafts_required: bool = True,
) -> list[str]:
    """Phrases for one page. Excluded locales and unknown locale tables are skipped.

    Postal placeholder, TODO, and the retention-confirmation comment are
    required only while the publication stamp is absent. The contact
    address and the visible retention sentence stay required after it.
    """
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
        draft_tokens = (POSTAL_ADDRESS, "TODO") if drafts_required else ()
        for token in (*draft_tokens, CONTACT_MAILTO, CONTACT_ADDRESS):
            if token not in text:
                errors.append(f"{relative}: missing {token}")
        if drafts_required and f"<!-- {EMAIL_RETENTION_NOTE} -->" not in text:
            errors.append(f"{relative}: missing the email-retention confirmation comment")
    if in_locale_folder and page_id == "privacy":
        if "do not use them for tracking" not in text:
            errors.append(f"{relative}: missing the host-log disclosure")
    return errors


def expected_html_paths(root: Path) -> set[str]:
    """Draft trees include every locale. A stamped tree ships release languages only."""
    launch = launch_locales(root)
    codes: tuple[str, ...] | set[str]
    if drafts_are_required(root, launch):
        codes = LOCALE_CODES
    else:
        codes = launch
    expected = set(ROOT_HTML)
    for code in codes:
        for page_id in PAGE_IDS:
            expected.add(f"{code}/{page_id}.html")
    return expected


def check_contract(root: Path) -> list[str]:
    errors: list[str] = []
    found = {path.relative_to(root).as_posix() for path in html_files(root)}
    expected = expected_html_paths(root)
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
        elif DRAFT_MARK in text:
            errors.append(f"{relative}: draft mark must be removed once the effective date is set")
        parts = Path(relative).parts
        locale = parts[0] if len(parts) == 2 and parts[0] in LOCALE_CODES else None
        if locale is not None and locale != "en":
            if PENDING_MARK not in text:
                errors.append(f"{relative}: missing the {PENDING_MARK} banner")
        elif PENDING_MARK in text:
            errors.append(f"{relative}: English page must not say {PENDING_MARK}")
        if "{{CONTACT_EMAIL}}" in text:
            errors.append(f"{relative}: still contains the contact-email placeholder")
        if "{{EMAIL_RETENTION_PERIOD}}" in text:
            errors.append(f"{relative}: still contains the email-retention placeholder")
        if "fordang.github.io" in text or "hosted by GitHub Pages" in text:
            errors.append(
                f"{relative}: names a site host that deploy config does not set"
            )
        lowered = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered:
                errors.append(f"{relative}: contains {phrase!r}")
        errors.extend(
            required_phrase_errors(
                relative, text, launch, drafts_required=drafts_required
            )
        )
    return errors


def check_tree(root: Path, *, contract: bool) -> list[str]:
    errors = check_documents(root)
    if contract:
        errors.extend(check_contract(root))
    return errors


# Word matches, not raw substrings: "today" is not a TODO.
RELEASE_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("draft", re.compile(r"(?<![A-Za-z])draft(?![A-Za-z])", re.I)),
    ("todo", re.compile(r"(?<![A-Za-z])todo(?![A-Za-z])", re.I)),
    ("placeholder", re.compile(r"(?<![A-Za-z])placeholder(?![A-Za-z])", re.I)),
    ("not finished", re.compile(r"(?<![A-Za-z])not finished(?![A-Za-z])", re.I)),
    ("question for counsel", re.compile(r"(?<![A-Za-z])question for counsel(?![A-Za-z])", re.I)),
    ("counsel still has to", re.compile(r"(?<![A-Za-z])counsel still has to(?![A-Za-z])", re.I)),
    ("still has to review", re.compile(r"(?<![A-Za-z])still has to review(?![A-Za-z])", re.I)),
    (
        "TBD before store release",
        re.compile(r"(?<![A-Za-z])TBD before store release(?![A-Za-z])", re.I),
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


def ship_html_files(root: Path) -> list[Path]:
    """Pages a release ships: root pages plus release_languages.

    Without review.json, every HTML file is scanned so a one-file fixture
    still exercises the banned phrases.
    """
    if not (root / "review.json").is_file():
        return html_files(root)
    launch = launch_locales(root)
    chosen: list[Path] = []
    for path in html_files(root):
        relative = path.relative_to(root).as_posix()
        parts = Path(relative).parts
        if relative in ROOT_HTML or (len(parts) == 2 and parts[0] in launch):
            chosen.append(path)
    return chosen


def release_text_errors(root: Path) -> list[str]:
    """Case-insensitive draft words in visible text, title, and meta description."""
    errors: list[str] = []
    for path in ship_html_files(root):
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


def _replace_gated_markers(dest: Path) -> None:
    for path in html_files(dest):
        text = path.read_text(encoding="utf-8")
        for old, new in GATED_MARKER_REPLACEMENTS:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def _strip_launch_draft_chrome(dest: Path) -> None:
    effective = "<p>Effective date: 23 October 2026. Last updated: 23 October 2026.</p>\n"
    for path in _launch_html_paths(dest):
        text = path.read_text(encoding="utf-8")
        text = text.replace(DRAFT_MARK, "")
        if "Effective date:" not in text:
            text = text.replace("</body>", effective + "</body>", 1)
        path.write_text(text, encoding="utf-8")


def _stage_marker_replaced_copy(source: Path, dest: Path) -> None:
    """Replace the four gated markers and keep this fixture's own unstamped checklist.

    The checklist is written here. It is not the repository checklist, so a
    stamped Final Review OK on the real site cannot change this test.
    """
    _copy_html_tree(source, dest)
    _replace_gated_markers(dest)
    _refresh_simulated_review(dest, stamp=False)


def _refresh_simulated_review(dest: Path, *, stamp: bool = False) -> None:
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
    review_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    languages = data.get("release_languages")
    checklist = dest / "release" / "checklist.json"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    if stamp:
        final_review_ok: dict[str, object] | None = {
            "by": "human:gabriel",
            "date": "2026-10-23",
            "languages": languages,
        }
        effective_date: str | None = "2026-10-23"
    else:
        final_review_ok = None
        effective_date = None
    checklist.write_text(
        json.dumps(
            {
                "site": {
                    "final_review_ok": final_review_ok,
                    "effective_date": effective_date,
                    "self_verified": [],
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


def test_r2_markers_replaced_still_blocks_release_words() -> list[str]:
    """After the four gated markers are gone, draft words still fail --release."""
    failures: list[str] = []
    expected = {
        "en/privacy.html": (
            "are not finished",
            "TBD before store release",
            "https://bridgekids.vendrato.com",
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
        checklist = json.loads((dest / "release" / "checklist.json").read_text(encoding="utf-8"))
        site = checklist.get("site") if isinstance(checklist, dict) else None
        if not isinstance(site, dict) or site.get("final_review_ok") is not None or site.get("effective_date") is not None:
            failures.append(f"the marker fixture checklist must stay unstamped, got {checklist}")
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
        for token in (
            "draft",
            "todo",
            "placeholder",
            "not finished",
            "question for counsel",
            "TBD before store release",
        ):
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
            if "release blocked by" not in item
            and "meta description still starts" not in item
            and "Final Review OK is not recorded" not in item
            and "effective_date is not set" not in item
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
        _copy_html_tree(ROOT, dest)
        _replace_gated_markers(dest)
        _strip_launch_draft_chrome(dest)
        for path in html_files(dest):
            path.write_text(scrub_release_words(path.read_text(encoding="utf-8")), encoding="utf-8")
        _refresh_simulated_review(dest, stamp=True)
        privacy = (dest / "en" / "privacy.html").read_text(encoding="utf-8")
        surface, _descriptions = release_surface(privacy)
        if "today" not in surface:
            failures.append("the clean scan should still allow today's play time")
        if 'class="draft"' not in privacy:
            failures.append("class=draft should remain an attribute and not be part of the scan")
        comment = (dest / "ja" / "privacy.html").read_text(encoding="utf-8")
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
    expect(
        "canonical link",
        (
            "<!DOCTYPE html><html><head>"
            f'<link rel="canonical" href="{SITE_URL}/en/privacy.html">'
            "</head><body></body></html>"
        ),
        None,
    )
    expect(
        "canonical host link",
        f'<!DOCTYPE html><html><body><a href="{SITE_URL}/">home</a></body></html>',
        None,
    )
    failures.extend(test_published_drops_draft_placeholder_requirements())
    failures.extend(test_published_body_drops_draft_notices())
    failures.extend(test_r2_markers_replaced_still_blocks_release_words())
    failures.extend(test_r2_clean_pages_pass_release_word_scan())
    failures.extend(test_release_bans_counsel_pending_and_host_tbd())
    failures.extend(test_stamped_checklist_passes_both_modes())
    failures.extend(test_release_output_omits_held_locales())
    return failures


def _published_legal_page() -> str:
    return (
        "<!DOCTYPE html><html><body>"
        "<p>children aged 3–10</p>"
        f"<p>{EMAIL_RETENTION_LINE}</p>"
        "<p>IP address. user agent. The publisher does not receive the logs and we do not use them for tracking.</p>"
        f'<p><a href="{CONTACT_MAILTO}">{CONTACT_ADDRESS}</a></p>'
        "</body></html>"
    )


def test_published_drops_draft_placeholder_requirements() -> list[str]:
    """After Final Review OK, draft markers are not required; contact and retention are."""
    failures: list[str] = []
    ready = _published_legal_page()
    draft_errors = required_phrase_errors("en/terms.html", ready, {"en"}, drafts_required=True)
    for token in (POSTAL_ADDRESS, "TODO", "email-retention confirmation"):
        if not any(token in item for item in draft_errors):
            failures.append(f"draft mode should still require {token}, got {draft_errors}")
    published_errors = required_phrase_errors(
        "en/terms.html", ready, {"en"}, drafts_required=False
    )
    for token in (POSTAL_ADDRESS, "TODO", "email-retention confirmation"):
        if any(token in item for item in published_errors):
            failures.append(f"publication should not require {token}, got {published_errors}")
    if published_errors:
        failures.append(f"a published legal page with contact and retention should pass, got {published_errors}")
    bare = "<html><body><p>children aged 3–10</p></body></html>"
    still = required_phrase_errors("en/privacy.html", bare, {"en"}, drafts_required=False)
    for token in (CONTACT_MAILTO, CONTACT_ADDRESS, EMAIL_RETENTION_LINE, "host-log disclosure"):
        if not any(token in item for item in still):
            failures.append(f"publication should still require {token!r}, got {still}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "review.json").write_text(
            json.dumps({"version": 1, "release_languages": ["en"], "records": []}) + "\n",
            encoding="utf-8",
        )
        checklist = root / "release" / "checklist.json"
        checklist.parent.mkdir()
        checklist.write_text(
            json.dumps(
                {
                    "site": {
                        "final_review_ok": {
                            "by": "human:gabriel",
                            "date": "2026-11-01",
                            "languages": ["en"],
                        },
                        "effective_date": "2026-11-01",
                        "self_verified": [],
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        index = "<!DOCTYPE html><html><body><p>children aged 3–10</p></body></html>"
        (root / "index.html").write_text(index, encoding="utf-8")
        (root / "404.html").write_text(
            "<!DOCTYPE html><html><body><p>Missing.</p></body></html>",
            encoding="utf-8",
        )
        folder = root / "en"
        folder.mkdir()
        for page_id in PAGE_IDS:
            text = index if page_id == "index" else ready
            (folder / f"{page_id}.html").write_text(text, encoding="utf-8")
        if drafts_are_required(root, {"en"}):
            failures.append("a signed checklist should clear the draft-placeholder requirement")
        errors = check_contract(root)
        blocked = [
            item
            for item in errors
            if "POSTAL_ADDRESS" in item or "missing TODO" in item or "email-retention confirmation" in item
        ]
        if blocked:
            failures.append(f"published contract should not require draft placeholders, got {blocked}")
        if errors:
            failures.append(f"published contract fixture should pass, got {errors}")
        held = root / "ja" / "privacy.html"
        held.parent.mkdir()
        held.write_text(ready, encoding="utf-8")
        unexpected = check_contract(root)
        if not any("unexpected HTML file ja/privacy.html" in item for item in unexpected):
            failures.append(f"a published tree should reject a held locale page, got {unexpected}")
        held.unlink()
        terms = root / "en" / "terms.html"
        terms.write_text(terms.read_text(encoding="utf-8").replace(CONTACT_MAILTO, "mailto:missing@example.com"), encoding="utf-8")
        # The address text is still the approved address inside the old mailto. Remove both.
        terms.write_text(
            "<!DOCTYPE html><html><body><p>children aged 3–10</p>"
            f"<p>{EMAIL_RETENTION_LINE}</p></body></html>",
            encoding="utf-8",
        )
        missing_contact = check_contract(root)
        if not any("en/terms.html" in item and CONTACT_MAILTO in item for item in missing_contact):
            failures.append(f"publication should still require the contact link, got {missing_contact}")
        if not any("en/terms.html" in item and CONTACT_ADDRESS in item for item in missing_contact):
            failures.append(f"publication should still require the contact address, got {missing_contact}")
    return failures


def test_published_body_drops_draft_notices() -> list[str]:
    """Published pages drop the body sentences that say the document is not in force."""
    import build_site

    failures: list[str] = []
    common = dict(
        title="T",
        description="Draft description.",
        heading="H",
        css_href="../css/site.css",
        icon_prefix="../",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
    )
    cases = (
        ("children", "Please read it as a draft"),
        ("terms", "They are not in force, they have not had legal review"),
    )
    for page_id, sentence in cases:
        draft = build_site.page(
            **common,
            body=build_site.PAGE_BODIES[page_id],
            published=None,
        )
        live = build_site.page(
            **common,
            body=build_site.PAGE_BODIES[page_id],
            published=("2026-11-01", "1 November 2026"),
        )
        if sentence not in draft:
            failures.append(f"draft {page_id} should keep {sentence!r}")
        if sentence in live:
            failures.append(f"published {page_id} should omit {sentence!r}")
        if "Effective date:" not in live:
            failures.append(f"published {page_id} should show the effective date")
    children = build_site.page(
        **common,
        body=build_site.PAGE_BODIES["children"],
        published=("2026-11-01", "1 November 2026"),
    )
    if "not in force" in children:
        failures.append("published children page should not disclaim that it is not in force")
    if "Ages 5" in build_site.PAGE_BODIES["children"] or "Ages 5" in children:
        failures.append("the children's notice should not name an Apple age band")
    privacy_body = build_site.PAGE_BODIES["privacy"]
    if "is in the Kids category" in privacy_body or "is listed in the Kids category" not in privacy_body:
        failures.append("privacy should say the app is listed in the Kids category")
    if "Counsel still has to review the finished app before each storefront." in privacy_body:
        failures.append("the old counsel-pending storefront sentence should be gone")
    if "Each new storefront gets its own legal review before the app is offered there." not in privacy_body:
        failures.append("privacy should give each storefront its own legal review")
    if "Stating that here is a question for counsel." in privacy_body:
        failures.append("the COPPA counsel sentence should be deleted")
    if "is a question for counsel before release." not in build_site.PAGE_BODIES["children"]:
        failures.append("the children's notice should keep its counsel question")
    if SITE_URL not in privacy_body or "TBD before store release" not in privacy_body:
        failures.append("privacy should name the canonical URL and leave the host TBD")
    if "This website," not in privacy_body:
        failures.append("privacy should name this website without naming a host")
    if "GitHub Pages" in privacy_body or "hosted by" in privacy_body or "fordang.github.io" in privacy_body:
        failures.append("privacy should not name a host or the github.io address")
    return failures


def test_release_bans_counsel_pending_and_host_tbd() -> list[str]:
    """--release blocks the counsel-pending phrases and the unsettled host line."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        blocked = root / "sample.html"
        blocked.write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body>"
            "<p>Counsel still has to review the finished app before each storefront.</p>"
            "<p>TBD before store release.</p>"
            "</body></html>",
            encoding="utf-8",
        )
        errors = release_text_errors(root)
        joined = "\n".join(errors)
        for token in ("counsel still has to", "still has to review", "TBD before store release"):
            if f"release blocked by {token!r}" not in joined:
                failures.append(f"release scan should report {token!r}, got {errors}")
        blocked.write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body>"
            "<p>Each new storefront gets its own legal review before the app is offered there.</p>"
            "<p>today's play time</p>"
            "</body></html>",
            encoding="utf-8",
        )
        cleared = release_text_errors(root)
        if cleared:
            failures.append(f"the replacement storefront sentence should pass the release scan, got {cleared}")
    return failures


def _published_site_page(*, legal: bool, privacy: bool) -> str:
    parts = [
        "<!DOCTYPE html><html><head><title>Ready</title>",
        '<meta name="description" content="Ready page.">',
        f'<link rel="canonical" href="{SITE_URL}/en/privacy.html">',
        "</head><body>",
        "<p>Effective date: 1 November 2026. Last updated: 1 November 2026.</p>",
        "<p>children aged 3–10</p>",
    ]
    if legal:
        parts.append(f"<p>{EMAIL_RETENTION_LINE}</p>")
        parts.append(f'<p><a href="{CONTACT_MAILTO}">{CONTACT_ADDRESS}</a></p>')
    if privacy:
        parts.append(
            "<p>IP address. user agent. The publisher does not receive the logs "
            "and we do not use them for tracking.</p>"
        )
    parts.append("</body></html>")
    return "".join(parts)


def test_stamped_checklist_passes_both_modes() -> list[str]:
    """A publishable tree with Final Review OK passes check_site in both modes."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "review.json").write_text(
            json.dumps({"version": 1, "release_languages": ["en"], "records": []}) + "\n",
            encoding="utf-8",
        )
        checklist = root / "release" / "checklist.json"
        checklist.parent.mkdir()
        checklist.write_text(
            json.dumps(
                {
                    "site": {
                        "final_review_ok": {
                            "by": "human:gabriel",
                            "date": "2026-11-01",
                            "languages": ["en"],
                        },
                        "effective_date": "2026-11-01",
                        "self_verified": [],
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        legal = _published_site_page(legal=True, privacy=False)
        privacy = _published_site_page(legal=True, privacy=True)
        index = _published_site_page(legal=False, privacy=False)
        missing = (
            "<!DOCTYPE html><html><head><title>Missing</title></head>"
            "<body><p>That address is not a page on this site.</p></body></html>"
        )
        (root / "index.html").write_text(index, encoding="utf-8")
        (root / "404.html").write_text(missing, encoding="utf-8")
        english = root / "en"
        english.mkdir()
        for page_id in PAGE_IDS:
            text = index if page_id == "index" else privacy if page_id == "privacy" else legal
            (english / f"{page_id}.html").write_text(text, encoding="utf-8")
        normal = check_tree(root, contract=True)
        if normal:
            failures.append(f"a stamped checklist should pass check_site, got {normal}")
        released = release_text_errors(root)
        if released:
            failures.append(f"a stamped checklist should pass check_site --release, got {released}")
        (english / "privacy.html").write_text(
            privacy.replace("</body>", "<p>TBD before store release.</p></body>"),
            encoding="utf-8",
        )
        still_normal = check_tree(root, contract=True)
        if still_normal:
            failures.append(f"the host TBD line should not fail the default check, got {still_normal}")
        blocked = release_text_errors(root)
        if not any("TBD before store release" in item for item in blocked):
            failures.append(f"--release should block the host TBD line, got {blocked}")
    return failures


def test_release_output_omits_held_locales() -> list[str]:
    """Published output and the release word scan stay inside release_languages."""
    failures: list[str] = []
    import build_site

    draft_codes = [code for code, _native, _english in build_site.locales_for_output(None)]
    if draft_codes != list(LOCALE_CODES):
        failures.append(f"a draft build should write every locale, got {draft_codes}")
    published_codes = [
        code
        for code, _native, _english in build_site.locales_for_output(("2026-11-01", "1 November 2026"))
    ]
    if published_codes != ["en"]:
        failures.append(f"a published build should write only en, got {published_codes}")
    nav = build_site.language_nav("privacy.html", "en", False)
    for code in LOCALE_CODES:
        if code == "en":
            if f"../{code}/privacy.html" not in nav:
                failures.append("the language switcher should link English")
            continue
        if f"../{code}/" in nav or f'hreflang="{code}"' in nav:
            failures.append(f"the language switcher should not link {code}")
    privacy = build_site.render_locale(
        "en", "English", "English", "privacy", "Privacy policy", None
    )
    if f'<link rel="canonical" href="{SITE_URL}/en/privacy.html">' not in privacy:
        failures.append("the privacy page should carry its canonical link")
    if "fordang.github.io" in privacy:
        failures.append("generated privacy HTML should not name the github.io host")
    home = build_site.render_root(None)
    if f'<link rel="canonical" href="{SITE_URL}/">' not in home:
        failures.append("the root page should canonicalise to the site origin")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "review.json").write_text(
            json.dumps({"version": 1, "release_languages": ["en"], "records": []}) + "\n",
            encoding="utf-8",
        )
        held = root / "ja" / "privacy.html"
        held.parent.mkdir()
        held.write_text(
            "<!DOCTYPE html><html><body><p>TODO placeholder draft</p></body></html>",
            encoding="utf-8",
        )
        (root / "en").mkdir()
        (root / "en" / "privacy.html").write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body><p>Ready.</p></body></html>",
            encoding="utf-8",
        )
        (root / "index.html").write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body><p>Ready.</p></body></html>",
            encoding="utf-8",
        )
        (root / "404.html").write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body><p>Ready.</p></body></html>",
            encoding="utf-8",
        )
        ignored = release_text_errors(root)
        if ignored:
            failures.append(f"a held locale should not fail the release word scan, got {ignored}")
        (root / "en" / "privacy.html").write_text(
            "<!DOCTYPE html><html><head><title>Ready</title></head><body><p>TODO</p></body></html>",
            encoding="utf-8",
        )
        seen = release_text_errors(root)
        if not any(item.startswith("en/privacy.html:") for item in seen):
            failures.append(f"an English TODO should fail the release word scan, got {seen}")
        if any(item.startswith("ja/") for item in seen):
            failures.append(f"the release word scan should leave out ja, got {seen}")
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
