#!/usr/bin/env python3
"""Checks for the Bridge Kids static site.

Fails if any HTML or SVG file contains a script, if a stylesheet or
document loads a third-party URL, if an href or src leaves the site
for anything other than an Apple app-store link or the approved
mailto address, if HTML links or fragments are broken, or if the
locale contract is wrong.

Valid HTML is checked separately with the Nu Html Checker in CI.
"""

from __future__ import annotations

import json
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
        for snippet in ("GitHub Pages", "do not use them for tracking"):
            if snippet not in text:
                errors.append(f"{relative}: missing the host-log disclosure ({snippet})")
    return errors


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
    return failures


def main() -> int:
    failures = self_test()
    if failures:
        print("Checker self-test failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    errors = check_tree(ROOT, contract=True)
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
