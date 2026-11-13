import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STATUS_URL = "https://www.cloudflarestatus.com/api/v2/status.json"
USER_AGENT = "TU-Dublin-Project-Preparation/1.0 (+https://www.tudublin.ie/)"


def is_healthy(status_data):
    try:
        indicator = status_data["status"]["indicator"]
    except (KeyError, TypeError) as exc:
        raise ValueError("response does not contain a status indicator") from exc

    if not isinstance(indicator, str):
        raise ValueError("status indicator must be text")

    return indicator == "none"


def fetch_status(url=STATUS_URL, timeout=5):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def main():
    try:
        data = fetch_status()
        description = data.get("status", {}).get("description", "No description")
        print(f"Cloudflare status: {description}")
        return 0 if is_healthy(data) else 1
    except HTTPError as exc:
        print(f"HTTP error: {exc.code}", file=sys.stderr)
    except (URLError, TimeoutError) as exc:
        print(f"Network error: {exc}", file=sys.stderr)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Response error: {exc}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
