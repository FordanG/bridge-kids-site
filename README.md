# Bridge Kids site

**DRAFT – pending legal review.**

Static privacy, children's privacy, support, and terms pages for Bridge Kids, the children's English-learning apps for iPhone, iPad, and Android. The publisher is Gabriel John Fordan, an individual developer.

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

`en/` is the source text. Every other locale repeats that English text and shows a **TRANSLATION PENDING** banner. Those pages are not translations. Do not machine-translate them. A reviewed human translation has to replace the English, remove the banner, and set the `lang` attribute on `<html>` (a comment in each non-English file says what to set).

The site root `index.html` is the language list plus links to the English documents. `404.html` is only for a later Pages site.

## What the drafts say

The text follows the Bridge Kids privacy design:

- no personal information collected by the publisher, and no Bridge Kids servers
- no accounts and no telemetry, analytics, advertising, or crash SDK
- on-device speech only, with an attempt-only fallback, and audio not stored
- store billing only (Apple In-App Purchase or Google Play Billing); no receipt server
- profiles and progress excluded from backups and from device transfer
- designed against the Apple Kids Category, Google Play Families, COPPA, the GDPR children's rules, the UK Age Appropriate Design Code, Japan's APPI, Brazil's ECA Digital, and Vietnam's Personal Data Protection Law

The drafts say where a decision is still open instead of inventing it. In-app purchases are not offered at launch. If purchases are added later, they go through the App Store, and these pages have to be updated first. Governing law is not chosen.

The app id, where a page names it, is `com.vendrato.bridgekids`.

## Contact and the remaining placeholder

The public contact email is [gabrieljohnfordan@gmail.com](mailto:gabrieljohnfordan@gmail.com), the address Gabriel approved. On the pages it is a `mailto:` link. No postal address and no telephone number are included.

- `{{POSTAL_ADDRESS_IF_REQUIRED}}` stands in for a postal address, and only if legal review says one must be published.

Each legal page has a **TODO** note next to that placeholder. Do not replace it with a home address or a guessed phone number.

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
- rejects external `href` and `src` values except `https` links to `apps.apple.com`, `itunes.apple.com`, and `play.google.com`, and except `mailto:gabrieljohnfordan@gmail.com`
- rejects remote CSS and remote SVG references
- rejects broken internal links and broken fragments
- requires the draft comment, the translation banner on non-English pages, the approved mailto, and the postal-address placeholder
- validates HTML, CSS, and SVG with the Nu Html Checker

The Nu jar is pinned by SHA-256 to the 12 October 2026 "latest" build (`26.10.12`). If that moving release URL no longer matches the pin, the workflow fails closed until someone updates both.

Run the same link checks locally with `python3 scripts/check_site.py`.

## Publish later, only after Gabriel approves

Do not do this as part of ordinary development, and do not do it from a pull request that he has not approved.

1. Finish legal review. Replace the postal-address placeholder only if counsel says it must be published. Add a human translation for a locale only after that translation is reviewed. Confirm the store privacy forms still match the text. Do not turn purchases on without updating these pages first.
2. Get Gabriel's approving review. Nothing merges to `main` without Gabriel. Branch protection should require his approval and this workflow.
3. Merge the approved change to `main`.
4. Only then, a person with admin rights turns on GitHub Pages: **Settings → Pages → Build and deployment → Deploy from a branch → Branch `main` → folder `/ (root)` → Save.**
5. Do not add a custom domain. The zero-spend plan keeps the free `github.io` host. `.nojekyll` is already in the repo so Pages will not run Jekyll on these files.
6. After the site loads, the expected URL is `https://fordang.github.io/bridge-kids-site/`. Use the live privacy and support URLs in App Store Connect and Play Console only after Gabriel says the publication is allowed. The children's notice and the terms are linked from those pages.

Official steps for the Pages setting: [Configuring a publishing source for your GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). This repository's workflows never flip that setting.

## Secrets

This repository holds no secrets and must not gain any. Do not commit an inbox password, a signing key, an API token, or a filled-in personal address "just for now."

## Open before publication

Counsel and Gabriel still need to close these points. The pages describe the product design; they do not certify compliance.

1. **Contact email.** Gabriel approved `gabrieljohnfordan@gmail.com`. It is the address on the pages. How long that mailbox may keep a message is still open (see below).
2. **Postal address and telephone.** Both are still omitted. COPPA's privacy-policy rule (16 CFR 312.4) generally requires the operator's name, address, telephone number, and email. The email is now published. Counsel has to say whether the address and telephone must still be filled in. `{{POSTAL_ADDRESS_IF_REQUIRED}}` stays a placeholder until that decision. With no in-app purchase at launch, counsel should also say whether Japan's Act on Specified Commercial Transactions still requires a public address.
3. **Publisher.** The drafts name Gabriel John Fordan, an individual developer, and no company. Confirm that no other legal entity should appear on the policy or the store listings.
4. **Governing law and venue** are not chosen. The terms say so. Consumer-protection forums may have to be named as well.
5. **Merchant of record** is not a launch question, because purchases are not offered. If purchases are added later through the App Store, who the merchant is still has to be stated correctly.
6. **Purchases.** The MVP has no in-app purchases. The privacy policy, terms, and support page say that, and they say a later purchase would go through the App Store. Do not ship a purchase without updating these drafts. The earlier subscription price, free-trial, Family Sharing, and seven-day grace statements are withdrawn.
7. **Age bands.** In the app they are about 3–5 and about 6–10. The architecture's store notes talk about Apple's Kids Category as one younger band and about Google Play Families audience labels that are not the same pair. The store listing, this text, and the parental gate need one agreed description.
8. **COPPA amended rule** (compliance date 22 April 2026). Confirm that a true zero-collection design, including no persistent identifiers, meets the amended rule, and that the written retention policy in the children's notice is sufficient.
9. **On-device data versus "collection."** Profiles never leave the device. The drafts disclose that storage and still say the publisher does not receive it. Counsel must confirm that the store answers "Data Not Collected" and "No data collected or shared" remain correct.
10. **Store diagnostics.** Apple and Google may show the developer diagnostics when a user has opted in with the store. The app does not ship a crash or analytics SDK. Confirm how the privacy forms should describe that.
11. **GDPR Article 8 and the UK Age Appropriate Design Code.** Confirm whether on-device storage or operating-system speech-model downloads create a controller, transparency, or assessment duty before an EU or UK release. Purchases are not part of the launch version.
12. **Japan APPI**, including the 2026 amendment's under-16 rules. The effective date depends on a cabinet order that still has to be watched.
13. **Brazil ECA Digital** (Law No. 15.211 of 2025, in force 17 March 2026, with enforcement discussed from January 2027). Legal review is required before a Brazil storefront, including store age assurance.
14. **Vietnam's Personal Data Protection Law** (in force 1 January 2026), including parental consent for younger children. Legal review is required before a Vietnam storefront.
15. **Translations.** Six locales are untranslated. Do not present them as localized policies. Some storefronts require a local-language privacy policy before that storefront opens.
16. **Email retention.** The contact address is published. Set how long that mailbox may keep a message. The drafts tell parents not to send a child's personal information and tell the publisher not to build a support database.
17. **Apple custom-license clauses** are included as a draft. Confirm they match Apple's current schedule, and confirm whether Google Play needs any extra clause.
18. **Backup exclusion** (progress does not survive a new device) is still stated. The seven-day Android offline grace was a subscription rule and is not part of this draft, because purchases are not offered at launch.
19. **Pages stay off** until Gabriel approves the publication itself, which is separate from approving a pull request that only adds drafts.
