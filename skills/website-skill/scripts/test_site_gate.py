#!/usr/bin/env python3
"""Tests for site_gate.py. Each test puts one deliberate fault in a clean site
and checks that the gate reports it. A clean site must pass first, or the
fault tests prove nothing.

  python3 test_site_gate.py
"""
import copy
import importlib.util
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("site_gate", HERE / "site_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

APEX = "example-client.com"
WWW = f"www.{APEX}"
ORIGIN = f"https://{APEX}"

ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {ORIGIN}/sitemap.xml
"""

SITEMAP = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>{ORIGIN}</loc></url>
<url><loc>{ORIGIN}/services/pumps</loc></url>
</urlset>
"""


def page(path, extra=""):
    url = ORIGIN if path == "/" else ORIGIN + path
    return f"""<!doctype html><html lang="en"><head>
<title>Page {path}</title>
<link rel="canonical" href="{url}">
<link rel="stylesheet" href="/_next/static/css/app.css">
<meta property="og:image" content="{ORIGIN}/og.webp">
{extra}</head><body><main><h1>Page</h1><img src="/images/hero.webp" alt="Hero"></main></body></html>"""


SECURITY = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "frame-ancestors 'self'",
    "Permissions-Policy": "camera=()",
    "Strict-Transport-Security": "max-age=31536000",
}


def clean_site():
    """A site with no faults. Keys: (scheme, host, path) or (scheme, host, '*')."""
    html = {"Content-Type": "text/html", **SECURITY}
    redirect_all = lambda path: (301, {"Location": f"{ORIGIN}{path}"}, "")  # noqa: E731
    return {
        ("https", APEX, "/"): (200, html, page("/")),
        ("https", APEX, "/services/pumps"): (200, html, page("/services/pumps")),
        ("https", APEX, "/robots.txt"): (200, {"Content-Type": "text/plain"}, ROBOTS),
        ("https", APEX, "/sitemap.xml"): (200, {"Content-Type": "application/xml"}, SITEMAP),
        ("https", APEX, "/og.webp"): (200, {"Content-Type": "image/webp", "Cache-Control": "public, max-age=2592000"}, "x"),
        ("https", APEX, "/images/hero.webp"): (200, {"Content-Type": "image/webp", "Cache-Control": "public, max-age=2592000"}, "x"),
        ("https", APEX, "/_next/static/css/app.css"): (200, {"Content-Type": "text/css", "Cache-Control": "public, max-age=31536000, immutable"}, "x"),
        ("https", APEX, "/gate-redirect-check"): (404, {}, "not found"),
        ("http", APEX, "*"): redirect_all,
        ("http", WWW, "*"): redirect_all,
        ("https", WWW, "*"): redirect_all,
    }


