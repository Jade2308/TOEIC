import os
import sys
import json
import time
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv(".env.local")
from google import genai
from google.genai import types

client = genai.Client()

ANSWERS = {
    32: 'A', 33: 'D', 34: 'C', 35: 'C', 36: 'A', 37: 'B', 38: 'A', 39: 'B', 40: 'D',
    41: 'C', 42: 'B', 43: 'D', 44: 'C', 45: 'D', 46: 'B', 47: 'B', 48: 'A', 49: 'D',
    50: 'C', 51: 'D', 52: 'A', 53: 'C', 54: 'C', 55: 'A', 56: 'A', 57: 'B', 58: 'A',
    59: 'C', 60: 'B', 61: 'A', 62: 'A', 63: 'D', 64: 'B', 65: 'D', 66: 'C', 67: 'A',
    68: 'B', 69: 'D', 70: 'D'
}

def extract_batch(batch_num, booklet_pages, trans_pages, q_range):
    out_file = f"raw_data/TEST 1 - ETS 2023/part3_batch{batch_num}.json"
    if os.path.exists(out_file):
        print(f"Batch {batch_num} already exists at {out_file}, skipping extraction.")
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"\n{'='*60}")
    print(f"Extracting Batch {batch_num}: Questions {q_range[0]} to {q_range[-1]}...")
    print(f"{'='*60}")

    uploaded_files = []
    for p in booklet_pages:
        print(f"Uploading booklet {p}...")
        uploaded_files.append(client.files.upload(file=f"tmp_p3/{p}"))
    for p in trans_pages:
        print(f"Uploading transcript {p}...")
        uploaded_files.append(client.files.upload(file=f"tmp_p3/{p}"))

    batch_answers = {str(k): ANSWERS[k] for k in q_range}

    prompt = f"""
You are an expert TOEIC Exam Specialist and Vietnamese Master Coach.
Your task is to extract TOEIC Part 3 (Conversations) data for Questions {q_range[0]} to {q_range[-1]}.

OFFICIAL ANSWER KEY (You MUST set correct_answer to strictly match this key):
{json.dumps(batch_answers, indent=2)}

INSTRUCTIONS:
1. For each conversation group in Questions {q_range[0]} to {q_range[-1]}:
   - Group info:
     * id: "test1-p3-gXX-YY" (e.g. "test1-p3-g32-34")
     * q_start: first question number (int)
     * q_end: last question number (int)
     * dialogue: list of dialogue lines. For each line:
       - speaker: "Man" / "Woman" / "Man 1" / "Man 2" etc.
       - text_en: exact English dialogue sentence from transcript
       - text_vi: fluent Vietnamese translation
   - Questions (3 questions per group):
     * id: "test1-qXX"
     * question_number: int (e.g. 32)
     * part: 3
     * question_text: English question prompt exactly as printed in the test booklet
     * options: {{ "A": "...", "B": "...", "C": "...", "D": "..." }} exactly from the test booklet
     * correct_answer: strictly from the answer key above ('A', 'B', 'C', or 'D')
     * question_type_tag: standard tag such as 'detail_lookup', 'wh_why', 'wh_what', 'wh_where', 'graphic', 'inference', 'instruction_action', 'intent'
     * evidence_quote: the exact sentence or phrase from the dialogue proving this answer
     * paraphrase_pair: {{"original": "...", "paraphrased": "..."}} if applicable, or null
     * explanation_vi: Comprehensive Vietnamese pedagogical coaching explanation:
       - Dịch câu hỏi và 4 đáp án sang tiếng Việt
       - Giải thích rõ tại sao đáp án đúng được chọn dựa vào dẫn chứng trong bài hội thoại
       - Phân tích bẫy (distractor traps) của các phương án sai nếu có
       - Bí quyết phản xạ hoặc từ vựng trọng tâm cần nhớ

Return a JSON object matching this schema:
{{
  "groups": [
    {{
      "id": "test1-p3-g32-34",
      "q_start": 32,
      "q_end": 34,
      "dialogue": [
        {{ "speaker": "Woman", "text_en": "...", "text_vi": "..." }}
      ],
      "questions": [
        {{
          "id": "test1-q32",
          "question_number": 32,
          "part": 3,
          "question_text": "...",
          "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
          "correct_answer": "A",
          "question_type_tag": "...",
          "evidence_quote": "...",
          "paraphrase_pair": {{ "original": "...", "paraphrased": "..." }},
          "explanation_vi": "..."
        }}
      ]
    }}
  ]
}}
"""

    models_to_try = [
        ("gemini-3.8-flash", 2),
        ("gemini-2.5-flash", 2),
        ("gemini-2.5-pro", 1)
    ]
    res_text = None
    for model_name, retries in models_to_try:
        if res_text:
            break
        for attempt in range(retries):
            try:
                print(f"Calling {model_name} (attempt {attempt+1}/{retries})...")
                res = client.models.generate_content(
                    model=model_name,
                    contents=uploaded_files + [prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                res_text = res.text
                print(f"[✓] Received response from {model_name}")
                break
            except Exception as e:
                print(f"[WARN] Error with {model_name} (attempt {attempt+1}): {e}")
                time.sleep(5)

    if not res_text:
        raise RuntimeError(f"Failed to extract Batch {batch_num}")

    data = json.loads(res_text)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved Batch {batch_num} to {out_file} with {len(data.get('groups', []))} groups.")
    return data

if __name__ == "__main__":
    b_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if b_num == 1:
        extract_batch(1, ["booklet_p7.png"], ["trans_p7.png", "trans_p8.png", "trans_p9.png", "trans_p10.png", "trans_p11.png"], range(32, 44))
    elif b_num == 2:
        extract_batch(2, ["booklet_p8.png"], ["trans_p12.png", "trans_p13.png", "trans_p14.png", "trans_p15.png", "trans_p16.png"], range(44, 56))
    elif b_num == 3:
        extract_batch(3, ["booklet_p9.png", "booklet_p10.png"], ["trans_p16.png", "trans_p17.png", "trans_p18.png", "trans_p19.png", "trans_p20.png", "trans_p21.png"], range(56, 71))
