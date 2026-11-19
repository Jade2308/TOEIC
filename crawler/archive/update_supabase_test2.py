import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local")

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from supabase import create_client

def main():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("Supabase credentials not configured.")
        return

    client = create_client(url, key)
    test_name = "ETS TOEIC 2023 - Test 2"

    print(f"[*] Querying existing groups for '{test_name}' in Supabase...")
    res = client.table("question_groups").select("id").eq("test_name", test_name).execute()
    old_group_ids = [r["id"] for r in (res.data or [])]
    print(f"  Found {len(old_group_ids)} old groups.")

    if old_group_ids:
        print("  [-] Deleting old questions...")
        # Batch delete in chunks of 50
        for i in range(0, len(old_group_ids), 50):
            chunk = old_group_ids[i:i+50]
            client.table("questions").delete().in_("group_id", chunk).execute()

        print("  [-] Deleting old question groups...")
        for i in range(0, len(old_group_ids), 50):
            chunk = old_group_ids[i:i+50]
            client.table("question_groups").delete().in_("id", chunk).execute()
        print("  [✓] Old Test 2 data deleted from Supabase.")

    # Load new authoritative dataset
    json_path = Path("processed_data/TEST 2 - ETS 2023/final/test_2___ets_2023_full.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_groups = data["question_groups"]
    new_questions = data["questions"]

    print(f"[*] Inserting {len(new_groups)} new question groups...")
    # Upsert in batches of 50
    for i in range(0, len(new_groups), 50):
        chunk = new_groups[i:i+50]
        client.table("question_groups").upsert(chunk).execute()
    print("  [✓] Question groups inserted.")

    print(f"[*] Inserting {len(new_questions)} new questions...")
    for i in range(0, len(new_questions), 50):
        chunk = new_questions[i:i+50]
        client.table("questions").upsert(chunk).execute()
    print("  [✓] All 200 questions inserted into Supabase!")

if __name__ == "__main__":
    main()
