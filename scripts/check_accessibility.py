from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "TU-Dublin-Project-Preparation/1.0 (+https://www.tudublin.ie/)"
GENERIC_LINK_TEXT = {"click here", "here", "read more", "more"}


class AccessibilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.title_parts = []
        self.in_title = False
        self.h1_count = 0
        self.main_count = 0
        self.missing_alt = 0
        self.links = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        elif tag == "img" and "alt" not in attributes:
            self.missing_alt += 1
        elif tag == "a":
            self.current_link = {
                "text": [],
                "aria_label": attributes.get("aria-label", ""),
            }

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "a" and self.current_link is not None:
            text = " ".join("".join(self.current_link["text"]).split())
            accessible_text = text or self.current_link["aria_label"].strip()
            self.links.append(accessible_text)
            self.current_link = None

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.current_link is not None:
            self.current_link["text"].append(data)


def inspect_html(html_text):
    parser = AccessibilityParser()
    parser.feed(html_text)

    errors = []
    title = " ".join("".join(parser.title_parts).split())

    if not parser.lang or not parser.lang.lower().startswith("en"):
        errors.append("page language must be identified as English")
    if not title:
        errors.append("page must have a non-empty title")
    if parser.h1_count != 1:
        errors.append("page must contain exactly one h1 heading")
    if parser.main_count != 1:
        errors.append("page must contain exactly one main region")
    if parser.missing_alt:
        errors.append("every image must have an alt attribute")

    for link_text in parser.links:
        normalised = " ".join(link_text.lower().split())
        if not normalised:
            errors.append("links must have accessible text")
        elif normalised in GENERIC_LINK_TEXT:
            errors.append(f"link text '{link_text}' does not describe its purpose")

    return errors


def read_html(location, timeout=5):
    parsed = urlparse(location)
    if parsed.scheme in {"http", "https"}:
        request = Request(location, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    return Path(location).read_text(encoding="utf-8")


def locations_to_check(location):
    parsed = urlparse(location)
    if parsed.scheme in {"http", "https"}:
        base = location.rstrip("/") + "/"
        return [("home page", base), ("operations page", urljoin(base, "operations.html"))]
    return [("page", location)]


def check_location(location, timeout=5):
    results = []
    for label, target in locations_to_check(location):
        html = read_html(target, timeout=timeout)
        results.append((label, inspect_html(html)))
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(
            "Usage: python scripts/check_accessibility.py <page-file-or-base-url>",
            file=sys.stderr,
        )
        return 2

    try:
        results = check_location(args[0])
    except HTTPError as exc:
        print(f"FAIL: HTTP {exc.code}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError, UnicodeError) as exc:
        print(f"FAIL: could not read page: {exc}", file=sys.stderr)
        return 1

    failures = 0
    for label, errors in results:
        if errors:
            for error in errors:
                print(f"FAIL {label}: {error}")
                failures += 1
        else:
            print(f"PASS {label}: selected accessibility rules passed")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
