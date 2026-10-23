# Bridge Kids site

**DRAFT – pending legal review.**

Static privacy, children's privacy, support, and terms pages for Bridge Kids, an app for children aged 3–10 on iPhone and iPad. The publisher is Gabriel John Fordan, an individual developer. The app is free.

These pages are drafts. They are not in force. They are not legal advice. Every HTML page carries `DRAFT – pending legal review` in an HTML comment and in the visible header and footer.

Nothing in this repository may merge to `main` without Gabriel's approval. Do not enable GitHub Pages, do not add a custom domain, and do not submit a store listing that points here until he approves publication and the open items below are closed.

This repository is public. After a merge, the draft text is readable on GitHub even while Pages is still off.

## Pages

Each locale is a folder. Each folder has the same five documents:

| File | Document |
| --- | --- |
| `index.html` | Short introduction and links |
| `privacy.html` | Privacy policy |
| `children.html` | Children's privacy and COPPA notice, including the data retention policy |
| `support.html` | Support and contact |
| `terms.html` | Terms of use |

Locales, in the parent-UI order from the architecture: `ja`, `en`, `zh-Hans`, `pt-BR`, `fil`, `vi`, `ne`. The language switcher is a row of links. Names are written in each language's own script. There are no flags.

The launch set is English and Japanese (`release_languages` in `review.json`). The language switcher, the root language list, and the `hreflang` links point only at those two. `zh-Hans`, `pt-BR`, `fil`, `vi`, and `ne` stay in the repository so they can be reviewed later. They are not linked from the launch pages. A direct file is still in the repo; it is not part of this release.

`en/` is the source text. Every other locale repeats that English text and shows a **TRANSLATION PENDING** banner. Those pages are not translations. Do not machine-translate them. A reviewed human translation has to replace the English, remove the banner, and set the `lang` attribute on `<html>` (a comment in each non-English file says what to set).

The site root `index.html` links the Japanese and English documents. `404.html` is only for a later Pages site.

## What the drafts say

The text follows the Bridge Kids privacy design:

- no personal information collected by the publisher, and no Bridge Kids servers
- no accounts and no telemetry, analytics, advertising, or crash SDK
- on-device speech only, with an attempt-only fallback, and audio not stored
- the app is free
- profiles and progress excluded from iOS backup
- designed against the Apple Kids Category, COPPA, the GDPR children's rules, the UK Age Appropriate Design Code, Japan's APPI, Brazil's ECA Digital, and Vietnam's Personal Data Protection Law

The drafts say where a decision is still open instead of inventing it. Governing law is not chosen. The public pages do not describe a second store or a charge inside the app.

The app id, where a page names it, is `com.vendrato.bridgekids`.

## Contact and the remaining placeholder

The public contact email is [gabrieljohnfordan@gmail.com](mailto:gabrieljohnfordan@gmail.com), the address Gabriel approved. On the pages it is a `mailto:` link. No postal address and no telephone number are included.

Messages to that address are kept only as long as needed to answer them and are deleted within 90 days after your request is resolved.

**TODO:** retention period pending Gabriel's confirmation.

- `{{POSTAL_ADDRESS_IF_REQUIRED}}` stands in for a postal address, and only if legal review says one must be published.

Each legal page has a **TODO** note next to that postal placeholder. Do not replace it with a home address or a guessed phone number. The 90-day line is marked in an HTML comment with the same confirmation note.

## How the files are built

The pages are plain HTML and one stylesheet. They load no JavaScript, no cookies, no analytics, and no fonts or images from anyone else. `css/site.css` names system fonts only.

Edit `scripts/content.py` (and the layout in `scripts/build_site.py` if the chrome changes), then regenerate:

```bash
python3 scripts/build_site.py
```

`python3 scripts/build_site.py --check` fails if the committed HTML drifts from the generator. GitHub Pages, when it is eventually turned on, serves the committed HTML. It does not need a build.

Preview locally from the repository root:

```bash
python3 -m http.server 8080
```

Then open `http://127.0.0.1:8080/`. Use only this kind of local preview. Do not upload the draft to another host.

## Checks

`.github/workflows/site-checks.yml` runs on `ubuntu-latest` for pull requests and for pushes to `main`. It does not deploy. It:

