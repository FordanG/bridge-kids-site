"""English source text for the Bridge Kids legal pages.

Other locales are this same text plus a translation-pending banner.
Do not machine-translate these strings.
"""

from __future__ import annotations

from site_map import (
    APP_ID,
    CONTACT_ADDRESS,
    CONTACT_MAILTO,
    EMAIL_RETENTION_LINE,
    EMAIL_RETENTION_NOTE,
    POSTAL_ADDRESS,
)

CONTACT_LINK = f'<a href="{CONTACT_MAILTO}">{CONTACT_ADDRESS}</a>'

CONTACT_SECTION = f"""
<section id="contact">
  <h2>Contact</h2>
  <p>Publisher: Gabriel John Fordan, an individual developer.</p>
  <dl>
    <dt>Email</dt>
    <dd>{CONTACT_LINK}</dd>
    <dt>Postal address</dt>
    <dd><code>{POSTAL_ADDRESS}</code></dd>
    <dt>Telephone</dt>
    <dd>Not published in this draft.</dd>
  </dl>
  <!-- {EMAIL_RETENTION_NOTE} -->
  <p>Messages to the support address are kept only as long as needed to answer them and are {EMAIL_RETENTION_LINE}.</p>
  <div class="todo">
    <p><strong>TODO:</strong> Replace <code>{POSTAL_ADDRESS}</code> only if legal review says a postal address must be published. Leave the placeholder until then. Do not invent a street address, a post-office box, or a telephone number to fill a gap.</p>
  </div>
</section>
"""

