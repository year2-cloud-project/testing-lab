import json
from pathlib import Path


CONFIG_PATH = Path("config/monitoring.json")


def validate_config(config):
    errors = []

    service = config.get("service")
    port = config.get("port")
    interval = config.get("interval_seconds")
    timeout = config.get("timeout_seconds")

    if not isinstance(service, str) or not service.strip():
        errors.append("service must not be empty")

    if (
        not isinstance(port, int)
        or isinstance(port, bool)
        or not 0 <= port <= 65535
    ):
        errors.append("port must be between 1 and 65535")

    if (
        not isinstance(interval, int)
        or isinstance(interval, bool)
        or interval <= 0
    ):
        errors.append("interval_seconds must be a positive integer")

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        errors.append("timeout_seconds must be a positive number")

    return errors


def main():
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = json.load(handle)

    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Configuration valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
