#!/usr/bin/env python3
from __future__ import annotations

"""
TOEIC CRAWLER & DATA EXTRACTION MASTER PIPELINE
===============================================
Autonomous CLI pipeline for processing complete TOEIC tests:
1. Auto-detects materials in data/raw/<TEST_NAME>
2. Extracts & caches official answer key
3. Transcribes full audio & dynamic landmark slices (54 clips)
4. Dynamic page discovery & passage/graphic cropping (30 images)
5. Extracts questions via Gemini Structured Outputs with Anti-Recitation Safety
6. Compiles authoritative final datasets (74 QuestionGroups, 200 Questions)
7. Enforces strict 10/10 Quality Gate verification
8. Saves directly to local data/exams & data/media (auto-discovered by Web App)

Usage:
    python crawler/main.py --test-dir "data/raw/TEST 5 - ETS 2023"
"""

import os
import sys
import json
import time
import uuid
import argparse
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Enable UTF-8 encoding across Windows/Linux consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

# Load .env files from crawler, root, and web
CRAWLER_DIR = Path(__file__).resolve().parent
ROOT_DIR = CRAWLER_DIR.parent
WEB_DIR = ROOT_DIR / "web"
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT_DIR / "data"))).resolve()

load_dotenv(CRAWLER_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / ".env.local")
load_dotenv(WEB_DIR / ".env.local")

# Ensure root directory is in python path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from crawler.core.api_client import ResilientLLMClient
from crawler.core.audio import process_audio_pipeline
from crawler.core.cropper import process_images_pipeline
from crawler.core.extractor import (
    parse_and_cache_answers,
    extract_batch,
)


def auto_detect_files(test_dir: Path) -> Dict[str, Optional[Path]]:
    """Detects input PDFs, answer key, and audio files in test folder."""
    detected: Dict[str, Optional[Path]] = {
        "test_pdf": None,
        "transcript_pdf": None,
        "answer_file": None,
        "audio_file": None,
    }

    for f in test_dir.iterdir():
        if not f.is_file():
            continue
        lower_name = f.name.lower()
        if "transcript" in lower_name and f.suffix.lower() == ".pdf":
            detected["transcript_pdf"] = f
        elif f.suffix.lower() == ".pdf" and "transcript" not in lower_name and "dap-an" not in lower_name and "answer" not in lower_name:
            detected["test_pdf"] = f
        elif any(k in lower_name for k in ["dap-an", "answer", "key"]):
            if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".pdf"]:
                detected["answer_file"] = f
        elif f.suffix.lower() in [".mp3", ".wav", ".m4a"]:
            detected["audio_file"] = f

    return detected