PRIVACY_BODY = f"""
<nav class="on-page" aria-label="On this page">
  <ol>
    <li><a href="#short">The short version</a></li>
    <li><a href="#who">Who we are</a></li>
    <li><a href="#app">What the app is</a></li>
    <li><a href="#not-collected">What we do not collect</a></li>
    <li><a href="#on-device">What stays on the device</a></li>
    <li><a href="#network">The network</a></li>
    <li><a href="#backups">Backups and a new device</a></li>
    <li><a href="#children">Children</a></li>
    <li><a href="#retention">How long information stays</a></li>
    <li><a href="#diagnostics">Store diagnostics</a></li>
    <li><a href="#website">This website</a></li>
    <li><a href="#laws">Store rules and privacy laws</a></li>
    <li><a href="#choices">Choices a parent has</a></li>
    <li><a href="#changes">Changes</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</nav>

<section id="short">
  <h2>The short version</h2>
  <ul>
    <li>Bridge Kids does not collect personal information. We have no accounts and no servers for this app.</li>
    <li>The app does not include analytics, advertising, attribution, or crash-reporting software.</li>
    <li>The app does not use the microphone and does not record audio.</li>
    <li>The app is free.</li>
    <li>Profiles and progress stay on the device. The app excludes them from iOS backup. They do not follow a child to a new device.</li>
    <li>A parent can delete a profile on the device. Removing the app removes its local data.</li>
    <li>The written data retention policy is in the <a href="children.html">Children's privacy and COPPA notice</a>.</li>
  </ul>
</section>

<section id="who">
  <h2>Who we are</h2>
  <p>Bridge Kids is published by Gabriel John Fordan, an individual developer. In this policy, "we" and "the publisher" mean that person. We are not Apple. The App Store and iOS follow Apple's own policies.</p>
</section>

<section id="app">
  <h2>What the app is</h2>
  <p>Bridge Kids is an app for children aged 3–10, used with a parent or guardian, on iPhone and iPad. The app id is {APP_ID}. The app is free. A parent sets the app up. The child uses a separate child area. Settings, deleting a profile, and links to these pages are behind a parental gate. The gate does not ask for a birth date or a birth year.</p>
  <p>A parent can keep up to four child profiles on one device. A profile can hold a nickname, an avatar chosen in the app, an age band, a learning direction, and an optional start date. On the App Store, the app is in the Kids category under Apple's "Ages 5 &amp; Under" band. It is designed for children aged 3–10.</p>
  <p>There are two learning directions: one teaches Japanese and one teaches American English. All lessons, pictures and audio are built into the app. The parent area is in English or Japanese.</p>
  <p>The child area does not show a price. The app is designed without streak counters.</p>
</section>

<section id="not-collected">
  <h2>What we do not collect</h2>
  <p>The app is built so that it does not send personal information to us, and we have no Bridge Kids server that could receive it. We do not collect:</p>
  <ul>
    <li>names, nicknames, avatars, age bands, or any other profile field</li>
    <li>progress, scores, attempts, or learning records</li>
    <li>audio or voice recordings (the app does not use the microphone)</li>
    <li>precise location, contacts, photos, or a camera roll</li>
    <li>an email address, a telephone number, or a password for Bridge Kids (there is no account)</li>
    <li>advertising identifiers or other device identifiers used for tracking, including IDFA and IDFV</li>
    <li>analytics events, advertising measurements, or crash reports from a kit inside the app</li>
    <li>payment card numbers, bank details, or billing addresses</li>
  </ul>
  <p>We do not sell or share personal information, including for targeted advertising. There is no third-party analytics, crash, or advertising software in the app, and the app includes no third-party SDKs.</p>
  <p>Information can still exist on the device, and Apple can still process App Store and iOS data under its own rules. Those cases are described below so they are not hidden behind the words "we do not collect."</p>
</section>

<section id="on-device">
  <h2>What stays on the device</h2>
  <p>The app can save the following in private storage on the device. None of it is sent to the publisher.</p>
  <h3>Child profile</h3>
  <p>A nickname, an avatar, an age band for a child aged 3–10, the learning direction, and an optional start date. Up to four profiles.</p>
  <h3>Learning record</h3>
  <p>Progress, a record of which words your child knows and is still practising, and collected stickers. A parent can look at progress in the parent area.</p>
  <h3>Settings</h3>
  <p>The parent-area language (English or Japanese), the daily play-time limit (one shared daily allowance per device, for all child profiles) and today's play time, and other settings.</p>
</section>

<section id="network">
  <h2>The network</h2>
  <p>All lessons, pictures and audio are built into the app. The app does not connect to the internet and downloads nothing after it is installed. App updates come through the App Store under Apple's rules. Links to these pages open in Safari only after a grown-up passes the parental gate.</p>
</section>

<section id="backups">
  <h2>Backups and a new device</h2>
  <p>Progress and settings are saved only on this device and aren't backed up. If you delete the app or switch to a new device, your child's progress, stickers and settings will start over.</p>
</section>

<section id="children">
  <h2>Children</h2>
  <p>Bridge Kids is directed to children. The <a href="children.html">Children's privacy and COPPA notice</a> is part of this policy. It includes the data retention policy. A parent should read it.</p>
  <p>We do not knowingly receive personal information from a child, or from anyone else, through the app. We do not have a database to search if a parent asks what we hold. The profile is on the device, and the parent can delete it there.</p>
</section>

<section id="retention">
  <h2>How long information stays</h2>
  <p>The full <a href="children.html#retention">data retention policy</a> is in the children's notice. In short:</p>
  <ul>
    <li>We do not retain personal information on a server. We do not collect it, and we do not run a Bridge Kids server.</li>
    <li>On the device, a profile and its learning record stay until a parent deletes that profile, the app is removed, or the operating system clears the app's storage.</li>
    <li>Messages to the support address, {CONTACT_LINK}, are kept only as long as needed to answer them and are {EMAIL_RETENTION_LINE}. They are not copied into an app database. There is no support database.</li>
  </ul>
</section>

<section id="diagnostics">
  <h2>Store diagnostics</h2>
  <p>The app does not include a crash-reporting or analytics library, and it does not send a crash log to us.</p>
  <p>Apple can still produce its own diagnostics. An App Store user can opt in to share analytics with developers. That program belongs to Apple. We do not combine it with a child profile, because the profile never reaches us. Data that Apple collects through its own programs is not part of the app's privacy label, which is "Data Not Collected."</p>
</section>

<section id="website">
  <h2>This website</h2>
  <p><strong>TODO:</strong> Name the site host when a deploy target is configured.</p>
  <p>These pages are static files. They do not set cookies, they do not run scripts, they do not load fonts or pictures from anyone else, and they do not use analytics. The site host may keep standard server logs, such as IP address and user agent, under its own policy. We do not receive those logs, and we do not use them for tracking. A browser translation of this page is not an official translation. The pages ask browsers not to translate them.</p>
</section>

<section id="laws">
  <h2>Store rules and privacy laws</h2>
  <p>This section says which rules the product was designed against. It is not a legal opinion, and it is not a statement that a regulator or a store has approved the app. Counsel still has to review the finished app before each storefront.</p>
  <h3>Apple Kids Category</h3>
  <p>The child area is for children aged 3–10. Links out and parent settings sit behind a parental gate. The app is free. The app does not include third-party advertising or third-party analytics, and it does not send personal information or device identifiers to the publisher or to an advertising network.</p>
  <h3>COPPA</h3>
  <p>The Children's Online Privacy Protection Act, including the amended rule that required compliance by 22 April 2026. Persistent identifiers can be personal information. The app is designed not to collect personal information, including those identifiers. The written retention policy is in the children's notice. The public email is in the contact section. The postal address and telephone number are not finished.</p>
  <h3>GDPR children's rules and the UK Age Appropriate Design Code</h3>
  <p>Article 8 of the GDPR, and the UK code, set extra care around children, including limits on nudge design. We do not receive children's personal data. The app is free and is designed without streak pressure. Whether on-device storage creates any duty before an EU or UK release, including a data-protection assessment, is open for legal review.</p>
  <h3>APPI (Japan)</h3>
  <p>The Act on the Protection of Personal Information, including under-16 changes in the 2026 amendment. The start of those changes depends on a cabinet order. The design does not collect personal information. That order still has to be watched.</p>
  <h3>Brazil, ECA Digital</h3>
  <p>The Digital Child and Adolescent Statute, Law No. 15.211 of 2025, in force on 17 March 2026, with enforcement discussed from January 2027. The design does not collect children's data. Offering the app in Brazil needs its own legal review, including any age-assurance step the stores apply.</p>
  <h3>Vietnam Personal Data Protection Law</h3>
  <p>Vietnam's Personal Data Protection Law, in force on 1 January 2026, includes parental-consent rules for younger children. The design does not collect personal data. Offering the app in Vietnam needs its own legal review.</p>
</section>

<section id="choices">
  <h2>Choices a parent has</h2>
  <ul>
    <li>Delete one child profile in the parent area, behind the parental gate. That removes that profile from the device.</li>
    <li>Remove the app. That removes the app's local data.</li>
    <li>Ask what we hold. Write to {CONTACT_LINK}. The design allows only one honest answer: we do not hold the child's information. Do not send a child's full name, date of birth, or a recording. We do not need them, and email is not a safe place for them.</li>
    <li>If you email us, you can ask us to delete your message. You can also contact your local data-protection authority.</li>
  </ul>
  <p>There is no password to reset and no cloud copy of progress.</p>
</section>

<section id="changes">
  <h2>Changes</h2>
  <p>If this policy changes after it is published, the date at the top will change and the public page will be updated. We have no accounts, so we cannot email users when the policy changes. The app is designed to open this page from the parent area, behind the parental gate, once the site is published.</p>
</section>
""" + CONTACT_SECTION

