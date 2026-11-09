# Design and copy rules

## Design direction

1. Get the palette from the logo. Sample the logo colors if there is no brand guide.
2. Put all colors and fonts in `@theme` in `globals.css`. Do not use a color that is not a token.
3. Use one component system for all pages. Mixed systems cause rework.
4. Make the design specific to the business. Use real photos of the sites, the team and the work of the client.
5. Ask the user for a reference site if the brief names no direction.

## Default rules

| Item | Rule |
|---|---|
| Animated number counters | Not permitted |
| Thick card borders on content pages | Not permitted |
| Stock photos | Only if the client has no photos and the user agrees. Log the license in `CREDITS.md` |
| Button text on a brand color | Must pass contrast. Check text on each brand color |

## Assets

1. Search the client folder first.
2. Rename files to lower-case, URL-safe names.
3. Trim logo margins. Keep a transparent version and a version for dark backgrounds.
4. Check SVG exports. Exports from design tools can lose CSS classes, and the logo then renders black.
5. Keep large source files out of `public/`.
6. Get images from a PDF with `pdfimages -png <file> <prefix>`, or PyMuPDF. A logo in a PDF can have a separate mask image. Join the mask to the image to get transparency.
7. Do not use an image that is less than the display width. An image under 800 pixels wide can go only in a small card.
8. Do not use a photo unless the facts sheet shows that it is the work of this client. Photos in a company profile can be stock photos, or can show another company.

## Optional house rules

Set these fields in `house_rules` in the plan. The gate then enforces them. Both are off by default.

| Field | Effect |
|---|---|
| `no_dashes` | Fails on em-dashes and en-dashes in copy and in `src/` |
| `no_eyebrows` | Fails on `eyebrow` or `kicker` in `src/` |

## CTA

Every page has a CTA that suits the buyer.

| Market | Main CTA |
|---|---|
| Qatar, UAE, India, B2B and local | WhatsApp with a prefilled message, and phone |
| SaaS, app | Sign up, or start a free trial |
| High-value consulting | Book a call, and a form |

Use `waLink()` from `site.ts` for each WhatsApp link.

## Copy

Website copy is client-facing. Write it in natural language for the buyer. Follow the style rules of the user, if they exist.

1. Write in the voice of the client. Use the words of the buyer.
2. Use full second-person sentences.
3. Do not use "No X, no Y", "Not X. Just Y." or three-word staccato lines.
4. Do not use "X, not Y" to answer an objection that nobody raised.
5. Do not use triplets, slogans in table cells or a dramatic closing line.
6. Do not use: "unlock", "elevate", "seamless", "world-class", "cutting-edge", "one-stop", "in today's fast-paced".
7. Do not recite the history of the client as a benefit. Give the consequence for the buyer.
8. Use a figure only with a source in `facts.md`.
9. A service page answers these questions: what is it, who is it for, what is included, why this company, what happens next.

## Page copy document for the client

Use this document if the client must approve the copy.

1. Address the client as "you" in all of the document.
2. Put all open questions in one "Questions for you" section near the top.
3. Label the HTML tag on every element, such as H1, H2, Body, Button. Do not state a level once and assume that it carries.
4. Do not include internal notes, sources or the history of the drafts.
5. Use the document format that the user prefers.
