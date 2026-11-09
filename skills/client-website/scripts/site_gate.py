#!/usr/bin/env python3
"""Blocking checks for a client website.

  site_gate.py plan <site-plan.json>
  site_gate.py build <project-dir> [--release]

The exit code is 1 if a check fails. Zero pages found is also a failure,
because a check that passes on nothing is worse than no check.
"""
import argparse
import json
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

DASHES = re.compile("[\u2013\u2014]")
PLACEHOLDER = re.compile(
    r"lorem ipsum|__FILL|\bplaceholder\b|\bcoming soon\b|example\.com|123456789|localhost:\d+",
    re.I,
)
PLACEHOLDER_CASED = re.compile(r"\bTODO\b|\bTBD\b|\bXXXX\b")
STOPWORDS = {"a", "an", "and", "the", "in", "of", "for", "to", "near", "me", "at", "on", "best", "top"}
COMMERCIAL = {"home", "service", "category", "location", "landing", "post"}
THIN_TYPES = {"service", "category", "location", "landing"}
PAGE_TYPES = COMMERCIAL | {"hub", "about", "contact", "team", "projects", "legal", "utility"}
ROUTE = re.compile(r"^/([a-z0-9-]+(/[a-z0-9-]+)*)?$")
MIN_WORDS = 250
IMAGE_FAIL_KB = 500
IMAGE_WARN_KB = 250
RASTER = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif"}
HOUSE_RULES = {"no_dashes": False, "no_eyebrows": False}


class Report:
    def __init__(self):
        self.fails = []
        self.warns = []

    def fail(self, where, message):
        self.fails.append(f"FAIL  {where}: {message}")

    def warn(self, where, message):
        self.warns.append(f"WARN  {where}: {message}")

    def finish(self, summary):
        for line in self.warns + self.fails:
            print(line)
        status = "FAILED" if self.fails else "PASSED"
        print(f"\n{status}: {summary}, {len(self.fails)} failed, {len(self.warns)} warnings")
        return 1 if self.fails else 0


