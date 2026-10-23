#!/usr/bin/env python3
"""Generate the static Bridge Kids legal pages.

Edit scripts/content.py and run this file again. The HTML in the locale
folders is generated so every language stays in step. Non-English pages
repeat the English draft and add a translation-pending banner. A copy
in another language is an AI draft by the product lead, taken to
ai_verified by that language's reviewer. There is no separate human
translator. This script does not translate.

Draft banners and the "Draft dated" line stay until release/checklist.json
has both Gabriel's Final Review OK and site.effective_date. When both
are set, this script removes the banners and writes that date as the
effective date and the last-updated date.

Usage:
  python3 scripts/build_site.py
  python3 scripts/build_site.py --check
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from content import PAGE_BODIES, PAGE_DESCRIPTIONS  # noqa: E402
import content_ja as ja  # noqa: E402
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
REVIEW_PATH = ROOT / "review.json"
CHECKLIST_PATH = ROOT / "release" / "checklist.json"

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
        "Delete a profile, understand backups, and contact the publisher.",
    ),
    ("terms.html", "Terms of use", "The license and App Store terms."),
)


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def esc_attr(value: str) -> str:
    return html.escape(value, quote=True)


def release_codes() -> list[str]:
    """Locales linked at launch. The list lives in review.json.

    English is required. Japanese is re-added when the ai_verified ja
    copy lands; until then it may be absent and is not linked.
    """
    try:
        data = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"review.json: cannot read release_languages ({exc})") from exc
    codes = data.get("release_languages") if isinstance(data, dict) else None
    known = {code for code, _native, _english in LOCALES}
    if (
        not isinstance(codes, list)
        or not codes
        or any(not isinstance(code, str) or code not in known for code in codes)
        or len(set(codes)) != len(codes)
        or "en" not in codes
    ):
        raise SystemExit(
            "review.json: release_languages must list known locales and include en"
        )
    return codes


def current_publication_stamp() -> tuple[str, str] | None:
    """Effective date label once Final Review OK and site.effective_date are both set."""
    from review_check import publication_stamp

    return publication_stamp(CHECKLIST_PATH, release_codes())


def release_rows() -> list[tuple[str, str, str]]:
    """Parent-UI order, limited to the launch languages."""
    chosen = set(release_codes())
    return [row for row in LOCALES if row[0] in chosen]


def language_nav(page_file: str, current_locale: str | None, from_root: bool) -> str:
    is_ja = current_locale == "ja"
    items: list[str] = []
    linked = {code for code, _native, _english in release_rows()}
    for code, native, english in release_rows():
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
    held = ""
    if current_locale is not None and current_locale not in linked:
        held = (
            f"<p>{esc(ja.CHROME_JA['held'])}</p>"
            if is_ja
            else (
                "<p>This language is not part of the current release "
                "and is not linked from the launch pages.</p>"
            )
        )
    nav_open = (
        f'<nav class="languages" aria-label="{esc(ja.CHROME_JA["languages"])}">'
        f"<p>{esc(ja.CHROME_JA['languages'])}</p><ul>"
        if is_ja
        else '<nav class="languages" aria-label="Languages"><p>Languages</p><ul>'
    )
    return nav_open + "".join(items) + "</ul>" + held + "</nav>"


def document_nav(current_page: str, locale: str = "en") -> str:
    labels = {
        "index": "Home",
        "privacy": "Privacy",
        "children": "Children's privacy",
        "support": "Support",
        "terms": "Terms",
    }
    if locale == "ja":
        labels = ja.DOC_NAV_LABELS_JA
    items: list[str] = []
    for page_id in PAGE_IDS:
        current = ' aria-current="page"' if page_id == current_page else ""
        items.append(
            f'<li><a href="{page_id}.html"{current}>{esc(labels[page_id])}</a></li>'
        )
    nav_open = (
        f'<nav class="documents" aria-label="{esc(ja.CHROME_JA["documents"])}">'
        f"<p>{esc(ja.CHROME_JA['documents'])}</p><ul>"
        if locale == "ja"
        else '<nav class="documents" aria-label="Documents"><p>Documents</p><ul>'
    )
    return nav_open + "".join(items) + "</ul></nav>"


def document_list(prefix: str) -> str:
    items = []
    for filename, label, summary in DOCUMENTS:
        items.append(
            f"<li><a href=\"{prefix}{filename}\">{esc(label)}</a>. {esc(summary)}</li>"
        )
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def alternate_links(page_file: str) -> str:
    links = []
    for code, _native, _english in release_rows():
        links.append(
            f'<link rel="alternate" hreflang="{esc(code)}" href="../{code}/{page_file}">'
        )
    links.append(
        f'<link rel="alternate" hreflang="x-default" href="../en/{page_file}">'
    )
    return "\n".join(links)


def pending_banner(native: str) -> str:
    return (
        '<div class="pending">'
        f"<p><strong>{esc(PENDING_MARK)}.</strong> "
        "This page still shows the English draft. "
        f"The {esc(native)} copy is an AI draft by the product lead "
        "and is taken to ai_verified by the JA reviewer. "
        "There is no separate human translator. "
        "Do not use a machine translation of this page as the policy.</p>"
        "</div>"
    )


def public_description(description: str, published: tuple[str, str] | None) -> str:
    """Drop the release-gated "Draft " meta prefix once the publication stamp is set."""
    if published is not None and description.startswith("Draft "):
        rest = description[len("Draft ") :]
        return rest[:1].upper() + rest[1:]
    return description


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
    published: tuple[str, str] | None = None,
    lang: str = "en",
    notice: str = "",
) -> str:
    description = public_description(description, published)
    alternate_block = f"\n{alternates}" if alternates else ""
    locale_block = f"\n{locale_note}" if locale_note else ""
    pending_block = f"\n{pending}" if pending else ""
    chrome = ja.CHROME_JA if lang == "ja" else None
    if published is None:
        draft_comment = f"<!-- {DRAFT_MARK} -->\n"
        draft_banner = (
            f'<p class="draft">{esc(DRAFT_MARK)}. This page is not a final legal document, '
            "and it is not in force.</p>\n"
        )
        dated = (
            f'<p>Draft dated <time datetime="{UPDATED}">{esc(UPDATED_LABEL)}</time>. '
            "The English text is the source draft.</p>"
        )
        footer_date = (
            f"<p><time datetime=\"{UPDATED}\">{esc(UPDATED_LABEL)}</time>. "
            f"{esc(DRAFT_MARK)}. This is not a final legal document.</p>"
        )
        if chrome:
            dated_time = f'<time datetime="{UPDATED}">{ja.ja_date_label(UPDATED)}</time>'
            draft_banner = f'<p class="draft">{esc(chrome["draft_banner"])}</p>\n'
            dated = "<p>" + chrome["dated"].format(date=dated_time) + "</p>"
            footer_date = "<p>" + chrome["footer_draft"].format(date=dated_time) + "</p>"
    else:
        iso, label = published
        draft_comment = ""
        draft_banner = ""
        dated = (
            f'<p>Effective date: <time datetime="{esc_attr(iso)}">{esc(label)}</time>. '
            f'Last updated: <time datetime="{esc_attr(iso)}">{esc(label)}</time>.</p>'
        )
        footer_date = dated
        if chrome:
            dated_time = (
                f'<time datetime="{esc_attr(iso)}">{ja.ja_date_label(iso)}</time>'
            )
            dated = (
                "<p>"
                + chrome["published"].format(effective=dated_time, updated=dated_time)
                + "</p>"
            )
            footer_date = dated
    notice_block = f"\n{notice}" if notice else ""
    skip = chrome["skip"] if chrome else "Skip to content"
    publisher = (
        chrome["footer_publisher"]
        if chrome
        else "Bridge Kids is published by Gabriel John Fordan, an individual developer."
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}" translate="no">
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
{draft_comment}<!-- Generated by scripts/build_site.py. Edit the sources under scripts/ and run the generator again. -->{locale_block}
<a class="skip" href="#content">{skip}</a>
<header class="wrap">
<p class="brand"><a href="{brand_href}">Bridge Kids</a></p>
{draft_banner}{header_nav}
</header>
<main class="wrap" id="content">{pending_block}
<h1>{esc(heading)}</h1>
{dated}{notice_block}
{body.strip()}
</main>
<footer class="wrap">
<p>{publisher}</p>
{footer_date}
</footer>
</body>
</html>
"""


