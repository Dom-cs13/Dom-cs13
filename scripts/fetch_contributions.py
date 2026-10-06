#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public contributions endpoint.
Outputs data/contributions.json with raw days and derived statistics.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "Dom-cs13"
DEFAULT_URL_TEMPLATE = "https://github.com/users/{username}/contributions"
DEFAULT_OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def parse_contributions_html(html_text: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html_text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        return []

    days: List[Dict[str, Any]] = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""

        if re.search(r"no contributions", text, re.IGNORECASE):
            count = 0
        else:
            match = re.search(r"(\d+)", text)
            count = int(match.group(1)) if match else 0

        level = int(td.get("data-level") or 0)
        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def fetch_days(username: str) -> List[Dict[str, Any]]:
    url = DEFAULT_URL_TEMPLATE.format(username=username)
    resp = requests.get(url, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    days = parse_contributions_html(resp.text)
    if not days:
        raise ValueError(f"No contribution cells found for user {username}")
    return days


def compute_current_streak(days: List[Dict[str, Any]]) -> Tuple[int, str | None, str | None]:
    if not days:
        return 0, None, None

    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1

    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1

    if streak == 0:
        return 0, None, None

    start_idx = idx + 1
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days: List[Dict[str, Any]]) -> Tuple[int, str | None, str | None]:
    if not days:
        return 0, None, None

    longest = 0
    run = 0
    longest_start = None
    longest_end = None
    run_start_idx = None

    for i, day in enumerate(days):
        if day["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = day["date"]
        else:
            run = 0

    return longest, longest_start, longest_end


def build_data(days: List[Dict[str, Any]], username: str = DEFAULT_USERNAME) -> Dict[str, Any]:
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly: Dict[str, int] = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]

    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": username,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {
            "start": days[0]["date"] if days else "",
            "end": days[-1]["date"] if days else "",
        },
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


def main() -> None:
    username = os.environ.get("GH_PROFILE_USER", DEFAULT_USERNAME)
    out_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT_PATH

    print(f"Fetching contributions for {username}...")
    days = fetch_days(username)
    data = build_data(days, username=username)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(
        f"Wrote {out_path}: {data['total_contributions']} contributions, "
        f"current streak {data['current_streak']['length']}, "
        f"longest streak {data['longest_streak']['length']}"
    )


if __name__ == "__main__":
    main()