def tokens(text):
    words = re.findall(r"[\w؀-ۿ]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def stem(word):
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def has_keyword(keyword, text):
    have = {stem(w) for w in tokens(text)}
    return all(stem(w) in have for w in tokens(keyword))


def scan_text(report, where, label, text):
    if not text:
        return
    if HOUSE_RULES["no_dashes"] and DASHES.search(text):
        report.fail(where, f"{label} contains an em-dash or en-dash")
    found = PLACEHOLDER.search(text) or PLACEHOLDER_CASED.search(text)
    if found:
        report.fail(where, f"{label} contains placeholder text: {found.group(0)!r}")


def check_copy(report, where, copy, strict=True):
    title = copy.get("title", "")
    description = copy.get("description", "")
    if not title:
        report.fail(where, "title is empty")
    elif len(title) > 60:
        report.fail(where, f"title has {len(title)} characters (maximum 60)")
    elif len(title) < 30 and strict:
        report.warn(where, f"title has {len(title)} characters (target 30 to 60)")
    if not description:
        report.fail(where, "description is empty")
    elif len(description) > 160:
        report.fail(where, f"description has {len(description)} characters (maximum 160)")
    elif len(description) < 120:
        if strict:
            report.fail(where, f"description has {len(description)} characters (minimum 120)")
        else:
            report.warn(where, f"description has {len(description)} characters (target 120 to 160)")
    if not copy.get("h1"):
        report.fail(where, "h1 is empty")
    for field in ("title", "description", "h1"):
        scan_text(report, where, field, copy.get(field, ""))


def check_plan(plan, report):
    HOUSE_RULES.update(plan.get("house_rules", {}))
    for field in ("client", "domain", "deploy", "keyword_source", "locales", "pages"):
        if not plan.get(field):
            report.fail("plan", f"{field} is missing")
    if report.fails:
        return

    domain = plan["domain"]
    scan_text(report, "plan", "domain", domain)
    scan_text(report, "plan", "client", plan["client"])
    scan_text(report, "plan", "keyword_source", plan["keyword_source"])
    if not domain.startswith("https://") or domain.endswith("/"):
        report.fail("plan", "domain must start with https:// and have no trailing slash")
    if re.search(r"\.(pages\.dev|vercel\.app)", domain):
        report.fail("plan", "domain must be the final host, not a preview host")
    if plan["deploy"] not in ("static", "server"):
        report.fail("plan", "deploy must be static or server")
    if plan["keyword_source"].lower() == "none":
        report.warn("plan", "the plan has no keyword data")

    defaults = [l for l in plan["locales"] if l.get("default")]
    if len(defaults) != 1 or defaults[0].get("prefix") != "":
        report.fail("plan", "locales must have 1 default locale with an empty prefix")
        return
    extra_locales = [l for l in plan["locales"] if not l.get("default")]

    routes, titles, descriptions, keywords = {}, {}, {}, {}
    for page in plan["pages"]:
        route = page.get("route", "")
        where = route or "(page without route)"
        if not ROUTE.match(route):
            report.fail(where, "route must be lower case with hyphens")
        if route in routes:
            report.fail(where, "route is a duplicate")
        routes[route] = page
        if page.get("type") not in PAGE_TYPES:
            report.fail(where, f"type {page.get('type')!r} is not valid")
        if not page.get("nav"):
            report.fail(where, "nav is empty")
        else:
            scan_text(report, where, "nav", page["nav"])
        check_copy(report, where, page)
        for store, field in ((titles, "title"), (descriptions, "description")):
            value = page.get(field, "").strip().lower()
            if value and value in store:
                report.fail(where, f"{field} is the same as on {store[value]}")
            store[value] = route

        for locale in extra_locales:
            copy = page.get("translations", {}).get(locale["key"])
            if not copy:
                report.fail(where, f"translations.{locale['key']} is missing")
            else:
                check_copy(report, localized(locale["prefix"], route), copy, strict=False)

        if page.get("type") in COMMERCIAL and not page.get("noindex"):
            keyword = page.get("primary_keyword", "")
            if not keyword:
                report.fail(where, "primary_keyword is missing")
                continue
            scan_text(report, where, "primary_keyword", keyword)
            key = " ".join(sorted(tokens(keyword)))
            if key in keywords:
                report.fail(where, f"primary_keyword is the same as on {keywords[key]}")
            keywords[key] = route
            if not has_keyword(keyword, page.get("title", "")):
                report.fail(where, f"title does not contain the keyword {keyword!r}")
            if page.get("volume") is None and plan["keyword_source"].lower() != "none":
                report.warn(where, "volume is null")

    if "/" not in routes:
        report.fail("plan", "the plan has no home page")
    types = {p.get("type") for p in plan["pages"]}
    for needed in ("contact", "legal"):
        if needed not in types:
            report.warn("plan", f"the plan has no {needed} page")
    for redirect in plan.get("redirects", []):
        if redirect.get("to") not in routes:
            report.fail("plan", f"redirect target {redirect.get('to')} is not in the plan")
    return len(plan["pages"])


class PageParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.meta = {}
        self.links = []
        self.anchors = []
        self.images = []
        self.h1 = []
        self.headings = []
        self.jsonld = []
        self.has_main = False
        self.visible = []
        self.main_text = []
        self._skip = 0
        self._svg = 0
        self._main = 0
        self._capture = None
        self._buffer = []
        self._script_ld = False
        self._heading = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "svg":
            self._svg += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self._script_ld = True
            self._buffer = []
        if tag in self.SKIP:
            self._skip += 1
            return
        if tag == "title" and not self._svg and self.title is None:
            self._capture = "title"
            self._buffer = []
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta.setdefault(key, a.get("content", ""))
        elif tag == "link":
            self.links.append(a)
        elif tag == "a" and a.get("href"):
            self.anchors.append(a["href"])
        elif tag == "img":
            self.images.append(a)
        elif tag == "main":
            self.has_main = True
            self._main += 1
        elif re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
            self._heading = tag
            if tag == "h1":
                self.h1.append("")

    def handle_endtag(self, tag):
        if tag == "svg" and self._svg:
            self._svg -= 1
        if tag == "script" and self._script_ld:
            self.jsonld.append("".join(self._buffer))
            self._script_ld = False
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if tag == "title" and self._capture == "title":
            self.title = "".join(self._buffer).strip()
            self._capture = None
        elif tag == "main":
            self._main = max(0, self._main - 1)
        elif tag == self._heading:
            self._heading = None

    def handle_data(self, data):
        if self._script_ld or self._capture:
            self._buffer.append(data)
            return
        if self._skip:
            return
        self.visible.append(data)
        if self._main:
            self.main_text.append(data)
        if self._heading == "h1" and self.h1:
            self.h1[-1] += data


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def ld_nodes(blocks, report, where):
    nodes = []
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as error:
            report.fail(where, f"JSON-LD does not parse: {error}")
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            nodes.extend(item.get("@graph", [item]))
    return nodes


def ld_types(node):
    value = node.get("@type", [])
    return value if isinstance(value, list) else [value]


def built_dir(root):
    for candidate in (root / "out", root / ".next" / "server" / "app"):
        if candidate.is_dir() and any(candidate.rglob("*.html")):
            return candidate
    return None


def built_routes(directory):
    routes = {}
    for file in directory.rglob("*.html"):
        relative = file.relative_to(directory).as_posix()
        parts = relative.split("/")
        if any(p.startswith("_") for p in parts) or parts[0] in ("404", "404.html", "500", "500.html"):
            continue
        route = "/" + relative[:-5]
        if route == "/index":
            route = "/"
        elif route.endswith("/index"):
            route = route[: -len("/index")]
        routes[route] = file
    return routes


def read_generated(directory, name):
    for candidate in (directory / name, directory / f"{name}.body"):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return None


def page_url(domain, path):
    return domain if path == "/" else f"{domain}{path}"


def localized(prefix, route):
    return f"{prefix}{'' if route == '/' else route}" or "/"


def link_path(href, domain):
    if href.startswith(domain):
        href = href[len(domain):] or "/"
    if not href.startswith("/") or href.startswith("//"):
        return None
    path = href.split("#")[0].split("?")[0]
    return path.rstrip("/") or "/"


def image_file(src, public, domain):
    if src.startswith(domain):
        src = src[len(domain):]
    if src.startswith("/_next/image"):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
        src = query.get("url", [""])[0]
    if not src.startswith("/") or src.startswith("//") or src.startswith("/_next/"):
        return None
    return public / urllib.parse.unquote(src.split("?")[0]).lstrip("/")


def check_page(report, ctx, path, route, locale, page, parsed, raw):
    where = path
    domain = ctx["domain"]
    default = locale.get("default")
    copy = page if default else page.get("translations", {}).get(locale["key"], {})
    release = ctx["release"]
    open_page = not page.get("noindex")

    if parsed.title != copy.get("title"):
        report.fail(where, f"title in HTML is {parsed.title!r}, plan has {copy.get('title')!r}")
    if parsed.meta.get("description") != copy.get("description"):
        report.fail(where, "meta description in HTML is not the same as the plan")
    if len(parsed.h1) != 1:
        report.fail(where, f"page has {len(parsed.h1)} H1 elements (must be 1)")
    elif clean(parsed.h1[0]) != clean(copy.get("h1", "")):
        report.fail(where, f"H1 in HTML is {clean(parsed.h1[0])!r}, plan has {copy.get('h1')!r}")
    if not parsed.has_main:
        report.fail(where, "page has no <main> element")
    for previous, current in zip(parsed.headings, parsed.headings[1:]):
        if current > previous + 1:
            report.warn(where, f"heading level jumps from H{previous} to H{current}")
            break

    canonical = [l.get("href", "") for l in parsed.links if l.get("rel") == "canonical"]
    expected = page_url(domain, path)
    if [c.rstrip("/") for c in canonical] != [expected]:
        report.fail(where, f"canonical is {canonical}, expected {expected}")

    if len(ctx["plan"]["locales"]) > 1:
        found = {l.get("hreflang"): l.get("href", "") for l in parsed.links if l.get("hreflang")}
        for other in ctx["plan"]["locales"]:
            want = page_url(domain, localized(other["prefix"], route))
            if found.get(other["hreflang"], "").rstrip("/") != want:
                report.fail(where, f"hreflang {other['hreflang']} is missing or wrong")
        if "x-default" not in found:
            report.fail(where, "hreflang x-default is missing")

    robots = parsed.meta.get("robots", "")
    if release and open_page and "noindex" in robots:
        report.fail(where, "page is noindex on a release build")
    if page.get("noindex") and "noindex" not in robots:
        report.fail(where, "plan says noindex, the HTML does not")

    for key in ("og:title", "og:description", "og:image"):
        if not parsed.meta.get(key):
            report.fail(where, f"{key} is missing")
    og_image = parsed.meta.get("og:image", "")
    if og_image:
        file = image_file(og_image, ctx["public"], domain)
        if file is not None:
            ctx["used_images"].add(file)
            if not file.is_file():
                report.fail(where, f"og:image file does not exist: {og_image}")

    nodes = ld_nodes(parsed.jsonld, report, where)
    types = {t for node in nodes for t in ld_types(node)}
    page_type = page.get("type")
    needed = {
        "service": ["Service", "BreadcrumbList"],
        "category": ["BreadcrumbList"],
        "location": ["BreadcrumbList"],
        "landing": ["BreadcrumbList"],
        "post": ["Article|BlogPosting", "BreadcrumbList"],
    }.get(page_type, [])
    for item in needed:
        if not types & set(item.split("|")):
            report.fail(where, f"JSON-LD {item} is missing")
    if page_type == "home" and not any(n.get("address") or n.get("legalName") for n in nodes):
        report.fail(where, "JSON-LD for the organization is missing")

    visible = clean(" ".join(parsed.visible))
    for node in nodes:
        if "FAQPage" not in ld_types(node):
            continue
        for question in node.get("mainEntity", []):
            if clean(question.get("name", "")) not in visible:
                report.fail(where, f"FAQ schema question is not on the page: {question.get('name')!r}")
            answer = question.get("acceptedAnswer", {}).get("text", "")
            if "**" in answer or re.search(r"\]\(", answer):
                report.fail(where, "FAQ schema answer contains Markdown")

    scan_text(report, where, "page text", visible)
    scan_text(report, where, "JSON-LD", " ".join(parsed.jsonld))
    for image in parsed.images:
        scan_text(report, where, "alt text", image.get("alt", ""))

    main_words = re.findall(r"[\w'؀-ۿ]+", " ".join(parsed.main_text))
    if page_type in THIN_TYPES and len(main_words) < MIN_WORDS:
        report.fail(where, f"page has {len(main_words)} words in <main> (minimum {MIN_WORDS})")
    keyword = page.get("primary_keyword")
    if default and keyword and page_type in COMMERCIAL:
        if not has_keyword(keyword, " ".join(main_words[:150])):
            report.warn(where, f"the keyword {keyword!r} is not in the first 150 words")

    if raw.count("opacity:0") > 0:
        report.warn(where, f"HTML has opacity:0 on {raw.count('opacity:0')} elements")

    preloads = [l for l in parsed.links if l.get("rel") == "preload" and l.get("as") == "image"]
    if len(preloads) > 2:
        report.fail(where, f"page preloads {len(preloads)} images (maximum 2)")

    for image in parsed.images:
        src = image.get("src", "")
        if "alt" not in image:
            report.fail(where, f"image has no alt attribute: {src}")
        file = image_file(src, ctx["public"], domain) if src else None
        if file is None:
            continue
        ctx["used_images"].add(file)
        if not file.is_file():
            report.fail(where, f"image file does not exist: {src}")

    for href in parsed.anchors:
        target = link_path(href, domain)
        if target is None:
            continue
        ctx["inbound"].setdefault(target, set())
        if target != path:
            ctx["inbound"][target].add(path)
        known = target in ctx["all_paths"]
        asset = (ctx["public"] / target.lstrip("/")).is_file()
        if not known and not asset:
            report.fail(where, f"internal link has no target: {href}")


def check_css(root, report):
    files = [f for d in (root / "out" / "_next" / "static", root / ".next" / "static")
             if d.is_dir() for f in d.rglob("*.css")]
    if not files:
        report.fail("css", "the build has no CSS file")
    for file in files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"@theme|@tailwind\b|@import\s+[\"']tailwindcss", text):
            report.fail("css", f"{file.name} contains source Tailwind code. The CSS did not compile")


