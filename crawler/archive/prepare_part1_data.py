import json
import uuid
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

# Sliced segments info for each question
q_audio_segments = {
    1: [
        {"id": "seg-q1-a", "speaker": "Speaker", "start_time": 6.7, "end_time": 10.2, "text_en": "(A) A woman is standing near a desk.", "text_vi": "(A) Một người phụ nữ đang đứng gần bàn làm việc.", "is_trap": False},
        {"id": "seg-q1-b", "speaker": "Speaker", "start_time": 10.5, "end_time": 14.2, "text_en": "(B) A woman is climbing some stairs.", "text_vi": "(B) Một người phụ nữ đang bước lên cầu thang.", "is_trap": False},
        {"id": "seg-q1-c", "speaker": "Speaker", "start_time": 14.5, "end_time": 18.2, "text_en": "(C) A woman is entering a building.", "text_vi": "(C) Một người phụ nữ đang đi vào một tòa nhà.", "is_trap": False},
        {"id": "seg-q1-d", "speaker": "Speaker", "start_time": 18.5, "end_time": 23.5, "text_en": "(D) A woman is looking at a map.", "text_vi": "(D) Một người phụ nữ đang nhìn vào bản đồ.", "is_trap": False},
    ],
    2: [
        {"id": "seg-q2-a", "speaker": "Speaker", "start_time": 5.0, "end_time": 8.5, "text_en": "(A) She is swimming in the water.", "text_vi": "(A) Cô ấy đang bơi dưới nước.", "is_trap": False},
        {"id": "seg-q2-b", "speaker": "Speaker", "start_time": 8.8, "end_time": 12.0, "text_en": "(B) She is jogging near the ocean.", "text_vi": "(B) Cô ấy đang chạy bộ gần bờ biển.", "is_trap": False},
        {"id": "seg-q2-c", "speaker": "Speaker", "start_time": 12.3, "end_time": 16.0, "text_en": "(C) Chairs are set up on the beach.", "text_vi": "(C) Những chiếc ghế được xếp trên bãi biển.", "is_trap": False},
        {"id": "seg-q2-d", "speaker": "Speaker", "start_time": 16.3, "end_time": 22.0, "text_en": "(D) A hat is lying on the sand.", "text_vi": "(D) Một chiếc mũ đang nằm trên cát.", "is_trap": False},
    ],
    3: [
        {"id": "seg-q3-a", "speaker": "Speaker", "start_time": 7.2, "end_time": 11.5, "text_en": "(A) She is reaching for an item from a display case.", "text_vi": "(A) Cô ấy đang với lấy một món đồ từ tủ trưng bày.", "is_trap": False},
        {"id": "seg-q3-b", "speaker": "Speaker", "start_time": 11.8, "end_time": 15.5, "text_en": "(B) She is holding on to a shopping cart.", "text_vi": "(B) Cô ấy đang giữ một chiếc xe đẩy mua sắm.", "is_trap": False},
        {"id": "seg-q3-c", "speaker": "Speaker", "start_time": 15.8, "end_time": 19.8, "text_en": "(C) Some goods are being arranged on shelves.", "text_vi": "(C) Một số hàng hóa đang được sắp xếp lên kệ.", "is_trap": True},
        {"id": "seg-q3-d", "speaker": "Speaker", "start_time": 20.1, "end_time": 24.5, "text_en": "(D) Some merchandise has fallen on the floor.", "text_vi": "(D) Một số hàng hóa bị rơi trên sàn.", "is_trap": False},
    ],
    4: [
        {"id": "seg-q4-a", "speaker": "Speaker", "start_time": 4.5, "end_time": 8.5, "text_en": "(A) A fence is being painted in a park.", "text_vi": "(A) Một hàng rào đang được sơn trong công viên.", "is_trap": True},
        {"id": "seg-q4-b", "speaker": "Speaker", "start_time": 8.8, "end_time": 12.5, "text_en": "(B) One of the women is putting on a jacket.", "text_vi": "(B) Một trong những người phụ nữ đang mặc áo khoác.", "is_trap": False},
        {"id": "seg-q4-c", "speaker": "Speaker", "start_time": 12.8, "end_time": 16.5, "text_en": "(C) Some people are working in a garden.", "text_vi": "(C) Một số người đang làm việc trong vườn.", "is_trap": False},
        {"id": "seg-q4-d", "speaker": "Speaker", "start_time": 16.8, "end_time": 22.5, "text_en": "(D) Some people are looking up at the trees.", "text_vi": "(D) Một số người đang nhìn lên những cái cây.", "is_trap": False},
    ],
    5: [
        {"id": "seg-q5-a", "speaker": "Speaker", "start_time": 5.2, "end_time": 8.9, "text_en": "(A) A carpet is being rolled up.", "text_vi": "(A) Một tấm thảm đang được cuộn lại.", "is_trap": True},
        {"id": "seg-q5-b", "speaker": "Speaker", "start_time": 9.2, "end_time": 12.6, "text_en": "(B) Some curtains have been closed.", "text_vi": "(B) Một số rèm cửa đã được đóng lại.", "is_trap": False},
        {"id": "seg-q5-c", "speaker": "Speaker", "start_time": 12.9, "end_time": 16.4, "text_en": "(C) Some cushions are piled on the floor.", "text_vi": "(C) Một số chiếc gối đệm chất đống trên sàn.", "is_trap": False},
        {"id": "seg-q5-d", "speaker": "Speaker", "start_time": 16.7, "end_time": 23.5, "text_en": "(D) Some reading materials have been placed in front of a sofa.", "text_vi": "(D) Một số tài liệu đọc đã được đặt phía trước ghế sofa.", "is_trap": False},
    ],
    6: [
        {"id": "seg-q6-a", "speaker": "Speaker", "start_time": 5.6, "end_time": 9.7, "text_en": "(A) Some musicians are performing on a porch.", "text_vi": "(A) Một số nhạc công đang biểu diễn trên hiên nhà.", "is_trap": False},
        {"id": "seg-q6-b", "speaker": "Speaker", "start_time": 10.0, "end_time": 13.3, "text_en": "(B) Some steps are being repaired.", "text_vi": "(B) Một số bậc thang đang được sửa chữa.", "is_trap": True},
        {"id": "seg-q6-c", "speaker": "Speaker", "start_time": 13.6, "end_time": 17.3, "text_en": "(C) Some music stands are being folded up.", "text_vi": "(C) Một số giá nhạc đang được gấp lại.", "is_trap": True},
        {"id": "seg-q6-d", "speaker": "Speaker", "start_time": 17.6, "end_time": 24.0, "text_en": "(D) Some instruments have been placed in their cases.", "text_vi": "(D) Một số nhạc cụ đã được cất vào trong hộp.", "is_trap": False},
    ],
}

