#!/usr/bin/env python3
import argparse
import json
import re
import socket
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


HISTORY_FILE = Path(".regex_pattern_history.json")
MAX_HISTORY = 10
REQUEST_TIMEOUT_SECONDS = 30


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self):
        return "\n".join(self.parts)


def fetch_page_text(url):
    with urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = TextExtractor()
    parser.feed(html)
    return parser.get_text()


def load_history(path=HISTORY_FILE):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_history(pattern, path=HISTORY_FILE):
    history = [p for p in load_history(path) if p != pattern]
    history.append(pattern)
    history = history[-MAX_HISTORY:]
    path.write_text(json.dumps(history), encoding="utf-8")
    return history


def run_search(text, pattern, ignore_case=False):
    flags = re.IGNORECASE if ignore_case else 0
    return re.findall(pattern, text, flags=flags)


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape a website and run regex search.")
    parser.add_argument("--url", help="Website URL to scrape")
    parser.add_argument(
        "--pattern",
        help="Regex pattern to search; if omitted you'll be prompted",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Enable case-insensitive regex matching",
    )
    parser.add_argument(
        "--show-history",
        action="store_true",
        help="Show saved last 10 patterns and exit",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.show_history:
        history = load_history()
        if not history:
            print("No saved patterns.")
            return
        print("Saved patterns (oldest -> newest):")
        for pattern in history:
            print(f"- {pattern}")
        return

    if not args.url:
        print("Error: --url is required.")
        sys.exit(1)

    if args.pattern:
        pattern = args.pattern
    elif sys.stdin.isatty():
        pattern = input("Enter regex pattern: ").strip()
    else:
        print("Error: --pattern is required in non-interactive mode.")
        sys.exit(1)
    if not pattern:
        print("Error: Pattern cannot be empty.")
        sys.exit(1)

    try:
        text = fetch_page_text(args.url)
    except socket.timeout:
        print(f"Failed to fetch URL: request timed out after {REQUEST_TIMEOUT_SECONDS} seconds.")
        sys.exit(1)
    except (URLError, HTTPError, ValueError) as exc:
        print(f"Failed to fetch URL: {exc}")
        sys.exit(1)
    try:
        matches = run_search(text, pattern, ignore_case=args.ignore_case)
    except re.error as exc:
        print(f"Invalid regex pattern: {exc}")
        sys.exit(1)

    try:
        save_history(pattern)
    except OSError as exc:
        print(f"Warning: could not save pattern history: {exc}")
    print(f"Found {len(matches)} match(es).")
    for index, match in enumerate(matches, start=1):
        print(f"{index}: {match}")


if __name__ == "__main__":
    main()