def locale_index_body() -> str:
    return f"""
<p>Privacy policy, children's privacy notice, support, and terms for Bridge Kids, an app for children aged 3–10 on iPhone and iPad.</p>
<p>Bridge Kids is published by Gabriel John Fordan, an individual developer. The app is free. It is designed not to collect personal information and not to use accounts or telemetry. It does not use the microphone, and it does not connect to the internet. Profiles and progress stay on the device and are excluded from iOS backup.</p>
<h2>Documents</h2>
{document_list("")}
<p>Email: <a href="{CONTACT_MAILTO}">{esc(CONTACT_ADDRESS)}</a>. The postal address, if one is required, is still a placeholder on the <a href="support.html">support page</a>.</p>
"""


def release_document_sections() -> str:
    rows = release_rows()
    blocks: list[str] = []
    for code, native, _english in rows:
        heading = "Documents" if len(rows) == 1 else f"{native} documents"
        blocks.append(f"<h2>{esc(heading)}</h2>\n{document_list(code + '/')}")
    return "\n".join(blocks)


def root_index_body() -> str:
    return f"""
<p>Privacy policy, children's privacy notice, support, and terms for Bridge Kids, an app for children aged 3–10 on iPhone and iPad.</p>
<p>Choose a language. The app's parent area is in English and Japanese.</p>
{language_nav("index.html", None, True)}
{release_document_sections()}
<p>Bridge Kids is published by Gabriel John Fordan, an individual developer. The app is free. Email: <a href="{CONTACT_MAILTO}">{esc(CONTACT_ADDRESS)}</a>. The postal address, if one is required, is still a placeholder.</p>
"""


