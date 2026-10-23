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

The launch set is English (`release_languages` in `review.json`). Japanese is re-added when the ai_verified ja copy lands (`release_languages_note`). Until then the language switcher, the root language list, and the `hreflang` links point only at English. `ja`, `zh-Hans`, `pt-BR`, `fil`, `vi`, and `ne` stay in the repository so they can be reviewed later. They are not linked from the launch pages. A direct file is still in the repo; it is not part of this release.

`en/` is the source text. Every other locale repeats that English text and shows a **TRANSLATION PENDING** banner. The banner says the copy is an AI draft by the product lead and is taken to `ai_verified` by the JA reviewer. There is no separate human translator. Do not machine-translate the pages. When a reviewed copy replaces the English, remove the banner and set the `lang` attribute on `<html>` (a comment in each non-English file says what to set).

The site root `index.html` links the English documents. `404.html` is only for a later Pages site.

## What the drafts say

The text follows the Bridge Kids privacy design:

- no personal information collected by the publisher, and no Bridge Kids servers
- no accounts and no telemetry, analytics, advertising, or crash SDK
- the app does not use the microphone and does not record audio
- lessons, pictures, and audio are built into the app, and the app does not connect to the internet
- the app is free
- progress, collected stickers, and settings stay on the device and are not backed up
- the daily play-time limit is one allowance per device
- the parent area is in English or Japanese
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
- requires the draft comment until Final Review OK and `site.effective_date` are both set, and the translation banner on non-English pages
- requires English phrases only on English pages: `children aged 3–10`, the 90-day retention line, `IP address`, and `user agent`, plus the approved mailto, the postal-address placeholder, the retention-confirmation comment, and the GitHub Pages log disclosure. Excluded locales skip those phrase checks. English strings are never required on a non-English page. Japanese phrases are added when that copy lands
- rejects Android, Google, subscription, and in-app-purchase wording in the HTML
- validates HTML, CSS, and SVG with the Nu Html Checker
- recomputes `review.json` source hashes and rejects a missing author, a reviewer who is also the author (except the JA self-verify case below), a reviewer outside the allowed identities, a `human_verified` record without a `human:<name>` reviewer, a launch page that links a locale outside `release_languages`, or a hash that does not match the page

The Nu jar is pinned by SHA-256 to the 12 October 2026 "latest" build (`26.10.12`). If that moving release URL no longer matches the pin, the workflow fails closed until someone updates both.

Run the same link checks locally with `python3 scripts/check_site.py`. Run `python3 scripts/review_check.py` for the review file. That command reports unreviewed release-language pages and does not fail on them. Locales outside `release_languages` are reported as excluded. `python3 scripts/review_check.py --release` is the later gate, following PRD §12.8. It checks the languages in `release_languages` (English for now). Unreviewed, flagged, and stale-hash pages in those languages fail. Every other locale is excluded, not failed. English passes as `ai_reviewed` by the author-rule reviewer (`ai-product-lead` is reviewed by `ai-ja-reviewer`, with `ai-qa` as the fallback, or by `human:<name>`; any other author is reviewed by `ai-product-lead` or `human:<name>`) or as `human_verified`. Japanese, once it is back in the launch set, passes as `ai_reviewed` by `ai-ja-reviewer` when `needs_native_check` is false. When that flag is true, Japanese passes only as `ai_verified` by `ai-ja-reviewer` with `reviewed_at` set, or as `human_verified`.

`--release` passes only when `release/checklist.json` has both Gabriel's Final Review OK and `site.effective_date` set to an ISO date. That date is the day the site goes public. The same command fails while any launch page still contains `{{POSTAL_ADDRESS_IF_REQUIRED}}`, the telephone line "Not published in this draft", "Governing law and venue are not chosen", or "retention period pending Gabriel's confirmation". Those placeholders stay in the drafts. They do not fail the default check. A missing OK or a missing effective date fails `--release` only. When both fields are set, `python3 scripts/build_site.py` removes the draft banners and writes `Effective date` and `Last updated` from `site.effective_date`. Until both are set, the banners and the "Draft dated" line stay, and `--release` fails. If the checklist is filled in but the HTML is not regenerated, `--release` still fails because the draft banner is present.

`python3 scripts/review_check.py --write` refreshes `source_hash` after a page edit. A changed hash resets that page to `unreviewed`. An unchanged review is left as it is.

## Content review

`review.json` has `release_languages` (`["en"]` until the ai_verified Japanese copy lands) and one record for each locale page (`ja`, `en`, `zh-Hans`, `pt-BR`, `fil`, `vi`, `ne` × `index`, `privacy`, `children`, `support`, `terms`). Every record starts as `unreviewed`. The author on those starting records is `ai-product-lead`. Non-English pages set `needs_native_check` because the visible text is still the English draft. The Japanese native check is the AI JA reviewer's second pass (`ai_verified`). A human reviewer is optional.

`source_hash` is `sha256:` plus the hex SHA-256 of the page's visible text. Visible text is the text inside `<body>`, excluding `<script>` and `<style>`. The hash is taken after Unicode NFC, after newlines are LF, and after the ends are trimmed. A content edit has to be followed by `--write` so the committed hash matches. A changed hash clears the previous review.

