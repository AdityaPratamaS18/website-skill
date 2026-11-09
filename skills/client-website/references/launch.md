# Hosting and launch: procedure

## Hosting decision

| Site needs | `deploy` | Host |
|---|---|---|
| Content pages, WhatsApp and phone CTA | `static` | Cloudflare Pages (no cost at normal traffic) |
| Form with an API route, login, payment, database | `server` | Vercel |

Use `static` by default. It has no server to fail and it works on any host.

## Preliminary requirements

1. GATE 4 approval from the user in the current session.
2. A pass from the build gate with `--release`.
3. The final domain, and access to its DNS.

## Procedure

```bash
SITE_INDEXABLE=1 npm run build
```

```bash
python3 <skill-dir>/scripts/site_gate.py build . --release
```

1. Deploy to the host.
2. Attach the apex domain and the `www` domain.
3. Make one host canonical, with a 301 redirect from the other host.
4. Add the old URLs from `redirects`.
5. Fetch 5 pages from the live domain. Check the status, the title, the canonical and the JSON-LD.
6. Check that `robots.txt` does not contain `Disallow: /`.
7. Fetch `sitemap.xml` from the live domain.
8. Give the user the Search Console steps: verify the domain and submit the sitemap.
9. Add the Google Business Profile URL to `site.ts` if the client has one.

## Redirect files

| Deploy | File |
|---|---|
| `static` on Cloudflare Pages | `public/_redirects`, one rule on each line: `/old /new 301` |
| `server` | `redirects()` in `next.config.ts` |

## Cloudflare Pages

WARNING: DO NOT REMOVE THE WWW CUSTOM DOMAIN TO "TIDY UP". THE REMOVAL DELETES THE DNS RECORD AND THE SSL CERTIFICATE, AND OLD WWW LINKS THEN SHOW A SECURITY WARNING.

1. Make the `www` to apex redirect with a Redirect Rule on the zone: `https://www.*` to `https://${1}`, code 301.
2. Set "Preserve query string" to on.
3. If Cloudflare says "This rule may not apply to your traffic", check that `www` returns `server: cloudflare`. The warning is false in this situation. Do not add a new proxied record.

A canonical tag is only a hint. The 301 is the instruction. Pages answer on both hosts until the 301 exists.

CAUTION: DO NOT PUT A `/*` BLOCK IN `public/_headers` WITH PATH RULES. CLOUDFLARE JOINS ALL MATCHED RULES, SO A TRAILING `max-age=0` CANCELS THE CACHE.

Use this `public/_headers` file. Add a line for each file at the root of `public/`.

```
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable
/images/*
  Cache-Control: public, max-age=2592000
/logo.webp
  Cache-Control: public, max-age=2592000
```

Set Browser Cache TTL to "Respect Existing Headers" on the zone.

## Vercel

1. Set `SITE_INDEXABLE=1` in the Production environment only. Preview builds then stay out of search.
2. Set `RESEND_API_KEY` in the Production environment.
3. Do not use `VERCEL_URL` as the canonical host. On production it is a deployment address behind a login.

## After launch

| Time | Action | System |
|---|---|---|
| Day 1 | Submit the sitemap | Search Console (the user) |
| Week 1 | Check that the pages are in the index | Search Console |
| Week 1 | Start the SEO content work, if the user wants it | The SEO system of the user |
| Month 1 | Full audit | An SEO audit tool |
