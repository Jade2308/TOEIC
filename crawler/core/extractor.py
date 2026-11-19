from __future__ import annotations

"""
Resilient Extraction Engine using Gemini Structured Outputs & Multi-Key Rotation.
Features Anti-Recitation Safety, Dynamic Transcript Injection, and Robust Batching.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from .api_client import ResilientLLMClient
from .schema import ToeicExtractionPayload


def get_resilient_client() -> ResilientLLMClient:
    """Initializes the multi-key resilient LLM client."""
    return ResilientLLMClient()


def parse_and_cache_answers(
    client: ResilientLLMClient,
    answer_file: Path,
    answers_dir: Path,
) -> Dict[str, str]:
    """Extracts official answer key mapping (Q1-200) from answer key image or PDF."""
    answers_dir.mkdir(parents=True, exist_ok=True)
    cache_path = answers_dir / "official_answers.json"
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) >= 195:
                    print(f"  [✓] Loaded {len(data)} verified answers from cache: {cache_path.name}")
                    return data
        except Exception:
            pass

    print(f"  [➔] Uploading and extracting official answer key from {answer_file.name}...")
    file_ref = client.upload_file_safe(answer_file)
    prompt = (
        "Extract all 200 answers shown in this TOEIC answer key table. "
        "Return a JSON object where keys are question numbers as strings ('1', '2', ... '200') "
        "and values are the correct uppercase letters ('A', 'B', 'C', or 'D'). "
        "Make sure all questions from 1 to 200 are included accurately. "
        "Return ONLY the valid JSON object without markdown formatting."
    )

    data = client.generate_json_with_retry(
        contents=[file_ref, prompt],
        temperature=0.0,
        max_retries=4,
    )

    # Normalize keys to strings and values to uppercase A, B, C, D
    cleaned = {}
    for k, v in data.items():
        k_str = str(k).strip()
        v_str = str(v).strip().upper()
        if k_str.isdigit() and v_str in ["A", "B", "C", "D"]:
            cleaned[k_str] = v_str

    if len(cleaned) >= 180:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        print(f"  [✓] Extracted & cached {len(cleaned)}/200 official answers to {cache_path.name}")
        return cleaned
    else:
        print(f"  [WARN] Answer key only parsed {len(cleaned)} answers. Retrying extraction...")
        # Fallback direct retry
        data2 = client.generate_json_with_retry(
            contents=[file_ref, prompt + " Be extremely thorough across all columns."],
            temperature=0.1,
            max_retries=3,
        )
        for k, v in data2.items():
            k_str = str(k).strip()
            v_str = str(v).strip().upper()
            if k_str.isdigit() and v_str in ["A", "B", "C", "D"]:
                cleaned[k_str] = v_str
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        return cleaned


def build_batch_prompt(
    part_num: int,
    q_start: int,
    q_end: int,
    test_name: str,
    answer_map: Dict[str, str],
    transcript_context: Optional[str] = None,
) -> str:
    """Builds coaching extraction prompt with anti-recitation safety and official key enforcement."""
    relevant_answers = {
        str(num): answer_map[str(num)] for num in range(q_start, q_end + 1) if str(num) in answer_map
    }

    answer_section = ""
    if relevant_answers:
        answer_section = (
            f"\nVERIFIED OFFICIAL ANSWER KEY (You MUST set correct_answer to match this key strictly for each question_number and explain why it is correct):\n"
            f"{json.dumps(relevant_answers)}\n"
        )

    transcript_section = ""
    if transcript_context:
        transcript_section = f"\nTRANSCRIPT AUDIO CONTEXT:\n{transcript_context}\n"

    safety_rules = ""
    if part_num in [6, 7]:
        safety_rules = (
            "ANTI-RECITATION INSTRUCTION: In the 'passage_text' field, provide a concise structural summary/outline "
            "(2-4 bullet points or sentences) rather than reproducing the entire copyrighted passage verbatim. "
            "Keep 'evidence_quote' concise (under 10 words).\n"
        )

    return f"""You are an elite TOEIC Master Coach and Content Architect.
Extract Part {part_num} (Questions {q_start} to {q_end}) for '{test_name}'.
STRICT INSTRUCTION: Only extract questions in range {q_start} to {q_end}. Do NOT include questions outside this range.
{answer_section}
{transcript_section}
{safety_rules}
STRICT REQUIREMENTS:
1. Every question MUST have an in-depth Vietnamese explanation (explanation_vi) containing:
   - Phân tích ngữ cảnh / cấu trúc ngữ pháp.
   - Vì sao đáp án đúng là chính xác (kèm dịch nghĩa).
   - Bẫy đề thi ETS (vì sao các lựa chọn khác sai/gây nhiễu).
   - Mẹo phản xạ nhanh (10s coaching tactic).
2. For reading & listening scripts, include concise 'evidence_quote' and 'paraphrase_pair' whenever applicable.
3. Assign appropriate 'question_type_tag' (e.g. word_form, conjunction, verb_tense, wh_where, passive_being_trap, inference, detail_lookup).
4. Conform strictly to the requested JSON schema.
"""


def extract_batch(
    client: ResilientLLMClient,
    test_file_ref: Any,
    transcript_file_ref: Optional[Any],
    part_num: int,
    q_start: int,
    q_end: int,
    test_name: str,
    answer_map: Dict[str, str],
    batch_file: Path,
    transcript_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Extracts a batch of questions from PDF using Gemini with Structured Outputs and cache."""
    if batch_file.exists():
        try:
            with open(batch_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                qs = [q["question_number"] for g in data.get("groups", []) for q in g.get("questions", [])]
                if len(qs) > 0 and min(qs) >= q_start and max(qs) <= q_end:
                    expected_count = q_end - q_start + 1
                    if len(qs) == expected_count:
                        print(f"  [✓] Batch Part {part_num} (Q{q_start}-Q{q_end}: {len(qs)} qs) already verified in cache.")
                        return data
        except Exception:
            pass

    print(f"  [➔] Querying Gemini for Part {part_num} (Questions {q_start} to {q_end})...")
    prompt = build_batch_prompt(part_num, q_start, q_end, test_name, answer_map, transcript_context)

    contents: List[Any] = [test_file_ref]
    if transcript_file_ref and part_num in [1, 2, 3, 4]:
        contents.append(transcript_file_ref)
    contents.append(prompt)

    start_t = time.time()
    data = client.generate_json_with_retry(
        contents=contents,
        response_schema=ToeicExtractionPayload,
        temperature=0.1,
        max_retries=5,
    )
    elapsed = time.time() - start_t

    total_q = sum(len(g.get("questions", [])) for g in data.get("groups", []))
    with open(batch_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Extracted Part {part_num} (Q{q_start}-Q{q_end}: {total_q} qs) in {elapsed:.1f}s.")
    return data