CHILDREN_BODY = f"""
<nav class="on-page" aria-label="On this page">
  <ol>
    <li><a href="#notice">This notice</a></li>
    <li><a href="#operator">Operator</a></li>
    <li><a href="#directed">Directed to children</a></li>
    <li><a href="#not-collected">Personal information</a></li>
    <li><a href="#on-device">On the device</a></li>
    <li><a href="#identifiers">Identifiers</a></li>
    <li><a href="#parents">Parents' rights</a></li>
    <li><a href="#retention">Data retention policy</a></li>
    <li><a href="#deletion">How to delete</a></li>
    <li><a href="#stores">Apple</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</nav>

<section id="notice">
  <h2>This notice</h2>
  <p>This is the children's privacy notice for Bridge Kids, including the notice for the Children's Online Privacy Protection Act (COPPA). It is part of the <a href="privacy.html">privacy policy</a>. The <a href="#retention">data retention policy</a> below is the written retention policy for the app.</p>
  <p>Please read it as a draft. It has not had legal review, and it is not in force.</p>
</section>

<section id="operator">
  <h2>Operator</h2>
  <p>The operator is Gabriel John Fordan, an individual developer. He is not a store, a school, or a childcare service. The public email is {CONTACT_LINK}. The postal address and telephone number are not finished. A COPPA policy usually includes those as well, so this notice cannot be published as final until legal review fills or formally resolves that gap. See Contact.</p>
</section>

<section id="directed">
  <h2>Directed to children</h2>
  <p>Bridge Kids is an app for children aged 3–10. A parent or guardian sets it up and uses the parent area. The child uses the child area. On the App Store, the app is in the Kids category under Apple's "Ages 5 &amp; Under" band. It is designed for children aged 3–10.</p>
  <p>The child is not asked to create an account, to type an email address, or to accept these terms. There is no account. A grown-up sets up the app, behind a parental gate. The gate does not ask for a birth year.</p>
</section>

<section id="not-collected">
  <h2>Personal information</h2>
  <p>The operator does not collect personal information from children. The app does not send profile information, learning records, or device identifiers to the operator. It does not use the microphone and does not record audio. There is no Bridge Kids account and no Bridge Kids server.</p>
  <p>The app can store a profile and a learning record on the device itself. That information is described in the next section so a parent can see it. It is not transmitted to us. Whether any law still treats that on-device storage as "collection" is a question for counsel before release. The app's App Store privacy label is "Data Not Collected."</p>
</section>

<section id="on-device">
  <h2>On the device</h2>
  <p>Private storage on the device can hold:</p>
  <ul>
    <li>a nickname, an avatar, an age band for a child aged 3–10, a learning direction, and an optional start date, for up to four profiles</li>
    <li>progress, a record of which words your child knows and is still practising, and collected stickers</li>
    <li>parent-area settings, including the language (English or Japanese) and the daily play-time limit (one shared daily allowance per device, for all child profiles), and today's play time</li>
  </ul>
  <p>A parent can see progress in the parent area. The app is free, so the child area does not show a price.</p>
</section>

<section id="identifiers">
  <h2>Identifiers</h2>
  <p>The app does not read the advertising identifier, does not read the identifier for vendors, and does not use a tracking SDK. COPPA treats persistent identifiers as personal information. The design does not collect them for the operator.</p>
</section>

<section id="parents">
  <h2>Parents' rights</h2>
  <p>A parent can refuse to let the child use the app. A parent can review what the app stores by looking at the parent area on the device: we cannot show a remote copy, because we do not have one. A parent can delete a profile on the device, or delete the app.</p>
  <p>A parent can refuse future collection. There is no collection by the operator to turn off. There is also no account to close.</p>
  <p>A parent may write to {CONTACT_LINK} to ask what we hold. Do not include a child's full name, exact birth date, photograph, or voice recording. We do not need them to answer. The answer the design allows is that we do not hold the child's information.</p>
</section>

<section id="retention">
  <h2>Data retention policy</h2>
  <p>This is the written data retention policy for Bridge Kids. It covers children and parents.</p>
  <h3>On our systems</h3>
  <p>We retain nothing. The publisher does not operate a Bridge Kids server, account system, analytics store, or support database. We do not retain personal information or persistent identifiers, because we never receive them. There is no retention schedule for a database we do not have, and no practice of keeping a child's file "just in case."</p>
  <h3>On the device</h3>
  <ul>
    <li>A profile and its learning record remain until the parent deletes that profile, the app is uninstalled, or the operating system deletes the app's storage, whichever comes first.</li>
    <li>The app excludes that data from iOS backup. It is not retained in iCloud, and it is not copied onto a new device.</li>
  </ul>
  <h3>Support messages</h3>
  <p>Messages to the support address, {CONTACT_LINK}, are kept only as long as needed to answer them and are {EMAIL_RETENTION_LINE}. Do not send a child's personal information. The publisher must not copy any such message into an app database. There is nowhere in the product to put it.</p>
  <h3>What this policy does not delete</h3>
  <p>We cannot delete a record held by Apple, and we cannot reach into a device. Device data is deleted by the parent, on the device, as described next.</p>
</section>

<section id="deletion">
  <h2>How to delete</h2>
  <ol>
    <li>Open the grown-ups area and complete the parental gate.</li>
    <li>Delete the child profile. The action is profile deletion in the parent area. Deleting a profile removes that profile's nickname, avatar, age band, direction, start date, and learning record from the device.</li>
    <li>Or remove the app from the device. That removes the app's local data, including every profile on that device.</li>
  </ol>
  <p>Steps for the parent area are on the <a href="support.html">support page</a>.</p>
  <p>We cannot perform this deletion for you, because we never receive the profile. That limit is a result of not collecting the data.</p>
</section>

<section id="stores">
  <h2>Apple</h2>
  <p>Apple distributes the app on the App Store and may process optional diagnostics under its own policies. We do not receive the child's profile from Apple. We do not allow a third-party advertising or analytics SDK to receive it either. Nothing in this notice authorizes a third party to collect personal information from a child through Bridge Kids.</p>
</section>
""" + CONTACT_SECTION

