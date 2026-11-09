# Client Website

A Claude Code skill that turns a client brief into an SEO-optimised Next.js website.

Give it a filled brief, a company profile or a proposal. Claude reads the sources, writes down the facts it can use, researches keywords, proposes a site plan and builds the pages. You approve the work at four points, and a script checks the finished HTML before anything goes live.

## Install

As a plugin, in Claude Code:

```text
/plugin marketplace add AdityaPratamaS18/client-website-skill
/plugin install client-website@client-website-skill
```

Or copy the skill folder by hand:

```bash
git clone https://github.com/AdityaPratamaS18/client-website-skill
cp -R client-website-skill/skills/client-website ~/.claude/skills/
```

You need Node.js 20 or later, Python 3 and `rsync`. A keyword tool connected to Claude Code improves the plan. Without one, the skill continues and tells you that volumes are missing.

## Use

```text
Build a website for Acme Plumbing from briefs/acme.docx
```

| Phase | What you get | Your approval |
|---|---|---|
| 1. Facts | A facts sheet with sources, and questions for the client | Gate 1 |
| 2. Site plan | URLs, keywords, titles and hosting | Gate 2 |
| 3. Scaffold | A Next.js project with the SEO code in place | |
| 4. Design | Header, footer and home page | Gate 3 |
| 5. Pages | Every page, checked by the script | |
| 6. Review | A preview at three screen widths | Gate 4 |
| 7. Launch | Release build, domain, redirects and sitemap | |

## How it works

`site-plan.json` holds every route, title, description and H1. The site reads its metadata and sitemap from that file, so the approved plan and the built site cannot drift apart without the check failing.

The skill only puts facts on the site that appear in your sources. Anything missing goes into a list of questions for the client.

Preview builds are blocked from search engines. Only a build with `SITE_INDEXABLE=1` can be indexed.

## What the gate checks

Run it yourself at any time:

```bash
python3 skills/client-website/scripts/site_gate.py plan path/to/site-plan.json
python3 skills/client-website/scripts/site_gate.py build path/to/project --release
```

It reads the built HTML and exits with an error if it finds any of these:

- A title, description or H1 that differs from the plan, or a length outside the limits
- A duplicate primary keyword, or a keyword missing from the title
- A planned page that was not built, or a built page that was not planned
- More or fewer than one H1, or no `<main>` element
- A wrong canonical or hreflang tag, or missing Open Graph tags
- Invalid or missing JSON-LD, or FAQ schema for questions that are not on the page
- A broken internal link, or a page that nothing links to
- A missing image, missing alt attribute or oversized image
- Thin service pages (under 250 words)
- Placeholder text such as lorem ipsum
- A sitemap that does not match the plan
- `noindex` or a blocked `robots.txt` on a release build
- CSS that did not compile, or a missing favicon

Two extra rules are off by default. Set `house_rules` in the plan to ban em-dashes and en-dashes, or to ban eyebrow labels above headings.

## Hosting

Static export on Cloudflare Pages is the default. Choose `server` hosting on Vercel if the site needs an API route, such as a contact form that sends email.

## Status

Version 0.1.0. Tested on Next.js 16.4.5 on macOS, with static and server builds and with English and Arabic routes. It has not been tested on Windows. How reliably Claude starts the skill from different wordings has not been measured.

## License

MIT
