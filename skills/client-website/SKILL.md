---
name: client-website
description: >
  Build a complete SEO-optimised Next.js website for a client or a business, from a brief to a
  launch-ready build. Use whenever the user wants a new site or a full rebuild from source
  material: "make a website for <client>", "build the site from this brief", "new client site",
  "turn this company profile into a website", "rebuild their WordPress site in Next.js", or when
  the user hands over a filled discovery brief, a company profile PDF or a proposal and wants the
  site made. Covers brief reading, the facts sheet, questions for the client, keyword research,
  the site plan, the design direction, the page build, blocking SEO checks, the preview and the
  launch. Works for any business type. Do NOT use to audit a live site, to fix SEO on one existing
  site, to write SEO articles for a site that is already live, or for WordPress work.
---

# Client website: procedure

This skill makes one client website from one brief. Each client gets one approved plan, one code base and one check script. The approved plan controls the routes, the titles, the descriptions, the headings and the sitemap.

In this document, `<skill-dir>` is the folder that contains this file, and `<client-folder>` is the folder for this client. If the user has no folder convention, use `clients/<client>/`.

## Preliminary requirements

1. Read the notes for this client, if they exist. Give the user the rules that apply, in 2 or 3 lines.
2. Find the brief, the company profile, the logo and the photos.
3. Make sure that Node.js, Python 3 and `rsync` are available.

WARNING: DO NOT PUT A FACT ON THE SITE IF THE BRIEF DOES NOT GIVE IT. AN INVENTED CERTIFICATE, CLIENT NAME, FIGURE OR TESTIMONIAL IS A LEGAL AND TRUST RISK FOR THE CLIENT.

## Phase 1: Facts

1. Read `references/brief-intake.md`.
2. Read each source file in full.
3. Write `<client-folder>/site-brief/facts.md`.
4. Crawl the current site if the client has one. Record each URL for the redirect map.
5. Write `<client-folder>/site-brief/questions-for-client.md` if facts are missing.

**GATE 1.** Show the user the facts sheet summary and the list of gaps. Stop until the user replies. Continue with gaps only if the user agrees. A page that needs a missing fact stays out of the plan, or it stays without that fact.

## Phase 2: Site plan

1. Read `references/site-plan.md`.
2. Do the keyword research for the market of the client.
3. Copy `<skill-dir>/assets/site-plan.template.json` to `<client-folder>/site-brief/site-plan.json`.
4. Fill in one entry for each page.
5. Compare the plan with the proposal, if one exists. Each item in the scope must have a page or a feature. A form in the scope needs `server` hosting, or an agreed replacement.
6. Run the plan gate. Correct each FAIL.

```bash
python3 <skill-dir>/scripts/site_gate.py plan <client-folder>/site-brief/site-plan.json
```

**GATE 2.** Show the user a table with these columns: URL, primary keyword, monthly volume, title. Also state the hosting choice. Stop until the user approves. Then write the approval in the plan as `"approved_by"` and `"approved_on"`. The build gate fails without these fields.

## Phase 3: Scaffold

1. Select the folder `<client-folder>/website/`.
2. Run the scaffold script. The script works with spaces and capital letters in the path.

```bash
bash <skill-dir>/scripts/scaffold.sh "<client-folder>/website" static
```

3. Use `server` in place of `static` only if the plan needs a server feature (see `references/launch.md`).
4. Copy the approved `site-plan.json` to `src/lib/site-plan.json`.
5. Replace each `__FILL` value in `src/lib/site.ts` with a value from the facts sheet.
6. Read the guides for metadata, images, fonts and static exports in `node_modules/next/dist/docs/01-app/`.

NOTE: Next.js changes between major versions. The guides in `node_modules` match the installed version. Your training data does not.

## Phase 4: Design direction

1. Read `references/design-and-copy.md`.
2. Make the color and type tokens from the logo. Put them in `globals.css`.
3. Make `public/logo.webp`, `public/og.webp` (1200 by 630 pixels) and `src/app/icon.png` from the logo.
4. Build the header, the footer and the home page only.
5. Start the preview. Use `npx serve out -l 3210` for a static site, after a build. Use `npm run dev` for a server site.
6. Open `http://127.0.0.1:3210` in a browser. Check the page at 375, 768 and 1280 pixels.

NOTE: An embedded browser can return HTTP 431 for `localhost`. The address `127.0.0.1` does not have this fault.

**GATE 3.** Show the user the home page. Stop until the user approves the design. All other pages use this design.

CAUTION: DO NOT BUILD THE OTHER PAGES BEFORE GATE 3. A LATE DESIGN CHANGE CAUSES A MIGRATION OF ALL PAGES.

## Phase 5: Pages

1. Read `references/seo-build-spec.md`.
2. Put content in typed data files in `src/lib/` (for example `services.ts`). Keep the page files thin.
3. Use one dynamic route with `generateStaticParams` for each repeated page type.
4. Get each title, description and H1 from the plan with `pageMetadata()` and `getPage()`.
5. Write the copy for the buyer, in the voice of the client. Use only facts from `facts.md`.
6. Add internal links as the spec gives.
7. Build the site.

```bash
npm run build
```

8. Run the build gate. Correct each FAIL at its cause. Do not change the gate to get a pass.

```bash
python3 <skill-dir>/scripts/site_gate.py build <client-folder>/website
```

9. Run `npx tsc --noEmit` and `npm run lint`.

## Phase 6: Review

1. Check each page type in the browser at 375, 768 and 1280 pixels.
2. Check each CTA: phone, WhatsApp, email and form.
3. If the user requires it, prepare the page copy for the client in one document. Follow `references/design-and-copy.md`.
4. Deploy a preview only when the user tells you to. A preview build is not indexable.

**GATE 4.** Give the user the preview URL and the gate result. Stop until the user approves the launch.

## Phase 7: Launch

1. Read `references/launch.md`.
2. Build with `SITE_INDEXABLE=1`.
3. Run the build gate with `--release`. The gate must pass.
4. Do the launch steps in `references/launch.md`.

WARNING: DO NOT CONNECT THE DOMAIN OR PUSH TO PRODUCTION WITHOUT AN APPROVAL IN THE CURRENT SESSION. THE LIVE DOMAIN AFFECTS THE BUSINESS OF THE CLIENT.

## Closeout

1. Give the user a list of the client actions that remain.
2. Record paths, decisions and lessons in the notes for this client.
3. Tell the user that the site is ready for SEO content work.

## Fixed rules

| Rule | Reason |
|---|---|
| One URL for each service | A one-page site gives a service no URL that can rank |
| One primary keyword for each URL | Two pages on one keyword compete with each other |
| The plan is the only source for titles and routes | The gate compares the built HTML with the plan |
| No animated stat counters | The HTML shows 0 before the script runs |
| Gates are scripts | Each fault that the scripts catch got past a person first |

## References

| File | Read it in |
|---|---|
| `references/brief-intake.md` | Phase 1 |
| `references/site-plan.md` | Phase 2 |
| `references/design-and-copy.md` | Phase 4 and Phase 6 |
| `references/seo-build-spec.md` | Phase 5 |
| `references/launch.md` | Phase 2 (hosting) and Phase 7 |
