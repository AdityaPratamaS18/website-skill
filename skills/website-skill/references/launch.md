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
5. On Cloudflare, do the AI crawler step (see "Cloudflare Pages" below).
6. Run the live gate on the final host. Correct each FAIL at the host or in the code.

```bash
python3 <skill-dir>/scripts/site_gate.py live <domain>
```

7. Do the tracker check (see "Tracker check" below).
8. Give the user the Search Console steps: verify the domain and submit the sitemap.
9. Add the Google Business Profile URL to `site.ts` if the client has one.

The live gate reads the site over the network. It checks these items:

| Item | FAIL | WARN |
|---|---|---|
| `robots.txt` | `Disallow: /` for all, more than 1 `User-agent: *` group, a block on Googlebot, Bingbot or an AI search crawler, no `Sitemap` line | A block on an AI training crawler, Cloudflare `Content-Signal` lines |
| Hosts | `http` not 301 to `https`, the other host (`www` or apex) not a 301 to the final host, a redirect that drops the path | A redirect that drops the query string, more than 2 hops |
| Headers | No `nosniff`, no `Referrer-Policy`, no `frame-ancestors`, `X-Robots-Tag: noindex` | No `Permissions-Policy`, no HSTS |
| Pages in the sitemap | Not HTTP 200, a noindex, a canonical that is not the URL, no og:image, an og:image that does not load | |
| Assets on the home page | Not HTTP 200 | `Cache-Control` below 1 day |

NOTE: The gate reads the home page and 9 pages from the sitemap. Use `--pages 50` to read more.

## Tracker check

The build gate cannot see a tracker that fails in the browser. Do this check on the live site, in the browser pane.

1. Open the home page.
2. Run `typeof window.clarity` in the console if the site has Clarity. The result must be `"function"`.
3. Run `typeof window.gtag` if the site has GA4. The result must be `"function"`.
4. Look in the network list for `clarity.js` and for a `collect` request to Google Analytics.
5. Click the phone link, then look for `click_call` in GA4 DebugView or in `window.dataLayer`.

On one past site, Clarity loaded nothing for months. The cause was `<Script id="clarity">`: the browser makes each element id a global, so `window.clarity` was the script element. The build gate now fails an element id that is the same as a tracker global.

| GA4 event | Fires on |
|---|---|
| `click_call` | A click on a `tel:` link |
| `click_whatsapp` | A click on a `wa.me`, `api.whatsapp.com` or `wa.link` link |
| `click_email` | A click on a `mailto:` link |
| `generate_lead` | A form submit that passes the browser validation |

Mark `click_call`, `click_whatsapp` and `generate_lead` as key events in GA4.

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
4. Turn on "Always Use HTTPS" and HSTS in SSL/TLS, Edge Certificates.

A canonical tag is only a hint. The 301 is the instruction. Pages answer on both hosts until the 301 exists.

### AI crawlers and the managed robots.txt

Cloudflare can put its own block in front of the `robots.txt` of the site. On one past site, this block disallowed 8 AI training crawlers, added `Content-Signal` lines and made a second `User-agent: *` group. The live file was not the file in the code.

1. Ask the client for a decision: allow AI crawlers, or block AI training only. Record it in `facts.md`.
2. Open the zone, then AI Crawl Control (older dashboards: Security, Bots).
3. Set "Manage your robots.txt" (managed robots.txt) to off, unless the client decided to block AI training.
4. Set "Block AI bots" to off, unless the client decided to block them.
5. Fetch `https://<domain>/robots.txt` and compare it with `out/robots.txt`.

NOTE: A block on an AI search crawler (OAI-SearchBot, PerplexityBot, Claude-SearchBot) is a FAIL in the live gate. A block on a training crawler (GPTBot, CCBot, Google-Extended) is a WARN.

### Headers file

The scaffold copies `assets/_headers` to `public/_headers` for a static site. It sets the security headers on each path and the cache time on each asset folder.

```
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: frame-ancestors 'self'
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable
/images/*
  Cache-Control: public, max-age=2592000
/logo.webp
  Cache-Control: public, max-age=2592000
/og.webp
  Cache-Control: public, max-age=2592000
```

CAUTION: DO NOT PUT `Cache-Control` IN THE `/*` BLOCK. CLOUDFLARE JOINS ALL MATCHED RULES, SO A `max-age=0` IN `/*` CANCELS THE CACHE OF EACH ASSET.

1. Add a line for each new folder in `public/`. On one past site, the new folder `/figures/` matched no rule and served `max-age=0, must-revalidate`.
2. Add a line for each file at the root of `public/`.
3. Set Browser Cache TTL to "Respect Existing Headers" on the zone.
4. After the deploy, fetch an image 2 times. The second response must show `cf-cache-status: HIT`.

NOTE: If the client site needs a frame on another site (a booking widget, for example), change `frame-ancestors` to list that host.

## Vercel

1. Set `SITE_INDEXABLE=1` in the Production environment only. Preview builds then stay out of search.
2. Set `RESEND_API_KEY` in the Production environment.
3. Do not use `VERCEL_URL` as the canonical host. On production it is a deployment address behind a login.

The scaffold adds `headers()` with the security headers to `next.config.ts` in `server` mode. Vercel does not read `public/_headers`.

### Apex and www on Vercel

1. Open the project, then Settings, Domains.
2. Add the final host (the host in `site-plan.json`).
3. Add the other host (`www` or apex).
4. Edit the other host. Set "Redirect to" the final host, with the code 301 (Vercel gives 308 by default; both are permanent).
5. At the DNS provider, add the records that Vercel shows. Usually: `A` for the apex to `76.76.21.21`, and `CNAME` for `www` to `cname.vercel-dns.com`.
6. Wait until both hosts show "Valid Configuration".
7. Run the live gate.

CAUTION: IF THE DNS IS ON CLOUDFLARE, SET THE RECORDS TO "DNS ONLY" (GREY CLOUD). A PROXIED RECORD STOPS THE VERCEL CERTIFICATE AND CAN MAKE A REDIRECT LOOP.

## After launch

| Time | Action | System |
|---|---|---|
| Day 1 | Run the live gate and the tracker check | `site_gate.py live`, browser pane |
| Day 1 | Submit the sitemap | Search Console (the user) |
| Week 1 | Check that the pages are in the index | Search Console |
| Week 1 | Start the SEO content work, if the user wants it | The SEO system of the user |
| Month 1 | Full audit | An SEO audit tool |
