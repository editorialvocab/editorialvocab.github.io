#!/usr/bin/env python3
"""
scripts/generate_web_pages_backup.py
═════════════════════════════════════
GitHub Actions failover for the website pipeline.

WHY THIS EXISTS
────────────────
The PRIMARY web pipeline is web_pipeline.py, running on GitLab CI
(mahadi07/rtejhs, `web_pipeline` stage, SCHEDULE_TYPE=web_pipeline,
09:15 UTC) and on the local laptop via local_runner.py. This script is
a BACKUP that runs entirely inside this repo (editorialvocab.github.io)
via GitHub Actions, so the site still gets today's pages even if
GitLab CI is down.

WHERE THE DATA COMES FROM
────────────────
mahadi07/rtejhs is public, so the workflow does a shallow clone of it
into GITLAB_SRC (see web-pipeline-backup.yml) before this script runs
— but only for EdData/data (the part that changes daily).

web_generator.py itself is now VENDORED into this repo, right next to
this script (scripts/web_generator.py), instead of being pulled from
the GitLab clone. It changes rarely, so keeping a local copy removes
an entire class of "did the clone actually contain it" failure modes.
If you update web_generator.py in mahadi07/rtejhs, copy the new
version here too — they're expected to drift only when you do that on
purpose.

The three tiny loader functions below are duplicated from
_load_vocab_from_file / _load_saved_wotd_entry / _load_saved_quiz_data
in mahadi07/rtejhs's main.py — deliberately NOT imported from there,
because main.py pulls in scrapers/vocabulary/firebase_campaign/etc.,
which would need a much heavier pip install just for a backup job that
only needs to read three small JSON files. If their on-disk JSON
layout ever changes in main.py, mirror the change here too.

BRANCH
────────────────
GitHub Pages serves this site from the `VSCode` branch — the workflow
checks out and pushes back to VSCode, not main.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Make sure this script's own directory (where the vendored
# web_generator.py lives) is searched first — explicit, rather than
# relying on Python's implicit "script dir goes in sys.path[0]"
# behavior, so this still works if the invocation style ever changes.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GITLAB_SRC = os.environ.get("GITLAB_SRC", "gitlab_src")

from web_generator import (          # noqa: E402  (needs sys.path set first)
    generate_wotd_page,
    generate_quiz_page,
    append_to_exam_archive,
    regenerate_static_pages,
    generate_monthly_index,
)


# ── Loader helpers (duplicated from main.py — see module docstring) ───────────

def _load_vocab_from_file(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh).get("wordMeaning", [])
    except Exception:
        return []


def _load_saved_wotd_entry(lang: str, date: str):
    try:
        display_date = datetime.strptime(date, "%d-%m-%Y").strftime("%d %B %Y")
        month_file = f"{date.split('-')[1]}-{date.split('-')[2]}"
        folder = "WordOfTheDayEnToBn" if lang == "bn" else "WordOfTheDayEnToHn"
        path = f"{GITLAB_SRC}/EdData/data/{folder}/{month_file}.json"
        with open(path, "r", encoding="utf-8") as fh:
            monthly_list = json.load(fh)
        for entry in monthly_list:
            if entry.get("date") == display_date:
                return entry
    except Exception:
        return None


def _load_saved_quiz_data(lang: str, date: str):
    try:
        folder = "DayOfTheQuizEnToBn" if lang == "bn" else "DayOfTheQuizEnToHn"
        path = f"{GITLAB_SRC}/EdData/data/{folder}/{date}.json"
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _maybe_run_monthly_index(current_date: str) -> bool:
    """Same two-window logic as maybe_run_monthly_index() in main.py."""
    day, month, year = (int(p) for p in current_date.split("-"))
    ran = False
    if day >= 28:
        try:
            generate_monthly_index(year, month)
            ran = True
        except Exception as e:
            print(f"⚠️  Monthly index (current month) error: {e}")
    if day <= 5:
        prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
        try:
            generate_monthly_index(prev_year, prev_month)
            ran = True
        except Exception as e:
            print(f"⚠️  Monthly index (previous month backfill) error: {e}")
    return ran


def main() -> None:
    current_date = os.environ.get("PIPELINE_DATE", "").strip() or \
        datetime.now(ZoneInfo("Asia/Dhaka")).strftime("%d-%m-%Y")

    print("=" * 60)
    print("WEB PIPELINE — GITHUB ACTIONS BACKUP")
    print(f"Date: {current_date}")
    print("=" * 60)

    vocab_bn = _load_vocab_from_file(f"{GITLAB_SRC}/EdData/data/EnToBnWord/{current_date}.json")
    vocab_hn = _load_vocab_from_file(f"{GITLAB_SRC}/EdData/data/EnToHnWord/{current_date}.json")
    wotd_bn_entry = _load_saved_wotd_entry("bn", current_date)
    wotd_hn_entry = _load_saved_wotd_entry("hn", current_date)

    if not wotd_bn_entry and not wotd_hn_entry:
        print(f"⚠️  No WOTD data found in mahadi07/rtejhs for {current_date} yet.")
        print("    Either today's main_pipeline hasn't run/pushed yet, or it failed.")
        print("    Exiting 1 — this workflow's own schedule will retry tomorrow.")
        sys.exit(1)

    quiz_bn = _load_saved_quiz_data("bn", current_date)
    quiz_hn = _load_saved_quiz_data("hn", current_date)

    page_gen_ok = False
    try:
        if wotd_bn_entry:
            generate_wotd_page("bn", wotd_bn_entry, vocab_bn, current_date)
            append_to_exam_archive("bn", wotd_bn_entry, current_date)
        else:
            print(f"⚠️  No Bengali WOTD entry for {current_date} — skipping BN pages")

        if quiz_bn and quiz_bn.get("questions"):
            generate_quiz_page("bn", quiz_bn, current_date)

        if wotd_hn_entry:
            generate_wotd_page("hn", wotd_hn_entry, vocab_hn, current_date)
            append_to_exam_archive("hn", wotd_hn_entry, current_date)
        else:
            print(f"⚠️  No Hindi WOTD entry for {current_date} — skipping HN pages")

        if quiz_hn and quiz_hn.get("questions"):
            generate_quiz_page("hn", quiz_hn, current_date)

        page_gen_ok = True
        print("✅ WOTD + quiz pages generated")
    except Exception as e:
        print(f"⚠️  Page generation error (non-fatal): {e}")

    try:
        regenerate_static_pages()
        print("✅ Sitemap / static pages regenerated")
    except Exception as e:
        print(f"⚠️  Sitemap regeneration error (non-fatal): {e}")

    monthly_ran = _maybe_run_monthly_index(current_date)
    print(f"{'✅' if monthly_ran else 'ℹ️ '} Monthly SEO index: "
          f"{'generated' if monthly_ran else 'not due today'}")

    sys.exit(0 if page_gen_ok else 1)


if __name__ == "__main__":
    main()
