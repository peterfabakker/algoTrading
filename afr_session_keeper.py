#!/usr/bin/env python3
"""
AFR Session Keeper - Refreshes page periodically to maintain session cookie
Stores cookie in /codeload/config/cookie.txt

Usage:
    Interactive mode (first time login):
        python afr_session_keeper.py --interactive

    Single refresh (for cron):
        python afr_session_keeper.py --once

    Continuous mode:
        python afr_session_keeper.py --loop
"""
import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIE_FILE = Path("/codeload/config/cookie.txt")
AFR_URL = "https://www.afr.com"
REFRESH_INTERVAL = 300  # 5 minutes (adjust as needed)


def save_cookies(context):
    """Save browser cookies to file."""
    cookies = context.cookies()
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
    print(f"[{time.strftime('%H:%M:%S')}] Saved {len(cookies)} cookies to {COOKIE_FILE}")


def convert_cookie_for_playwright(cookie):
    """Convert browser extension cookie format to Playwright format."""
    # Map sameSite values from browser extensions to Playwright
    same_site_map = {
        "no_restriction": "None",
        "unspecified": "Lax",
        "lax": "Lax",
        "strict": "Strict",
        "none": "None",
    }

    # Build Playwright-compatible cookie
    pw_cookie = {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie.get("path", "/"),
    }

    # Handle sameSite
    same_site = cookie.get("sameSite", "Lax")
    if isinstance(same_site, str):
        pw_cookie["sameSite"] = same_site_map.get(same_site.lower(), "Lax")

    # Handle expiration (browser uses expirationDate, Playwright uses expires)
    if "expirationDate" in cookie:
        pw_cookie["expires"] = cookie["expirationDate"]
    elif "expires" in cookie:
        pw_cookie["expires"] = cookie["expires"]

    # Optional fields
    if cookie.get("secure"):
        pw_cookie["secure"] = True
    if cookie.get("httpOnly"):
        pw_cookie["httpOnly"] = True

    return pw_cookie


def load_cookies(context):
    """Load cookies from file if they exist."""
    if COOKIE_FILE.exists():
        try:
            cookies = json.loads(COOKIE_FILE.read_text())
            # Convert cookies to Playwright format
            pw_cookies = [convert_cookie_for_playwright(c) for c in cookies]
            context.add_cookies(pw_cookies)
            print(f"Loaded {len(pw_cookies)} cookies from {COOKIE_FILE}")
            return True
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to load cookies: {e}")
    return False


def run_once(headless=True):
    """Single refresh - suitable for cron jobs."""
    if not COOKIE_FILE.exists():
        print(f"ERROR: No cookie file found at {COOKIE_FILE}")
        print("Run with --interactive first to log in and create cookies.")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        if not load_cookies(context):
            print("ERROR: Failed to load cookies")
            browser.close()
            return 1

        page = context.new_page()
        try:
            page.goto(AFR_URL, wait_until="networkidle", timeout=60000)
            save_cookies(context)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Session refreshed successfully")
            browser.close()
            return 0
        except Exception as e:
            print(f"ERROR: {e}")
            browser.close()
            return 1


def run_interactive():
    """Interactive mode for initial login."""
    print("=" * 50)
    print("AFR Session Keeper - Interactive Login")
    print(f"Cookie file: {COOKIE_FILE}")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Try to load existing cookies
        cookies_loaded = load_cookies(context)

        page = context.new_page()
        page.goto(AFR_URL, wait_until="networkidle")

        if not cookies_loaded:
            print("\n" + "=" * 50)
            print("No existing cookies found.")
            print("Please log in with Apple ID in the browser window...")
            print("Press Enter here once you're logged in...")
            print("=" * 50)
        else:
            print("\nCookies loaded. Verify you're logged in.")
            print("If not, please log in now.")
            print("Press Enter when ready to save cookies...")

        input()
        save_cookies(context)
        browser.close()
        print("\nDone! You can now use --once for cron jobs.")
        return 0


def run_loop():
    """Continuous refresh mode."""
    if not COOKIE_FILE.exists():
        print(f"ERROR: No cookie file found at {COOKIE_FILE}")
        print("Run with --interactive first to log in and create cookies.")
        return 1

    print("=" * 50)
    print("AFR Session Keeper - Continuous Mode")
    print(f"Cookie file: {COOKIE_FILE}")
    print(f"Refresh interval: {REFRESH_INTERVAL} seconds")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        if not load_cookies(context):
            print("ERROR: Failed to load cookies")
            browser.close()
            return 1

        page = context.new_page()
        page.goto(AFR_URL, wait_until="networkidle")
        save_cookies(context)

        print(f"\nStarting auto-refresh every {REFRESH_INTERVAL} seconds...")
        print("Press Ctrl+C to stop.\n")

        refresh_count = 0
        while True:
            try:
                time.sleep(REFRESH_INTERVAL)
                page.reload(wait_until="networkidle")
                refresh_count += 1
                save_cookies(context)
                print(f"[{time.strftime('%H:%M:%S')}] Refresh #{refresh_count} complete")
            except KeyboardInterrupt:
                print("\n\nStopping session keeper...")
                save_cookies(context)
                break
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)
                try:
                    page.goto(AFR_URL, wait_until="networkidle")
                except:
                    pass

        browser.close()
        print("Done. Cookies saved.")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="AFR Session Keeper - Maintain login session cookies"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: opens browser for manual login"
    )
    group.add_argument(
        "--once", "-o",
        action="store_true",
        help="Single refresh: load cookies, refresh page, save cookies (for cron)"
    )
    group.add_argument(
        "--loop", "-l",
        action="store_true",
        help="Continuous mode: keep refreshing in a loop"
    )

    args = parser.parse_args()

    if args.interactive:
        sys.exit(run_interactive())
    elif args.once:
        sys.exit(run_once())
    elif args.loop:
        sys.exit(run_loop())


if __name__ == "__main__":
    main()
