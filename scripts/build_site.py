#!/usr/bin/env python3
"""Generate the static Bridge Kids legal pages.

Edit scripts/content.py and run this file again. The HTML in the locale
folders is generated so every language stays in step. Non-English pages
repeat the English draft and add a translation-pending banner. This
script does not translate.

Usage:
  python3 scripts/build_site.py
  python3 scripts/build_site.py --check
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from content import PAGE_BODIES, PAGE_DESCRIPTIONS  # noqa: E402
from site_map import (  # noqa: E402
    CONTACT_ADDRESS,
    CONTACT_MAILTO,
    DRAFT_MARK,
    LOCALES,
    PAGE_IDS,
    PAGES,
    PENDING_MARK,
    UPDATED,
    UPDATED_LABEL,
)

ROOT = SCRIPT_DIR.parent

TITLES = {
    "index": "Bridge Kids – Privacy, support, and terms",
    "privacy": "Privacy Policy – Bridge Kids",
    "children": "Children's Privacy and COPPA Notice – Bridge Kids",
    "support": "Support – Bridge Kids",
    "terms": "Terms of Use – Bridge Kids",
    "404": "Page not found – Bridge Kids",
}

DOCUMENTS = (
    ("privacy.html", "Privacy policy", "What the app handles, and what it does not collect."),
    (
        "children.html",
        "Children's privacy and COPPA notice",
        "The children's notice, including the data retention policy.",
    ),
    (
        "support.html",
        "Support",
        "Delete a profile, understand speech and backups, and contact the publisher.",
    ),
    ("terms.html", "Terms of use", "The draft license and App Store terms."),
)


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def esc_attr(value: str) -> str:
    return html.escape(value, quote=True)


def language_nav(page_file: str, current_locale: str | None, from_root: bool) -> str:
    items: list[str] = []
    for code, native, english in LOCALES:
        href = f"{code}/{page_file}" if from_root else f"../{code}/{page_file}"
        current = ' aria-current="true"' if code == current_locale else ""
        gloss = ""
        if english != native:
            gloss = f' <span class="visually-hidden">({esc(english)})</span>'
        items.append(
            "<li>"
            f'<a href="{href}" hreflang="{esc(code)}" lang="{esc(code)}"{current}>'
            f"{esc(native)}{gloss}</a></li>"
        )
    return (
        '<nav class="languages" aria-label="Languages">'
        "<p>Languages</p><ul>"
        + "".join(items)
        + "</ul></nav>"
    )


def document_nav(current_page: str) -> str:
    labels = {
        "index": "Home",
        "privacy": "Privacy",
        "children": "Children's privacy",
        "support": "Support",
        "terms": "Terms",
    }
    items: list[str] = []
    for page_id in PAGE_IDS:
        current = ' aria-current="page"' if page_id == current_page else ""
        items.append(
            f'<li><a href="{page_id}.html"{current}>{esc(labels[page_id])}</a></li>'
        )
    return (
        '<nav class="documents" aria-label="Documents">'
        "<p>Documents</p><ul>"
        + "".join(items)
        + "</ul></nav>"
    )


def document_list(prefix: str) -> str:
    items = []
    for filename, label, summary in DOCUMENTS:
        items.append(
            f"<li><a href=\"{prefix}{filename}\">{esc(label)}</a>. {esc(summary)}</li>"
        )
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def alternate_links(page_file: str) -> str:
    links = []
    for code, _native, _english in LOCALES:
        links.append(
            f'<link rel="alternate" hreflang="{esc(code)}" href="../{code}/{page_file}">'
        )
    links.append(
        f'<link rel="alternate" hreflang="x-default" href="../en/{page_file}">'
    )
    return "\n".join(links)


def pending_banner(code: str, native: str) -> str:
    return (
        '<div class="pending">'
        f"<p><strong>{esc(PENDING_MARK)}.</strong> "
        "This page is in English. A human translation into "
        f'<span lang="{esc(code)}">{esc(native)}</span> '
        "has not been written or reviewed. This is not a translation. "
        "Do not use a machine translation of this page as the policy.</p>"
        "</div>"
    )


def page(
    *,
    title: str,
    description: str,
    heading: str,
    body: str,
    css_href: str,
    icon_prefix: str,
    brand_href: str,
    header_nav: str,
    pending: str,
    alternates: str,
    locale_note: str,
) -> str:
    alternate_block = f"\n{alternates}" if alternates else ""
    locale_block = f"\n{locale_note}" if locale_note else ""
    pending_block = f"\n{pending}" if pending else ""
    return f"""<!DOCTYPE html>