# Read existing questions from test1_part1.json
json_path = Path("processed_data/TEST 1 - ETS 2023/final/test1_part1.json")
with open(json_path, "r", encoding="utf-8") as f:
    old_data = json.load(f)

old_questions = old_data.get("questions", [])

# Fixed stable UUIDs for each Part 1 group to ensure deterministic updates
GROUP_UUIDS = {
    1: "696c6bb7-30c9-4c05-b758-6dbeb48d5c29",  # Reuse existing Q1 group id
    2: "696c6bb7-30c9-4c05-b758-6dbeb48d5c30",
    3: "696c6bb7-30c9-4c05-b758-6dbeb48d5c31",
    4: "696c6bb7-30c9-4c05-b758-6dbeb48d5c32",
    5: "696c6bb7-30c9-4c05-b758-6dbeb48d5c33",
    6: "696c6bb7-30c9-4c05-b758-6dbeb48d5c34",
}

new_groups = []
new_questions = []

for q in old_questions:
    q_num = q["question_number"]
    g_id = GROUP_UUIDS[q_num]
    
    group_obj = {
        "id": g_id,
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 1,
        "passage_text": None,
        "image_url": f"/images/test1/part1_q{q_num}.jpg",
        "audio_url": f"/audio/test1/part1_q{q_num}.mp3",
        "transcript_segments": q_audio_segments.get(q_num, [])
    }
    new_groups.append(group_obj)
    
    q_copy = dict(q)
    q_copy["group_id"] = g_id
    new_questions.append(q_copy)

payload = {
    "metadata": {
        "test_name": "ETS TOEIC 2023 - Test 1",
        "total_groups": len(new_groups),
        "total_questions": len(new_questions)
    },
    "question_groups": new_groups,
    "questions": new_questions
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"[✓] Updated {json_path} with {len(new_groups)} groups and {len(new_questions)} questions.")

# Now sync with Supabase
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
if url and key:
    sp = create_client(url, key)
    print("[-] Upserting question_groups to Supabase...")
    res_g = sp.table("question_groups").upsert(new_groups).execute()
    print(f"    [✓] Upserted {len(res_g.data)} question groups.")
    
    print("[-] Upserting questions to Supabase...")
    res_q = sp.table("questions").upsert(new_questions).execute()
    print(f"    [✓] Upserted {len(res_q.data)} questions.")
    print("\n[SUCCESS] Part 1 data is fully synced with Supabase!")
else:
    print("[WARN] Supabase credentials not found in env.")