- checks the committed HTML against the generator
- rejects `<script>` tags, inline event handlers, and `javascript:` URLs
- rejects external `href` and `src` values except `https` links to `apps.apple.com` and `itunes.apple.com`, and except `mailto:gabrieljohnfordan@gmail.com`
- rejects remote CSS and remote SVG references
- rejects broken internal links and broken fragments
- requires the draft comment, the translation banner on non-English pages, the approved mailto, the postal-address placeholder, the 90-day email-retention line and its confirmation comment, the ages 3–10 description, and the GitHub Pages log disclosure on the privacy page
- rejects Android, Google, subscription, and in-app-purchase wording in the HTML
- validates HTML, CSS, and SVG with the Nu Html Checker
- recomputes `review.json` source hashes and rejects a missing author, a reviewer who is also the author, a reviewer outside the allowed identities, a `human_verified` record without a `human:<name>` reviewer, a launch page that links a locale outside `release_languages`, or a hash that does not match the page

The Nu jar is pinned by SHA-256 to the 12 October 2026 "latest" build (`26.10.12`). If that moving release URL no longer matches the pin, the workflow fails closed until someone updates both.

Run the same link checks locally with `python3 scripts/check_site.py`. Run `python3 scripts/review_check.py` for the review file. That command reports unreviewed release-language pages and does not fail on them. Locales outside `release_languages` are reported as excluded. `python3 scripts/review_check.py --release` is the later gate, following PRD §12.8. It checks only `en` and `ja`. Unreviewed, flagged, and stale-hash pages in those languages fail. The other five locales are excluded, not failed. English passes as `ai_reviewed` by the author-rule reviewer (`ai-product-lead` is reviewed by `ai-ja-reviewer`, with `ai-qa` as the fallback, or by `human:<name>`; any other author is reviewed by `ai-product-lead` or `human:<name>`) or as `human_verified`. Japanese passes as `ai_reviewed` by `ai-ja-reviewer` when `needs_native_check` is false. When that flag is true, Japanese passes only as `ai_verified` by `ai-ja-reviewer` with `reviewed_at` set, or as `human_verified`. The reviewer is never the author. `--release` also requires Gabriel's Final Review OK in `release/checklist.json`. That one sign-off covers the legal pages. A missing OK fails the release check. It does not fail the default site check. `python3 scripts/review_check.py --write` refreshes `source_hash` after a page edit and leaves an existing review untouched.

## Content review

`review.json` has `release_languages` (`["en", "ja"]` for this MVP) and one record for each locale page (`ja`, `en`, `zh-Hans`, `pt-BR`, `fil`, `vi`, `ne` × `index`, `privacy`, `children`, `support`, `terms`). Every record starts as `unreviewed`. The author on those starting records is `ai-product-lead`. Non-English pages set `needs_native_check` because the visible text is still the English draft. The Japanese native check is the AI JA reviewer's second pass (`ai_verified`). A human reviewer is optional.

`source_hash` is `sha256:` plus the hex SHA-256 of the page's visible text. Visible text is the text inside `<body>`, excluding `<script>` and `<style>`. The hash is taken after Unicode NFC, after newlines are LF, and after the ends are trimmed. A content edit has to be followed by `--write` so the committed hash matches.

Allowed authors and reviewers are `ai-product-lead`, `ai-ja-reviewer`, `ai-qa`, `ai-designer`, and `human:<name>`. The reviewer has to be a different identity from the author. `self_verified` does not replace that second person.

`release/checklist.json` records Gabriel's Final Review OK for the site. Until he signs, `final_review_ok` is null. The shape he records is `{"by":"human:gabriel","date":"YYYY-MM-DD","languages":["en","ja"]}`. The languages have to match `release_languages`.

## Publish later, only after Gabriel approves

Do not do this as part of ordinary development, and do not do it from a pull request that he has not approved.