<html lang="en" translate="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="theme-color" content="#fbf7f0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1c1917" media="(prefers-color-scheme: dark)">
<title>{esc(title)}</title>
<meta name="description" content="{esc_attr(description)}">
<link rel="stylesheet" href="{css_href}">
<link rel="icon" href="{icon_prefix}favicon.ico" sizes="32x32">
<link rel="icon" href="{icon_prefix}favicon.svg" type="image/svg+xml">{alternate_block}
</head>
<body>
<!-- {DRAFT_MARK} -->
<!-- Generated by scripts/build_site.py. Edit the sources under scripts/ and run the generator again. -->{locale_block}
<a class="skip" href="#content">Skip to content</a>
<header class="wrap">
<p class="brand"><a href="{brand_href}">Bridge Kids</a></p>
<p class="draft">{esc(DRAFT_MARK)}. This page is not a final legal document, and it is not in force.</p>
{header_nav}
</header>
<main class="wrap" id="content">{pending_block}
<h1>{esc(heading)}</h1>
<p>Draft dated <time datetime="{UPDATED}">{esc(UPDATED_LABEL)}</time>. The English text is the source draft.</p>
{body.strip()}
</main>
<footer class="wrap">
<p>Bridge Kids is published by Gabriel John Fordan, an individual developer.</p>
<p><time datetime="{UPDATED}">{esc(UPDATED_LABEL)}</time>. {esc(DRAFT_MARK)}. This is not a final legal document.</p>
</footer>
</body>
</html>
"""


def locale_index_body() -> str:
    return f"""
<p>Privacy policy, children's privacy notice, support, and terms for Bridge Kids, an app for children aged 3–10 on iPhone and iPad.</p>
<p>Bridge Kids is published by Gabriel John Fordan, an individual developer. The app is free. It is designed not to collect personal information, not to use accounts or telemetry, and not to send a child's voice off the device. Speech recognition stays on the device. Profiles are excluded from iOS backup.</p>
<h2>Documents</h2>
{document_list("")}
<p>Email: <a href="{CONTACT_MAILTO}">{esc(CONTACT_ADDRESS)}</a>. The postal address, if one is required, is still a placeholder on the <a href="support.html">support page</a>.</p>
"""


def root_index_body() -> str:
    return f"""
<p>Privacy policy, children's privacy notice, support, and terms for Bridge Kids, an app for children aged 3–10 on iPhone and iPad.</p>
<p>Choose a language. English is the only text that has been written. Every other language shows that English text with a banner that says a human translation is still waiting. Those pages are not translations, and a browser translation is not one either.</p>
{language_nav("index.html", None, True)}
<h2>English documents</h2>
{document_list("en/")}
<p>Bridge Kids is published by Gabriel John Fordan, an individual developer. The app is free. Email: <a href="{CONTACT_MAILTO}">{esc(CONTACT_ADDRESS)}</a>. The postal address, if one is required, is still a placeholder.</p>
"""


def not_found_body() -> str:
    return f"""
<p>That address is not a page on this site. The links below stay inside the site.</p>
{language_nav("index.html", None, True)}
<h2>English documents</h2>
{document_list("en/")}
"""


def render_locale(code: str, native: str, english: str, page_id: str, heading: str) -> str:
    page_file = f"{page_id}.html"
    if page_id == "index":
        body = locale_index_body()
    else:
        body = PAGE_BODIES[page_id]
    pending = ""
    locale_note = ""
    if code != "en":
        pending = pending_banner(code, native)
        locale_note = (
            f"<!-- Locale folder: {code}. The visible text is English until a human "
            f"translation is reviewed. When you translate this file, set the html lang "
            f"attribute to {code}. -->"
        )
    header = language_nav(page_file, code, False) + "\n" + document_nav(page_id)
    return page(
        title=TITLES[page_id],
        description=PAGE_DESCRIPTIONS[page_id],
        heading=heading,
        body=body,
        css_href="../css/site.css",
        icon_prefix="../",
        brand_href="index.html",
        header_nav=header,
        pending=pending,
        alternates=alternate_links(page_file),
        locale_note=locale_note,
    )


def render_root() -> str:
    return page(
        title=TITLES["index"],
        description=PAGE_DESCRIPTIONS["index"],
        heading="Bridge Kids",
        body=root_index_body(),
        css_href="css/site.css",
        icon_prefix="",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
    )


def render_404() -> str:
    return page(
        title=TITLES["404"],
        description=PAGE_DESCRIPTIONS["404"],
        heading="Page not found",
        body=not_found_body(),
        css_href="css/site.css",
        icon_prefix="",
        brand_href="index.html",
        header_nav="",
        pending="",
        alternates="",
        locale_note="",
    )


def render_all() -> dict[str, str]:
    files = {
        "index.html": render_root(),
        "404.html": render_404(),
    }
    for code, native, english in LOCALES:
        for page_id, heading in PAGES:
            files[f"{code}/{page_id}.html"] = render_locale(
                code, native, english, page_id, heading
            )
    return files


def main(argv: list[str]) -> int:
    check_only = argv == ["--check"]
    if argv and not check_only:
        print("Usage: python3 scripts/build_site.py [--check]", file=sys.stderr)
        return 2
    files = render_all()
    mismatched: list[str] = []
    for relative, text in files.items():
        if not text.endswith("\n"):
            text += "\n"
        target = ROOT / relative
        if check_only:
            current = target.read_text(encoding="utf-8") if target.is_file() else None
            if current != text:
                mismatched.append(relative)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    if check_only and mismatched:
        print("Generated HTML is out of date:", file=sys.stderr)
        for relative in mismatched:
            print(f"  {relative}", file=sys.stderr)
        print("Run: python3 scripts/build_site.py", file=sys.stderr)
        return 1
    if check_only:
        print(f"Generated HTML matches the sources ({len(files)} files).")
    else:
        print(f"Wrote {len(files)} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
