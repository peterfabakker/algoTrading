#!/usr/bin/env python3
"""
AFR Session Keeper - Refreshes page periodically to maintain session cookie
Stores cookie in /codeload/config/cookie.txt
"""
import json
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


def load_cookies(context):
    """Load cookies from file if they exist."""
    if COOKIE_FILE.exists():
        try:
            cookies = json.loads(COOKIE_FILE.read_text())
            context.add_cookies(cookies)
            print(f"Loaded {len(cookies)} cookies from {COOKIE_FILE}")
            return True
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to load cookies: {e}")
    return False


def main():
    print("=" * 50)
    print("AFR Session Keeper")
    print(f"Cookie file: {COOKIE_FILE}")
    print(f"Refresh interval: {REFRESH_INTERVAL} seconds")
    print("=" * 50)

    with sync_playwright() as p:
        # Launch browser (set headless=True after initial login works)
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
            input()
        else:
            # Check if we're actually logged in
            time.sleep(3)
            print("\nChecking login status...")
            # Give user a chance to verify
            print("If you're NOT logged in, please log in now and press Enter.")
            print("If you ARE logged in, just press Enter to start auto-refresh.")
            input()

        # Save cookies after login
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


if __name__ == "__main__":
    main()
