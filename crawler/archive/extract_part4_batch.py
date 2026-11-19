import os
import sys
import json
import time
from dotenv import load_dotenv
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
load_dotenv(".env.local")
from google import genai
from google.genai import types

client = genai.Client()

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

def extract_batch(batch_num, booklet_paths, trans_paths, q_range):
    out_file = f"raw_data/TEST 1 - ETS 2023/part4_batch{batch_num}.json"
    if os.path.exists(out_file):
        print(f"Batch {batch_num} already exists at {out_file}, skipping.", flush=True)
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"\n{'='*60}", flush=True)
    print(f"Extracting Part 4 Batch {batch_num}: Questions {q_range[0]} to {q_range[-1]}...", flush=True)
    print(f"{'='*60}", flush=True)

    pil_images = []
    for p in booklet_paths:
        print(f"Loading booklet image {p}...", flush=True)
        pil_images.append(Image.open(p))
    for p in trans_paths:
        print(f"Loading transcript image {p}...", flush=True)
        pil_images.append(Image.open(p))

    batch_answers = {str(k): ANSWERS[k] for k in q_range}

    prompt = f"""
You are an expert TOEIC Exam Specialist and Vietnamese Master Coach.
Your task is to extract TOEIC Part 4 (Short Talks) data for Questions {q_range[0]} to {q_range[-1]}.

OFFICIAL ANSWER KEY (You MUST set correct_answer to strictly match this key):
{json.dumps(batch_answers, indent=2)}

INSTRUCTIONS:
1. For each talk group in Questions {q_range[0]} to {q_range[-1]}:
   - Group info:
     * id: "test1-p4-gXX_YY" (e.g. "test1-p4-g71_73")
     * q_start: first question number (int)
     * q_end: last question number (int)
     * dialogue: list of talk sentence lines spoken by the single speaker. For each line:
       - speaker: "Speaker" or speaker's name if identified in the talk (e.g. "Lisa Campbell", "Abdi", "Yuri Yamakawa", "Vinod Singh")
       - text_en: exact English sentence from the transcript
       - text_vi: fluent Vietnamese translation
   - Questions (3 questions per talk):
     * id: "test1-qXX"
     * question_number: int (e.g. 71)
     * part: 4
     * question_text: English question prompt exactly as printed in the test booklet
     * options: {{ "A": "...", "B": "...", "C": "...", "D": "..." }} exactly from the test booklet
     * correct_answer: strictly from the answer key above ('A', 'B', 'C', or 'D')
     * question_type_tag: standard tag such as 'detail_lookup', 'wh_why', 'wh_what', 'wh_where', 'graphic', 'inference', 'instruction_action', 'intent'
     * evidence_quote: the exact sentence or phrase from the talk proving this answer
     * paraphrase_pair: {{"original": "...", "paraphrased": "..."}} if applicable, or null
     * explanation_vi: Comprehensive Vietnamese pedagogical coaching explanation:
       - Dịch câu hỏi và 4 đáp án sang tiếng Việt
       - Giải thích rõ tại sao đáp án đúng được chọn dựa vào dẫn chứng trong bài nói
       - Phân tích bẫy (distractor traps) của các phương án sai nếu có
       - Bí quyết phản xạ hoặc từ vựng trọng tâm cần nhớ

Return a JSON object matching this schema:
{{
  "groups": [
    {{
      "id": "test1-p4-g71_73",
      "q_start": 71,
      "q_end": 73,
      "dialogue": [
        {{ "speaker": "Speaker", "text_en": "...", "text_vi": "..." }}
      ],
      "questions": [
        {{
          "id": "test1-q71",
          "question_number": 71,
          "part": 4,
          "question_text": "...",
          "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
          "correct_answer": "C",
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

    models_to_try = ["gemini-2.5-flash", "gemini-3.8-flash"]
    res = None
    for model_name in models_to_try:
        try:
            print(f"Calling Gemini ({model_name})...", flush=True)
            res = client.models.generate_content(
                model=model_name,
                contents=[*pil_images, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            print(f"[✓] Successfully generated with {model_name}!", flush=True)
            break
        except Exception as e:
            print(f"[WARN] Error with {model_name}: {e}. Trying next model...", flush=True)
            time.sleep(2)

    if not res:
        raise RuntimeError("Failed to generate content with all available models!")

    data = json.loads(res.text)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {out_file} with {len(data.get('groups', []))} groups!", flush=True)
    return data

if __name__ == "__main__":
    # Batch 1: Q71-82 (4 groups)
    extract_batch(
        batch_num=1,
        booklet_paths=["tmp_p3/booklet_p11.png"],
        trans_paths=["tmp_p4/trans_p20.png", "tmp_p4/trans_p21.png", "tmp_p4/trans_p22.png"],
        q_range=range(71, 83)
    )

    # Batch 2: Q83-94 (4 groups)
    extract_batch(
        batch_num=2,
        booklet_paths=["tmp_p3/booklet_p12.png"],
        trans_paths=["tmp_p4/trans_p23.png", "tmp_p4/trans_p24.png", "tmp_p4/trans_p25.png", "tmp_p4/trans_p26.png"],
        q_range=range(83, 95)
    )

    # Batch 3: Q95-100 (2 groups)
    extract_batch(
        batch_num=3,
        booklet_paths=["tmp_p3/booklet_p13.png"],
        trans_paths=["tmp_p4/trans_p27.png", "tmp_p4/trans_p28.png"],
        q_range=range(95, 101)
    )

    print("\n[✓] All 3 Part 4 batches extracted successfully!", flush=True)
