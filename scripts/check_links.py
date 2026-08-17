#!/usr/bin/env python3
"""Check that every external link in the repo's markdown files is reachable.

Used by CI. Exits non-zero if any link fails after retries.
Standard library only, so CI needs nothing beyond Python 3.9+.
"""

import concurrent.futures
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"https?://[^\s\)\]>\"']+")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
    "agentic-engineer-path-link-check"
)
TIMEOUT = 30
RETRIES = 3
# Some hosts return 403 to any non-browser client. Treat these codes as
# "alive" because the resource exists; only connection failures and 404-class
# codes should fail the build.
ACCEPTABLE_CODES = {200, 301, 302, 303, 307, 308, 403, 405, 429, 999}


def collect_links() -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            url = match.group(0).rstrip(".,;:")
            links.setdefault(url, []).append(str(md.relative_to(ROOT)))
    return links


def check(url: str) -> tuple[str, bool, str]:
    last_error = "unknown"
    for attempt in range(1, RETRIES + 1):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                code = resp.getcode()
        except urllib.error.HTTPError as err:
            code = err.code
        except Exception as err:  # noqa: BLE001
            last_error = f"{type(err).__name__}: {err}"
            time.sleep(2 * attempt)
            continue
        if code in ACCEPTABLE_CODES:
            return url, True, str(code)
        last_error = f"HTTP {code}"
        time.sleep(2 * attempt)
    return url, False, last_error


def main() -> int:
    links = collect_links()
    print(f"Checking {len(links)} unique links...")
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for url, ok, detail in pool.map(check, sorted(links)):
            status = "ok" if ok else "FAIL"
            print(f"  [{status}] {detail:>24}  {url}")
            if not ok:
                failures.append((url, detail))
    if failures:
        print(f"\n{len(failures)} link(s) failed:")
        for url, detail in failures:
            print(f"  {url} ({detail}) in {', '.join(links[url])}")
        return 1
    print("\nAll links reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
