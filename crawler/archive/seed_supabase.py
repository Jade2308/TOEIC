#!/usr/bin/env python3
"""
scripts/seed_supabase.py
========================
Imports extracted TOEIC JSON datasets into Supabase PostgreSQL tables:
- question_groups
- questions

Usage:
    python scripts/seed_supabase.py "processed_data/TEST 1 - ETS 2023/final/test1_full.json"
    python scripts/seed_supabase.py "processed_data/TEST 1 - ETS 2023/final/test1_part1.json" "processed_data/TEST 1 - ETS 2023/final/test1_part2.json"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 stdout on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("[ERROR] 'supabase' package is not installed. Run: pip install supabase")
    sys.exit(1)


def seed_file(sp_client, json_path: Path):
    print(f"\n[*] Processing file: {json_path.name}")
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    groups = payload.get("question_groups", [])
    questions = payload.get("questions", [])

    if not groups and not questions:
        print(f"[!] No groups or questions found in {json_path.name}")
        return

    print(f"    ➔ Question Groups: {len(groups)}")
    print(f"    ➔ Questions      : {len(questions)}")

    try:
        # Upsert question groups
        if groups:
            res_g = sp_client.table("question_groups").upsert(groups).execute()
            print(f"    [✓] Successfully upserted {len(groups)} question_groups!")

        # Upsert questions
        if questions:
            res_q = sp_client.table("questions").upsert(questions).execute()
            print(f"    [✓] Successfully upserted {len(questions)} questions!")

    except Exception as e:
        err_msg = str(e)
        print(f"\n[ERROR] Supabase insert failed: {err_msg}")
        if "42501" in err_msg or "row-level security" in err_msg.lower():
            print("\n" + "=" * 70)
            print("(!) SUPABASE RLS PERMISSION REQUIRED")
            print("=" * 70)
            print("Supabase blocked insertion because Row Level Security (RLS) is active")
            print("and requires public insert permission. Please open Supabase SQL Editor and run:")
            print("\n--- COPY & PASTE INTO SUPABASE SQL EDITOR ---")
            print("ALTER TABLE question_groups DISABLE ROW LEVEL SECURITY;")
            print("ALTER TABLE questions DISABLE ROW LEVEL SECURITY;")
            print("---------------------------------------------\n")
            print("Or provide SUPABASE_SERVICE_ROLE_KEY in .env file.")
            print("=" * 70 + "\n")
        raise e


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase with extracted TOEIC JSON questions.")
    parser.add_argument("files", nargs="+", help="Paths to extracted JSON files")
    args = parser.parse_args()

    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    # Prefer service role key if user provided it, otherwise use anon key
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
    )

    if not url or not key:
        print("[ERROR] Supabase credentials not found in .env!")
        print("Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.")
        sys.exit(1)

    print("=" * 70)
    print(" TOEIC DATASET SEEDER -> SUPABASE POSTGRESQL")
    print("=" * 70)
    print(f"[*] Supabase URL : {url}")
    print(f"[*] Auth Key     : {key[:16]}...")
    print("=" * 70)

    sp_client = create_client(url, key)

    success_count = 0
    for file_str in args.files:
        f_path = Path(file_str)
        if not f_path.exists():
            print(f"[WARN] File not found: {f_path}")
            continue
        try:
            seed_file(sp_client, f_path)
            success_count += 1
        except Exception:
            break

    if success_count == len(args.files):
        print(f"\n[DONE] All {success_count} file(s) imported into Supabase successfully!\n")


if __name__ == "__main__":
    main()