1. Finish legal review. Replace the postal-address placeholder only if counsel says it must be published. Confirm the 90-day email retention line with Gabriel. Add a human translation for a locale only after that translation is reviewed. Confirm the App Store privacy form still matches the text.
2. Get Gabriel's approving review. Nothing merges to `main` without Gabriel. Branch protection should require his approval and this workflow.
3. Merge the approved change to `main`.
4. Only then, a person with admin rights turns on GitHub Pages: **Settings → Pages → Build and deployment → Deploy from a branch → Branch `main` → folder `/ (root)` → Save.**
5. Do not add a custom domain. The zero-spend plan keeps the free `github.io` host. `.nojekyll` is already in the repo so Pages will not run Jekyll on these files.
6. After the site loads, the expected URL is `https://fordang.github.io/bridge-kids-site/`. Use the live privacy and support URLs in App Store Connect only after Gabriel says the publication is allowed. The children's notice and the terms are linked from those pages. The privacy page says GitHub Pages may keep standard server logs, such as IP address and user agent, under its own policy, and that the publisher does not receive or use them for tracking.

Official steps for the Pages setting: [Configuring a publishing source for your GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). This repository's workflows never flip that setting.

## Secrets

This repository holds no secrets and must not gain any. Do not commit an inbox password, a signing key, an API token, or a filled-in personal address "just for now."

## Open before publication

Counsel and Gabriel still need to close these points. The pages describe the product design; they do not certify compliance.

1. **Contact email.** Gabriel approved `gabrieljohnfordan@gmail.com`. It is the address on the pages.
2. **Email retention.** The pages say a message is kept only as long as needed to answer it and is deleted within 90 days after your request is resolved. **TODO:** retention period pending Gabriel's confirmation. The drafts tell parents not to send a child's personal information and tell the publisher not to build a support database.
3. **Postal address and telephone.** Both are still omitted. COPPA's privacy-policy rule (16 CFR 312.4) generally requires the operator's name, address, telephone number, and email. The email is now published. Counsel has to say whether the address and telephone must still be filled in. `{{POSTAL_ADDRESS_IF_REQUIRED}}` stays a placeholder until that decision. The app is free. Counsel should say whether Japan's Act on Specified Commercial Transactions still requires a public address.
4. **Publisher.** The drafts name Gabriel John Fordan, an individual developer, and no company. Confirm that no other legal entity should appear on the policy or the store listing.
5. **Governing law and venue** are not chosen. The terms say so. Consumer-protection forums may have to be named as well.
6. **Age.** The drafts describe the app as for children aged 3–10. On-device scoring still differs for ages 3–5 and 6–10. Confirm that this matches the App Store age label and the parental gate.
7. **COPPA amended rule** (compliance date 22 April 2026). Confirm that a true zero-collection design, including no persistent identifiers, meets the amended rule, and that the written retention policy in the children's notice is sufficient.
8. **On-device data versus "collection."** Profiles never leave the device. The drafts disclose that storage and still say the publisher does not receive it. Counsel must confirm that the App Store answer "Data Not Collected" remains correct.
9. **Store diagnostics.** Apple may show the developer diagnostics when a user has opted in with the App Store. The app does not ship a crash or analytics SDK. Confirm how the privacy form should describe that.
10. **GDPR Article 8 and the UK Age Appropriate Design Code.** Confirm whether on-device storage or operating-system speech-model downloads create a controller, transparency, or assessment duty before an EU or UK release.
11. **Japan APPI**, including the 2026 amendment's under-16 rules. The effective date depends on a cabinet order that still has to be watched.
12. **Brazil ECA Digital** (Law No. 15.211 of 2025, in force 17 March 2026, with enforcement discussed from January 2027). Legal review is required before a Brazil storefront, including store age assurance.
13. **Vietnam's Personal Data Protection Law** (in force 1 January 2026), including parental consent for younger children. Legal review is required before a Vietnam storefront.
14. **Translations.** Six locales are untranslated. Do not present them as localized policies. Some storefronts require a local-language privacy policy before that storefront opens.
15. **Apple custom-license clauses** are included as a draft, including Apple's warranty sentence on the purchase price of the app. Confirm they match Apple's current schedule. The app is free.
16. **Backup exclusion** (progress does not survive a new device) is still stated for iOS. Confirm that is what should be promised to parents.
17. **GitHub Pages logs.** The privacy page says the host may keep standard server logs, such as IP address and user agent, under GitHub's own policy, and that the publisher does not receive or use them for tracking. Confirm that sentence is enough.
18. **Pages stay off** until Gabriel approves the publication itself, which is separate from approving a pull request that only adds drafts.
