import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv(".env.local")
load_dotenv(".env")

# Pop local cwd so it doesn't import local supabase directory
if sys.path[0] in [".", os.getcwd()]:
    sys.path.pop(0)

from supabase import create_client

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("[ERROR] Supabase credentials not found!")
    sys.exit(1)

sp = create_client(url, key)

json_path = Path("processed_data/TEST 1 - ETS 2023/final/test1_part3.json")
with open(json_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

groups = payload.get("question_groups", [])
questions = payload.get("questions", [])

print(f"Preparing to update Supabase with {len(groups)} groups and {len(questions)} questions for Part 3...")

# Clean up old part 3 data
try:
    print("Deleting old Part 3 records from Supabase...")
    res_del_q = sp.table("questions").delete().eq("part", 3).execute()
    print(f"  [✓] Deleted old questions: {len(res_del_q.data)}")
    res_del_g = sp.table("question_groups").delete().eq("part", 3).execute()
    print(f"  [✓] Deleted old groups: {len(res_del_g.data)}")
except Exception as e:
    print(f"[WARN] Error during delete (continuing): {e}")

print("Inserting new Part 3 question groups...")
res_g = sp.table("question_groups").upsert(groups).execute()
print(f"  [✓] Successfully upserted {len(res_g.data)} question_groups into Supabase!")

print("Inserting new Part 3 questions...")
clean_questions = [{k: v for k, v in q.items() if k != "image_url"} for q in questions]
res_q = sp.table("questions").upsert(clean_questions).execute()
print(f"  [✓] Successfully upserted {len(res_q.data)} questions into Supabase!")

print("\n[VERIFICATION]")
verify_q = sp.table("questions").select("id, question_number, correct_answer").eq("part", 3).order("question_number").execute()
print(f"Total Part 3 questions in Supabase now: {len(verify_q.data)}")
for q in verify_q.data:
    print(f"  Q{q['question_number']:2d}: {q['correct_answer']}")