def not_found_body() -> str:
    return f"""
<p>That address is not a page on this site. The links below stay inside the site.</p>
{language_nav("index.html", None, True)}
{release_document_sections()}
"""


def render_locale(
    code: str,
    native: str,
    english: str,
    page_id: str,
    heading: str,
    published: tuple[str, str] | None,
) -> str:
    page_file = f"{page_id}.html"
    is_ja = code == "ja"
    if is_ja:
        body = ja.INDEX_BODY_JA if page_id == "index" else ja.PAGE_BODIES_JA[page_id]
    elif page_id == "index":
        body = locale_index_body()
    else:
        body = PAGE_BODIES[page_id]
    pending = ""
    locale_note = ""
    if code not in ("en", "ja"):
        pending = pending_banner(native)
        locale_note = (
            f"<!-- Locale folder: {code}. The visible text is the English draft. "
            f"A copy in this language is an AI draft by the product lead and is taken "
            f"to ai_verified by the language reviewer. There is no separate human "
            f"translator. When that copy replaces this text, set the html lang "
            f"attribute to {code}. -->"
        )
    header = language_nav(page_file, code, False) + "\n" + document_nav(page_id, code)
    return page(
        title=ja.TITLES_JA[page_id] if is_ja else TITLES[page_id],
        description=ja.PAGE_DESCRIPTIONS_JA[page_id] if is_ja else PAGE_DESCRIPTIONS[page_id],
        heading=ja.HEADINGS_JA[page_id] if is_ja else heading,
        body=body,
        css_href="../css/site.css",
        icon_prefix="../",
        brand_href="index.html",
        header_nav=header,
        pending=pending,
        alternates=alternate_links(page_file),
        locale_note=locale_note,
        published=published,
        lang="ja" if is_ja else "en",
        notice=ja.PREVAILS_NOTICE_HTML if is_ja and page_id in ja.PREVAILS_NOTICE_PAGES else "",
    )


def render_root(published: tuple[str, str] | None) -> str:
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
        published=published,
    )


def render_404(published: tuple[str, str] | None) -> str:
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
        published=published,
    )


def render_all() -> dict[str, str]:
    published = current_publication_stamp()
    files = {
        "index.html": render_root(published),
        "404.html": render_404(published),
    }
    for code, native, english in LOCALES:
        for page_id, heading in PAGES:
            files[f"{code}/{page_id}.html"] = render_locale(
                code, native, english, page_id, heading, published
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
