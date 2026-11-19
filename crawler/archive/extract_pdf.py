#!/usr/bin/env python3
"""
scripts/extract_pdf.py
======================
TOEIC PDF Question Extractor & Coaching Pipeline using Google GenAI SDK (Gemini 2.5 Flash).
Uses Gemini's Structured Outputs / JSON Schema to extract TOEIC test questions,
automatically generates detailed Vietnamese explanations (explanation_vi),
classifies question_type_tag, extracts evidence_quote, and identifies paraphrase pairs.

Produces a standard JSON ready for direct import into Supabase (question_groups & questions).

Usage:
    python scripts/extract_pdf.py --test-pdf path/to/test.pdf --answer-pdf path/to/key.pdf -o toeic_extracted.json
"""

import os
import sys
import json
import time
import uuid
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure UTF-8 stdout on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables (.env)
from dotenv import load_dotenv
load_dotenv()

try:
    from pydantic import BaseModel, Field
    from google import genai
    from google.genai import types
except ImportError as e:
    print(f"[ERROR] Required package missing: {e}")
    print("Please activate the 'toeic-pipeline' conda environment:")
    print("    conda activate toeic-pipeline")
    sys.exit(1)


# ==============================================================================
# PYDANTIC SCHEMAS FOR STRUCTURED GEMINI OUTPUT
# ==============================================================================

class ParaphrasePairSchema(BaseModel):
    original: str = Field(
        description="Exact phrase or expression from the passage or listening script"
    )
    paraphrased: str = Field(
        description="Equivalent synonym or paraphrased phrase in the correct answer choice"
    )


class OptionsSchema(BaseModel):
    A: str = Field(description="Option A text")
    B: str = Field(description="Option B text")
    C: str = Field(description="Option C text")
    D: Optional[str] = Field(default=None, description="Option D text (null/omitted for Part 2)")


class QuestionSchema(BaseModel):
    question_number: int = Field(
        description="Question number in the test (1 to 200)"
    )
    part: int = Field(
        description="TOEIC Part number (1 to 7)"
    )
    question_type_tag: str = Field(
        description=(
            "Standard coaching tag: word_form, conjunction, verb_tense, preposition, "
            "vocabulary, wh_where, wh_when, homophone_trap, passive_being_trap, "
            "indirect_response, inference, detail_lookup, graphic, instruction_action"
        )
    )
    question_text: Optional[str] = Field(
        default=None,
        description="The question prompt (can be null for Part 1 and Part 2)"
    )
    options: OptionsSchema = Field(
        description="Options object containing choices A, B, C, and D"
    )
    correct_answer: str = Field(
        description="Single capital letter corresponding to correct choice: 'A', 'B', 'C', or 'D'"
    )
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
    part: int = Field(
        description="TOEIC Part number (1 to 7)"
    )
    passage_text: Optional[str] = Field(
        default=None,
        description="Full reading passage text in clean Markdown for Part 6 and 7; null for Part 1-5"
    )
    audio_script: Optional[str] = Field(
        default=None,
        description="Transcript of the audio dialogue or short talk if provided in the key"
    )
    questions: List[QuestionSchema] = Field(
        description="List of questions linked to this context or single question for Part 1, 2, 5"
    )


class ToeicExtractionPayload(BaseModel):
    test_name: str = Field(
        description="Name of the test, e.g. 'ETS TOEIC 2024 - Practice Test 1'"
    )
    groups: List[QuestionGroupSchema] = Field(
        description="Extracted question groups with linked questions"
    )


# ==============================================================================
# PIPELINE IMPLEMENTATION
# ==============================================================================

def get_gemini_client() -> genai.Client:
    """Initialize Google GenAI client with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY or GOOGLE_API_KEY is not set.")
        print("Please set your Gemini API key in .env or run:")
        print("    $env:GEMINI_API_KEY = 'your_gemini_api_key'")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def build_system_prompt(part_filter: Optional[int] = None) -> str:
    """System instruction for expert TOEIC pedagogical extraction."""
    part_instruction = (
        f"Focus specifically on extracting Part {part_filter} questions."
        if part_filter
        else "Extract questions across the specified sections of the test."
    )

    return f"""You are an elite TOEIC Master Coach and Exam Content Architect.
Your mission is to extract TOEIC test questions from the provided PDF(s) and transform them into an adaptive coaching dataset.

{part_instruction}

