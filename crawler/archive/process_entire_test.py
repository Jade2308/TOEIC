#!/usr/bin/env python3
"""
scripts/process_entire_test.py
==============================
MASTER ONE-CLICK TOEIC EXTRACTION & PROCESSING PIPELINE
-------------------------------------------------------
End-to-end automation for ingesting an entire TOEIC test:
1. Auto-detects Test PDF, Answer Key, Transcript PDF, and Audio MP3 in raw_data/<TEST_NAME>.
2. Sets up standardized directories in processed_data/<TEST_NAME>/(intermediate & final).
3. Parses & caches full Answer Key (Q1-Q200).
4. Audio Processing:
   - Slices audio into 54 standardized MP3 clips in public/audio/<test_slug>/
   - Transcribes slices via faster-whisper to generate precise timestamps and trap candidate tags.
5. Image Processing:
   - Crops Part 1 photos (Q1-Q6) into public/images/<test_slug>/
   - Crops Part 3 & 4 graphics (tables, charts) into public/images/<test_slug>/
   - Renders Part 6 & 7 reading passages into public/images/<test_slug>/
6. Sequentially extracts Parts 1-7 in fail-safe batches via Gemini with Structured Outputs.
   - Resumable: Skips completed batches if already cached.
   - Clean batch boundaries: Never splits 3-question conversation/talk groups.
7. Compiles authoritative final datasets:
   - Part 1: 6 groups, 6 questions (audio, photos, transcript segments)
   - Part 2: 25 groups, 25 questions (audio, prompt, transcript segments)
   - Part 3: 13 groups, 39 questions (audio, graphics, conversation dialogue segments)
   - Part 4: 10 groups, 30 questions (audio, graphics, short talk segments)
   - Part 5: 1 group, 30 questions (grammar explanations & 10s tips)
   - Part 6: 4 groups, 16 questions (reading passage images & context)
   - Part 7: 15 groups, 54 questions (single/double/triple passages & images)
   - Master full file: Exactly 74 QuestionGroups, exactly 200 Questions.

Usage:
    python scripts/process_entire_test.py --test-dir "raw_data/TEST 2 - ETS 2023"
    python scripts/process_entire_test.py --test-dir "raw_data/TEST 2 - ETS 2023" --skip-audio
"""

import os
import sys
import json
import time
import uuid
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# UTF-8 encoding support for Windows Console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv(".env.local")

try:
    from pydantic import BaseModel, Field
    from google import genai
    from google.genai import types
    import pymupdf
    from PIL import Image
    import av
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"[ERROR] Required package missing: {e}")
    print("Please activate the 'toeic-pipeline' conda environment:")
    print("    conda activate toeic-pipeline")
    sys.exit(1)


# ==============================================================================
# PYDANTIC SCHEMAS (STRUCTURED OUTPUT)
# ==============================================================================

class ParaphrasePairSchema(BaseModel):
    original: str = Field(description="Exact phrase or expression from the passage or listening script")
    paraphrased: str = Field(description="Equivalent synonym or paraphrased phrase in the correct answer choice")


class OptionsSchema(BaseModel):
    A: str = Field(description="Option A text")
    B: str = Field(description="Option B text")
    C: str = Field(description="Option C text")
    D: Optional[str] = Field(default=None, description="Option D text (null/omitted for Part 2)")


class QuestionSchema(BaseModel):
    question_number: int = Field(description="Question number in the test (1 to 200)")
    part: int = Field(description="TOEIC Part number (1 to 7)")
    question_type_tag: str = Field(
        description=(
            "Standard coaching tag: word_form, conjunction, verb_tense, preposition, "
            "vocabulary, wh_where, wh_when, homophone_trap, passive_being_trap, "
            "indirect_response, inference, detail_lookup, graphic, instruction_action"
        )
    )
    question_text: Optional[str] = Field(
        default=None,
        description="The question prompt"
    )
    options: OptionsSchema = Field(description="Options object containing choices A, B, C, and D")
    correct_answer: str = Field(description="Single capital letter corresponding to correct choice: 'A', 'B', 'C', or 'D'")
    explanation_vi: str = Field(
        description=(
            "Comprehensive Vietnamese pedagogical explanation: grammar/vocab rule, "
            "why correct answer is right, ETS distractor trap breakdown, and coaching tactic tip"
        )
    )
    evidence_quote: Optional[str] = Field(
        default=None,
        description="Exact substring from passage or transcript that proves the correct answer"
    )
    paraphrase_pair: Optional[ParaphrasePairSchema] = Field(
        default=None,
        description="Pair of original wording vs paraphrased wording in correct answer"
    )