SUPPORT_BODY = f"""
<nav class="on-page" aria-label="On this page">
  <ol>
    <li><a href="#no-account">No account</a></li>
    <li><a href="#gate">The parental gate</a></li>
    <li><a href="#delete">Delete a profile</a></li>
    <li><a href="#offline">Offline use</a></li>
    <li><a href="#new-device">A new device</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#what-to-write">What to include</a></li>
  </ol>
</nav>

<section id="no-account">
  <h2>No account</h2>
  <p>Bridge Kids is an app for children aged 3–10 on iPhone and iPad. It has no sign-up, no password, and no login. This page has no form and no chat. Nothing you type in the browser is sent, because the page does not run code and has nowhere to type. We cannot look up a child or a progress record. We do not have them.</p>
  <p>The privacy policy and the children's notice explain what stays on the device: <a href="privacy.html">Privacy policy</a>, <a href="children.html">Children's privacy and COPPA notice</a>.</p>
</section>

<section id="gate">
  <h2>The parental gate</h2>
  <p>Settings, deleting a profile, and links out to these pages are behind a gate meant for a grown-up. The gate does not ask for a birth year. It is a barrier, not a guarantee that nobody can pass it. The app is free, so the child area has no price to show.</p>
</section>

<section id="delete">
  <h2>Delete a profile</h2>
  <ol>
    <li>Open the grown-ups control from the child home or the progress map, and complete the gate.</li>
    <li>In the parent area, delete the profile you want to remove.</li>
  </ol>
  <p>Deletion removes that profile's nickname, avatar, age band, learning direction, optional start date, and learning record from the device. Removing the whole app removes every profile's local data on that device.</p>
</section>

<section id="offline">
  <h2>Offline use</h2>
  <p>Everything the app needs is built in, so it works without an internet connection from the first launch. Nothing is downloaded after installation.</p>
</section>

<section id="new-device">
  <h2>A new device</h2>
  <p>Progress and settings are saved only on this device and aren't backed up. If you delete the app or switch to a new device, your child's progress, stickers and settings will start over.</p>
</section>
""" + CONTACT_SECTION + f"""
<section id="what-to-write">
  <h2>What to include</h2>
  <p>Write to {CONTACT_LINK}. Include the device type (iPhone or iPad) and what you expected to happen. Leave out the child's real name, a voice recording, and screenshots that show a nickname. We do not need them, and email is a poor place for them.</p>
</section>
"""

