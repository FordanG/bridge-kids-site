"""English source text for the Bridge Kids legal pages.

Other locales are this same text plus a translation-pending banner.
Do not machine-translate these strings.
"""

from __future__ import annotations

from site_map import CONTACT_EMAIL, POSTAL_ADDRESS

CONTACT_SECTION = f"""
<section id="contact">
  <h2>Contact</h2>
  <p>Publisher: Gabriel John Fordan, an individual developer.</p>
  <dl>
    <dt>Email</dt>
    <dd><code>{CONTACT_EMAIL}</code></dd>
    <dt>Postal address</dt>
    <dd><code>{POSTAL_ADDRESS}</code></dd>
    <dt>Telephone</dt>
    <dd>Not published in this draft.</dd>
  </dl>
  <div class="todo">
    <p><strong>TODO:</strong> Replace <code>{CONTACT_EMAIL}</code> with the public contact address Gabriel John Fordan approves. Do not publish a personal email address until he chooses one.</p>
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
    <li><a href="#speech">Microphone and speech</a></li>
    <li><a href="#purchases">Purchases</a></li>
    <li><a href="#network">Downloads and the network</a></li>
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
    <li>Speech recognition runs on the device. If that is not available, the app only notes that the child tried. Audio is not stored and is not sent to us.</li>
    <li>Parents pay Apple or Google. We never see the payment card or the billing address.</li>
    <li>Profiles and progress stay on the device. The app excludes them from backups and from device-to-device transfer. They do not follow a child to a new device.</li>
    <li>A parent can delete a profile on the device. Removing the app removes its local data. Cancel a subscription in the store, or it can renew.</li>
    <li>The written data retention policy is in the <a href="children.html">Children's privacy and COPPA notice</a>.</li>
  </ul>
</section>

<section id="who">
  <h2>Who we are</h2>
  <p>Bridge Kids is published by Gabriel John Fordan, an individual developer. In this policy, "we" and "the publisher" mean that person. We are not Apple and we are not Google. Their stores, payment services, and operating systems follow their own policies.</p>
  <p>This draft does not name a company. Whether any legal entity other than the individual publisher should appear here is unresolved.</p>
</section>

<section id="app">
  <h2>What the app is</h2>
  <p>Bridge Kids is an English-learning app for young children, used with a parent or guardian, on iPhone, iPad, and Android. A parent sets the app up. The child uses a separate child area. Purchases, subscription management, settings, deleting a profile, and links to these pages are behind a parental gate. The gate does not ask for a birth date or a birth year.</p>
  <p>A parent can keep up to four child profiles on one device. A profile can hold a nickname, an avatar chosen in the app, an age band, a learning direction, and an optional start date. The age bands in the app are about 3 to 5 and about 6 to 10. Apple's and Google's store age labels are different from those bands. The exact store age selection is not final in this draft.</p>
  <p>There are two learning directions. One uses Japanese speech on the device. The other uses American English speech on the device. The parent area can be shown in Japanese, English, Simplified Chinese, Brazilian Portuguese, Filipino, Vietnamese, or Nepali. This website uses that same list. Only the English text has been written.</p>
  <p>The child area does not show prices. The app is designed without streak counters and without prompts that push a child toward a purchase.</p>
</section>

<section id="not-collected">
  <h2>What we do not collect</h2>
  <p>The app is built so that it does not send personal information to us, and we have no Bridge Kids server that could receive it. We do not collect:</p>
  <ul>
    <li>names, nicknames, avatars, age bands, or any other profile field</li>
    <li>progress, scores, attempts, or learning records</li>
    <li>microphone audio, or text produced by speech recognition</li>
    <li>precise location, contacts, photos, or a camera roll</li>
    <li>an email address, a telephone number, or a password for Bridge Kids (there is no account)</li>
    <li>advertising identifiers or other device identifiers used for tracking, including IDFA, IDFV, and the Android advertising ID</li>
    <li>analytics events, advertising measurements, or crash reports from a kit inside the app</li>
    <li>payment card numbers, bank details, or billing addresses</li>
  </ul>
  <p>We do not sell personal information. We do not share it with advertisers. There is no third-party analytics, crash, or advertising software in the app, and the child-facing side of the app is built without third-party code.</p>
  <p>Information can still exist on the device, and Apple or Google can still process store and operating-system data under their own rules. Those cases are described below so they are not hidden behind the words "we do not collect."</p>
</section>

<section id="on-device">
  <h2>What stays on the device</h2>
  <p>The app can save the following in private storage on the device. None of it is sent to the publisher.</p>
  <h3>Child profile</h3>
  <p>A nickname, an avatar, an age band (about 3 to 5, or about 6 to 10), the learning direction, and an optional start date. Up to four profiles.</p>
  <h3>Learning record</h3>
  <p>Progress, the on-device learning model, smileys, and speaking attempts. A parent can look at progress in the parent area. For ages about 3 to 5, a speaking try is encouraged and is not scored. For ages about 6 to 10, a lenient check runs on the device.</p>
  <h3>Settings</h3>
  <p>The parent-area language and other settings.</p>
  <h3>Subscription status</h3>
  <p>A local note of whether the store subscription is active. On iOS this note is kept in the Keychain for this device only. It is not a copy of a payment card. The store is the record of the purchase.</p>
</section>

<section id="speech">
  <h2>Microphone and speech</h2>
  <p>The microphone lets a child try saying a word or phrase. This is what the app does with that audio.</p>
  <ul>
    <li>Recognition is on-device only. The app does not include a cloud speech service.</li>
    <li>On Apple devices, the app requests on-device recognition and does not use Apple's server speech path.</li>
    <li>On Android, the app uses the on-device recognizer. It does not use the Android recognizer that Google describes as likely to stream audio to remote servers.</li>
    <li>The language is the language of the learning direction: Japanese, or American English.</li>
    <li>Audio is handled in memory for the attempt. It is not written to disk, not added to the learning record, and not sent to us.</li>
    <li>If the device produces recognition text, that text stays in memory only long enough to compare the attempt, and is then discarded. It is not written to disk and not sent to us.</li>
    <li>If on-device recognition is not available, the app uses an attempt-only check that also stays on the device. It can tell that the child spoke. It does not need a transcript.</li>
    <li>The operating system may download a speech model from Apple or Google the first time speech is needed. That download is between the device and Apple or Google. The child's voice is not uploaded by Bridge Kids as part of it.</li>
    <li>If microphone permission is declined, the child can keep learning by listening and tapping. The permission explanation is for the parent, behind the gate. The app does not nag the child.</li>
  </ul>
</section>

<section id="purchases">
  <h2>Purchases</h2>
  <p>An optional subscription is sold only by Apple In-App Purchase or Google Play Billing. We do not run a checkout, and we do not run a receipt server. We never receive the payment card number, the billing address, or the store's payment record.</p>
  <ul>
    <li>The price, billing period, tax, and renewal terms are shown by the store before payment. This draft does not lock a price.</li>
    <li>There is no free trial and no introductory discount in the current design.</li>
    <li>Chapters 1, 2, and 4 in each direction work without a subscription. A subscription unlocks the other chapters, both directions, and up to four profiles on that device.</li>
    <li>Calling the subscription a family plan means those profiles on that device. Apple Family Sharing for the subscription is off. The purchase does not spread to other Apple IDs through Family Sharing, and it does not move between iOS and Android. There is no Bridge Kids account to carry it.</li>
    <li>On Android, if the store cannot be reached, the current design can keep paid chapters available on that device for seven days after the last on-device check, and then show them as sleeping. Downloaded material is not deleted.</li>
    <li>A purchase can sit pending while the store waits for a parent's approval. The child area still does not show a price.</li>
    <li>Restore and subscription management are in the parent area, behind the gate. Cancellation is done with Apple or Google. See <a href="support.html">Support</a>.</li>
  </ul>
</section>

<section id="network">
  <h2>Downloads and the network</h2>
  <p>Content packs are hosted by Apple and Google, not by us. After a pack is on the device, the child area is meant to work offline. The device may still contact Apple or Google to download or update a pack, to complete or restore a purchase, or to download an on-device speech model. We do not operate those connections, and we do not see the child's profile in them.</p>
</section>

<section id="backups">
  <h2>Backups and a new device</h2>
  <p>Profiles, progress, and settings are stored so the operating system will not copy them into a backup or a device-to-device transfer.</p>
  <ul>
    <li>On iOS, the app's data directory is excluded from backup.</li>
    <li>On Android, backup is turned off, and the current design also excludes the data from cloud backup and from device transfer.</li>
  </ul>
  <p>If the device is replaced, restored from a backup, or the app is removed, the profiles and progress do not come back. This is intentional. A subscription can still be restored from the same store account, because the store keeps the purchase. We cannot restore progress, because we never received it.</p>
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
    <li>Microphone audio and recognition text are not kept after the speaking attempt.</li>
    <li>Apple or Google keep store purchases under their own rules. We do not keep a payment record.</li>
    <li>No support inbox is published yet. There is no support database.</li>
  </ul>
</section>

<section id="diagnostics">
  <h2>Store diagnostics</h2>
  <p>The app does not include a crash-reporting or analytics library, and it does not send a crash log to us.</p>
  <p>Apple and Google can still produce their own diagnostics. An App Store user can opt in to share analytics with developers. Google Play can show Android vitals for users who opted in to usage and diagnostics. Those programs belong to the stores. We do not combine them with a child profile, because the profile never reaches us. How the store privacy forms should describe this, next to the planned answers "Data Not Collected" and "No data collected or shared," is open for legal review before release.</p>
</section>

<section id="website">
  <h2>This website</h2>
  <p>These pages are static files. They do not set cookies, they do not run scripts, they do not load fonts or pictures from anyone else, and they do not use analytics. Browser translation of this draft is not an official translation. The pages ask browsers not to translate them.</p>
  <p>The site is intended, later, for free GitHub Pages, and only after Gabriel John Fordan approves publication. These drafts are not the live policy URL until that happens.</p>
</section>

<section id="laws">
  <h2>Store rules and privacy laws</h2>
  <p>This section says which rules the product was designed against. It is not a legal opinion, and it is not a statement that a regulator or a store has approved the app. Counsel still has to review the finished app before each storefront.</p>
  <h3>Apple Kids Category</h3>
  <p>The child area is for children. Links out, purchases, and parent settings sit behind a parental gate. The app does not include third-party advertising or third-party analytics, and it does not send personal information or device identifiers to the publisher or to an advertising network.</p>
  <h3>Google Play Families</h3>
  <p>The app does not use the advertising ID. Microphone audio stays on the device, as described above. The Families disclosure and the Data safety form still have to be completed from the finished app.</p>
  <h3>COPPA</h3>
  <p>The Children's Online Privacy Protection Act, including the amended rule that required compliance by 22 April 2026. Persistent identifiers can be personal information. The app is designed not to collect personal information, including those identifiers. The written retention policy is in the children's notice. The operator's public email, postal address, and telephone number are not finished. See the contact section.</p>
  <h3>GDPR children's rules and the UK Age Appropriate Design Code</h3>
  <p>Article 8 of the GDPR, and the UK code, set extra care around children, including limits on nudge design. We do not receive children's personal data. The app is designed without streak pressure and without purchase prompts to the child. Whether on-device storage, speech-model downloads, or store billing create any duty before an EU or UK release, including a data-protection assessment, is open.</p>
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
    <li>Refuse the microphone. Listening and tapping still work.</li>
    <li>Delete one child profile in the parent area, behind the parental gate. That removes that profile from the device. It does not cancel a subscription.</li>
    <li>Remove the app. That removes the app's local data. Cancel the subscription with Apple or Google, or it can renew.</li>
    <li>Ask what we hold. When an address is published, write to <code>{CONTACT_EMAIL}</code>. The design allows only one honest answer: we do not hold the child's information. Do not send a child's full name, date of birth, or a recording. We do not need them, and this draft has no secure place to put them.</li>
  </ul>
  <p>There is no password to reset and no cloud copy of progress to download.</p>
</section>

<section id="changes">
  <h2>Changes</h2>
  <p>If this policy changes after it is published, the date at the top will change and the public page will be updated. We have no accounts, so we cannot email users about a change. The app is designed to open this page from the parent area, behind the parental gate, once the site is published.</p>
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
    <li><a href="#speech">Microphone</a></li>
    <li><a href="#identifiers">Identifiers</a></li>
    <li><a href="#parents">Parents' rights</a></li>
    <li><a href="#retention">Data retention policy</a></li>
    <li><a href="#deletion">How to delete</a></li>
    <li><a href="#stores">Apple and Google</a></li>
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
  <p>The operator is Gabriel John Fordan, an individual developer. He is not a store, a school, or a childcare service. The public email, postal address, and telephone number are not finished. They are required content for a COPPA policy in the usual case, so this notice cannot be published as final until legal review fills or formally resolves that gap. See Contact.</p>
</section>

<section id="directed">
  <h2>Directed to children</h2>
  <p>Bridge Kids is directed to children. A parent or guardian sets it up and uses the parent area. The child uses the child area. The in-app age bands are about 3 to 5 and about 6 to 10. Store age categories use the stores' own labels and are not final in this draft.</p>
  <p>The child is not asked to create an account, to type an email address, or to accept these terms. A grown-up does that, behind a parental gate. The gate does not ask for a birth year.</p>
</section>

<section id="not-collected">
  <h2>Personal information</h2>
  <p>The operator does not collect personal information from children. The app does not send profile information, learning records, audio, or device identifiers to the operator. There is no Bridge Kids account and no Bridge Kids server.</p>
  <p>The app can store a profile and a learning record on the device itself. That information is described in the next section so a parent can see it. It is not transmitted to us. Whether any law still treats that on-device storage as "collection" is a question for counsel before release. The store privacy forms are planned as "Data Not Collected" on the App Store and "No data collected" and "No data shared" on Google Play, and those answers have to be checked against this disclosure.</p>
</section>

<section id="on-device">
  <h2>On the device</h2>
  <p>Private storage on the device can hold:</p>
  <ul>
    <li>a nickname, an avatar, an age band, a learning direction, and an optional start date, for up to four profiles</li>
    <li>progress, the on-device learning model, smileys, and speaking attempts</li>
    <li>parent-area settings, including language</li>
    <li>a local note of subscription status, which is not payment-card data</li>
  </ul>
  <p>A parent can see progress in the parent area. The child area does not show prices.</p>
</section>

<section id="speech">
  <h2>Microphone</h2>
  <p>If a parent allows the microphone, the child can try speaking. Audio stays in memory on the device for that attempt. It is not stored, not sent to the operator, and not sent to an advertising network. Recognition text, if the device creates any, is discarded when the attempt is judged. If the device cannot do on-device recognition, the app only marks that the child tried, still on the device.</p>
  <p>The app does not use a cloud speech recognizer. A speech model may be downloaded by the operating system from Apple or Google. That is a store or system download, not a Bridge Kids upload of the child's voice.</p>
</section>

<section id="identifiers">
  <h2>Identifiers</h2>
  <p>The app does not read the advertising identifier on iOS or Android, does not read the identifier for vendors, and does not use a tracking SDK. The Android advertising-ID permission is not part of the app. COPPA treats persistent identifiers as personal information. The design does not collect them for the operator.</p>
</section>

<section id="parents">
  <h2>Parents' rights</h2>
  <p>A parent can refuse to let the child use the app, refuse the microphone, and still use listen-and-tap. A parent can review what the app stores by looking at the parent area on the device: we cannot show a remote copy, because we do not have one. A parent can delete a profile on the device, or delete the app.</p>
  <p>A parent can refuse future collection. There is no collection by the operator to turn off. There is also no account to close.</p>
  <p>When a contact address exists, a parent may write to <code>{CONTACT_EMAIL}</code> to ask what we hold. Do not include a child's full name, exact birth date, photograph, or voice recording. We do not need them to answer. The answer the design allows is that we hold nothing about the child.</p>
</section>

<section id="retention">
  <h2>Data retention policy</h2>
  <p>This is the written data retention policy for Bridge Kids. It covers children and parents.</p>
  <h3>On our systems</h3>
  <p>We retain nothing. The publisher does not operate a Bridge Kids server, account system, analytics store, or support database. We do not retain personal information, persistent identifiers, audio, or transcripts, because we never receive them. There is no retention schedule for a database we do not have, and no practice of keeping a child's file "just in case."</p>
  <h3>On the device</h3>
  <ul>
    <li>A profile and its learning record remain until the parent deletes that profile, the app is uninstalled, or the operating system deletes the app's storage, whichever comes first.</li>
    <li>The app excludes that data from operating-system backups and from Android device-to-device transfer. It is not retained by the app in iCloud or in Google backup, and it is not copied onto a new device.</li>
    <li>Microphone audio is not retained. It exists in memory during the attempt and is then discarded. It is not written to disk.</li>
    <li>Recognition text is not retained. It exists in memory only for the match and is then discarded. It is not written to disk.</li>
    <li>The subscription-status note stays in private device storage until the app is removed or the store updates it. It is not a payment card. Apple or Google retain the purchase under their own rules.</li>
  </ul>
  <h3>Support messages</h3>
  <p>No support address is published yet. If <code>{CONTACT_EMAIL}</code> is later approved, parents should not send a child's personal information. The publisher must not copy any such message into an app database. There is nowhere in the product to put it. How long an ordinary email may remain in a mailbox is not decided. Legal review has to set that period before the address is published. Until then, do not send children's information.</p>
  <h3>What this policy does not delete</h3>
  <p>We cannot delete a record held by Apple or Google, and we cannot reach into a device. Store account and purchase records follow the store's privacy policy. Device data is deleted by the parent, on the device, as described next.</p>
</section>

<section id="deletion">
  <h2>How to delete</h2>
  <ol>
    <li>Open the grown-ups area and complete the parental gate.</li>
    <li>Delete the child profile. The labels in the app can still change before release. The action is profile deletion in the parent area. Deleting a profile removes that profile's nickname, avatar, age band, direction, start date, and learning record from the device.</li>
    <li>Or remove the app from the device. That removes the app's local data, including every profile on that device.</li>
  </ol>
  <p>Deletion on the device does not cancel a subscription. Cancel with Apple or Google. Steps are on the <a href="support.html">support page</a>.</p>
  <p>We cannot perform this deletion for you, because we never receive the profile. That limit is a result of not collecting the data.</p>
</section>

<section id="stores">
  <h2>Apple and Google</h2>
  <p>Apple and Google process downloads, purchases, and optional diagnostics under their own policies. We do not receive the child's profile from them. We do not allow a third-party advertising or analytics SDK to receive it either. Nothing in this notice authorizes a third party to collect personal information from a child through Bridge Kids.</p>
</section>
""" + CONTACT_SECTION

