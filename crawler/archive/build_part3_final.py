import os
import sys
import json
import uuid

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ANSWERS = {
    32: 'A', 33: 'D', 34: 'C', 35: 'C', 36: 'A', 37: 'B', 38: 'A', 39: 'B', 40: 'D',
    41: 'C', 42: 'B', 43: 'D', 44: 'C', 45: 'D', 46: 'B', 47: 'B', 48: 'A', 49: 'D',
    50: 'C', 51: 'D', 52: 'A', 53: 'C', 54: 'C', 55: 'A', 56: 'A', 57: 'B', 58: 'A',
    59: 'C', 60: 'B', 61: 'A', 62: 'A', 63: 'D', 64: 'B', 65: 'D', 66: 'C', 67: 'A',
    68: 'B', 69: 'D', 70: 'D'
}

group_audio_starts = {
    "g32_34": 834.0,
    "g35_37": 912.0,
    "g38_40": 983.5,
    "g41_43": 1054.0,
    "g44_46": 1136.5,
    "g47_49": 1218.5,
    "g50_52": 1294.0,
    "g53_55": 1365.5,
    "g56_58": 1441.0,
    "g59_61": 1531.0,
    "g62_64": 1616.0,
    "g65_67": 1711.0,
    "g68_70": 1798.5,
}

graphics_map = {
    "g62_64": "/images/test1/part3_g62_64.png",
    "g65_67": "/images/test1/part3_g65_67.png",
    "g68_70": "/images/test1/part3_g68_70.png",
}

question_graphics_map = {
    63: "/images/test1/part3_q63.png",
    66: "/images/test1/part3_q66.png",
    69: "/images/test1/part3_q69.png",
}

# Load whisper raw segments
with open("processed_data/TEST 1 - ETS 2023/intermediate/whisper/part3_whisper_raw.json", "r", encoding="utf-8") as f:
    whisper_segs = json.load(f)

# Load batch files
with open("processed_data/TEST 1 - ETS 2023/intermediate/batches/part3_batch1.json", "r", encoding="utf-8") as f:
    b1 = json.load(f)["groups"]

with open("processed_data/TEST 1 - ETS 2023/intermediate/batches/part3_batch2.json", "r", encoding="utf-8") as f:
    b2 = json.load(f)["groups"]

with open("processed_data/TEST 1 - ETS 2023/intermediate/batches/part3_g56_58.json", "r", encoding="utf-8") as f:
    b_56_58 = json.load(f)["groups"]

with open("processed_data/TEST 1 - ETS 2023/intermediate/batches/part3_batch3.json", "r", encoding="utf-8") as f:
    b3 = json.load(f)["groups"]

# Merge all groups in exact order
all_raw_groups = b1 + b2 + b_56_58 + b3
# Sort by q_start
all_raw_groups.sort(key=lambda g: g.get("q_start", 0) or g["questions"][0]["question_number"])

print(f"Total merged groups: {len(all_raw_groups)}")

final_groups = []
final_questions = []

for g in all_raw_groups:
    qs = g["questions"]
    q_start = qs[0]["question_number"]
    q_end = qs[-1]["question_number"]
    g_key = f"g{q_start}_{q_end}"
    
    # Deterministic UUID for Supabase compatibility
    g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test1-p3-{g_key}"))

    audio_start = group_audio_starts.get(g_key, 0.0)
    audio_url = f"/audio/test1/part3_{g_key}.mp3"
    image_url = graphics_map.get(g_key, None)

    # Find whisper segments belonging to this conversation dialogue
    group_whisper = [s for s in whisper_segs if s["start"] >= audio_start - 1.0 and s["end"] <= audio_start + 110.0]
    
    raw_dialogue = g.get("dialogue", [])
    transcript_segments = []

    conv_whisper = [s for s in group_whisper if not any(k in s["text"].lower() for k in ["refer to the following", "no. 3", "no. 4", "no. 5", "no. 6", "no. 7"])]
    
    if raw_dialogue:
        num_lines = len(raw_dialogue)
        d_start = 5.5
        d_end = 35.0
        if conv_whisper:
            d_start = max(4.0, round(conv_whisper[0]["start"] - audio_start, 2))
            d_end = round(conv_whisper[-1]["end"] - audio_start, 2)
        
        step = (d_end - d_start) / max(1, num_lines)
        for idx, line in enumerate(raw_dialogue):
            seg_start = round(d_start + idx * step, 2)
            seg_end = round(d_start + (idx + 1) * step, 2)
            transcript_segments.append({
                "id": f"seg-p3-{q_start}-{idx+1:02d}",
                "speaker": line.get("speaker", "Speaker"),
                "start_time": seg_start,
                "end_time": seg_end,
                "text_en": line.get("text_en", "").strip(),
                "text_vi": line.get("text_vi", "").strip(),
                "is_trap": False
            })

    group_obj = {
        "id": g_id,
        "test_name": "ETS TOEIC 2023 - Test 1",
        "part": 3,
        "image_url": image_url,
        "audio_url": audio_url,
        "passage_text": None,
        "transcript_segments": transcript_segments
    }
    final_groups.append(group_obj)

    # Process questions
    for q in qs:
        q_num = q["question_number"]
        q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test1-q{q_num}"))
        correct_letter = ANSWERS.get(q_num, q.get("correct_answer", "A"))

        opts = q.get("options", {})
        cleaned_options = {
            "A": opts.get("A", "").strip(),
            "B": opts.get("B", "").strip(),
            "C": opts.get("C", "").strip(),
            "D": opts.get("D", "").strip(),
        }

        q_obj = {
            "id": q_id,
            "group_id": g_id,
            "question_number": q_num,
            "part": 3,
            "question_text": q.get("question_text", "").strip(),
            "options": cleaned_options,
            "correct_answer": correct_letter,
            "explanation_vi": q.get("explanation_vi", "").strip(),
            "question_type_tag": q.get("question_type_tag", "detail_lookup"),
            "evidence_quote": q.get("evidence_quote", None),
            "paraphrase_pair": q.get("paraphrase_pair", None),
            "image_url": question_graphics_map.get(q_num, None)
        }
        final_questions.append(q_obj)

output_payload = {
    "test_name": "ETS TOEIC 2023 - Test 1",
    "part": 3,
    "total_groups": len(final_groups),
    "total_questions": len(final_questions),
    "question_groups": final_groups,
    "questions": final_questions
}

out_file = "processed_data/TEST 1 - ETS 2023/final/test1_part3.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(output_payload, f, ensure_ascii=False, indent=2)

print(f"\n[✓] Successfully compiled test1_part3.json with UUIDs!")
print(f"Total groups: {len(final_groups)} (Expected: 13)")
print(f"Total questions: {len(final_questions)} (Expected: 39)")
print("Question numbers:", [q["question_number"] for q in final_questions])
