# SEO build specification

## Code structure

| Item | Location | Rule |
|---|---|---|
| Plan | `src/lib/site-plan.json` | Change it only with approval from the user |
| Business data | `src/lib/site.ts` | The only place for contact data |
| Content | `src/lib/<collection>.ts` | Typed arrays. Add an item and the page exists |
| Shared parts | `src/components/` | Starter: `Analytics`, `JsonLd`, `WhatsAppButton`, `MapEmbed`, `ContactForm` |
| SEO helpers | `src/lib/seo.ts` | Starter file. Do not repeat this code in a page |
| Page files | `src/app/**/page.tsx` | Thin. Server Components by default |

## Each page

```tsx
export const metadata = pageMetadata("/about");
```

A dynamic route uses this form:

```tsx
export function generateStaticParams() {
  return services.map((s) => ({ slug: s.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return pageMetadata(`/services/${slug}`);
}
```

## Page content

| Page type | Required content |
|---|---|
| Service, category, landing | H1, answer to the search in the first 100 words, what is included, who it is for, proof, process, FAQ, CTA, links to 3 related pages |
| Hub | Short intro and a link to each child page |
| Home | Offer in the H1, proof near the top, link to each main service, CTA |
| Contact | NAP (name, address, phone), hours, map link, CTA |
| Privacy | Legal name, what the site collects (form data, analytics cookies), the purpose, who receives it, how long it stays, how to ask for removal, contact email. Use only the trackers and forms that the site has. Ask the user to get the text checked for the country of the client |

1. Use 1 H1 on each page. Do not skip a heading level.
2. Write at least 300 words on service, category, location and landing pages. The gate fails a page with fewer than 250 words.
3. Include the primary keyword in the first 100 words.
4. Link from each page to at least 1 other page in the body. The gate fails a page with no inbound links.
5. Use descriptive link text. Do not use "click here" or "read more".

## Structured data

Use the builders in `seo.ts`. `organizationLd()` is in the layout. It adds `geo` from `site.geo` and `hasMap` from `site.mapUrl`. Get both from the Google Maps pin of the client (open the share link, then read the coordinates in the URL).

| Page type | Schema |
|---|---|
| All | Organization or a subtype (in the layout) |
| Service | `serviceLd`, `breadcrumbLd` |
| Category, location, landing | `breadcrumbLd` |
| Post | `articleLd`, `breadcrumbLd` |
| Any page with a visible FAQ | `faqLd` |

Select the most exact subtype in `site.schemaType`: `ProfessionalService`, `GeneralContractor`, `WholesaleStore`, `MedicalClinic`, `Bakery` and so on.

1. Add FAQ schema only if the questions show on the page.
2. Do not put Markdown in the answers. `faqLd` removes link and bold syntax.
3. Do not add `aggregateRating` unless the page shows real reviews.

## Performance

| Item | Rule |
|---|---|
| Fonts | `next/font`. A maximum of 2 families. Add the `arabic` subset for Arabic |
| Images | WebP. Width of 2 times the largest display width |
| Hero image | Maximum 1600 pixels wide. Below 250 KB if possible |
| Other images | 720 pixels wide for cards and 960 for page heroes |
| Preload | Only the image for LCP (the largest element in the first view). If the hero image is below the fold at 375 pixels, do not preload it |
| Client Components | Only for interaction. Keep them small and low in the tree |
| Analytics | `Analytics.tsx`. It adds a script only if the ID exists. It sets the Consent Mode v2 defaults and sends the lead events (see `launch.md`, "Tracker check") |
| Map | `MapEmbed.tsx`. A keyless Google Maps frame with `loading="lazy"`. Do not use a Maps API key on a static site |
| WhatsApp | `WhatsAppButton.tsx` is in the layout. It shows only if `site.whatsapp.number` is set |
| Animation | Content must show if the script does not run |

Next.js 16 replaced the `priority` prop of `next/image`. Use `preload` and `loading="eager"` on the LCP image only.

CAUTION: DO NOT PRELOAD AN IMAGE BELOW THE FOLD. ON ONE PAST SITE, A 238 KB PRELOADED IMAGE COMPETED WITH THE HERO.

With `output: "export"`, `next/image` makes a plain `<img>`, with no resize and no format change. Make each source file the correct size before you add it. Use `cwebp` or `sharp`.

### Scroll reveal

Do not set `opacity: 0` in the HTML. Add a class to `<html>` from an inline script, and hide content only under that class:

```tsx
<script dangerouslySetInnerHTML={{ __html: "document.documentElement.classList.add('reveal-ready');" }} />
```

Honor `prefers-reduced-motion`.

## Accessibility

1. Use `alt=""` on a decorative image next to text with the same words. Screen readers otherwise read the words 2 times.
2. Write a real description in `alt` on each other image. Do not fill `alt` with keywords.
3. Make text contrast meet WCAG AA. Check button text on the brand color.
4. Use a tap target of at least 44 pixels on mobile.
5. Give each form field a label.

