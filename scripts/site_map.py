"""Shared map of the Bridge Kids static site.

The generator and the checker both import this so the published files
and the CI contract cannot drift apart.
"""

from __future__ import annotations

# Parent UI languages from Bridge Kids architecture v2, section 6.
# Native names are in each language's own script. No flags.
LOCALES: tuple[tuple[str, str, str], ...] = (
    ("ja", "日本語", "Japanese"),
    ("en", "English", "English"),
    ("zh-Hans", "简体中文", "Chinese, Simplified"),
    ("pt-BR", "Português (Brasil)", "Portuguese, Brazil"),
    ("fil", "Filipino", "Filipino"),
    ("vi", "Tiếng Việt", "Vietnamese"),
    ("ne", "नेपाली", "Nepali"),
)

LOCALE_CODES: tuple[str, ...] = tuple(code for code, _native, _english in LOCALES)

# Page file stem -> heading used as the h1 on locale pages.
PAGES: tuple[tuple[str, str], ...] = (
    ("index", "Bridge Kids"),
    ("privacy", "Privacy policy"),
    ("children", "Children's privacy and COPPA notice"),
    ("support", "Support"),
    ("terms", "Terms of use"),
)

PAGE_IDS: tuple[str, ...] = tuple(page_id for page_id, _heading in PAGES)

LEGAL_PAGE_IDS: frozenset[str] = frozenset(
    {"privacy", "children", "support", "terms"}
)

DRAFT_MARK = "DRAFT – pending legal review"
PENDING_MARK = "TRANSLATION PENDING"
CONTACT_ADDRESS = "gabrieljohnfordan@gmail.com"
CONTACT_MAILTO = "mailto:gabrieljohnfordan@gmail.com"
# Public origin of this site. No CNAME is added here, and nothing is published.
SITE_URL = "https://bridgekids.vendrato.com"
APP_ID = "com.vendrato.bridgekids"
POSTAL_ADDRESS = "{{POSTAL_ADDRESS_IF_REQUIRED}}"
EMAIL_RETENTION_LINE = "deleted within 90 days after your request is resolved"
EMAIL_RETENTION_NOTE = "retention period pending Gabriel's confirmation"
UPDATED = "2026-10-23"
UPDATED_LABEL = "23 October 2026"

ROOT_HTML: frozenset[str] = frozenset({"index.html", "404.html"})