def check_icon(root, report):
    app = root / "src" / "app"
    found = list(app.glob("icon.*")) + list(app.glob("favicon.*")) + [
        f for f in [root / "public" / "favicon.ico"] if f.is_file()]
    if not found:
        report.fail("icon", "the site has no favicon. Add src/app/icon.png from the logo")


def check_source(root, report):
    source = root / "src"
    if not source.is_dir():
        report.fail("src", "folder does not exist")
        return
    for file in source.rglob("*"):
        if file.suffix not in {".ts", ".tsx", ".css", ".json", ".md", ".mdx"}:
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        where = file.relative_to(root).as_posix()
        if HOUSE_RULES["no_dashes"] and DASHES.search(text):
            report.fail(where, "file contains an em-dash or en-dash")
        if "__FILL" in text and file.name != "site-plan.template.json":
            report.fail(where, "file contains a __FILL value")
        is_plan = file.name == "site-plan.json"
        if HOUSE_RULES["no_eyebrows"] and not is_plan and re.search(r"eyebrow|kicker", text, re.I):
            report.fail(where, "file contains an eyebrow or kicker element")


def check_build(root, release, report):
    plan_file = root / "src" / "lib" / "site-plan.json"
    if not plan_file.is_file():
        report.fail("plan", f"{plan_file} does not exist")
        return 0
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    check_plan(plan, report)
    if report.fails:
        return 0
    if not plan.get("approved_by") or not plan.get("approved_on"):
        report.fail("plan", "approved_by and approved_on are missing (GATE 2)")

    directory = built_dir(root)
    if directory is None:
        report.fail("build", "no built HTML found. Run npm run build first")
        return 0

    domain = plan["domain"]
    routes = built_routes(directory)
    pages = {p["route"]: p for p in plan["pages"]}
    expected = {}
    for route, page in pages.items():
        for locale in plan["locales"]:
            expected[localized(locale["prefix"], route)] = (route, locale)

    for path in sorted(set(expected) - set(routes)):
        report.fail(path, "the plan has this page, the build does not")
    for path in sorted(set(routes) - set(expected)):
        report.fail(path, "the build has this page, the plan does not")
    if not (directory / "404.html").is_file() and not (directory / "_not-found.html").is_file():
        report.fail("build", "no 404 page found")

    ctx = {
        "plan": plan,
        "domain": domain,
        "release": release,
        "public": root / "public",
        "inbound": {},
        "used_images": set(),
        "all_paths": set(routes),
    }

    checked = 0
    for path in sorted(set(routes) & set(expected)):
        raw = routes[path].read_text(encoding="utf-8")
        parsed = PageParser()
        parsed.feed(raw)
        route, locale = expected[path]
        check_page(report, ctx, path, route, locale, pages[route], parsed, raw)
        checked += 1

    for path, (route, _) in expected.items():
        if path != "/" and not pages[route].get("noindex") and path in routes:
            if not ctx["inbound"].get(path):
                report.fail(path, "no other page links to this page")

    for file in sorted(ctx["used_images"]):
        if file.is_file() and file.suffix.lower() in RASTER:
            size = file.stat().st_size / 1024
            label = file.relative_to(ctx["public"]).as_posix()
            if size > IMAGE_FAIL_KB:
                report.fail(label, f"image is {size:.0f} KB (maximum {IMAGE_FAIL_KB})")
            elif size > IMAGE_WARN_KB:
                report.warn(label, f"image is {size:.0f} KB (target {IMAGE_WARN_KB})")

    sitemap = read_generated(directory, "sitemap.xml")
    if sitemap is None:
        report.fail("sitemap", "sitemap.xml was not built")
    else:
        tree = ElementTree.fromstring(sitemap)
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        rows = {el.text.strip().rstrip("/") for el in tree.iter(f"{namespace}loc")}
        wanted = {page_url(domain, r) for r, p in pages.items() if not p.get("noindex")}
        for url in sorted(wanted - rows):
            report.fail("sitemap", f"URL is missing: {url}")
        for url in sorted(rows - wanted):
            report.fail("sitemap", f"URL is not in the plan: {url}")

    robots = read_generated(directory, "robots.txt")
    if robots is None:
        report.fail("robots", "robots.txt was not built")
    elif release:
        if re.search(r"^Disallow:\s*/\s*$", robots, re.M):
            report.fail("robots", "robots.txt blocks the site on a release build")
        if "Sitemap:" not in robots:
            report.fail("robots", "robots.txt has no Sitemap line")

    if plan["deploy"] == "static" and not (root / "out").is_dir():
        report.fail("build", "deploy is static, but out/ does not exist")

    check_source(root, report)
    check_css(root, report)
    check_icon(root, report)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan_command = commands.add_parser("plan")
    plan_command.add_argument("plan")
    build_command = commands.add_parser("build")
    build_command.add_argument("project")
    build_command.add_argument("--release", action="store_true")
    args = parser.parse_args()

    report = Report()
    if args.command == "plan":
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        count = check_plan(plan, report) or 0
        if not count and not report.fails:
            report.fail("plan", "the plan has no pages")
        return report.finish(f"{count} pages checked in the plan")

    count = check_build(Path(args.project).resolve(), args.release, report)
    if not count and not report.fails:
        report.fail("build", "pages checked: 0")
    mode = "release" if args.release else "preview"
    return report.finish(f"pages checked: {count} ({mode} mode)")


if __name__ == "__main__":
    sys.exit(main())
