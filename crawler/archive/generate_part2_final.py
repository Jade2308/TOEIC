import os
import sys
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

# Load whisper raw segments
with open("processed_data/TEST 1 - ETS 2023/intermediate/whisper/part2_whisper_raw.json", "r", encoding="utf-8") as f:
    whisper_segs = json.load(f)

# Load gemini extracted 25 questions
with open("processed_data/TEST 1 - ETS 2023/intermediate/answers/part2_extracted_raw.json", "r", encoding="utf-8") as f:
    gemini_data = json.load(f)
    gemini_questions = gemini_data["questions"]

ranges = {
    7:  (293.8, 310.8),
    8:  (313.1, 330.9),
    9:  (332.6, 350.4),
    10: (352.0, 370.2),
    11: (370.3, 390.0),
    12: (391.0, 410.2),
    13: (410.3, 427.4),
    14: (429.5, 446.4),
    15: (448.1, 466.9),
    16: (468.6, 487.9),
    17: (488.0, 506.9),
    18: (507.0, 526.1),
    19: (528.1, 546.2),
    20: (547.9, 566.4),
    21: (568.0, 585.3),
    22: (587.1, 607.8),
    23: (608.7, 628.5),
    24: (630.6, 650.8),
    25: (652.5, 672.4),
    26: (673.9, 692.9),
    27: (694.6, 715.1),
    28: (716.2, 736.9),
    29: (738.6, 758.6),
    30: (760.4, 779.6),
    31: (781.3, 801.8),
}

q_starts = [
    (7, 2), (8, 10), (9, 18), (10, 26), (11, 34), (12, 42), (13, 50),
    (14, 58), (15, 66), (16, 74), (17, 82), (18, 90), (19, 98), (20, 107),
    (21, 115), (22, 123), (23, 130), (24, 138), (25, 146), (26, 154),
    (27, 162), (28, 170), (29, 178), (30, 186), (31, 194), (32, 202)
]

def extract_timestamps(q_num, start_idx, next_idx):
    t_base = ranges[q_num][0]
    sub = whisper_segs[start_idx:next_idx]
    clip_dur = round(ranges[q_num][1] - t_base, 2)
    
    # Defaults
    q_start = 2.0
    q_end = 5.0
    a_start = 5.5
    a_end = 8.5
    b_start = 9.0
    b_end = 12.0
    c_start = 12.5
    c_end = min(clip_dur - 1.0, 16.0)
    
    if len(sub) >= 8:
        # Standard:
        # sub[0] = Number X
        # sub[1] = Question
        # sub[2] = A, sub[3] = text A
        # sub[4] = B, sub[5] = text B
        # sub[6] = C, sub[7] = text C (and possibly sub[8])
        q_start = max(0.5, round(sub[1]["start"] - t_base, 2))
        q_end = round(sub[1]["end"] - t_base, 2)
        
        a_start = round(sub[2]["start"] - t_base, 2)
        a_end = round(sub[3]["end"] - t_base, 2)
        
        b_start = round(sub[4]["start"] - t_base, 2)
        b_end = round(sub[5]["end"] - t_base, 2)
        
        c_start = round(sub[6]["start"] - t_base, 2)
        c_end = round(sub[-1]["end"] - t_base, 2)
    elif len(sub) == 7: # Q22
        # sub[0] = Number 22
        # sub[1] = Question
        # sub[2] = A, sub[3] = text A
        # sub[4] = B, sub[5] = text B
        # sub[6] = text C
        q_start = max(0.5, round(sub[1]["start"] - t_base, 2))
        q_end = round(sub[1]["end"] - t_base, 2)
        a_start = round(sub[2]["start"] - t_base, 2)
        a_end = round(sub[3]["end"] - t_base, 2)
        b_start = round(sub[4]["start"] - t_base, 2)
        b_end = round(sub[5]["end"] - t_base, 2)
        c_start = round(sub[6]["start"] - t_base, 2)
        c_end = round(sub[6]["end"] - t_base, 2)
    
    # Ensure sequential integrity
    if a_start <= q_end:
        a_start = round(q_end + 0.4, 2)
    if a_end <= a_start:
        a_end = round(a_start + 2.5, 2)
    if b_start <= a_end:
        b_start = round(a_end + 0.4, 2)
    if b_end <= b_start:
        b_end = round(b_start + 2.5, 2)
    if c_start <= b_end:
        c_start = round(b_end + 0.4, 2)
    if c_end <= c_start:
        c_end = round(c_start + 2.5, 2)
        
    return (q_start, q_end, a_start, a_end, b_start, b_end, c_start, c_end)