Allowed authors and reviewers are `ai-product-lead`, `ai-ja-reviewer`, `ai-qa`, `ai-designer`, and `human:<name>`. The reviewer has to be a different identity from the author, except PRD §12.8 exception (b). `allow_ja_self_verified` is true and is marked "confirm at Final Review". The exception is only a `ja` page authored by `ai-ja-reviewer`, first passed as `ai_reviewed` by `ai-product-lead`, then `ai_verified` by `ai-ja-reviewer` in a later session. It needs a matching entry in `release/ja-review-log.json` and the path listed in `site.self_verified`. If the flag is false or absent, or the log or the list does not match, `self_verified: true` fails. No page is self-verified in this draft.

`release/checklist.json` records Gabriel's Final Review OK and the public effective date. Until he signs, `final_review_ok` is null and `effective_date` is null. The shape he records is `{"by":"human:gabriel","date":"YYYY-MM-DD","languages":["en"]}`. The languages have to match `release_languages`. `effective_date` is the ISO date of the day the site goes public. `self_verified` is the list of paths using exception (b); it is empty now.

## Publish later, only after Gabriel approves

Do not do this as part of ordinary development, and do not do it from a pull request that he has not approved.

1. Finish legal review. Replace the postal-address placeholder only if counsel says it must be published. Confirm the 90-day email retention line with Gabriel. Choose governing law. Add the JA reviewer's `ai_verified` Japanese copy before linking `ja` again. Confirm the App Store privacy form still matches the text.
2. Get Gabriel's approving review. Nothing merges to `main` without Gabriel. Branch protection should require his approval and this workflow. In `release/checklist.json`, record `final_review_ok` as `{"by":"human:gabriel","date":"YYYY-MM-DD","languages":["en"]}` (the languages must match `release_languages`) and set `site.effective_date` to the ISO date the site goes public.
3. Regenerate with `python3 scripts/build_site.py`. The generator removes `DRAFT – pending legal review` and writes `Effective date` and `Last updated` from `site.effective_date`. Then `python3 scripts/review_check.py --write` and `python3 scripts/review_check.py --release`. `--release` passes only when the Final Review OK and the effective date are both set, the built pages no longer show the draft banner, and the launch pages no longer contain the postal, telephone, governing-law, or retention-confirmation placeholders. The default site check does not use `--release`, so those open items do not fail CI while the pages are still drafts.
4. Merge the approved change to `main`.
5. Only then, a person with admin rights turns on GitHub Pages: **Settings → Pages → Build and deployment → Deploy from a branch → Branch `main` → folder `/ (root)` → Save.**
6. Do not add a custom domain. The zero-spend plan keeps the free `github.io` host. `.nojekyll` is already in the repo so Pages will not run Jekyll on these files.
7. After the site loads, the expected URL is `https://fordang.github.io/bridge-kids-site/`. Use the live privacy and support URLs in App Store Connect only after Gabriel says the publication is allowed. The children's notice and the terms are linked from those pages. The privacy page says GitHub Pages may keep standard server logs, such as IP address and user agent, under its own policy, and that the publisher does not receive or use them for tracking.

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
6. **Age.** The drafts describe the app as for children aged 3–10. On the App Store the Kids category uses Apple's "Ages 5 & Under" band. Confirm that this matches the parental gate.
7. **COPPA amended rule** (compliance date 22 April 2026). Confirm that a true zero-collection design, including no persistent identifiers, meets the amended rule, and that the written retention policy in the children's notice is sufficient.
8. **On-device data versus "collection."** Profiles never leave the device. The drafts disclose that storage and still say the publisher does not receive it. Counsel must confirm that the App Store answer "Data Not Collected" remains correct.
9. **Store diagnostics.** Apple may show the developer diagnostics when a user has opted in with the App Store. The app does not ship a crash or analytics SDK. Confirm how the privacy form should describe that.
10. **GDPR Article 8 and the UK Age Appropriate Design Code.** Confirm whether on-device storage creates a controller, transparency, or assessment duty before an EU or UK release.
11. **Japan APPI**, including the 2026 amendment's under-16 rules. The effective date depends on a cabinet order that still has to be watched.
12. **Brazil ECA Digital** (Law No. 15.211 of 2025, in force 17 March 2026, with enforcement discussed from January 2027). Legal review is required before a Brazil storefront, including store age assurance.
13. **Vietnam's Personal Data Protection Law** (in force 1 January 2026), including parental consent for younger children. Legal review is required before a Vietnam storefront.
14. **Translations.** Japanese is not linked until the JA reviewer's ai_verified copy lands. The other locales are untranslated. Do not present them as localized policies. Some storefronts require a local-language privacy policy before that storefront opens. The copy is an AI draft taken to ai_verified by the language reviewer. There is no separate human translator.
15. **Apple custom-license clauses** are included as a draft, including Apple's warranty sentence on the purchase price of the app. Confirm they match Apple's current schedule. The app is free.
16. **Backup exclusion.** Progress and settings are saved only on the device and are not backed up. Collected stickers are part of what starts over on a new device. Confirm that is what should be promised to parents.
17. **GitHub Pages logs.** The privacy page says the host may keep standard server logs, such as IP address and user agent, under GitHub's own policy, and that the publisher does not receive or use them for tracking. Confirm that sentence is enough.
18. **Pages stay off** until Gabriel approves the publication itself, which is separate from approving a pull request that only adds drafts.