## Data files

A data file holds content only. Do not give an export the name of a global.

CAUTION: DO NOT EXPORT A NAME SUCH AS `process`, `fetch`, `URL`, `window` OR `location` FROM A FILE IN `src/`. `export const process = [...]` IN A DATA FILE BROKE A NEXT.JS 16 BUILD, BECAUSE THE NAME HID THE NODE GLOBAL. THE BUILD GATE FAILS THIS.

Use a name that tells the content: `processSteps`, `officeLocations`.

Do not give an element an `id` that is the same as a tracker global (`clarity`, `gtag`, `dataLayer`, `fbq`). The browser makes each element id a global, and the tracker then does not load. The build gate fails this too.

## Languages

Use route groups: `app/(en)/...` and `app/(ar)/ar/...`, each group with its own root layout and `lang` and `dir` values.

Keep the English URLs at the root when a site with rankings gets a second language. Put the second language under its prefix (`/ar/...`). A move of English to `/en/` loses the rankings.

1. Add the locale to `locales` in the plan, with `prefix` set to `/ar`.
2. Add `translations.ar` to each page.
3. Call `pageMetadata(route, { locale: "ar" })` in Arabic pages.
4. Keep 1 sitemap row for each page. `sitemap.ts` adds the alternates.
5. Use CSS logical properties (`ms-`, `me-`, `ps-`, `pe-`), so that RTL layout needs no copy of the styles.

CAUTION: DO NOT LIST `/ar/...` AS SEPARATE SITEMAP ROWS. SEARCH ENGINES THEN TREAT THE 2 VERSIONS AS UNRELATED PAGES.

A dictionary object cannot pass from a Server Component to a Client Component if it contains functions. Pass plain strings.

### Arabic and RTL: lessons from past sites

| Rule | Reason |
|---|---|
| Put all copy in a typed dictionary (`i18n/en.ts`, `i18n/ar.ts` with the type `typeof en`) from the first day, even for 1 language | A missing Arabic key is then a build error. On one past site, the move of 3,800 lines of copy out of JSX was most of the work |
| Write a string with a value as a template (`"{count} products"`) and fill it with a `fill()` helper. Do not use a function | A function cannot pass to a Client Component. The first build of one past site failed on this |
| In the Arabic layout, give the Arabic fonts the same CSS variables as the Latin fonts | Each font class then works in both languages. Select an Arabic font that also has Latin letters (IBM Plex Sans Arabic, for example) |
| Set `letter-spacing: normal` on all text under `[dir="rtl"]` | Letter spacing breaks the joins of Arabic letters |
| Put a phone number, an email, a product code or a product name in an inner `<span dir="ltr">` | The bidi algorithm puts the parts of these strings in the wrong order |
| Put `dir="ltr"` on the inner span, not on a positioned element | `start` and `end` resolve against the direction of the element itself. On one past site, `dir="ltr"` on an `end-4` element pinned it to the wrong side |
| Read `Math.abs(scrollLeft)` in a carousel | `scrollLeft` is negative in RTL |
| Export a list of the slugs that have no Arabic copy, and show it at GATE 4 | A page with no Arabic copy falls back to English with no error |
| Do not translate product names that are printed on the pack | The buyer must quote the exact name back |
| Get a native speaker at the client to read the Arabic before launch. Record the name and the date in `facts.md` | On one past site, an AI wrote the Arabic and the client did not review it |

NOTE: The build gate checks Arabic titles and descriptions with the WARN limits only, because Arabic text is shorter than English text.

## Contact form

| Deploy | Form |
|---|---|
| `static` | `ContactForm.tsx` with Web3Forms, plus WhatsApp, phone and email links. The form posts from the browser to Web3Forms, so the site needs no API route |
| `server` | `/api/contact` route with validation, a honeypot field and Resend. Without `RESEND_API_KEY`, the route must return an error. It must not report success |

Web3Forms setup for a static site:

1. Make the access key at web3forms.com with the email of the client that gets the messages.
2. Put the key in `site.web3formsKey`. The key is public by design. It only sends to the email that owns it.
3. Pass the key from a Server Component: `<ContactForm accessKey={site.web3formsKey} subject="New enquiry from the website" />`. Do not import `site.ts` in the form, or the plan goes into the browser bundle.
4. Keep the hidden `botcheck` field. It is the honeypot: a person does not see it, so a value in it means a bot.
5. Send 1 test message from the live site. Make sure that the client received it.
6. Name Web3Forms and the data that the form sends in the privacy policy.

The form shows nothing if the key is empty. Without a key, the CTA is WhatsApp, phone and email only.

## Build gate results

| Result | Action |
|---|---|
| FAIL | Correct the cause and run the gate again |
| WARN | Correct it, or tell the user why it stays |
| `pages checked: 0` | The gate found no HTML. Run the build first |