SUPPORT_BODY = f"""
<nav class="on-page" aria-label="On this page">
  <ol>
    <li><a href="#no-account">No account</a></li>
    <li><a href="#gate">The parental gate</a></li>
    <li><a href="#delete">Delete a profile</a></li>
    <li><a href="#microphone">Microphone</a></li>
    <li><a href="#speech">Speech</a></li>
    <li><a href="#offline">Offline use</a></li>
    <li><a href="#new-device">A new device</a></li>
    <li><a href="#subscription">Subscriptions</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#what-to-write">If you write to us later</a></li>
  </ol>
</nav>

<section id="no-account">
  <h2>No account</h2>
  <p>Bridge Kids has no sign-up, no password, and no login. This page has no form and no chat. Nothing you type in the browser is sent, because the page does not run code and has nowhere to type. We cannot look up a child, a receipt, or a progress record. We do not have them.</p>
  <p>The privacy policy and the children's notice explain what stays on the device: <a href="privacy.html">Privacy policy</a>, <a href="children.html">Children's privacy and COPPA notice</a>.</p>
</section>

<section id="gate">
  <h2>The parental gate</h2>
  <p>Purchases, restoring a purchase, managing a subscription, settings, deleting a profile, and links out to these pages are behind a gate meant for a grown-up. The gate does not ask for a birth year. It is a barrier, not a guarantee that nobody can pass it. The child area does not show prices.</p>
</section>

<section id="delete">
  <h2>Delete a profile</h2>
  <ol>
    <li>Open the grown-ups control from the child home or the progress map, and complete the gate.</li>
    <li>In the parent area, delete the profile you want to remove.</li>
  </ol>
  <p>The exact button labels can still change before release. Deletion removes that profile's nickname, avatar, age band, learning direction, optional start date, and learning record from the device. It does not cancel a store subscription. Removing the whole app removes every profile's local data on that device.</p>
</section>

<section id="microphone">
  <h2>Microphone</h2>
  <p>The microphone is optional. You can refuse it in the system permission prompt. The child can still listen and tap. The reason for the permission is shown to the parent, behind the gate. The app does not keep asking the child.</p>
  <p>To change the choice later, use the system settings for Bridge Kids on the device and turn the microphone on or off. That switch belongs to the operating system.</p>
</section>

<section id="speech">
  <h2>Speech</h2>
  <p>Speaking is recognized on the device, in Japanese or in American English, matching the learning direction. Audio is not saved. If the device cannot run on-device recognition, the app still accepts the attempt and does not send audio to a server. Younger children (about 3 to 5) are not scored. Older children (about 6 to 10) get a lenient on-device check.</p>
</section>

<section id="offline">
  <h2>Offline use</h2>
  <p>After the content packs have downloaded from Apple or Google, the child area is meant to work without a connection. The child area does not show a network error. A parent handles retries from the parent area. The first setup tells the parent the download size before the packs are fetched.</p>
</section>

<section id="new-device">
  <h2>A new device</h2>
  <p>Profiles and progress do not move to a new device, and they do not come back from a backup. The app excludes them from iOS backup, from Android backup, and from Android device transfer. This is deliberate.</p>
  <p>A subscription can be restored on a new device that uses the same store account. Restoring the subscription does not restore progress. You would set up profiles again.</p>
</section>

<section id="subscription">
  <h2>Subscriptions</h2>
  <p>Payment is only through the App Store or Google Play. We never see your card. There is no free trial in the current design. Chapters 1, 2, and 4 in each direction are available without a subscription. A subscription unlocks the other chapters, both directions, and up to four profiles on that device.</p>
  <p>Apple Family Sharing for this subscription is off. The plan does not extend to other Apple IDs through Family Sharing, and it does not transfer between iPhone and Android.</p>
  <p>The store shows the price and the renewal terms before you pay. A subscription renews until you cancel it with the store. Deleting the app, deleting a profile, or reinstalling does not cancel it.</p>
  <h3>Manage or cancel on Apple devices</h3>
  <p><a href="https://apps.apple.com/account/subscriptions">Apple subscription settings</a>. You can also open Settings, then your Apple ID, then Subscriptions. Choose Bridge Kids, then cancel. Apple's screen shows whether access continues through the end of the period you already paid.</p>
  <h3>Manage or cancel on Google Play</h3>
  <p><a href="https://play.google.com/store/account/subscriptions">Google Play subscriptions</a>. You can also open the Play Store app, then Payments and subscriptions, then Subscriptions. Cancel there.</p>
  <p>Inside Bridge Kids, behind the gate, restore and manage are designed to hand off to the same store. If a purchase is waiting for family approval in the store, it stays pending until the store account holder accepts or declines it.</p>
  <p>On Android, if the device is offline, the current design keeps paid chapters available for seven days after the last successful check with the store, then shows them as sleeping. Nothing already downloaded is deleted. When the store is reachable again, the app checks the purchase on the device.</p>
  <p>Refunds are requested from the store that charged you. We do not hold the payment and we cannot see the store's payment record.</p>
</section>
""" + CONTACT_SECTION + f"""
<section id="what-to-write">
  <h2>If you write to us later</h2>
  <p>Once <code>{CONTACT_EMAIL}</code> is a real address, include the store you used (Apple or Google), the device type (iPhone, iPad, or Android), and what you expected to happen. Leave out the child's real name, a voice recording, and screenshots that show a nickname. We do not need them, and email is a poor place for them.</p>
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
    <li><a href="#subscriptions">Subscriptions and billing</a></li>
    <li><a href="#apple">Apple App Store</a></li>
    <li><a href="#google">Google Play</a></li>
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
  <p>These are draft terms for the Bridge Kids apps. They are not in force, they have not had legal review, and they are not legal advice. The English text is the source. A browser translation is not a set of terms.</p>
  <p>Do not treat a missing clause as a promise. Several decisions are still open, including governing law, the public contact details, and the final subscription price. They are marked where they come up.</p>
</section>

<section id="who">
  <h2>Who offers the app</h2>
  <p>Bridge Kids is offered by Gabriel John Fordan, an individual developer. If you accept the published terms, the agreement is between you and that publisher. It is not an agreement with Apple, and it is not an agreement with Google, except for the store terms you already have with them.</p>
</section>

<section id="agreement">
  <h2>Agreeing</h2>
  <p>A parent or legal guardian agrees to these terms for a child and for the store account that pays. The child is not asked to accept a contract. If you are a child reading this, please hand the device to a grown-up before using anything behind the parental gate.</p>
  <p>Once these terms are published and in force, do not download or use the app if you do not agree to them. Store rules may also require you to accept the store's own terms before you can install the app.</p>
</section>

<section id="the-app">
  <h2>The app</h2>
  <p>Bridge Kids is an English-learning app for young children on iPhone, iPad, and Android. It is a learning aid. It is not a school, not a medical device, and not a childcare service. We do not promise a learning result, a reading level, or a test score.</p>
  <p>The child area is separate from the parent area. Up to four child profiles can exist on one device. Two learning directions exist: one with Japanese speech on the device, and one with American English speech on the device. Chapters 1, 2, and 4 in each direction are the free chapters in the current design.</p>
</section>

<section id="license">
  <h2>License</h2>
  <p>The publisher grants you a personal, non-exclusive, non-transferable, revocable license to use the app on devices you own or control, as the store's usage rules allow. We reserve every right that this license does not grant.</p>
  <p>The app, its artwork, audio, animation, and text are owned by the publisher or used with permission. You may not copy the content packs, resell access, or present the app as your own product. You may not reverse engineer the app except where a statute forbids that limit.</p>
  <p>Apple, App Store, iOS, iPadOS, and iPhone are marks of Apple. Google, Android, and Google Play are marks of Google. They are named here to identify the stores. The publisher is not affiliated with Apple or Google.</p>
</section>

<section id="parents">
  <h2>Parents and children</h2>
  <p>You are responsible for the device, the store account, the subscription, and for deciding whether a child may use the app. The parental gate stands in front of purchases, subscription management, settings, profile deletion, and links to these pages. The gate does not ask for a birth year. It reduces the chance that a child acts alone. It is not a promise that a determined person cannot get past it.</p>
  <p>The child area does not show prices. Do not use the parent area to show a child a checkout.</p>
</section>

<section id="accounts">
  <h2>No accounts</h2>
  <p>Bridge Kids does not have user accounts. There is nothing to register. The Apple ID or Google account that pays is the store's account, under the store's terms. A subscription does not create a Bridge Kids profile in the cloud.</p>
</section>

<section id="subscriptions">
  <h2>Subscriptions and billing</h2>
  <p>Optional paid access is an auto-renewable subscription billed only by Apple or Google. We do not take payment-card data, and we do not run a receipt server.</p>
  <ul>
    <li>The store displays the price, the currency, tax, the billing period, and the renewal terms before you confirm. Those store terms control the charge. This draft does not state a price, because the price is not final.</li>
    <li>There is no free trial and no introductory price in the current design.</li>
    <li>Chapters 1, 2, and 4 in each direction do not need a subscription. A subscription unlocks the other chapters, both directions, and up to four profiles on that device.</li>
    <li>"Family plan" means those profiles on the device tied to the store account that paid. It does not mean Apple Family Sharing. Family Sharing for this subscription is off. The subscription does not move to another Apple ID through Family Sharing, and it does not move between iOS and Android.</li>
    <li>The subscription renews until you cancel it in the store account. Deleting the app or a profile does not cancel it. How to cancel is on the <a href="support.html">support page</a>.</li>
    <li>On Android, the current design allows about seven days of offline use of paid chapters after the last on-device check, and then shows those chapters as sleeping. Downloaded material is not deleted.</li>
    <li>Refunds follow the store's rules. Ask the store that charged you. We cannot see the payment record.</li>
    <li>Who the merchant of record is can differ by store and by country. This draft does not decide that question. The store's checkout is the authority for the charge you see.</li>
  </ul>
</section>

<section id="apple">
  <h2>Apple App Store</h2>
  <p>If you downloaded Bridge Kids from the Apple App Store, Apple requires the following points in a custom license. They are included here as a draft, and counsel must confirm they still match Apple's current schedule before submission.</p>
  <ol>
    <li>This agreement is between you and Gabriel John Fordan only, and not with Apple. The publisher, not Apple, is solely responsible for the app and its content.</li>
    <li>The license is limited and non-transferable. You may use the app on Apple-branded products that you own or control, as permitted by the Usage Rules in Apple's Media Services terms.</li>
    <li>The publisher is solely responsible for maintenance and support. Apple has no obligation to provide maintenance or support for the app.</li>
    <li>If the app fails to conform to any applicable warranty, you may notify Apple, and Apple may refund the purchase price. To the maximum extent permitted by law, Apple has no other warranty obligation for the app. Any other claim, loss, liability, damage, cost, or expense attributable to a failure to conform to a warranty is the publisher's responsibility.</li>
    <li>The publisher, not Apple, is responsible for addressing claims relating to the app or to possession or use of the app, including product-liability claims, claims that the app fails to meet a legal or regulatory requirement, and claims under consumer protection or similar legislation.</li>
    <li>The publisher, not Apple, is responsible for the investigation, defense, settlement, and discharge of any claim that the app, or your possession and use of it, infringes a third party's intellectual-property right.</li>
    <li>You represent that you are not located in a country subject to a United States government embargo, and that you are not listed on any United States government list of prohibited or restricted parties.</li>
    <li>Questions, complaints, and claims go to the publisher, at the contact details in the contact section. Those details are placeholders until legal review finishes.</li>
    <li>You must also comply with third-party terms that apply while you use the app, including your wireless-carrier terms where a network is used.</li>
    <li>Apple and Apple's subsidiaries are third-party beneficiaries of these terms. Once you accept them, Apple has the right to enforce them against you.</li>
  </ol>
</section>

<section id="google">
  <h2>Google Play</h2>
  <p>If you downloaded Bridge Kids from Google Play, you also use Google's store terms and billing. Google handles the charge, the store account, and store refunds. The publisher is responsible for the app. Google does not, by these terms, endorse Bridge Kids. Counsel must confirm whether Google's current developer terms require any extra clause before submission.</p>
</section>

<section id="privacy">
  <h2>Privacy</h2>
  <p>The <a href="privacy.html">privacy policy</a> and the <a href="children.html">children's privacy and COPPA notice</a> describe how little information leaves the device. They include the data retention policy. Using the app after those documents are in force means the parent has had a chance to read them. The child's information is not the price of a subscription: the app is designed not to send it to us.</p>
</section>

<section id="use">
  <h2>Acceptable use</h2>
  <p>Use the app for the child's learning, under a parent's supervision. Do not use it to advertise to children, to collect information from children, or to bypass the parental gate in order to put a checkout in front of a child. Do not interfere with the content-pack checks that confirm a pack came from the publisher's release process. Do not send us a child's personal information.</p>
</section>

<section id="availability">
  <h2>Availability</h2>
  <p>We may change, pause, or withdraw the app or a chapter. Content packs depend on Apple and Google hosting them. Offline use depends on a download that already finished. We do not promise that a store, a network, or an on-device speech model will be available. Progress stored only on the device can be lost if the device is lost, replaced, or restored from a backup. That loss is a consequence of excluding the data from backups. The <a href="privacy.html#backups">privacy policy</a> states it in plain language.</p>
</section>

<section id="liability">
  <h2>Warranties and liability</h2>
  <p>This section is a draft and needs legal review more than any other. Mandatory consumer rights stay in force. In many places, including Japan, the European Union, the United Kingdom, Brazil, Vietnam, and parts of the United States, a private term cannot remove a right that a statute gives a consumer. Those rights remain. This draft does not choose the country whose law applies. See the next section.</p>
  <p>To the extent a mandatory rule does not say otherwise, the app is provided as available, without a warranty of uninterrupted service or of a particular learning outcome, and the publisher is not liable for progress that existed only on the device, for a store outage, or for a subscription a parent did not cancel. Nothing in this paragraph limits liability that the law says cannot be limited, including liability for fraud or for death or personal injury caused by negligence where that limit is forbidden.</p>
  <p>If a term in this draft is unenforceable, the rest of the draft remains for review. That sentence does not make the draft binding.</p>
</section>

<section id="law">
  <h2>Governing law</h2>
  <p>Governing law and venue are not chosen. This draft does not name a country, a court, or an arbitration program. <strong>TODO:</strong> Gabriel John Fordan and counsel must choose the governing law, and must say whether any consumer-protection forum has to be named, before these terms are published. Do not infer a jurisdiction from the language of this draft or from where the website is hosted.</p>
</section>

<section id="changes">
  <h2>Changes</h2>
  <p>If the terms change after publication, the date on the page will change. We cannot email a change notice, because there are no accounts. The new page is the notice. Continued use after the new terms are in force is the parent's decision. A subscription already bought remains subject to the store's renewal rules as well.</p>
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
    "support": "Draft support for Bridge Kids: delete a profile, manage a subscription, and contact the publisher.",
    "terms": "Draft terms of use for the Bridge Kids apps on iOS and Android.",
    "404": "That page is not on the Bridge Kids site.",
}
