import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


USER_AGENT = "TU-Dublin-Project-Preparation/1.0 (+https://www.tudublin.ie/)"


def fetch_text(url, timeout=5):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def check_site(base_url, timeout=5):
    base = base_url.rstrip("/") + "/"
    home = fetch_text(base, timeout=timeout)
    if "Campus Status" not in home:
        raise ValueError("home page does not contain expected Campus Status content")

    status_text = fetch_text(urljoin(base, "status.json"), timeout=timeout)
    status = json.loads(status_text)
    if status.get("service") != "Campus Status":
        raise ValueError("status.json does not identify Campus Status")
    if status.get("status") != "operational":
        raise ValueError("status.json does not report operational status")

    return True


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python scripts/check_site.py <base-url>", file=sys.stderr)
        return 2

    try:
        check_site(args[0])
    except HTTPError as exc:
        print(f"FAIL: HTTP {exc.code}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"FAIL: network error: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: deployed Campus Status service is reachable and reports expected content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
