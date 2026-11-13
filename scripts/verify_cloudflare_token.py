import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


VERIFY_URL = "https://api.cloudflare.com/client/v4/user/tokens/verify"
USER_AGENT = "TU-Dublin-Project-Preparation/1.0 (+https://www.tudublin.ie/)"


def load_local_env(path=".env"):
    env_file = Path(path)
    if not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip())


def verify_token(token, timeout=5):
    request = Request(
        VERIFY_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def main():
    load_local_env()
    token = os.getenv("CLOUDFLARE_API_TOKEN")

    if not token:
        print("CLOUDFLARE_API_TOKEN is not set", file=sys.stderr)
        return 2

    try:
        data = verify_token(token)
    except HTTPError as exc:
        print(f"Authentication/API error: HTTP {exc.code}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Response error: {exc}", file=sys.stderr)
        return 2

    status = data.get("result", {}).get("status")
    if data.get("success") is True and status == "active":
        print("Cloudflare API token is valid and active")
        return 0

    print("Cloudflare API token was not verified as active", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