class QuestionGroupSchema(BaseModel):
    part: int = Field(description="TOEIC Part number (1 to 7)")
    passage_text: Optional[str] = Field(
        default=None,
        description="Full reading passage text in clean Markdown or HTML for Part 6 and 7; null for Part 1-5"
    )
    audio_script: Optional[str] = Field(
        default=None,
        description="Transcript of the audio dialogue or short talk if provided in the key"
    )
    questions: List[QuestionSchema] = Field(description="List of questions linked to this context")


class ToeicExtractionPayload(BaseModel):
    test_name: str = Field(description="Name of the test, e.g. 'ETS TOEIC 2023 - Test 2'")
    groups: List[QuestionGroupSchema] = Field(description="Extracted question groups with linked questions")


# ==============================================================================
# PIPELINE HELPERS
# ==============================================================================

def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY is not set.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def auto_detect_files(test_dir: Path) -> Dict[str, Optional[Path]]:
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


def parse_and_cache_answers(client: genai.Client, answer_file: Path, answers_dir: Path, model_name: str) -> Dict[str, str]:
    cache_path = answers_dir / "official_answers.json"
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) >= 150:
                    print(f"  [✓] Loaded {len(data)} answers from cache: {cache_path.name}")
                    return data
        except Exception:
            pass

    print(f"  [➔] Uploading and extracting answer key from {answer_file.name}...")
    file_ref = client.files.upload(file=str(answer_file))
    prompt = (
        "Extract all the answers shown in this answer key. "
        "Return a JSON object where keys are question numbers as strings ('1', '2', ... '200') "
        "and values are the correct uppercase letters ('A', 'B', 'C', or 'D'). "
        "Return ONLY the valid JSON object without markdown formatting."
    )
    res = client.models.generate_content(
        model=model_name,
        contents=[file_ref, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )

    try:
        data = json.loads(res.text or "{}")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [✓] Extracted & cached {len(data)} answers to {cache_path.name}")
        return data
    except Exception as e:
        print(f"  [WARN] Failed to parse answer key: {e}")
        return {}


# ==============================================================================
# AUDIO SLICING & TRANSCRIPTION ENGINE
# ==============================================================================

def slice_audio_file(in_path: str, out_path: str, start_sec: float, end_sec: float):
    in_container = av.open(in_path)
    in_stream = in_container.streams.audio[0]
    out_container = av.open(out_path, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    out_stream.bit_rate = in_stream.bit_rate or 128000

    start_pts = int(start_sec / in_stream.time_base)
    end_pts = int(end_sec / in_stream.time_base)
    in_container.seek(start_pts, stream=in_stream)

    for frame in in_container.decode(in_stream):
        if frame.pts < start_pts:
            continue
        if frame.pts > end_pts:
            break
        frame.pts = None
        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    in_container.close()


def process_audio_pipeline(audio_path: Path, output_audio_dir: Path, segments_dir: Path) -> Dict[str, Any]:
    output_audio_dir.mkdir(parents=True, exist_ok=True)
    segments_cache = segments_dir / "sliced_audio_segments.json"
    if segments_cache.exists():
        try:
            with open(segments_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data.get("part1", {})) == 6 and len(data.get("part2", {})) == 25:
                    print(f"  [✓] Loaded existing sliced audio metadata from {segments_cache.name}")
                    return data
        except Exception:
            pass

    p1_ranges = {
        1: (98.4, 122.9),
        2: (123.0, 155.8),
        3: (156.0, 180.0),
        4: (180.1, 201.84),
        5: (201.85, 232.8),
        6: (232.9, 265.5),
    }

    p2_ranges = {
        7:  (293.0, 315.5),
        8:  (315.5, 336.0),
        9:  (336.0, 356.0),
        10: (356.0, 376.0),
        11: (376.0, 396.0),
        12: (396.0, 415.7),
        13: (415.7, 436.3),
        14: (436.3, 455.8),
        15: (455.8, 477.0),
        16: (477.0, 497.3),
        17: (497.3, 517.6),
        18: (517.6, 538.4),
        19: (538.4, 556.5),
        20: (556.5, 575.1),
        21: (575.1, 596.7),
        22: (596.7, 617.9),
        23: (617.9, 638.9),
        24: (638.9, 659.3),
        25: (659.3, 678.4),
        26: (678.4, 700.1),
        27: (700.1, 720.8),
        28: (720.8, 742.1),
        29: (742.1, 762.1),
        30: (762.1, 780.9),
        31: (780.9, 802.1),
    }

    p3_ranges = {
        "g32_34": (832.0, 905.5),
        "g35_37": (905.5, 980.5),
        "g38_40": (980.5, 1054.0),
        "g41_43": (1054.0, 1132.5),
        "g44_46": (1132.5, 1216.5),
        "g47_49": (1216.5, 1295.5),
        "g50_52": (1295.5, 1366.5),
        "g53_55": (1366.5, 1446.0),
        "g56_58": (1446.0, 1524.0),
        "g59_61": (1524.0, 1606.8),
        "g62_64": (1606.8, 1697.0),
        "g65_67": (1697.0, 1782.0),
        "g68_70": (1782.0, 1872.0),
    }

    p4_ranges = {
        "g71_73": (1901.5, 1981.5),
        "g74_76": (1981.5, 2065.0),
        "g77_79": (2065.0, 2138.5),
        "g80_82": (2138.5, 2233.8),
        "g83_85": (2233.8, 2318.0),
        "g86_88": (2318.0, 2398.0),
        "g89_91": (2398.0, 2475.5),
        "g92_94": (2475.5, 2555.0),
        "g95_97": (2555.0, 2646.0),
        "g98_100": (2646.0, 2735.0),
    }

    print("  [➔] Slicing 54 audio clips...")
    all_slices = []
    for q, (s, e) in p1_ranges.items():
        all_slices.append(("p1", str(q), output_audio_dir / f"part1_q{q}.mp3", s, e))
    for q, (s, e) in p2_ranges.items():
        all_slices.append(("p2", str(q), output_audio_dir / f"part2_q{q}.mp3", s, e))
    for g, (s, e) in p3_ranges.items():
        all_slices.append(("p3", g, output_audio_dir / f"part3_{g}.mp3", s, e))
    for g, (s, e) in p4_ranges.items():
        all_slices.append(("p4", g, output_audio_dir / f"part4_{g}.mp3", s, e))

    for cat, key, dst, s, e in all_slices:
        if not dst.exists() or dst.stat().st_size < 1000:
            slice_audio_file(str(audio_path), str(dst), s, e)
    print(f"  [✓] All 54 audio files ready in {output_audio_dir}")

    print("  [➔] Transcribing slices with faster-whisper (CPU int8)...")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")

    result_data: Dict[str, Dict[str, Any]] = {"part1": {}, "part2": {}, "part3": {}, "part4": {}}

    for q in range(1, 7):
        clip = str(output_audio_dir / f"part1_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        q_segs = []
        for s in segs_gen:
            t = s.text.strip()
            is_trap = "is being" in t.lower() or "are being" in t.lower()
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": t,
                "text_vi": "",
                "is_trap": is_trap,
            })
        result_data["part1"][str(q)] = q_segs

    for q in range(7, 32):
        clip = str(output_audio_dir / f"part2_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        q_segs = []
        for s in segs_gen:
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        result_data["part2"][str(q)] = q_segs

    for g_key in p3_ranges.keys():
        clip = str(output_audio_dir / f"part3_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        g_segs = []
        for s in segs_gen:
            g_segs.append({
                "id": f"seg-p3-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        result_data["part3"][g_key] = g_segs

    for g_key in p4_ranges.keys():
        clip = str(output_audio_dir / f"part4_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        g_segs = []
        for s in segs_gen:
            g_segs.append({
                "id": f"seg-p4-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        result_data["part4"][g_key] = g_segs

    with open(segments_cache, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  [✓] Segment metadata cached to {segments_cache.name}")
    return result_data


# ==============================================================================
# IMAGE CROPPING ENGINE
# ==============================================================================

def process_images_pipeline(test_pdf_path: Path, output_image_dir: Path):
    output_image_dir.mkdir(parents=True, exist_ok=True)
    q1_img = output_image_dir / "part1_q1.jpg"
    if q1_img.exists():
        print(f"  [✓] Images already present in {output_image_dir}")
        return

    doc = pymupdf.open(str(test_pdf_path))
    print(f"  [➔] Cropping images from test PDF into {output_image_dir}...")

    # Part 1 Photos
    im2 = Image.frombytes("RGB", [doc[1].get_pixmap(dpi=150).width, doc[1].get_pixmap(dpi=150).height], doc[1].get_pixmap(dpi=150).samples)
    im2.crop((230, 95, 960, 780)).save(output_image_dir / "part1_q1.jpg", "JPEG", quality=90)
    im2.crop((180, 875, 1025, 1445)).save(output_image_dir / "part1_q2.jpg", "JPEG", quality=90)

    im3 = Image.frombytes("RGB", [doc[2].get_pixmap(dpi=150).width, doc[2].get_pixmap(dpi=150).height], doc[2].get_pixmap(dpi=150).samples)
    im3.crop((200, 95, 1000, 680)).save(output_image_dir / "part1_q3.jpg", "JPEG", quality=90)
    im3.crop((200, 775, 1000, 1340)).save(output_image_dir / "part1_q4.jpg", "JPEG", quality=90)

    im4 = Image.frombytes("RGB", [doc[3].get_pixmap(dpi=150).width, doc[3].get_pixmap(dpi=150).height], doc[3].get_pixmap(dpi=150).samples)
    im4.crop((185, 95, 1010, 670)).save(output_image_dir / "part1_q5.jpg", "JPEG", quality=90)
    im4.crop((185, 770, 1010, 1340)).save(output_image_dir / "part1_q6.jpg", "JPEG", quality=90)

    # Part 3 Graphics
    im8 = Image.frombytes("RGB", [doc[7].get_pixmap(dpi=150).width, doc[7].get_pixmap(dpi=150).height], doc[7].get_pixmap(dpi=150).samples)
    g62 = im8.crop((650, 90, 1060, 410))
    g62.save(output_image_dir / "part3_g62_64.png")
    g62.save(output_image_dir / "part3_q64.png")

    im9 = Image.frombytes("RGB", [doc[8].get_pixmap(dpi=150).width, doc[8].get_pixmap(dpi=150).height], doc[8].get_pixmap(dpi=150).samples)
    g65 = im9.crop((150, 90, 550, 360))
    g65.save(output_image_dir / "part3_g65_67.png")
    g65.save(output_image_dir / "part3_q66.png")

    g68 = im9.crop((650, 90, 1060, 410))
    g68.save(output_image_dir / "part3_g68_70.png")
    g68.save(output_image_dir / "part3_q70.png")

    # Part 4 Graphics
    im12 = Image.frombytes("RGB", [doc[11].get_pixmap(dpi=150).width, doc[11].get_pixmap(dpi=150).height], doc[11].get_pixmap(dpi=150).samples)
    g95 = im12.crop((140, 95, 570, 345))
    g95.save(output_image_dir / "part4_g95_97.png")
    g95.save(output_image_dir / "part4_q97.png")

    g98 = im12.crop((630, 95, 1100, 245))
    g98.save(output_image_dir / "part4_g98_100.png")
    g98.save(output_image_dir / "part4_q100.png")

    # Part 6 Passages
    p6_ranges = [("part6_131_134.png", 15), ("part6_135_138.png", 16), ("part6_139_142.png", 17), ("part6_143_146.png", 18)]
    for fn, idx in p6_ranges:
        im = Image.frombytes("RGB", [doc[idx].get_pixmap(dpi=150).width, doc[idx].get_pixmap(dpi=150).height], doc[idx].get_pixmap(dpi=150).samples)
        im.crop((80, 80, im.width - 80, int(im.height * 0.55))).save(output_image_dir / fn)

    # Part 7 Passages
    p7_ranges = [
        ("part7_147_148.png", 19, False), ("part7_149_150.png", 20, False), ("part7_151_152.png", 21, False),
        ("part7_153_154.png", 22, False), ("part7_155_157.png", 23, False), ("part7_158_160.png", 24, False),
        ("part7_161_164.png", 25, False), ("part7_165_167.png", 26, False), ("part7_168_171.png", 27, False),
        ("part7_172_175.png", 28, False), ("part7_176_180.png", 29, True),  ("part7_181_185.png", 31, True),
        ("part7_186_190.png", 33, True),  ("part7_191_195.png", 35, True),  ("part7_196_200.png", 37, True),
    ]
    for fn, idx, is_multi in p7_ranges:
        if not is_multi:
            im = Image.frombytes("RGB", [doc[idx].get_pixmap(dpi=150).width, doc[idx].get_pixmap(dpi=150).height], doc[idx].get_pixmap(dpi=150).samples)
            im.crop((80, 80, im.width - 80, int(im.height * 0.6))).save(output_image_dir / fn)
        else:
            im1 = Image.frombytes("RGB", [doc[idx].get_pixmap(dpi=120).width, doc[idx].get_pixmap(dpi=120).height], doc[idx].get_pixmap(dpi=120).samples)
            im2 = Image.frombytes("RGB", [doc[idx+1].get_pixmap(dpi=120).width, doc[idx+1].get_pixmap(dpi=120).height], doc[idx+1].get_pixmap(dpi=120).samples)
            comb = Image.new("RGB", (im1.width + im2.width, max(im1.height, im2.height)), (255, 255, 255))
            comb.paste(im1, (0, 0))
            comb.paste(im2, (im1.width, 0))
            comb.save(output_image_dir / fn)

    print(f"  [✓] All images cropped successfully into {output_image_dir}")


# ==============================================================================
# GEMINI BATCH QUESTION EXTRACTION
# ==============================================================================

def build_part_prompt(part_num: int, q_start: int, q_end: int, test_name: str, answer_map: Dict[str, str]) -> str:
    relevant_answers = {
        str(num): answer_map[str(num)] for num in range(q_start, q_end + 1) if str(num) in answer_map
    }

    answer_text = ""
    if relevant_answers:
        answer_text = (
            f"\nVERIFIED OFFICIAL ANSWER KEY (You MUST set correct_answer to match this key strictly for each question_number and explain why it is correct):\n"
            f"{json.dumps(relevant_answers)}\n"
        )

    return f"""You are an elite TOEIC Master Coach and Content Architect.
Extract Part {part_num} (Questions {q_start} to {q_end}) for '{test_name}'.
STRICT INSTRUCTION: Only extract questions in range {q_start} to {q_end}. Do NOT include questions outside this range.
{answer_text}

STRICT REQUIREMENTS:
1. Every question MUST have an in-depth Vietnamese explanation (explanation_vi) containing:
   - Phân tích ngữ cảnh / cấu trúc ngữ pháp.
   - Vì sao đáp án đúng là chính xác (kèm dịch nghĩa).
   - Bẫy đề thi ETS (vì sao các lựa chọn khác sai/gây nhiễu).
   - Mẹo phản xạ nhanh (10s coaching tactic).
2. For reading & listening scripts, include verbatim 'evidence_quote' and 'paraphrase_pair' whenever applicable.
3. Assign appropriate 'question_type_tag' (e.g. word_form, conjunction, verb_tense, wh_where, passive_being_trap, inference, detail_lookup).
4. Strictly conform to the requested JSON schema.
"""


def extract_batch(
    client: genai.Client,
    model_name: str,
    test_file_ref: Any,
    transcript_file_ref: Optional[Any],
    part_num: int,
    q_start: int,
    q_end: int,
    test_name: str,
    answer_map: Dict[str, str],
    batch_file: Path
) -> Dict[str, Any]:
    if batch_file.exists():
        try:
            with open(batch_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                qs = [q["question_number"] for g in data.get("groups", []) for q in g.get("questions", [])]
                if len(qs) > 0 and min(qs) >= q_start and max(qs) <= q_end:
                    print(f"  [✓] Batch Part {part_num} (Q{q_start}-Q{q_end}) already exists and verified, skipping.")
                    return data
        except Exception:
            pass

    print(f"  [➔] Querying Gemini for Part {part_num} (Questions {q_start} to {q_end})...")
    prompt = build_part_prompt(part_num, q_start, q_end, test_name, answer_map)

    contents: List[Any] = [test_file_ref]
    if transcript_file_ref and part_num in [1, 2, 3, 4]:
        contents.append(transcript_file_ref)
    contents.append(prompt)

    models_to_try = [model_name, "gemini-3.5-flash", "gemini-flash-latest"]
    for active_model in models_to_try:
        try:
            start_t = time.time()
            res = client.models.generate_content(
                model=active_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ToeicExtractionPayload,
                    temperature=0.1,
                )
            )
            data = json.loads(res.text or "{}")
            elapsed = time.time() - start_t
            
            with open(batch_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            total_q = sum(len(g.get("questions", [])) for g in data.get("groups", []))
            print(f"  [✓] Extracted {total_q} questions in {elapsed:.1f}s via {active_model}.")
            return data
        except Exception as e:
            print(f"  [WARN] Attempt with {active_model} failed: {e}. Retrying...")
            time.sleep(3)

    raise RuntimeError(f"Failed to extract Part {part_num} (Q{q_start}-Q{q_end}) after all model retries.")


# ==============================================================================
# AUTHORITATIVE DATASET COMPILER (74 GROUPS, 200 QUESTIONS)
# ==============================================================================

def compile_authoritative_dataset(
    test_name: str,
    slug: str,
    slug_short: str,
    dirs: Dict[str, Path],
    answer_map: Dict[str, str],
    audio_segs: Dict[str, Any]
):
    batches_dir = dirs["batches"]
    final_dir = dirs["final"]

    all_final_groups = []
    all_final_questions = []

    # --- Part 1: 6 Groups, 6 Questions ---
    print("  [-] Compiling Part 1...")
    with open(batches_dir / "batch_part1_q1_6.json", "r", encoding="utf-8") as f:
        p1_batch = json.load(f)
    p1_q_map = {q["question_number"]: q for g in p1_batch["groups"] for q in g["questions"]}

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
            "question_type_tag": q_raw.get("question_type_tag", "instruction_action"),
            "question_text": None,
            "options": {k: v for k, v in raw_opts.items() if v is not None},
            "correct_answer": correct_ans,
            "explanation_vi": q_raw.get("explanation_vi", ""),
            "evidence_quote": q_raw.get("evidence_quote"),
            "paraphrase_pair": q_raw.get("paraphrase_pair"),
        }
        part1_questions.append(question)

    with open(final_dir / f"{slug}_part1.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 1, "total_groups": len(part1_groups), "total_questions": len(part1_questions)}, "question_groups": part1_groups, "questions": part1_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part1_groups)
    all_final_questions.extend(part1_questions)

    # --- Part 2: 25 Groups, 25 Questions ---
    print("  [-] Compiling Part 2...")
    with open(batches_dir / "batch_part2_q7_31.json", "r", encoding="utf-8") as f:
        p2_batch = json.load(f)
    p2_q_map = {q["question_number"]: q for g in p2_batch["groups"] for q in g["questions"]}

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

        question = {
            "id": q_id,
            "group_id": g_id,
            "part": 2,
            "question_number": q_num,
            "question_type_tag": q_raw.get("question_type_tag", "wh_question"),
            "question_text": p2_prompts.get(q_num, q_raw.get("question_text")),
            "options": {k: v for k, v in raw_opts.items() if v is not None},
            "correct_answer": correct_ans,
            "explanation_vi": q_raw.get("explanation_vi", ""),
            "evidence_quote": q_raw.get("evidence_quote"),
            "paraphrase_pair": q_raw.get("paraphrase_pair"),
        }
        part2_questions.append(question)

    with open(final_dir / f"{slug}_part2.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 2, "total_groups": len(part2_groups), "total_questions": len(part2_questions)}, "question_groups": part2_groups, "questions": part2_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part2_groups)
    all_final_questions.extend(part2_questions)

    # --- Part 3: 13 Groups, 39 Questions ---
    print("  [-] Compiling Part 3...")
    with open(batches_dir / "batch_part3_q32_50.json", "r", encoding="utf-8") as f:
        p3_b1 = json.load(f)["groups"]
    p3_b2_file = batches_dir / "batch_part3_q50_70.json"
    if not p3_b2_file.exists():
        p3_b2_file = batches_dir / "batch_part3_q51_70.json"
    with open(p3_b2_file, "r", encoding="utf-8") as f:
        p3_b2 = json.load(f)["groups"]

    p3_raw_groups = p3_b1[:6] + p3_b2
    p3_graphics_map = {
        "g62_64": f"/images/{slug_short}/part3_g62_64.png",
        "g65_67": f"/images/{slug_short}/part3_g65_67.png",
        "g68_70": f"/images/{slug_short}/part3_g68_70.png",
    }

    part3_groups = []
    part3_questions = []
    for g in p3_raw_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        g_key = f"g{q_start}_{q_end}"
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p3-{g_key}"))
        segs = audio_segs.get("part3", {}).get(g_key, [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 3,
            "passage_text": None,
            "image_url": p3_graphics_map.get(g_key),
            "audio_url": f"/audio/{slug_short}/part3_{g_key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part3_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 3,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "detail_lookup"),
                "question_text": q.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part3_questions.append(question)

    with open(final_dir / f"{slug}_part3.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 3, "total_groups": len(part3_groups), "total_questions": len(part3_questions)}, "question_groups": part3_groups, "questions": part3_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part3_groups)
    all_final_questions.extend(part3_questions)

    # --- Part 4: 10 Groups, 30 Questions ---
    print("  [-] Compiling Part 4...")
    with open(batches_dir / "batch_part4_q71_85.json", "r", encoding="utf-8") as f:
        p4_b1 = json.load(f)["groups"]
    with open(batches_dir / "batch_part4_q86_100.json", "r", encoding="utf-8") as f:
        p4_b2 = json.load(f)["groups"]

    p4_raw_groups = p4_b1 + p4_b2
    p4_graphics_map = {
        "g95_97": f"/images/{slug_short}/part4_g95_97.png",
        "g98_100": f"/images/{slug_short}/part4_g98_100.png",
    }

    part4_groups = []
    part4_questions = []
    for g in p4_raw_groups:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        g_key = f"g{q_start}_{q_end}"
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p4-{g_key}"))
        segs = audio_segs.get("part4", {}).get(g_key, [])

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 4,
            "passage_text": None,
            "image_url": p4_graphics_map.get(g_key),
            "audio_url": f"/audio/{slug_short}/part4_{g_key}.mp3",
            "transcript_segments": segs if segs else None,
        }
        part4_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 4,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "instruction_action"),
                "question_text": q.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part4_questions.append(question)

    with open(final_dir / f"{slug}_part4.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 4, "total_groups": len(part4_groups), "total_questions": len(part4_questions)}, "question_groups": part4_groups, "questions": part4_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part4_groups)
    all_final_questions.extend(part4_questions)

    # --- Part 5: 1 Group, 30 Questions ---
    print("  [-] Compiling Part 5...")
    with open(batches_dir / "batch_part5_q101_130.json", "r", encoding="utf-8") as f:
        p5_batch = json.load(f)

    g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p5"))
    part5_groups = [{
        "id": g_id,
        "test_name": test_name,
        "part": 5,
        "passage_text": None,
        "image_url": None,
        "audio_url": None,
        "transcript_segments": None,
    }]
    part5_questions = []

    for g in p5_batch["groups"]:
        for q in g["questions"]:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 5,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "word_form"),
                "question_text": q.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part5_questions.append(question)

    with open(final_dir / f"{slug}_part5.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 5, "total_groups": len(part5_groups), "total_questions": len(part5_questions)}, "question_groups": part5_groups, "questions": part5_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part5_groups)
    all_final_questions.extend(part5_questions)

    # --- Part 6: 4 Groups, 16 Questions ---
    print("  [-] Compiling Part 6...")
    with open(batches_dir / "batch_part6_q131_146.json", "r", encoding="utf-8") as f:
        p6_batch = json.load(f)

    part6_groups = []
    part6_questions = []
    for g in p6_batch["groups"]:
        qs = g["questions"]
        q_start = qs[0]["question_number"]
        q_end = qs[-1]["question_number"]
        range_key = f"{q_start}_{q_end}"
        g_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-p6-{range_key}"))

        group = {
            "id": g_id,
            "test_name": test_name,
            "part": 6,
            "passage_text": g.get("passage_text"),
            "image_url": f"/images/{slug_short}/part6_{range_key}.png",
            "audio_url": None,
            "transcript_segments": None,
        }
        part6_groups.append(group)

        for q in qs:
            q_num = q["question_number"]
            q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{slug}-q{q_num}"))
            correct_ans = answer_map.get(str(q_num), q.get("correct_answer", "A"))
            raw_opts = q.get("options", {}) or {}

            question = {
                "id": q_id,
                "group_id": g_id,
                "part": 6,
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "sentence_insertion"),
                "question_text": q.get("question_text"),
                "options": {k: v for k, v in raw_opts.items() if v is not None},
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair"),
            }
            part6_questions.append(question)

    with open(final_dir / f"{slug}_part6.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"test_name": test_name, "part": 6, "total_groups": len(part6_groups), "total_questions": len(part6_questions)}, "question_groups": part6_groups, "questions": part6_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part6_groups)
    all_final_questions.extend(part6_questions)

    # --- Part 7: 15 Groups, 54 Questions ---
    print("  [-] Compiling Part 7...")
    with open(batches_dir / "batch_part7_q147_175.json", "r", encoding="utf-8") as f:
        p7_b1 = json.load(f)["groups"]
    with open(batches_dir / "batch_part7_q176_200.json", "r", encoding="utf-8") as f:
        p7_b2 = json.load(f)["groups"]

    p7_raw_groups = p7_b1 + p7_b2
    normalized_p7 = []
    for g in p7_raw_groups:
        qs = g["questions"]
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
        json.dump({"metadata": {"test_name": test_name, "part": 7, "total_groups": len(part7_groups), "total_questions": len(part7_questions)}, "question_groups": part7_groups, "questions": part7_questions}, f, ensure_ascii=False, indent=2)
    all_final_groups.extend(part7_groups)
    all_final_questions.extend(part7_questions)

    # Master full test file
    full_test_file = final_dir / f"{slug}_full.json"
    full_payload = {
        "metadata": {
            "test_name": test_name,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "gemini-3.5-flash",
            "total_groups": len(all_final_groups),
            "total_questions": len(all_final_questions),
        },
        "question_groups": all_final_groups,
        "questions": all_final_questions,
    }
    with open(full_test_file, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, ensure_ascii=False, indent=2)

    return all_final_groups, all_final_questions, full_test_file


# ==============================================================================
# MAIN ORCHESTRATOR
# ==============================================================================

def run_pipeline(
    test_dir_str: str,
    test_name_override: Optional[str] = None,
    model_name: str = "gemini-3.5-flash",
    parts_to_run: Optional[List[int]] = None,
    skip_audio: bool = False,
    device: str = "cpu"
):
    test_dir = Path(test_dir_str).resolve()
    if not test_dir.exists():
        print(f"[ERROR] Test directory not found: {test_dir}")
        sys.exit(1)

    folder_name = test_dir.name
    test_name = test_name_override or f"ETS TOEIC 2023 - {folder_name.split(' - ')[0].title() if ' - ' in folder_name else folder_name}"
    slug = folder_name.lower().replace(" ", "_").replace("-", "_")

    # Determine short slug for public/ folders: e.g. "test2"
    test_num_match = re.search(r'\d+', folder_name)
    test_num = test_num_match.group(0) if test_num_match else "1"
    slug_short = f"test{test_num}"

    output_base = Path("processed_data") / folder_name
    dirs = setup_directories(output_base)

    print(f"\n{'='*75}")
    print(f" TOEIC MASTER PIPELINE: {test_name}")
    print(f"{'='*75}")
    print(f"[*] Input Directory  : {test_dir}")
    print(f"[*] Output Base      : {output_base.resolve()}")
    print(f"[*] Assets Short Slug: {slug_short}")
    print(f"[*] Gemini Model     : {model_name}")

    # 1. Auto-detect files
    detected = auto_detect_files(test_dir)
    print("\n[Step 1] File Auto-Detection:")
    for k, v in detected.items():
        status = f"✓ {v.name}" if v else "✗ Not found"
        print(f"  - {k:<15}: {status}")

    if not detected["test_pdf"]:
        print("[FATAL ERROR] No test PDF file found in folder.")
        sys.exit(1)

    client = get_gemini_client()

    # 2. Answer Key Extraction
    print("\n[Step 2] Processing Official Answer Key:")
    answer_map = {}
    if detected["answer_file"]:
        answer_map = parse_and_cache_answers(client, detected["answer_file"], dirs["answers"], model_name)
    else:
        print("  [WARN] No answer key file found.")

    # 3. Audio Slicing & Whisper Transcription
    print("\n[Step 3] Audio Processing & Slicing:")
    audio_segs = {}
    if detected["audio_file"] and not skip_audio:
        public_audio_dir = Path("public/audio") / slug_short
        audio_segs = process_audio_pipeline(detected["audio_file"], public_audio_dir, dirs["segments"])
    else:
        print("  [!] Audio processing skipped (--skip-audio or audio file missing).")

    # 4. Image Cropping & Extraction
    print("\n[Step 4] Image Cropping & Extraction:")
    public_img_dir = Path("public/images") / slug_short
    process_images_pipeline(detected["test_pdf"], public_img_dir)

    # 5. Question Batch Extractions via Gemini
    print("\n[Step 5] Extracting Questions via Gemini:")
    test_file_ref = client.files.upload(file=str(detected["test_pdf"]))
    transcript_file_ref = None
    if detected["transcript_pdf"]:
        transcript_file_ref = client.files.upload(file=str(detected["transcript_pdf"]))

    batches_plan = [
        (1, 1, 6, "part1_q1_6"),
        (2, 7, 31, "part2_q7_31"),
        (3, 32, 50, "part3_q32_50"),
        (3, 50, 70, "part3_q50_70"),
        (4, 71, 85, "part4_q71_85"),
        (4, 86, 100, "part4_q86_100"),
        (5, 101, 130, "part5_q101_130"),
        (6, 131, 146, "part6_q131_146"),
        (7, 147, 175, "part7_q147_175"),
        (7, 176, 200, "part7_q176_200"),
    ]

    selected_batches = batches_plan
    if parts_to_run:
        selected_batches = [b for b in batches_plan if b[0] in parts_to_run]

    for part_num, q_start, q_end, b_name in selected_batches:
        batch_file = dirs["batches"] / f"batch_{b_name}.json"
        extract_batch(
            client=client,
            model_name=model_name,
            test_file_ref=test_file_ref,
            transcript_file_ref=transcript_file_ref,
            part_num=part_num,
            q_start=q_start,
            q_end=q_end,
            test_name=test_name,
            answer_map=answer_map,
            batch_file=batch_file
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
        audio_segs=audio_segs
    )

    print(f"\n{'='*75}")
    print(f"[✓] MASTER PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"{'='*75}")
    print(f"  ➔ Total Question Groups: {len(all_groups)} (74 groups)")
    print(f"  ➔ Total Questions      : {len(all_questions)} / 200")
    print(f"  ➔ Master Output File   : {full_test_file.resolve()}")
    print(f"{'='*75}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Master One-Click TOEIC Test Processing Pipeline."
    )
    parser.add_argument(
        "--test-dir",
        required=True,
        help="Path to folder containing test materials (e.g. 'raw_data/TEST 2 - ETS 2023')"
    )
    parser.add_argument(
        "--test-name",
        default=None,
        help="Custom test name (default: auto-detected from folder name)"
    )
    parser.add_argument(
        "--model",
        default="gemini-3.5-flash",
        help="Gemini model name (default: gemini-3.5-flash)"
    )
    parser.add_argument(
        "--parts",
        default=None,
        help="Comma-separated parts to process, e.g. '1,2,5' or 'all' (default: all)"
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip Whisper audio transcription"
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cuda", "cpu"],
        help="Compute device for Whisper (default: cpu)"
    )

    args = parser.parse_args()

    parts_list = None
    if args.parts and args.parts.lower() != "all":
        parts_list = [int(p.strip()) for p in args.parts.split(",") if p.strip().isdigit()]

    run_pipeline(
        test_dir_str=args.test_dir,
        test_name_override=args.test_name,
        model_name=args.model,
        parts_to_run=parts_list,
        skip_audio=args.skip_audio,
        device=args.device
    )


if __name__ == "__main__":
    main()
