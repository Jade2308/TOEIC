import os
import sys
import json
import uuid

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ANSWERS = {
    71: "C", 72: "D", 73: "B",
    74: "C", 75: "D", 76: "B",
    77: "C", 78: "A", 79: "B",
    80: "D", 81: "C", 82: "A",
    83: "D", 84: "A", 85: "A",
    86: "B", 87: "D", 88: "C",
    89: "A", 90: "B", 91: "D",
    92: "D", 93: "C", 94: "B",
    95: "A", 96: "D", 97: "C",
    98: "C", 99: "B", 100: "B"
}

group_audio_starts = {
    "g71_73": 1921.0,
    "g74_76": 2001.0,
    "g77_79": 2081.0,
    "g80_82": 2165.0,
    "g83_85": 2243.0,
    "g86_88": 2325.0,
    "g89_91": 2408.0,
    "g92_94": 2496.0,
    "g95_97": 2579.0,
    "g98_100": 2658.0,
}

graphics_map = {
    "g95_97": "/images/test1/part4_g95_97.png",
    "g98_100": "/images/test1/part4_g98_100.png",
}

question_graphics_map = {
    96: "/images/test1/part4_q96.png",
    99: "/images/test1/part4_q99.png",
}

def build_part4():
    # Load whisper raw segments
    whisper_file = "processed_data/TEST 1 - ETS 2023/intermediate/whisper/part4_whisper_raw.json"
    if not os.path.exists(whisper_file):
        print(f"[ERROR] {whisper_file} not found!")
        return False
    with open(whisper_file, "r", encoding="utf-8") as f:
        whisper_segs = json.load(f)

    # Load batch files
    batch_dir = "processed_data/TEST 1 - ETS 2023/intermediate/batches"
    with open(f"{batch_dir}/part4_batch1.json", "r", encoding="utf-8") as f:
        b1 = json.load(f)["groups"]
    with open(f"{batch_dir}/part4_batch2.json", "r", encoding="utf-8") as f:
        b2 = json.load(f)["groups"]
    with open(f"{batch_dir}/part4_batch3.json", "r", encoding="utf-8") as f:
        b3 = json.load(f)["groups"]

    all_raw_groups = b1 + b2 + b3
    all_raw_groups.sort(key=lambda g: g.get("q_start", 0) or g["questions"][0]["question_number"])
    print(f"Total merged groups: {len(all_raw_groups)}")

    final_groups = []
    final_questions = []

    for g in all_raw_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        g_key = f"g{q_start}_{q_end}"

        # Deterministic UUID for Supabase
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test1-p4-{g_key}"))

        audio_start = group_audio_starts.get(g_key, 0.0)
        audio_url = f"/audio/test1/part4_{g_key}.mp3"
        image_url = graphics_map.get(g_key, None)

        group_whisper = [s for s in whisper_segs if s["start"] >= audio_start - 1.0 and s["end"] <= audio_start + 110.0]

        raw_dialogue = g.get("dialogue", [])
        transcript_segments = []

        conv_whisper = [s for s in group_whisper if not any(k in s["text"].lower() for k in ["question 7", "question 8", "question 9", "number 7", "number 8", "number 9", "number 100"])]

        if raw_dialogue:
            num_lines = len(raw_dialogue)
            d_start = 5.0
            d_end = 35.0
            if conv_whisper:
                d_start = max(4.0, round(conv_whisper[0]["start"] - audio_start, 2))
                d_end = round(conv_whisper[-1]["end"] - audio_start, 2)

            step = (d_end - d_start) / max(1, num_lines)
            for idx, line in enumerate(raw_dialogue):
                seg_start = round(d_start + idx * step, 2)
                seg_end = round(d_start + (idx + 1) * step, 2)
                transcript_segments.append({
                    "id": f"seg-p4-{q_start}-{idx+1:02d}",
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
            "part": 4,
            "image_url": image_url,
            "audio_url": audio_url,
            "passage_text": None,
            "transcript_segments": transcript_segments
        }
        final_groups.append(group_obj)

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
                "part": 4,
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
        "part": 4,
        "total_groups": len(final_groups),
        "total_questions": len(final_questions),
        "question_groups": final_groups,
        "questions": final_questions
    }

    out_file = "processed_data/TEST 1 - ETS 2023/final/test1_part4.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Successfully compiled test1_part4.json!")
    print(f"Total groups: {len(final_groups)} (Expected: 10)")
    print(f"Total questions: {len(final_questions)} (Expected: 30)")
    print("Question numbers:", [q["question_number"] for q in final_questions])
    return True

if __name__ == "__main__":
    build_part4()