STRICT COACHING GUIDELINES:
1. QUESTION TYPE TAGS (question_type_tag):
   Accurately assign one of the following tags to each question:
   - Part 1: 'passive_being_trap' (is/are being V3 on static items), 'passive_state' (arranged, positioned).
   - Part 2: 'wh_where', 'wh_when', 'homophone_trap' (repeated/similar sounds), 'indirect_response' (not direct Yes/No).
   - Part 5: 'word_form' (Noun/Adj/Adv/Verb suffixes), 'conjunction' (clause vs noun phrase), 'verb_tense' (time clauses), 'preposition', 'vocabulary'.
   - Part 6 & 7: 'inference' (implied meaning), 'detail_lookup' (facts/numbers), 'paraphrase_pair', 'graphic'.

2. EXPLANATION IN VIETNAMESE (explanation_vi):
   Every question MUST have an in-depth, structured explanation in Vietnamese:
   - Phân tích ngữ cảnh / cấu trúc ngữ pháp (Vị trí ô trống, từ loại, thì, từ để hỏi).
   - Vì sao đáp án đúng là chính xác (Dẫn chứng, ngữ nghĩa).
   - Bẫy đề thi ETS (Tại sao các phương án khác gây nhiễu, bẫy lặp âm, bẫy thì).
   - Mẹo phản xạ nhanh (Ví dụ: quy tắc 10s cho câu từ loại, mẹo loại Yes/No cho câu hỏi WH).

3. EVIDENCE QUOTE (evidence_quote):
   For reading (Part 6 & 7) and listening with scripts (Part 3 & 4), extract the exact verbatim substring that proves the correct answer.

4. PARAPHRASE PAIR (paraphrase_pair):
   Whenever the answer paraphrases the passage/audio, capture the exact original phrase and its paraphrased equivalent.

5. OUTPUT FORMAT:
   You must strictly conform to the requested JSON Schema without wrapping markdown quotes.
