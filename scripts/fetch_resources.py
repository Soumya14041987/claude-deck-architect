#!/usr/bin/env python3
"""
fetch_resources.py — refreshes data/topics.json entries with live GitHub repo
metadata (stars, last-updated) for a given topic's curated repo list. Not
required for deck generation (which can run entirely offline from cached
data) — this is a maintenance script to periodically re-verify links.

Usage:
    python3 fetch_resources.py --topic "bedrock-agentcore"
    python3 fetch_resources.py --all

Respects GITHUB_TOKEN if set (raises the unauthenticated rate limit of
60/hour to 5,000/hour). On a 403 rate-limit response, backs off using the
X-RateLimit-Reset header and retries once; if still rate-limited, leaves the
cached entry untouched and reports it.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
TOPICS_PATH = REPO_ROOT / "data" / "topics.json"

GITHUB_API = "https://api.github.com/repos/{owner_repo}"


def gh_request(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.headers
    except urllib.error.HTTPError as e:
        if e.code == 403:
            reset = e.headers.get("X-RateLimit-Reset")
            if reset:
                wait = max(0, int(reset) - int(time.time())) + 1
                print(f"Rate limited, sleeping {wait}s before retry...", file=sys.stderr)
                time.sleep(min(wait, 60))
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read().decode("utf-8")), resp.headers
        raise


def owner_repo_from_url(url: str):
    parts = url.rstrip("/").split("github.com/")
    if len(parts) != 2:
        return None
    segments = parts[1].split("/")
    if len(segments) < 2:
        return None
    return f"{segments[0]}/{segments[1]}"


def refresh_topic(topic_key: str, topic_data: dict):
    for repo_entry in topic_data.get("repos", []):
        owner_repo = owner_repo_from_url(repo_entry.get("url", ""))
        if not owner_repo:
            continue
        try:
            data, _ = gh_request(GITHUB_API.format(owner_repo=owner_repo))
            repo_entry["stars"] = data.get("stargazers_count")
            repo_entry["last_updated"] = data.get("pushed_at")
            print(f"  {owner_repo}: {repo_entry['stars']} stars, updated {repo_entry['last_updated']}")
        except Exception as e:
            print(f"  {owner_repo}: fetch failed ({e}) — leaving cached entry untouched", file=sys.stderr)
    return topic_data


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--topic", help="Single topic key in topics.json to refresh")
    group.add_argument("--all", action="store_true", help="Refresh every topic")
    args = ap.parse_args()

    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        topics = json.load(f)

    keys = list(topics.keys()) if args.all else [args.topic]
    for key in keys:
        if key not in topics:
            print(f"Unknown topic key: {key}", file=sys.stderr)
            continue
        print(f"Refreshing {key}...")
        topics[key] = refresh_topic(key, topics[key])

    with open(TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)
    print(f"Wrote {TOPICS_PATH}")


if __name__ == "__main__":
    main()