class Server:
    """A local server that answers for any host, with the scheme taken from
    X-Forwarded-Proto. The test changes self.site to put in a fault."""

    def __init__(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def answer(self, with_body):
                scheme = self.headers.get("X-Forwarded-Proto", "http")
                host = self.headers.get("Host", "")
                path = self.path.split("?")[0]
                entry = server.site.get((scheme, host, path)) or server.site.get((scheme, host, "*"))
                if entry is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                if callable(entry):
                    entry = entry(self.path)
                status, headers, body = entry
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                data = body.encode()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                if with_body:
                    self.wfile.write(data)

            def do_GET(self):
                self.answer(True)

            def do_HEAD(self):
                self.answer(False)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.connect = f"127.0.0.1:{self.httpd.server_address[1]}"
        self.site = clean_site()
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def stop(self):
        self.httpd.shutdown()


class LiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.server.site = clean_site()

    def run_live(self):
        report = gate.Report()
        count = gate.check_live(APEX, report, pages=10, connect=self.server.connect)
        return report, count

    def assert_fail(self, text):
        report, _ = self.run_live()
        joined = "\n".join(report.fails)
        self.assertIn(text, joined, f"expected a FAIL with {text!r}. Fails:\n{joined}\nWarns:\n" + "\n".join(report.warns))

    def assert_warn(self, text):
        report, _ = self.run_live()
        joined = "\n".join(report.warns)
        self.assertIn(text, joined, f"expected a WARN with {text!r}. Warns:\n{joined}")

    def set(self, key, status=None, headers=None, body=None, drop_header=None):
        old = self.server.site[key]
        old_status, old_headers, old_body = old
        new_headers = dict(old_headers if headers is None else headers)
        if drop_header:
            new_headers.pop(drop_header, None)
        self.server.site[key] = (old_status if status is None else status, new_headers,
                                 old_body if body is None else body)

    def test_clean_site_passes(self):
        report, count = self.run_live()
        self.assertEqual(report.fails, [])
        self.assertEqual(report.warns, [])
        self.assertEqual(count, 2)

    def test_duplicate_star_groups(self):
        robots = "User-agent: *\nContent-Signal: search=yes,ai-train=no\nAllow: /\n\n" + ROBOTS
        self.set(("https", APEX, "/robots.txt"), body=robots)
        self.assert_fail("2 'User-agent: *' groups")
        self.assert_warn("Content-Signal")

    def test_ai_answer_bot_block_fails(self):
        self.set(("https", APEX, "/robots.txt"), body="User-agent: OAI-SearchBot\nDisallow: /\n\n" + ROBOTS)
        self.assert_fail("blocks OAI-SearchBot")

    def test_ai_training_bot_block_warns(self):
        robots = "User-agent: GPTBot\nUser-agent: CCBot\nDisallow: /\n\n" + ROBOTS
        self.set(("https", APEX, "/robots.txt"), body=robots)
        report, _ = self.run_live()
        self.assertEqual(report.fails, [])
        self.assert_warn("blocks GPTBot")

    def test_robots_blocks_all(self):
        self.set(("https", APEX, "/robots.txt"), body=f"User-agent: *\nDisallow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n")
        self.assert_fail("'Disallow: /'")

    def test_robots_without_sitemap(self):
        self.set(("https", APEX, "/robots.txt"), body="User-agent: *\nAllow: /\n")
        self.assert_fail("has no Sitemap line")

    def test_www_serves_the_site(self):
        self.server.site[("https", WWW, "*")] = (200, {"Content-Type": "text/html"}, page("/"))
        self.assert_fail("Both hosts serve the site")

    def test_www_temporary_redirect(self):
        self.server.site[("https", WWW, "*")] = lambda path: (302, {"Location": f"{ORIGIN}{path}"}, "")
        self.assert_fail("Use a permanent 301")

    def test_www_redirect_drops_path(self):
        self.server.site[("https", WWW, "*")] = (301, {"Location": f"{ORIGIN}/"}, "")
        self.assert_fail("redirect drops the path")

    def test_redirect_drops_query(self):
        self.server.site[("https", WWW, "*")] = lambda path: (301, {"Location": f"{ORIGIN}{path.split('?')[0]}"}, "")
        self.assert_warn("drops the query string")

    def test_http_not_redirected(self):
        self.server.site[("http", APEX, "*")] = (200, {"Content-Type": "text/html"}, page("/"))
        self.assert_fail(f"http://{APEX}: must 301")

    def test_missing_nosniff(self):
        self.set(("https", APEX, "/"), drop_header="X-Content-Type-Options")
        self.assert_fail("X-Content-Type-Options")

    def test_missing_frame_ancestors(self):
        self.set(("https", APEX, "/"), drop_header="Content-Security-Policy")
        self.assert_fail("frame-ancestors")

    def test_missing_referrer_policy(self):
        self.set(("https", APEX, "/"), drop_header="Referrer-Policy")
        self.assert_fail("Referrer-Policy")

    def test_missing_permissions_policy_warns(self):
        self.set(("https", APEX, "/"), drop_header="Permissions-Policy")
        self.assert_warn("Permissions-Policy")

    def test_missing_og_image(self):
        body = page("/services/pumps").replace(f'<meta property="og:image" content="{ORIGIN}/og.webp">', "")
        self.set(("https", APEX, "/services/pumps"), body=body)
        self.assert_fail("og:image is missing")

    def test_og_image_not_found(self):
        self.server.site[("https", APEX, "/og.webp")] = (404, {"Content-Type": "text/html"}, "")
        self.assert_fail("og:image returns HTTP 404")

    def test_canonical_on_wrong_host(self):
        body = page("/services/pumps").replace(f'href="{ORIGIN}/services/pumps"', f'href="https://{WWW}/services/pumps"')
        self.set(("https", APEX, "/services/pumps"), body=body)
        self.assert_fail("canonical is https://www.")

    def test_noindex_on_live_page(self):
        self.set(("https", APEX, "/services/pumps"), body=page("/services/pumps", '<meta name="robots" content="noindex">'))
        self.assert_fail("meta robots noindex")

    def test_sitemap_url_on_other_host(self):
        self.set(("https", APEX, "/sitemap.xml"), body=SITEMAP.replace(f"{ORIGIN}/services", f"https://{WWW}/services"))
        self.assert_fail("URL is on another host")

    def test_image_folder_without_cache_rule(self):
        self.set(("https", APEX, "/images/hero.webp"), headers={"Content-Type": "image/webp", "Cache-Control": "public, max-age=0, must-revalidate"})
        self.assert_warn("Add a rule for /images/*")

    def test_given_host_redirects(self):
        self.server.site[("https", APEX, "/")] = (301, {"Location": f"https://{WWW}/"}, "")
        self.assert_fail("Give the final host")


class SourceTests(unittest.TestCase):
    def check(self, files):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in files.items():
                path = root / "src" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            report = gate.Report()
            gate.check_source(root, report)
            return report

    def test_clean_data_file_passes(self):
        report = self.check({"lib/process.ts": "export const processSteps = [1, 2];\nexport const locations = [];\n"})
        self.assertEqual(report.fails, [])

    def test_export_shadows_process(self):
        report = self.check({"lib/services.ts": "export const process = [{ step: 1 }];\n"})
        self.assertIn("hides the global", "\n".join(report.fails))

    def test_export_function_shadows_fetch(self):
        report = self.check({"lib/api.ts": "export async function fetch() {}\n"})
        self.assertIn("'fetch'", "\n".join(report.fails))

    def test_clarity_element_id(self):
        report = self.check({"components/Analytics.tsx": '<Script id="clarity" strategy="lazyOnload">'})
        self.assertIn("window.clarity", "\n".join(report.fails))

    def test_safe_tracker_id_passes(self):
        report = self.check({"components/Analytics.tsx": '<Script id="microsoft-clarity" strategy="lazyOnload">'})
        self.assertEqual(report.fails, [])


class StarterTests(unittest.TestCase):
    """The starter files are the source of each new site. A fault here
    goes to every client."""

    def test_starter_source_passes(self):
        root = HERE.parent / "assets" / "starter"
        report = gate.Report()
        saved = dict(gate.HOUSE_RULES)
        gate.HOUSE_RULES.update({"no_dashes": True, "no_eyebrows": True})
        try:
            gate.check_source(root, report)
        finally:
            gate.HOUSE_RULES.update(saved)
        fails = [f for f in report.fails if "__FILL" not in f]
        self.assertEqual(fails, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
