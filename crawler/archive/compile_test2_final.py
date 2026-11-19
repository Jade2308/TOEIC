import os
import sys
import json
import uuid
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def compile_test2():
    test_name = "ETS TOEIC 2023 - Test 2"
    slug = "test_2___ets_2023"
    
    base_dir = Path("processed_data/TEST 2 - ETS 2023")
    batches_dir = base_dir / "intermediate" / "batches"
    segments_dir = base_dir / "intermediate" / "segments"
    final_dir = base_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load official answers
    with open(base_dir / "intermediate" / "answers" / "official_answers.json", "r", encoding="utf-8") as f:
        official_answers = json.load(f)

    # 2. Load sliced audio segments
    with open(segments_dir / "sliced_audio_segments.json", "r", encoding="utf-8") as f:
        audio_segs = json.load(f)

    all_groups = []
    all_questions = []

    # =========================================================================
    # PART 1: 6 Groups, 6 Questions
    # =========================================================================
    print("[-] Compiling Part 1...")
    with open(batches_dir / "batch_part1_q1_6.json", "r", encoding="utf-8") as f:
        p1_batch = json.load(f)
    
    p1_batch_questions = {q["question_number"]: q for g in p1_batch["groups"] for q in g["questions"]}
    
    part1_groups = []
    part1_questions = []

    for q_num in range(1, 7):
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p1-q{q_num}"))
        q_raw = p1_batch_questions.get(q_num, {})

        # Sliced audio segments for this question
        segs = audio_segs.get("part1", {}).get(str(q_num), [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 1,
            "passage_text": None,
            "image_url": f"/images/test2/part1_q{q_num}.jpg",
            "audio_url": f"/audio/test2/part1_q{q_num}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part1_groups.append(group)

        q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
        correct_ans = official_answers.get(str(q_num), q_raw.get("correct_answer", "A"))
        raw_opts = q_raw.get("options", {}) or {}
        cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

        question = {
            "id": q_id,
            "group_id": g_id,
            "part": 1,
            "question_number": q_num,
            "question_type_tag": q_raw.get("question_type_tag", "instruction_action"),
            "question_text": None,
            "options": cleaned_opts,
            "correct_answer": correct_ans,
            "explanation_vi": q_raw.get("explanation_vi", ""),
            "evidence_quote": q_raw.get("evidence_quote"),
            "paraphrase_pair": q_raw.get("paraphrase_pair"),
        }
        part1_questions.append(question)

    # Save Part 1 file
    with open(final_dir / f"{slug}_part1.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 1, "total_groups": len(part1_groups), "total_questions": len(part1_questions)},
            "question_groups": part1_groups,
            "questions": part1_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 1: {len(part1_groups)} groups, {len(part1_questions)} questions")
    all_groups.extend(part1_groups)
    all_questions.extend(part1_questions)

    # =========================================================================
    # PART 2: 25 Groups, 25 Questions
    # =========================================================================
    print("[-] Compiling Part 2...")
    with open(batches_dir / "batch_part2_q7_31.json", "r", encoding="utf-8") as f:
        p2_batch = json.load(f)

    p2_batch_questions = {q["question_number"]: q for g in p2_batch["groups"] for q in g["questions"]}
    part2_groups = []
    part2_questions = []

    # Question text mapping for Part 2 prompts
    p2_prompts = {
        7: "Who's responsible for hiring at our fitness center?",
        8: "Where do you usually purchase office supplies?",
        9: "What time does Mr. Park usually leave?",
        10: "Do you want to present your research to the marketing team?",
        11: "Our company picnic is on Friday, isn't it?",
        12: "Isn't the bus supposed to stop here?",
        13: "We should fill this order quickly, shouldn't we?",
        14: "How do you like your new job?",
        15: "Let's go to the cafeteria for lunch today.",
        16: "When will we hire the new interns?",
        17: "How often should I mail these statements?",
        18: "Why did you put that food in the freezer?",
        19: "Could you print the agenda for the meeting?",
        20: "How far are you from the clinic?",
        21: "Didn't you get to print out of the company newsletter from Emiko?",
        22: "When do you need to renew your passport?",
        23: "Who can help me find replacement parts for my computer?",
        24: "I can't make it to the company dinner tonight.",
        25: "Do you work in this neighborhood?",
        26: "It's time for our quarterly earnings report, isn't it?",
        27: "What did you do with the guest list that I sent you?",
        28: "Did you see the announcement about Emily's promotion?",
        29: "Let's try our best to finish the project on time.",
        30: "Where's the store manager?",
        31: "The software you're using isn't very reliable.",
    }

    for q_num in range(7, 32):
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p2-q{q_num}"))
        q_raw = p2_batch_questions.get(q_num, {})
        segs = audio_segs.get("part2", {}).get(str(q_num), [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 2,
            "passage_text": None,
            "image_url": None,
            "audio_url": f"/audio/test2/part2_q{q_num}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part2_groups.append(group)

        q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
        correct_ans = official_answers.get(str(q_num), q_raw.get("correct_answer", "A"))
        raw_opts = q_raw.get("options", {}) or {}
        cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

        question = {
            "id": q_id,
            "group_id": g_id,
            "part": 2,
            "question_number": q_num,
            "question_type_tag": q_raw.get("question_type_tag", "wh_question"),
            "question_text": p2_prompts.get(q_num, q_raw.get("question_text")),
            "options": cleaned_opts,
            "correct_answer": correct_ans,
            "explanation_vi": q_raw.get("explanation_vi", ""),
            "evidence_quote": q_raw.get("evidence_quote"),
            "paraphrase_pair": q_raw.get("paraphrase_pair"),
        }
        part2_questions.append(question)

    with open(final_dir / f"{slug}_part2.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 2, "total_groups": len(part2_groups), "total_questions": len(part2_questions)},
            "question_groups": part2_groups,
            "questions": part2_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 2: {len(part2_groups)} groups, {len(part2_questions)} questions")
    all_groups.extend(part2_groups)
    all_questions.extend(part2_questions)

    # =========================================================================
    # PART 3: 13 Groups, 39 Questions
    # =========================================================================
    print("[-] Compiling Part 3...")
    with open(batches_dir / "batch_part3_q32_50.json", "r", encoding="utf-8") as f:
        p3_b1 = json.load(f)["groups"]
    with open(batches_dir / "batch_part3_q50_70.json", "r", encoding="utf-8") as f:
        p3_b2 = json.load(f)["groups"]

    # Combine: First 6 groups from p3_b1 (Q32-49), all 7 groups from p3_b2 (Q50-70)
    p3_raw_groups = p3_b1[:6] + p3_b2

    p3_graphics_map = {
        "g62_64": "/images/test2/part3_g62_64.png",
        "g65_67": "/images/test2/part3_g65_67.png",
        "g68_70": "/images/test2/part3_g68_70.png",
    }

    part3_groups = []
    part3_questions = []

    for g in p3_raw_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        g_key = f"g{q_start}_{q_end}"

        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p3-{g_key}"))
        segs = audio_segs.get("part3", {}).get(g_key, [])
        img_url = p3_graphics_map.get(g_key, None)

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 3,
            "passage_text": None,
            "image_url": img_url,
            "audio_url": f"/audio/test2/part3_{g_key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part3_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
            correct_ans = official_answers.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}
            cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 3,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "detail_lookup"),
                "question_text": q.get("question_text"),
                "options": cleaned_opts,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part3_questions.append(question)

    with open(final_dir / f"{slug}_part3.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 3, "total_groups": len(part3_groups), "total_questions": len(part3_questions)},
            "question_groups": part3_groups,
            "questions": part3_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 3: {len(part3_groups)} groups, {len(part3_questions)} questions")
    all_groups.extend(part3_groups)
    all_questions.extend(part3_questions)

    # =========================================================================
    # PART 4: 10 Groups, 30 Questions
    # =========================================================================
    print("[-] Compiling Part 4...")
    with open(batches_dir / "batch_part4_q71_85.json", "r", encoding="utf-8") as f:
        p4_b1 = json.load(f)["groups"]
    with open(batches_dir / "batch_part4_q86_100.json", "r", encoding="utf-8") as f:
        p4_b2 = json.load(f)["groups"]

    p4_raw_groups = p4_b1 + p4_b2

    p4_graphics_map = {
        "g95_97": "/images/test2/part4_g95_97.png",
        "g98_100": "/images/test2/part4_g98_100.png",
    }

    part4_groups = []
    part4_questions = []

    for g in p4_raw_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        g_key = f"g{q_start}_{q_end}"

        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p4-{g_key}"))
        segs = audio_segs.get("part4", {}).get(g_key, [])
        img_url = p4_graphics_map.get(g_key, None)

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 4,
            "passage_text": None,
            "image_url": img_url,
            "audio_url": f"/audio/test2/part4_{g_key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part4_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
            correct_ans = official_answers.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}
            cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 4,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "instruction_action"),
                "question_text": q.get("question_text"),
                "options": cleaned_opts,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part4_questions.append(question)

    with open(final_dir / f"{slug}_part4.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 4, "total_groups": len(part4_groups), "total_questions": len(part4_questions)},
            "question_groups": part4_groups,
            "questions": part4_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 4: {len(part4_groups)} groups, {len(part4_questions)} questions")
    all_groups.extend(part4_groups)
    all_questions.extend(part4_questions)

    # =========================================================================
    # PART 5: 1 Group, 30 Questions
    # =========================================================================
    print("[-] Compiling Part 5...")
    with open(batches_dir / "batch_part5_q101_130.json", "r", encoding="utf-8") as f:
        p5_batch = json.load(f)

    g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p5"))
    part5_group = {
        "id": g_id,
        "test_name": test_name,
        "part": 5,
        "passage_text": None,
        "image_url": None,
        "audio_url": None,
        "transcript_segments": None,
    }
    part5_groups = [part5_group]
    part5_questions = []

    for g in p5_batch["groups"]:
        for q in g["questions"]:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
            correct_ans = official_answers.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}
            cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 5,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "word_form"),
                "question_text": q.get("question_text"),
                "options": cleaned_opts,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part5_questions.append(question)

    with open(final_dir / f"{slug}_part5.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 5, "total_groups": len(part5_groups), "total_questions": len(part5_questions)},
            "question_groups": part5_groups,
            "questions": part5_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 5: {len(part5_groups)} groups, {len(part5_questions)} questions")
    all_groups.extend(part5_groups)
    all_questions.extend(part5_questions)

    # =========================================================================
    # PART 6: 4 Groups, 16 Questions
    # =========================================================================
    print("[-] Compiling Part 6...")
    with open(batches_dir / "batch_part6_q131_146.json", "r", encoding="utf-8") as f:
        p6_batch = json.load(f)

    p6_img_map = {
        "131_134": "/images/test2/part6_131_134.png",
        "135_138": "/images/test2/part6_135_138.png",
        "139_142": "/images/test2/part6_139_142.png",
        "143_146": "/images/test2/part6_143_146.png",
    }

    part6_groups = []
    part6_questions = []

    for g in p6_batch["groups"]:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        range_key = f"{q_start}_{q_end}"
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p6-{range_key}"))

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 6,
            "passage_text": g.get("passage_text"),
            "image_url": p6_img_map.get(range_key),
            "audio_url": None,
            "transcript_segments": None,
        }
        part6_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
            correct_ans = official_answers.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}
            cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 6,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "sentence_insertion"),
                "question_text": q.get("question_text"),
                "options": cleaned_opts,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part6_questions.append(question)

    with open(final_dir / f"{slug}_part6.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 6, "total_groups": len(part6_groups), "total_questions": len(part6_questions)},
            "question_groups": part6_groups,
            "questions": part6_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 6: {len(part6_groups)} groups, {len(part6_questions)} questions")
    all_groups.extend(part6_groups)
    all_questions.extend(part6_questions)

    # =========================================================================
    # PART 7: 15 Groups, 54 Questions
    # =========================================================================
    print("[-] Compiling Part 7...")
    with open(batches_dir / "batch_part7_q147_175.json", "r", encoding="utf-8") as f:
        p7_b1 = json.load(f)["groups"]
    with open(batches_dir / "batch_part7_q176_200.json", "r", encoding="utf-8") as f:
        p7_b2 = json.load(f)["groups"]

    p7_raw_groups = p7_b1 + p7_b2
    normalized_p7_groups = []
    for g in p7_raw_groups:
        qs = g["questions"]
        q_nums = [q["question_number"] for q in qs]
        if 176 in q_nums and 186 in q_nums:
            # Split into 176-180 and 186-190
            qs_176 = [q for q in qs if 176 <= q["question_number"] <= 180]
            qs_186 = [q for q in qs if 186 <= q["question_number"] <= 190]
            normalized_p7_groups.append({"part": 7, "passage_text": g.get("passage_text"), "questions": qs_176})
            normalized_p7_groups.append({"part": 7, "passage_text": g.get("passage_text"), "questions": qs_186})
        else:
            normalized_p7_groups.append(g)

    # Sort groups by starting question number
    normalized_p7_groups.sort(key=lambda x: x["questions"][0]["question_number"])

    part7_groups = []
    part7_questions = []

    for g in normalized_p7_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        range_key = f"{q_start}_{q_end}"
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-p7-{range_key}"))

        img_url = f"/images/test2/part7_{range_key}.png"

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 7,
            "passage_text": g.get("passage_text"),
            "image_url": img_url,
            "audio_url": None,
            "transcript_segments": None,
        }
        part7_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ets2023-test2-q{q_num}"))
            correct_ans = official_answers.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}
            cleaned_opts = {k: v for k, v in raw_opts.items() if v is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 7,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "detail_lookup"),
                "question_text": q.get("question_text"),
                "options": cleaned_opts,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part7_questions.append(question)

    with open(final_dir / f"{slug}_part7.json", "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {"test_name": test_name, "part": 7, "total_groups": len(part7_groups), "total_questions": len(part7_questions)},
            "question_groups": part7_groups,
            "questions": part7_questions,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Part 7: {len(part7_groups)} groups, {len(part7_questions)} questions")
    all_groups.extend(part7_groups)
    all_questions.extend(part7_questions)

    # =========================================================================
    # MASTER MERGE: 74 Groups, Exactly 200 Questions
    # =========================================================================
    full_test_file = final_dir / f"{slug}_full.json"
    full_payload = {
        "metadata": {
            "test_name": test_name,
            "generated_at": "2026-10-31 17:15:00",
            "model_used": "gemini-3.5-flash",
            "total_groups": len(all_groups),
            "total_questions": len(all_questions),
        },
        "question_groups": all_groups,
        "questions": all_questions,
    }

    with open(full_test_file, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*75}")
    print(f"[✓] TEST 2 FULL DATASET COMPILED SUCCESSFULLY!")
    print(f"{'='*75}")
    print(f"  ➔ Total Question Groups: {len(all_groups)} (expected 74)")
    print(f"  ➔ Total Questions      : {len(all_questions)} / 200")
    print(f"  ➔ Master Output File   : {full_test_file.resolve()}")
    print(f"{'='*75}\n")

if __name__ == "__main__":
    compile_test2()
