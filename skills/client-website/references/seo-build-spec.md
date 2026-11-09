# SEO build specification

## Code structure

| Item | Location | Rule |
|---|---|---|
| Plan | `src/lib/site-plan.json` | Change it only with approval from the user |
| Business data | `src/lib/site.ts` | The only place for contact data |
| Content | `src/lib/<collection>.ts` | Typed arrays. Add an item and the page exists |
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

Use the builders in `seo.ts`. `organizationLd()` is in the layout.

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
| Analytics | `Analytics.tsx`. It adds a script only if the ID exists |
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

## Languages

Use route groups: `app/(en)/...` and `app/(ar)/ar/...`, each group with its own root layout and `lang` and `dir` values.

1. Add the locale to `locales` in the plan, with `prefix` set to `/ar`.
2. Add `translations.ar` to each page.
3. Call `pageMetadata(route, { locale: "ar" })` in Arabic pages.
4. Keep 1 sitemap row for each page. `sitemap.ts` adds the alternates.
5. Use CSS logical properties (`ms-`, `me-`, `ps-`, `pe-`), so that RTL layout needs no copy of the styles.

CAUTION: DO NOT LIST `/ar/...` AS SEPARATE SITEMAP ROWS. SEARCH ENGINES THEN TREAT THE 2 VERSIONS AS UNRELATED PAGES.

A dictionary object cannot pass from a Server Component to a Client Component if it contains functions. Pass plain strings.

## Contact form

| Deploy | Form |
|---|---|
| `static` | WhatsApp, phone and email links. No API route is possible |
| `server` | `/api/contact` route with validation, a honeypot field and Resend. Without `RESEND_API_KEY`, the route must return an error. It must not report success |

## Build gate results

| Result | Action |
|---|---|
| FAIL | Correct the cause and run the gate again |
| WARN | Correct it, or tell the user why it stays |
| `pages checked: 0` | The gate found no HTML. Run the build first |