TERMS_BODY = f"""
<nav class="on-page" aria-label="On this page">
  <ol>
    <li><a href="#draft">This draft</a></li>
    <li><a href="#who">Who offers the app</a></li>
    <li><a href="#agreement">Agreeing</a></li>
    <li><a href="#the-app">The app</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#parents">Parents and children</a></li>
    <li><a href="#accounts">No accounts</a></li>
    <li><a href="#apple">Apple App Store</a></li>
    <li><a href="#privacy">Privacy</a></li>
    <li><a href="#use">Acceptable use</a></li>
    <li><a href="#availability">Availability</a></li>
    <li><a href="#liability">Warranties and liability</a></li>
    <li><a href="#law">Governing law</a></li>
    <li><a href="#changes">Changes</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</nav>

<section id="draft">
  <h2>This draft</h2>
  <p>These are draft terms for the Bridge Kids app. They are not in force, they have not had legal review, and they are not legal advice. The English text is the source. A browser translation is not a set of terms.</p>
  <p>Do not treat a missing clause as a promise. Several decisions are still open, including governing law and whether a postal address must be published. They are marked where they come up. The public email is in the contact section.</p>
</section>

<section id="who">
  <h2>Who offers the app</h2>
  <p>Bridge Kids is offered by Gabriel John Fordan, an individual developer. If you accept the published terms, the agreement is between you and that publisher. It is not an agreement with Apple, except for the App Store terms you already have with Apple.</p>
</section>

<section id="agreement">
  <h2>Agreeing</h2>
  <p>A parent or legal guardian agrees to these terms for a child. The child is not asked to accept a contract. If you are a child reading this, please hand the device to a grown-up before using anything behind the parental gate.</p>
  <p>Once these terms are published and in force, do not download or use the app if you do not agree to them. Store rules may also require you to accept the store's own terms before you can install the app.</p>
</section>

<section id="the-app">
  <h2>The app</h2>
  <p>Bridge Kids is an app for children aged 3–10 on iPhone and iPad. The app id is {APP_ID}. The app is free. It is a learning aid. It is not a school, not a medical device, and not a childcare service. We do not promise a learning result, a reading level, or a test score.</p>
  <p>The child area is separate from the parent area. Up to four child profiles can exist on one device. Two learning directions exist: one teaches Japanese and one teaches American English.</p>
</section>

<section id="license">
  <h2>License</h2>
  <p>The publisher grants you a personal, non-exclusive, non-transferable, revocable license to use the app on devices you own or control, as the store's usage rules allow. We reserve every right that this license does not grant.</p>
  <p>The app, its artwork, audio, animation, and text are owned by the publisher or used with permission. You may not copy the lessons, pictures, or audio, resell access, or present the app as your own product. You may not reverse engineer the app except where a statute forbids that limit.</p>
  <p>Apple, App Store, iOS, iPadOS, and iPhone are marks of Apple. They are named here to identify the store. The publisher is not affiliated with Apple.</p>
</section>

<section id="parents">
  <h2>Parents and children</h2>
  <p>You are responsible for the device and for deciding whether a child may use the app. The parental gate stands in front of settings, profile deletion, and links to these pages. The gate does not ask for a birth year. It reduces the chance that a child acts alone. It is not a promise that a determined person cannot get past it.</p>
  <p>The app is free. The child area does not show a price.</p>
</section>

<section id="accounts">
  <h2>No accounts</h2>
  <p>Bridge Kids does not have user accounts. There is nothing to register. Installing the app from the App Store does not create a Bridge Kids profile in the cloud.</p>
</section>

<section id="apple">
  <h2>Apple App Store</h2>
  <p>If you downloaded Bridge Kids from the Apple App Store, Apple requires the following points in a custom license. They are included here as a draft, and counsel must confirm they still match Apple's current schedule before submission.</p>
  <ol>
    <li>This agreement is between you and Gabriel John Fordan only, and not with Apple. The publisher, not Apple, is solely responsible for the app and its content.</li>
    <li>The license is limited and non-transferable. You may use the app on Apple-branded products that you own or control, as permitted by the Usage Rules in Apple's Media Services terms.</li>
    <li>The publisher is solely responsible for maintenance and support. Apple has no obligation to provide maintenance or support for the app.</li>
    <li>If the app fails to conform to any applicable warranty, you may notify Apple, and Apple may refund the purchase price, if any (the app is free). To the maximum extent permitted by law, Apple has no other warranty obligation for the app. Any other claim, loss, liability, damage, cost, or expense attributable to a failure to conform to a warranty is the publisher's responsibility.</li>
    <li>The publisher, not Apple, is responsible for addressing claims relating to the app or to possession or use of the app, including product-liability claims, claims that the app fails to meet a legal or regulatory requirement, and claims under consumer protection or similar legislation.</li>
    <li>The publisher, not Apple, is responsible for the investigation, defense, settlement, and discharge of any claim that the app, or your possession and use of it, infringes a third party's intellectual-property right.</li>
    <li>You represent that you are not located in a country subject to a United States government embargo, and that you are not listed on any United States government list of prohibited or restricted parties.</li>
    <li>Questions, complaints, and claims go to the publisher, at the email in the contact section. The postal address is still a placeholder until legal review decides whether one must be published.</li>
    <li>You must also comply with third-party terms that apply while you use the app, including your wireless-carrier terms where a network is used.</li>
    <li>Apple and Apple's subsidiaries are third-party beneficiaries of these terms. Once you accept them, Apple has the right to enforce them against you.</li>
  </ol>
</section>

<section id="privacy">
  <h2>Privacy</h2>
  <p>The <a href="privacy.html">privacy policy</a> and the <a href="children.html">children's privacy and COPPA notice</a> describe how little information leaves the device. They include the data retention policy. Using the app after those documents are in force means the parent has had a chance to read them. The app is designed not to send a child's information to us.</p>
</section>

<section id="use">
  <h2>Acceptable use</h2>
  <p>Use the app for the child's learning, under a parent's supervision. Do not use it to advertise to children, to collect information from children, or to bypass the parental gate. Do not send us a child's personal information.</p>
</section>

<section id="availability">
  <h2>Availability</h2>
  <p>We may change, pause, or withdraw the app or a chapter. The lessons are built into the app. We do not promise that the App Store will keep offering the app or its updates. Progress and settings are saved only on this device and aren't backed up. If you delete the app or switch to a new device, your child's progress, stickers and settings will start over. The <a href="privacy.html#backups">privacy policy</a> states it in plain language.</p>
</section>

<section id="liability">
  <h2>Warranties and liability</h2>
  <p>This section is a draft and needs legal review more than any other. Mandatory consumer rights stay in force. In many places, including Japan, the European Union, the United Kingdom, Brazil, Vietnam, and parts of the United States, a private term cannot remove a right that a statute gives a consumer. Those rights remain. This draft does not choose the country whose law applies. See the next section.</p>
  <p>To the extent a mandatory rule does not say otherwise, the app is provided as available, without a warranty of uninterrupted service or of a particular learning outcome, and the publisher is not liable for progress that existed only on the device or for a store outage. Nothing in this paragraph limits liability that the law says cannot be limited, including liability for fraud or for death or personal injury caused by negligence where that limit is forbidden.</p>
  <p>If a term in this draft is unenforceable, the rest of the draft remains for review. That sentence does not make the draft binding.</p>
</section>

<section id="law">
  <h2>Governing law</h2>
  <p>Governing law and venue are not chosen. This draft does not name a country, a court, or an arbitration program. <strong>TODO:</strong> Gabriel John Fordan and counsel must choose the governing law, and must say whether any consumer-protection forum has to be named, before these terms are published. Do not infer a jurisdiction from the language of this draft or from where the website is hosted.</p>
</section>

<section id="changes">
  <h2>Changes</h2>
  <p>If the terms change after publication, the date on the page will change. We cannot email a change notice, because there are no accounts. The new page is the notice. Continued use after the new terms are in force is the parent's decision.</p>
</section>
""" + CONTACT_SECTION

PAGE_BODIES: dict[str, str] = {
    "privacy": PRIVACY_BODY,
    "children": CHILDREN_BODY,
    "support": SUPPORT_BODY,
    "terms": TERMS_BODY,
}

PAGE_DESCRIPTIONS: dict[str, str] = {
    "index": "Draft privacy, children's privacy, support, and terms for Bridge Kids.",
    "privacy": "Draft privacy policy for Bridge Kids. The app does not collect personal information.",
    "children": "Draft children's privacy and COPPA notice for Bridge Kids, including the data retention policy.",
    "support": "Draft support for Bridge Kids: delete a profile, backups, and contact the publisher.",
    "terms": "Draft terms of use for Bridge Kids on iPhone and iPad.",
    "404": "That page is not on the Bridge Kids site.",
}
