import os
import sys
from dotenv import load_dotenv
from supabase import create_client

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
sp = create_client(url, key)

res_g = sp.table("question_groups").select("id, part, image_url, audio_url, transcript_segments").eq("part", 1).execute()
print(f"Part 1 Groups count in Supabase: {len(res_g.data)}")
for g in res_g.data:
    segs = g.get("transcript_segments") or []
    print(f"  Group {g['id']}: image={g['image_url']}, audio={g['audio_url']}, segs={len(segs)}")

res_q = sp.table("questions").select("id, group_id, question_number, correct_answer").eq("part", 1).order("question_number").execute()
print(f"\nPart 1 Questions count in Supabase: {len(res_q.data)}")
for q in res_q.data:
    print(f"  Q{q['question_number']}: group={q['group_id']}, answer={q['correct_answer']}")