"""


def get_answer_key_map(client: genai.Client, answer_path: str) -> Dict[str, str]:
    """Extracts or loads cached answer key mapping {question_num: letter}."""
    cache_file = Path(answer_path).with_suffix(".answers.json")
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) > 0:
                    print(f"[✓] Loaded {len(data)} answers from cache: {cache_file.name}")
                    return data
        except Exception:
            pass

    print(f"[1b/4] Parsing answer key from {Path(answer_path).name} with Gemini 2.5 Flash...")
    file_ref = client.files.upload(file=answer_path)
    prompt = (
        "Extract all the answers shown in this answer key. "
        "Return a JSON object where the keys are the question numbers as strings (\"1\", \"2\", ... \"200\") "
        "and the values are the correct uppercase letters (\"A\", \"B\", \"C\", or \"D\"). "
        "Return ONLY the valid JSON object."
    )
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[file_ref, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )
    try:
        data = json.loads(res.text or "{}")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[✓] Successfully parsed & cached {len(data)} answers to {cache_file.name}")
        return data
    except Exception as e:
        print(f"[WARN] Failed to parse answer key JSON: {e}")
        return {}


def extract_toeic_data(
    test_pdf_path: str,
    answer_pdf_path: Optional[str] = None,
    output_path: str = "extracted_toeic_data.json",
    model_name: str = "gemini-2.5-flash",
    part_filter: Optional[int] = None,
    test_name: str = "ETS TOEIC Test",
    audio_transcript_path: Optional[str] = None,
    import_to_supabase: bool = False,
    transcript_pdf_path: Optional[str] = None,
    limit_questions: Optional[int] = None
) -> Dict[str, Any]:
    """
    Reads test PDF and answer PDF/image, calls Gemini with Structured Output,
    and formats data for Supabase import.
    """
    client = get_gemini_client()

    print(f"\n{'='*70}")
    print(f" TOEIC PDF EXTRACTOR & COACHING PIPELINE (Gemini Structured Outputs)")
    print(f"{'='*70}")
    print(f"[*] Test PDF       : {Path(test_pdf_path).resolve()}")
    if answer_pdf_path:
        print(f"[*] Answer Key     : {Path(answer_pdf_path).resolve()}")
    if transcript_pdf_path:
        print(f"[*] Transcript PDF : {Path(transcript_pdf_path).resolve()}")
    print(f"[*] Model          : {model_name}")
    print(f"[*] Target Section : {f'Part {part_filter}' if part_filter else 'All Parts'}")
    if limit_questions:
        print(f"[*] Question Limit : {limit_questions} questions")
    print(f"[*] Output File    : {Path(output_path).resolve()}")
    print(f"{'='*70}\n")

    contents_payload: List[Any] = []

    # Upload Test PDF
    print("[1/4] Uploading Test PDF to Gemini Files API...")
    test_file_ref = client.files.upload(file=test_pdf_path)
    print(f"[✓] Test PDF uploaded: {test_file_ref.name}")
    contents_payload.append(test_file_ref)

    # Process and load Answer Key if provided
    answer_map: Dict[str, str] = {}
    if answer_pdf_path and Path(answer_pdf_path).exists():
        answer_map = get_answer_key_map(client, answer_pdf_path)

    # Upload Transcript PDF if provided
    if transcript_pdf_path and Path(transcript_pdf_path).exists():
        print(f"[1c/4] Uploading Listening Transcript PDF to Gemini Files API...")
        trans_file_ref = client.files.upload(file=transcript_pdf_path)
        print(f"[✓] Transcript PDF uploaded: {trans_file_ref.name}")
        contents_payload.append(trans_file_ref)

    # Filter answer key relevant to targeted part
    part_ranges = {
        1: range(1, 7),
        2: range(7, 32),
        3: range(32, 71),
        4: range(71, 101),
        5: range(101, 131),
        6: range(131, 147),
        7: range(147, 201),
    }
    relevant_keys: Dict[str, str] = {}
    if part_filter and part_filter in part_ranges:
        relevant_keys = {str(k): answer_map[str(k)] for k in part_ranges[part_filter] if str(k) in answer_map}
    elif answer_map:
        relevant_keys = answer_map

    answer_prompt_section = ""
    if relevant_keys:
        answer_prompt_section = (
            f"\nVERIFIED OFFICIAL ANSWER KEY (You MUST set correct_answer to match this key strictly for each question_number and explain why it is correct):\n"
            f"{json.dumps(relevant_keys)}\n"
        )

    # Add prompt instructions
    limit_prompt = f"Extract exactly {limit_questions} questions." if limit_questions else ""
    user_prompt = f"""Please extract questions for {f'Part {part_filter}' if part_filter else 'all available parts'} from the uploaded test PDF.
{answer_prompt_section}
{limit_prompt}
Test Name: "{test_name}".
Generate thorough Vietnamese explanations with ETS trap identification, question type tags, evidence quotes, and paraphrase pairs.
"""
    contents_payload.append(user_prompt)

    # System instruction & Structured output config
    system_instruction = build_system_prompt(part_filter)

    # Call Gemini model
    print(f"[2/4] Querying {model_name} with Structured Output Schema...")
    start_time = time.time()

    active_model = model_name
    try:
        response = client.models.generate_content(
            model=active_model,
            contents=contents_payload,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ToeicExtractionPayload,
                temperature=0.2,
            )
        )
    except Exception as e:
        print(f"[WARN] Call with '{active_model}' failed: {e}")
        fallback_model = "gemini-2.0-flash"
        print(f"[INFO] Retrying with model '{fallback_model}'...")
        active_model = fallback_model
        response = client.models.generate_content(
            model=active_model,
            contents=contents_payload,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ToeicExtractionPayload,
                temperature=0.2,
            )
        )

    duration = time.time() - start_time
    print(f"[✓] Received structured extraction in {duration:.2f}s.")

    # Parse JSON
    print("[3/4] Parsing and formatting for Supabase schema...")
    raw_text = response.text or "{}"
    parsed_dict = json.loads(raw_text)

    # Load audio transcript segments if provided
    audio_segments = None
    if audio_transcript_path and Path(audio_transcript_path).exists():
        with open(audio_transcript_path, "r", encoding="utf-8") as f:
            audio_segments = json.load(f)
        print(f"[+] Loaded {len(audio_segments)} audio transcript segments from {audio_transcript_path}")

    # Build Supabase database format
    db_question_groups: List[Dict[str, Any]] = []
    db_questions: List[Dict[str, Any]] = []

    extracted_groups = parsed_dict.get("groups", [])
    for g_idx, group in enumerate(extracted_groups):
        group_uuid = str(uuid.uuid4())
        part_num = group.get("part", 1)
        passage_text = group.get("passage_text")

        group_record = {
            "id": group_uuid,
            "test_name": test_name,
            "part": part_num,
            "passage_text": passage_text,
            "image_url": None,
            "audio_url": None,
            "transcript_segments": audio_segments if (part_num in (1, 2, 3, 4) and audio_segments) else None
        }
        db_question_groups.append(group_record)

        for q in group.get("questions", []):
            question_uuid = str(uuid.uuid4())
            q_num = q.get("question_number", 1)
            raw_options = q.get("options", {}) or {}
            cleaned_options = {k: v for k, v in raw_options.items() if v is not None}
            official_ans = answer_map.get(str(q_num))
            correct_ans = official_ans if official_ans else q.get("correct_answer", "A")

            db_questions.append({
                "id": question_uuid,
                "group_id": group_uuid,
                "part": q.get("part", part_num),
                "question_number": q_num,
                "question_type_tag": q.get("question_type_tag", "unclassified"),
                "question_text": q.get("question_text"),
                "options": cleaned_options,
                "correct_answer": correct_ans,
                "explanation_vi": q.get("explanation_vi", ""),
                "evidence_quote": q.get("evidence_quote"),
                "paraphrase_pair": q.get("paraphrase_pair")
            })

    output_payload = {
        "metadata": {
            "test_name": test_name,
            "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": active_model,
            "total_groups": len(db_question_groups),
            "total_questions": len(db_questions)
        },
        "question_groups": db_question_groups,
        "questions": db_questions
    }

    # Save to JSON
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    print(f"\n[4/4] Successfully generated Supabase-compatible dataset:")
    print(f"      ➔ Groups    : {len(db_question_groups)}")
    print(f"      ➔ Questions : {len(db_questions)}")
    print(f"      ➔ Saved to  : {out_path.resolve()}")

    # Direct Supabase import if requested
    if import_to_supabase:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if supabase_url and supabase_key:
            print("\n[+] Direct Supabase Import enabled. Inserting records...")
            try:
                from supabase import create_client
                sp_client = create_client(supabase_url, supabase_key)

                # Insert groups
                res_groups = sp_client.table("question_groups").upsert(db_question_groups).execute()
                print(f"[✓] Upserted {len(db_question_groups)} question_groups into Supabase.")

                # Insert questions
                res_questions = sp_client.table("questions").upsert(db_questions).execute()
                print(f"[✓] Upserted {len(db_questions)} questions into Supabase.")
            except Exception as sp_err:
                print(f"[WARN] Supabase direct insert failed: {sp_err}")
                print("You can still import the generated JSON manually or via API.")
        else:
            print("[INFO] Direct Supabase import skipped: NEXT_PUBLIC_SUPABASE_URL / KEY not found in .env.")

    return output_payload


def main():
    parser = argparse.ArgumentParser(
        description="TOEIC PDF Exam Extractor & Vietnamese Coaching Generator via Google GenAI SDK."
    )
    parser.add_argument("--test-pdf", required=True, help="Path to test questions PDF")
    parser.add_argument("--answer-key", "--answer-pdf", dest="answer_key", default=None, help="Path to answer key (PDF or PNG/JPG image)")
    parser.add_argument("--transcript-pdf", default=None, help="Path to transcript PDF (for listening parts)")
    parser.add_argument("-o", "--output", default="toeic_extracted.json", help="Path to output JSON file")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Gemini model name (default: gemini-2.5-flash)")
    parser.add_argument("-p", "--part", type=int, choices=[1, 2, 3, 4, 5, 6, 7], default=None, help="Target TOEIC Part to extract (default: all)")
    parser.add_argument("--limit-questions", type=int, default=None, help="Limit number of questions to extract")
    parser.add_argument("--test-name", default="ETS TOEIC 2023 - Test 1", help="Name label for test session")
    parser.add_argument("--audio-transcript", default=None, help="Path to output JSON from process_audio.py to attach audio segments")
    parser.add_argument("--import-supabase", action="store_true", help="Directly insert records into Supabase if credentials exist")

    args = parser.parse_args()

    try:
        extract_toeic_data(
            test_pdf_path=args.test_pdf,
            answer_pdf_path=args.answer_key,
            output_path=args.output,
            model_name=args.model,
            part_filter=args.part,
            test_name=args.test_name,
            audio_transcript_path=args.audio_transcript,
            import_to_supabase=args.import_supabase,
            transcript_pdf_path=args.transcript_pdf,
            limit_questions=args.limit_questions
        )
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