# Map gemini questions by question_number
gq_map = {q["question_number"]: q for q in gemini_questions}

new_groups = []
new_questions = []

# Deterministic namespace UUIDs for Part 2 Test 1
for i in range(len(q_starts) - 1):
    q_num, start_idx = q_starts[i]
    _, next_idx = q_starts[i+1]
    
    gq = gq_map[q_num]
    q_start, q_end, a_start, a_end, b_start, b_end, c_start, c_end = extract_timestamps(q_num, start_idx, next_idx)
    
    group_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test1-p2-group-q{q_num}"))
    question_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test1-p2-q{q_num}"))
    
    transcript_segments = [
        {
            "id": f"seg-p2-q{q_num}-q",
            "speaker": "Speaker",
            "start_time": q_start,
            "end_time": q_end,
            "text_en": gq["question_text"],
            "text_vi": gq["question_vi"],
            "is_trap": False
        },
        {
            "id": f"seg-p2-q{q_num}-a",
            "speaker": "Speaker",
            "start_time": a_start,
            "end_time": a_end,
            "text_en": f"(A) {gq['option_A']}",
            "text_vi": f"(A) {gq['option_A_vi']}",
            "is_trap": gq["option_A_is_trap"]
        },
        {
            "id": f"seg-p2-q{q_num}-b",
            "speaker": "Speaker",
            "start_time": b_start,
            "end_time": b_end,
            "text_en": f"(B) {gq['option_B']}",
            "text_vi": f"(B) {gq['option_B_vi']}",
            "is_trap": gq["option_B_is_trap"]
        },
        {
            "id": f"seg-p2-q{q_num}-c",
            "speaker": "Speaker",
            "start_time": c_start,
            "end_time": c_end,
            "text_en": f"(C) {gq['option_C']}",
            "text_vi": f"(C) {gq['option_C_vi']}",
            "is_trap": gq["option_C_is_trap"]
        }
    ]
    
    group_obj = {
        "id": group_id,
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 2,
        "passage_text": None,
        "image_url": None,
        "audio_url": f"/audio/test1/part2_q{q_num}.mp3",
        "transcript_segments": transcript_segments
    }
    new_groups.append(group_obj)
    
    # Strip any leading (A), (B), (C) from Gemini text if already included
    opt_a = gq["option_A"].strip()
    if opt_a.startswith("(A) "): opt_a = opt_a[4:]
    opt_b = gq["option_B"].strip()
    if opt_b.startswith("(B) "): opt_b = opt_b[4:]
    opt_c = gq["option_C"].strip()
    if opt_c.startswith("(C) "): opt_c = opt_c[4:]
    
    question_obj = {
        "id": question_id,
        "group_id": group_id,
        "part": 2,
        "question_number": q_num,
        "question_type_tag": gq["question_type_tag"],
        "question_text": gq["question_text"],
        "options": {
            "A": f"(A) {opt_a}",
            "B": f"(B) {opt_b}",
            "C": f"(C) {opt_c}"
        },
        "correct_answer": gq["correct_answer"],
        "explanation_vi": gq["explanation_vi"],
        "evidence_quote": None,
        "paraphrase_pair": None
    }
    new_questions.append(question_obj)

payload = {
    "metadata": {
        "test_name": "ETS TOEIC 2023 - Test 1",
        "extracted_at": "2026-10-29",
        "model_used": "gemini-2.5-flash",
        "total_groups": len(new_groups),
        "total_questions": len(new_questions)
    },
    "question_groups": new_groups,
    "questions": new_questions
}

out_file = "processed_data/TEST 1 - ETS 2023/final/test1_part2.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"[✓] Saved {len(new_groups)} groups and {len(new_questions)} questions to {out_file}")
