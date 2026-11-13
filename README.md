# Campus Status - Part 3 starter update

These files extend the existing team Campus Status repository for the Testing and DevOps block in Project Preparation.

Apply the supplied update to the existing repository. Do not create a replacement repository or discard the Git history and documentation from the earlier project work.

The practical work tests configuration and automation, checks a real external status service, builds a small static site from Markdown, and deploys the tested site to Cloudflare Pages.

## Setup

From the project root:

```bash
python -m pip install -r requirements.txt
```

Run the current tests with:

```bash
python -m pytest -q
```

Run the configuration validator with:

```bash
python scripts/validate_config.py
```

Do not commit real passwords or API tokens.