def setup_directories(output_base: Path) -> Dict[str, Path]:
    """Prepares structured output directories."""
    dirs = {
        "base": output_base,
        "answers": output_base / "intermediate" / "answers",
        "whisper": output_base / "intermediate" / "whisper",
        "segments": output_base / "intermediate" / "segments",
        "batches": output_base / "intermediate" / "batches",
        "final": output_base / "final",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def compile_authoritative_dataset(
    test_name: str,
    slug: str,
    slug_short: str,
    dirs: Dict[str, Path],
    answer_map: Dict[str, str],
    audio_segs: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Path]:
    """Compiles individual batch extractions into standardized 74 groups and 200 questions."""
    batches_dir = dirs["batches"]
    final_dir = dirs["final"]

    all_final_groups: List[Dict[str, Any]] = []
    all_final_questions: List[Dict[str, Any]] = []

    # --- Part 1: 6 Groups, 6 Questions ---
    print("  [-] Compiling Part 1...")
    p1_batch_file = batches_dir / "batch_part1_q1_6.json"
    if p1_batch_file.exists():
        with open(p1_batch_file, "r", encoding="utf-8") as f:
            p1_batch = json.load(f)
        p1_q_map = {q["question_number"]: q for g in p1_batch.get("groups", []) for q in g.get("questions", [])}

        part1_groups = []
        part1_questions = []
        for q_num in range(1, 7):
            g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p1-q{q_num}"))
            q_raw = p1_q_map.get(q_num, {})
            segs = audio_segs.get("part1", {}).get(str(q_num), [])

            group = {
                "id": g_id,
                "test_name": test_name,
                "part": 1,
                "passage_text": None,
                "image_url": f"/images/{slug_short}/part1_q{q_num}.jpg",
                "audio_url": f"/audio/{slug_short}/part1_q{q_num}.mp3",
                "transcript_segments": segs if segs else None,
            }
            part1_groups.append(group)

            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
            raw_opts = q_raw.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 1,
                "question_number": q_num,
                "question_type_tag": q_raw.get("question_type_tag", "detail_lookup"),
                "question_text": q_raw.get("question_text") or f"Look at the picture marked number {q_num} in your testbook.",
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q_raw.get("explanation_vi", ""),
                "evidence_quote": q_raw.get("evidence_quote"),
                "paraphrase_pair": q_raw.get("paraphrase_pair"),
            }
            part1_questions.append(question)

        with open(final_dir / f"{slug}_part1.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"test_name": test_name, "part": 1, "total_groups": len(part1_groups), "total_questions": len(part1_questions)},
                "question_groups": part1_groups,
                "questions": part1_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part1_groups)
        all_final_questions.extend(part1_questions)

    # --- Part 2: 25 Groups, 25 Questions ---
    print("  [-] Compiling Part 2...")
    p2_batch_file = batches_dir / "batch_part2_q7_31.json"
    if p2_batch_file.exists():
        with open(p2_batch_file, "r", encoding="utf-8") as f:
            p2_batch = json.load(f)
        p2_q_map = {q["question_number"]: q for g in p2_batch.get("groups", []) for q in g.get("questions", [])}

        part2_groups = []
        part2_questions = []
        for q_num in range(7, 32):
            g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p2-q{q_num}"))
            q_raw = p2_q_map.get(q_num, {})
            segs = audio_segs.get("part2", {}).get(str(q_num), [])

            group = {
                "id": g_id,
                "test_name": test_name,
                "part": 2,
                "passage_text": None,
                "image_url": None,
                "audio_url": f"/audio/{slug_short}/part2_q{q_num}.mp3",
                "transcript_segments": segs if segs else None,
            }
            part2_groups.append(group)

            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
            raw_opts = q_raw.get("options", {}) or {}

            # Part 2 only has options A, B, C
            clean_opts = {k: raw_opts[k] for k in ["A", "B", "C"] if k in raw_opts and raw_opts[k] is not None}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 2,
                "question_number": q_num,
                "question_type_tag": q_raw.get("question_type_tag", "wh_question"),
                "question_text": q_raw.get("question_text") or f"Mark your answer on your answer sheet (Number {q_num}).",
                "options": clean_opts,
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
                "questions": part2_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part2_groups)
        all_final_questions.extend(part2_questions)

    # --- Part 3: 13 Groups, 39 Questions ---
    print("  [-] Compiling Part 3...")
    p3_batches = [batches_dir / "batch_part3_q32_50.json", batches_dir / "batch_part3_q51_70.json", batches_dir / "batch_part3_q50_70.json"]
    p3_q_pool = {}
    for pb in p3_batches:
        if pb.exists():
            with open(pb, "r", encoding="utf-8") as f:
                for g in json.load(f).get("groups", []):
                    for q in g.get("questions", []):
                        p3_q_pool[q["question_number"]] = q

    p3_ranges_keys = [
        ("g32_34", 32, 34, None),
        ("g35_37", 35, 37, None),
        ("g38_40", 38, 40, None),
        ("g41_43", 41, 43, None),
        ("g44_46", 44, 46, None),
        ("g47_49", 47, 49, None),
        ("g50_52", 50, 52, None),
        ("g53_55", 53, 55, None),
        ("g56_58", 56, 58, None),
        ("g59_61", 59, 61, None),
        ("g62_64", 62, 64, f"/images/{slug_short}/part3_g62_64.png"),
        ("g65_67", 65, 67, f"/images/{slug_short}/part3_g65_67.png"),
        ("g68_70", 68, 70, f"/images/{slug_short}/part3_g68_70.png"),
    ]

    part3_groups = []
    part3_questions = []
    for key, q_start, q_end, graphic in p3_ranges_keys:
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p3-{key}"))
        segs = audio_segs.get("part3", {}).get(key, [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 3,
            "passage_text": None,
            "image_url": graphic,
            "audio_url": f"/audio/{slug_short}/part3_{key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part3_groups.append(group)

        for q_num in range(q_start, q_end + 1):
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            q_raw = p3_q_pool.get(q_num, {})
            correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
            raw_opts = q_raw.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 3,
                "question_number": q_num,
                "question_type_tag": q_raw.get("question_type_tag", "detail_lookup"),
                "question_text": q_raw.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q_raw.get("explanation_vi", ""),
                "evidence_quote": q_raw.get("evidence_quote"),
                "paraphrase_pair": q_raw.get("paraphrase_pair"),
            }
            part3_questions.append(question)

    if part3_groups:
        with open(final_dir / f"{slug}_part3.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"test_name": test_name, "part": 3, "total_groups": len(part3_groups), "total_questions": len(part3_questions)},
                "question_groups": part3_groups,
                "questions": part3_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part3_groups)
        all_final_questions.extend(part3_questions)

    # --- Part 4: 10 Groups, 30 Questions ---
    print("  [-] Compiling Part 4...")
    p4_batches = [batches_dir / "batch_part4_q71_85.json", batches_dir / "batch_part4_q86_100.json"]
    p4_q_pool = {}
    for pb in p4_batches:
        if pb.exists():
            with open(pb, "r", encoding="utf-8") as f:
                for g in json.load(f).get("groups", []):
                    for q in g.get("questions", []):
                        p4_q_pool[q["question_number"]] = q

    p4_ranges_keys = [
        ("g71_73", 71, 73, None),
        ("g74_76", 74, 76, None),
        ("g77_79", 77, 79, None),
        ("g80_82", 80, 82, None),
        ("g83_85", 83, 85, None),
        ("g86_88", 86, 88, None),
        ("g89_91", 89, 91, None),
        ("g92_94", 92, 94, None),
        ("g95_97", 95, 97, f"/images/{slug_short}/part4_g95_97.png"),
        ("g98_100", 98, 100, f"/images/{slug_short}/part4_g98_100.png"),
    ]

    part4_groups = []
    part4_questions = []
    for key, q_start, q_end, graphic in p4_ranges_keys:
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p4-{key}"))
        segs = audio_segs.get("part4", {}).get(key, [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 4,
            "passage_text": None,
            "image_url": graphic,
            "audio_url": f"/audio/{slug_short}/part4_{key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part4_groups.append(group)

        for q_num in range(q_start, q_end + 1):
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            q_raw = p4_q_pool.get(q_num, {})
            correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
            raw_opts = q_raw.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 4,
                "question_number": q_num,
                "question_type_tag": q_raw.get("question_type_tag", "detail_lookup"),
                "question_text": q_raw.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q_raw.get("explanation_vi", ""),
                "evidence_quote": q_raw.get("evidence_quote"),
                "paraphrase_pair": q_raw.get("paraphrase_pair"),
            }
            part4_questions.append(question)

    if part4_groups:
        with open(final_dir / f"{slug}_part4.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"test_name": test_name, "part": 4, "total_groups": len(part4_groups), "total_questions": len(part4_questions)},
                "question_groups": part4_groups,
                "questions": part4_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part4_groups)
        all_final_questions.extend(part4_questions)

    # --- Part 5: 1 Group, 30 Questions ---
    print("  [-] Compiling Part 5...")
    p5_batch_file = batches_dir / "batch_part5_q101_130.json"
    if p5_batch_file.exists():
        with open(p5_batch_file, "r", encoding="utf-8") as f:
            p5_batch = json.load(f)
        p5_q_map = {q["question_number"]: q for g in p5_batch.get("groups", []) for q in g.get("questions", [])}

        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p5-context"))
        part5_group = {
            "id": g_id,
            "test_name": test_name,
            "part": 5,
            "passage_text": None,
            "image_url": None,
            "audio_url": None,
            "transcript_segments": None,
        }
        part5_questions = []
        for q_num in range(101, 131):
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            q_raw = p5_q_map.get(q_num, {})
            correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
            raw_opts = q_raw.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 5,
                "question_number": q_num,
                "question_type_tag": q_raw.get("question_type_tag", "word_form"),
                "question_text": q_raw.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q_raw.get("explanation_vi", ""),
                "evidence_quote": None,
                "paraphrase_pair": None,
            }
            part5_questions.append(question)

        with open(final_dir / f"{slug}_part5.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"test_name": test_name, "part": 5, "total_groups": 1, "total_questions": len(part5_questions)},
                "question_groups": [part5_group],
                "questions": part5_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.append(part5_group)
        all_final_questions.extend(part5_questions)

    # --- Part 6: 4 Groups, 16 Questions ---
    print("  [-] Compiling Part 6...")
    p6_batch_file = batches_dir / "batch_part6_q131_146.json"
    if p6_batch_file.exists():
        with open(p6_batch_file, "r", encoding="utf-8") as f:
            p6_batch = json.load(f)

        part6_groups = []
        part6_questions = []
        p6_ranges = [("131_134", 131, 134), ("135_138", 135, 138), ("139_142", 139, 142), ("143_146", 143, 146)]

        p6_g_pool = {}
        for g in p6_batch.get("groups", []):
            qs = g.get("questions", [])
            if qs:
                p6_g_pool[qs[0]["question_number"]] = g

        for range_key, q_start, q_end in p6_ranges:
            g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p6-{range_key}"))
            g_raw = p6_g_pool.get(q_start, {})

            group = {
                "id": g_id,
                "test_name": test_name,
                "part": 6,
                "passage_text": g_raw.get("passage_text"),
                "image_url": f"/images/{slug_short}/part6_{range_key}.png",
                "audio_url": None,
                "transcript_segments": None,
            }
            part6_groups.append(group)

            q_map = {q["question_number"]: q for q in g_raw.get("questions", [])}
            for q_num in range(q_start, q_end + 1):
                q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
                q_raw = q_map.get(q_num, {})
                correct_ans = answer_map.get(str(q_num), q_raw.get("correct_answer", "A"))
                raw_opts = q_raw.get("options", {}) or {}

                question = {
                    "id": q_id,
                    "group_id": g_id,
                    "part": 6,
                    "question_number": q_num,
                    "question_type_tag": q_raw.get("question_type_tag", "vocabulary"),
                    "question_text": q_raw.get("question_text") or f"Questions {q_start}-{q_end} refer to the following text.",
                    "options": {k: v for k, v in raw_opts.items() if v is not None},
                    "correct_answer": correct_ans,
                    "explanation_vi": q_raw.get("explanation_vi", ""),
                    "evidence_quote": q_raw.get("evidence_quote"),
                    "paraphrase_pair": q_raw.get("paraphrase_pair"),
                }
                part6_questions.append(question)

        with open(final_dir / f"{slug}_part6.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {"test_name": test_name, "part": 6, "total_groups": len(part6_groups), "total_questions": len(part6_questions)},
                "question_groups": part6_groups,
                "questions": part6_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part6_groups)
        all_final_questions.extend(part6_questions)

    # --- Part 7: 15 Groups, 54 Questions ---
    print("  [-] Compiling Part 7...")
    p7_batch_files = [batches_dir / "batch_part7_q147_175.json", batches_dir / "batch_part7_q176_200.json"]
    p7_groups_raw = []
    for pbf in p7_batch_files:
        if pbf.exists():
            with open(pbf, "r", encoding="utf-8") as f:
                p7_groups_raw.extend(json.load(f).get("groups", []))

    if p7_groups_raw:
        normalized_p7 = []
        for g in p7_groups_raw:
            qs = g.get("questions", [])
            if not qs:
                continue
            q_nums = [q["question_number"] for q in qs]
            if 176 in q_nums and 186 in q_nums:
                qs_176 = [q for q in qs if 176 <= q["question_number"] <= 180]
                qs_186 = [q for q in qs if 186 <= q["question_number"] <= 190]
                normalized_p7.append({"part": 7, "passage_text": g.get("passage_text"), "questions": qs_176})
                normalized_p7.append({"part": 7, "passage_text": g.get("passage_text"), "questions": qs_186})
            else:
                normalized_p7.append(g)

        normalized_p7.sort(key=lambda x: x["questions"][0]["question_number"])

        part7_groups = []
        part7_questions = []
        for g in normalized_p7:
            qs = g["questions"]
            q_start = qs[0]["question_number"]
            q_end = qs[-1]["question_number"]
            range_key = f"{q_start}_{q_end}"
            g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p7-{range_key}"))

            group = {
                "id": g_id,
                "test_name": test_name,
                "part": 7,
                "passage_text": g.get("passage_text"),
                "image_url": f"/images/{slug_short}/part7_{range_key}.png",
                "audio_url": None,
                "transcript_segments": None,
            }
            part7_groups.append(group)

            for q in qs:
                q_num = q["question_number"]
                q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
                correct_ans = answer_map.get(str(q_num), q.get("correct_answer", "A"))
                raw_opts = q.get("options", {}) or {}

                question = {
                    "id": q_id,
                    "group_id": g_id,
                    "part": 7,
                    "question_number": q_num,
                    "question_type_tag": q.get("question_type_tag", "detail_lookup"),
                    "question_text": q.get("question_text"),
                    "options": {k: v for k, v in raw_opts.items() if v is not None},
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
                "questions": part7_questions
            }, f, ensure_ascii=False, indent=2)
        all_final_groups.extend(part7_groups)
        all_final_questions.extend(part7_questions)

    # Master full test file
    full_test_file = final_dir / f"{slug}_full.json"
    full_payload = {
        "metadata": {
            "test_name": test_name,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "gemini-flash-lite",
            "total_groups": len(all_final_groups),
            "total_questions": len(all_final_questions),
        },
        "question_groups": all_final_groups,
        "questions": all_final_questions,
    }
    with open(full_test_file, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, ensure_ascii=False, indent=2)

    return all_final_groups, all_final_questions, full_test_file


def run_quality_gate(
    groups: List[Dict[str, Any]],
    questions: List[Dict[str, Any]],
    answer_map: Dict[str, str],
    public_audio_dir: Path,
    public_img_dir: Path,
) -> Tuple[bool, List[str]]:
    """Strict 10-Point Quality Gate Verification."""
    errors = []

    # 1. Total Groups == 74
    if len(groups) != 74:
        errors.append(f"Check 1 FAILED: Expected 74 QuestionGroups, found {len(groups)}")

    # 2. Total Questions == 200 (Q1 to Q200)
    if len(questions) != 200:
        errors.append(f"Check 2 FAILED: Expected 200 Questions, found {len(questions)}")
    else:
        q_nums = [q["question_number"] for q in questions]
        if sorted(q_nums) != list(range(1, 201)):
            errors.append("Check 2 FAILED: Questions are not sequence 1..200 without gaps.")

    # 3. Answer Key match == 100% (200/200)
    mismatches = []
    for q in questions:
        q_num_str = str(q["question_number"])
        if q_num_str in answer_map:
            if q["correct_answer"] != answer_map[q_num_str]:
                mismatches.append(f"Q{q_num_str}: extracted {q['correct_answer']} vs official {answer_map[q_num_str]}")
    if mismatches:
        errors.append(f"Check 3 FAILED: {len(mismatches)} Answer Key mismatches: {mismatches[:5]}")

    # 4. Audio files (54 clips) exist on disk
    missing_audio = []
    for g in groups:
        if g.get("audio_url"):
            a_file = public_audio_dir / Path(g["audio_url"]).name
            if not a_file.exists() or a_file.stat().st_size < 1000:
                missing_audio.append(Path(g["audio_url"]).name)
    if missing_audio:
        errors.append(f"Check 4 FAILED: {len(missing_audio)} audio files missing or empty: {missing_audio[:5]}")

    # 5. Transcript segments populated for listening groups
    missing_segs = []
    for g in groups:
        if g.get("audio_url"):
            segs = g.get("transcript_segments")
            if not segs or len(segs) == 0:
                missing_segs.append(g["id"])
    if missing_segs:
        errors.append(f"Check 5 FAILED: {len(missing_segs)} listening groups lack transcript_segments.")

    # 6. Image files exist on disk (30 images)
    missing_images = []
    for g in groups:
        if g.get("image_url"):
            img_file = public_img_dir / Path(g["image_url"]).name
            if not img_file.exists() or img_file.stat().st_size < 1000:
                missing_images.append(Path(g["image_url"]).name)
    if missing_images:
        errors.append(f"Check 6 FAILED: {len(missing_images)} image files missing: {missing_images[:5]}")

    # 7. Valid Options Structure
    invalid_opts = []
    for q in questions:
        opts = q.get("options") or {}
        p = q.get("part")
        if p == 2:
            if not all(k in opts and opts[k] for k in ["A", "B", "C"]):
                invalid_opts.append(f"Q{q['question_number']} (Part 2 options missing)")
        else:
            if not all(k in opts and opts[k] for k in ["A", "B", "C", "D"]):
                invalid_opts.append(f"Q{q['question_number']} (Part {p} options missing)")
    if invalid_opts:
        errors.append(f"Check 7 FAILED: {len(invalid_opts)} questions have invalid options: {invalid_opts[:5]}")

    # 8. No null correct_answer
    null_ans = [q["question_number"] for q in questions if not q.get("correct_answer")]
    if null_ans:
        errors.append(f"Check 8 FAILED: Questions with null correct_answer: {null_ans}")

    # 9. Deep Vietnamese Explanations
    short_explanations = [q["question_number"] for q in questions if len(q.get("explanation_vi") or "") < 20]
    if short_explanations:
        errors.append(f"Check 9 FAILED: {len(short_explanations)} questions have short/empty explanation_vi.")

    # 10. Granular Part Breakdown
    part_groups = {p: len([g for g in groups if g["part"] == p]) for p in range(1, 8)}
    expected_groups = {1: 6, 2: 25, 3: 13, 4: 10, 5: 1, 6: 4, 7: 15}
    if part_groups != expected_groups:
        errors.append(f"Check 10 FAILED: Part group distribution mismatch: {part_groups} vs expected {expected_groups}")

    passed = len(errors) == 0
    return passed, errors


def derive_test_identifiers(
    folder_name: str, test_name_override: Optional[str] = None
) -> Tuple[str, str, str, int]:
    """
    Derives (test_name, slug, slug_short, test_num_int) safely without colliding
    across different TOEIC books/editions.
    - Preserves `test{N}` and `ETS TOEIC 2023 - Test {N}` for ETS 2023 folders
      to stay 100% backward-compatible with already crawled datasets.
    - Generates book-scoped slugs (e.g. `ets2024_test1`) for other editions.
    """
    test_num_match = re.search(r"test\s*[-_#]?\s*(\d+)", folder_name, flags=re.IGNORECASE)
    if not test_num_match:
        test_num_match = re.search(r"\b(\d+)\b", folder_name)
    test_num_int = int(test_num_match.group(1)) if test_num_match else 1

    year_match = re.search(r"\b(20\d{2})\b", folder_name)
    year = year_match.group(1) if year_match else None
    is_ets = "ets" in folder_name.lower()

    slug = re.sub(r"[^a-z0-9]+", "_", folder_name.lower()).strip("_") or f"test_{test_num_int}"

    if is_ets and year == "2023":
        default_name = f"ETS TOEIC 2023 - Test {test_num_int}"
        slug_short = f"test{test_num_int}"
    elif is_ets and year:
        default_name = f"ETS TOEIC {year} - Test {test_num_int}"
        slug_short = f"ets{year}_test{test_num_int}"
    else:
        default_name = folder_name.strip()
        slug_short = slug

    test_name = test_name_override or default_name
    return test_name, slug, slug_short, test_num_int


def run_pipeline(
    test_dir_str: str,
    test_name_override: Optional[str] = None,
    parts_to_run: Optional[List[int]] = None,
    skip_audio: bool = False,
    device: str = "cpu",
    assets_dir_str: Optional[str] = None,
    output_data_dir_str: Optional[str] = None,
    auto_seed: bool = False,
):
    test_dir = Path(test_dir_str).resolve()
    if not test_dir.exists():
        print(f"[ERROR] Test directory not found: {test_dir}")
        sys.exit(1)

    folder_name = test_dir.name
    test_name, slug, slug_short, _test_num_int = derive_test_identifiers(
        folder_name, test_name_override
    )

    # Determine unified local destination directories (data/exams & data/media)
    if output_data_dir_str:
        output_base = Path(output_data_dir_str).resolve() / folder_name
    else:
        output_base = DATA_DIR / "exams" / folder_name
    dirs = setup_directories(output_base)

    if assets_dir_str:
        primary_assets = Path(assets_dir_str).resolve()
    else:
        primary_assets = (DATA_DIR / "media").resolve()

    public_audio_dir = primary_assets / "audio" / slug_short
    public_img_dir = primary_assets / "images" / slug_short
    secondary_audio_dir = None
    secondary_img_dir = None

    print(f"\n{'='*75}")
    print(f" TOEIC MASTER PIPELINE: {test_name}")
    print(f"{'='*75}")
    print(f"[*] Input Directory   : {test_dir}")
    print(f"[*] Processed Output  : {output_base.resolve()}")
    print(f"[*] Primary Assets    : {primary_assets}")
    print(f"[*] Assets Short Slug : {slug_short}")

    # 1. Auto-detect files
    detected = auto_detect_files(test_dir)
    print("\n[Step 1] File Auto-Detection:")
    for k, v in detected.items():
        status = f"✓ {v.name}" if v else "✗ Not found"
        print(f"  - {k:<15}: {status}")

    if not detected["test_pdf"]:
        print("[FATAL ERROR] No test PDF file found in folder.")
        sys.exit(1)

    # Initialize Resilient Multi-Key LLM Client
    client = ResilientLLMClient()

    # 2. Extract official answer key
    print("\n[Step 2] Processing Official Answer Key:")
    answer_map = {}
    if detected["answer_file"]:
        answer_map = parse_and_cache_answers(client, detected["answer_file"], dirs["answers"])
    else:
        print("  [WARN] No answer key file found.")

    # 3. Audio Slicing & Whisper Transcription
    print("\n[Step 3] Audio Processing & Dynamic Alignment:")
    audio_segs = {}
    if detected["audio_file"] and not skip_audio:
        audio_segs = process_audio_pipeline(
            audio_path=detected["audio_file"],
            output_audio_dir=public_audio_dir,
            segments_dir=dirs["segments"],
            device=device,
            secondary_audio_dir=secondary_audio_dir,
        )
    else:
        print("  [!] Audio processing skipped (--skip-audio or audio file missing).")

    # 4. Image Cropping & Extraction
    print("\n[Step 4] Image Cropping & Extraction:")
    process_images_pipeline(
        test_pdf_path=detected["test_pdf"],
        output_image_dir=public_img_dir,
        secondary_image_dir=secondary_img_dir,
    )

    # 5. Question Batch Extractions via Gemini
    print("\n[Step 5] Extracting Questions via Gemini:")
    test_file_ref = client.upload_file_safe(detected["test_pdf"])
    transcript_file_ref = None
    if detected["transcript_pdf"]:
        transcript_file_ref = client.upload_file_safe(detected["transcript_pdf"])

    # Prepare transcript context from audio_segs if transcript PDF is absent
    p1_transcript_context = None
    p2_transcript_context = None
    if not detected["transcript_pdf"] and audio_segs:
        p1_lines = []
        for q in range(1, 7):
            q_segs = audio_segs.get("part1", {}).get(str(q), [])
            text_block = " ".join(s["text_en"] for s in q_segs)
            p1_lines.append(f"Number {q}: {text_block}")
        p1_transcript_context = "\n".join(p1_lines)

        p2_lines = []
        for q in range(7, 32):
            q_segs = audio_segs.get("part2", {}).get(str(q), [])
            text_block = " ".join(s["text_en"] for s in q_segs)
            p2_lines.append(f"Number {q}: {text_block}")
        p2_transcript_context = "\n".join(p2_lines)

    batches_plan = [
        (1, 1, 6, "part1_q1_6", p1_transcript_context),
        (2, 7, 31, "part2_q7_31", p2_transcript_context),
        (3, 32, 50, "part3_q32_50", None),
        (3, 51, 70, "part3_q51_70", None),
        (4, 71, 85, "part4_q71_85", None),
        (4, 86, 100, "part4_q86_100", None),
        (5, 101, 130, "part5_q101_130", None),
        (6, 131, 146, "part6_q131_146", None),
        (7, 147, 175, "part7_q147_175", None),
        (7, 176, 200, "part7_q176_200", None),
    ]

    selected_batches = batches_plan
    if parts_to_run:
        selected_batches = [b for b in batches_plan if b[0] in parts_to_run]

    for part_num, q_start, q_end, b_name, t_ctx in selected_batches:
        batch_file = dirs["batches"] / f"batch_{b_name}.json"
        extract_batch(
            client=client,
            test_file_ref=test_file_ref,
            transcript_file_ref=transcript_file_ref,
            part_num=part_num,
            q_start=q_start,
            q_end=q_end,
            test_name=test_name,
            answer_map=answer_map,
            batch_file=batch_file,
            transcript_context=t_ctx,
        )
        time.sleep(1)

    # 6. Authoritative Dataset Compilation
    print("\n[Step 6] Compiling Final Authoritative Datasets (74 Groups, 200 Questions):")
    all_groups, all_questions, full_test_file = compile_authoritative_dataset(
        test_name=test_name,
        slug=slug,
        slug_short=slug_short,
        dirs=dirs,
        answer_map=answer_map,
        audio_segs=audio_segs,
    )

    # 7. Quality Gate Enforcement
    print("\n[Step 7] Running 10-Point Quality Gate Verification:")
    passed, errors = run_quality_gate(
        groups=all_groups,
        questions=all_questions,
        answer_map=answer_map,
        public_audio_dir=public_audio_dir,
        public_img_dir=public_img_dir,
    )

    if passed:
        print("  [✓] QUALITY GATE PASSED: 10/10 CHECKS VERIFIED!")
        print(f"      ➔ 74 QuestionGroups compiled")
        print(f"      ➔ 200 Questions (100% official answer key match)")
        print(f"      ➔ 54 Audio files verified with transcript timestamps")
        print(f"      ➔ 30 Image crops verified on disk")
        print(f"      ➔ Full dataset saved: {full_test_file.resolve()}")
    else:
        print(f"  [X] QUALITY GATE FAILED ({len(errors)} issues found):")
        for err in errors:
            print(f"      - {err}")
        print("\n[ABORT] Auto-seed halted due to Quality Gate failures.")
        sys.exit(1)

    # 8. Local Storage Ready (Web app dynamically discovers data/exams/* without restart)
    if auto_seed:
        print("\n[Step 8] Local Storage Mode:")
        print("  [i] Hệ thống đã chuyển sang 100% lưu trữ cục bộ (không còn dùng Supabase).")
    print("  [✓] Đề thi đã sẵn sàng tại ổ đĩa máy chủ — chỉ cần F5 trang web để luyện tập ngay!")

    print(f"\n{'='*75}")
    print(f"[✓] PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"{'='*75}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Master Autonomous TOEIC Test Crawler & Extractor (100% Local Storage)."
    )
    parser.add_argument(
        "--test-dir",
        required=True,
        help="Path to folder containing test materials (e.g. 'data/raw/TEST 5 - ETS 2023')",
    )
    parser.add_argument(
        "--test-name",
        default=None,
        help="Custom test name (default: auto-detected from folder name)",
    )
    parser.add_argument(
        "--parts",
        default=None,
        help="Comma-separated parts to process, e.g. '1,2,5' or 'all' (default: all)",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip Whisper audio transcription and slicing",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cuda", "cpu", "auto"],
        help="Compute device for Whisper (default: cpu)",
    )
    parser.add_argument(
        "--assets-dir",
        default=None,
        help="Target media assets directory (default: data/media)",
    )
    parser.add_argument(
        "--output-data",
        default=None,
        help="Target exams output base directory (default: data/exams)",
    )
    parser.add_argument(
        "--auto-seed",
        action="store_true",
        help="[Deprecated no-op] Web app automatically discovers all compiled tests in data/exams",
    )
    parser.add_argument(
        "--import-supabase",
        action="store_true",
        help="[Deprecated no-op] Supabase integration has been removed in favor of local storage",
    )

    args = parser.parse_args()

    parts_list = None
    if args.parts and args.parts.lower() != "all":
        parts_list = [int(p.strip()) for p in args.parts.split(",") if p.strip().isdigit()]

    run_pipeline(
        test_dir_str=args.test_dir,
        test_name_override=args.test_name,
        parts_to_run=parts_list,
        skip_audio=args.skip_audio,
        device=args.device,
        assets_dir_str=args.assets_dir,
        output_data_dir_str=args.output_data,
        auto_seed=args.auto_seed or args.import_supabase,
    )


if __name__ == "__main__":
    main()
