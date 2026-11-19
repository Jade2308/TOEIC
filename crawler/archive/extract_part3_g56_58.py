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
    56: 'A', 57: 'B', 58: 'A'
}

out_file = "raw_data/TEST 1 - ETS 2023/part3_g56_58.json"

print("Uploading files for Group 56-58...")
f_book = client.files.upload(file="tmp_p3/booklet_p9.png")
f_t16 = client.files.upload(file="tmp_p3/trans_p16.png")
f_t17 = client.files.upload(file="tmp_p3/trans_p17.png")

prompt = f"""
You are an expert TOEIC Exam Specialist and Vietnamese Master Coach.
Your task is to extract TOEIC Part 3 (Conversations) data for Questions 56, 57, 58 ONLY.

OFFICIAL ANSWER KEY (Strictly match this):
{json.dumps(ANSWERS, indent=2)}

INSTRUCTIONS:
Extract Group 56-58 (Conversation with three speakers: Marion, Man, Francesca):
- Group id: "test1-p3-g56-58"
- q_start: 56, q_end: 58
- dialogue: each line with speaker ("Man", "Marion", "Francesca"), text_en, text_vi
- questions (56, 57, 58):
  * id: "test1-q56", "test1-q57", "test1-q58"
  * question_number: 56, 57, 58
  * part: 3
  * question_text: English question prompt from booklet_p9
  * options: {{ "A": "...", "B": "...", "C": "...", "D": "..." }} from booklet_p9
  * correct_answer: 'A', 'B', 'A'
  * question_type_tag: standard tag
  * evidence_quote: exact sentence proving answer
  * paraphrase_pair: {{"original": "...", "paraphrased": "..."}} or null
  * explanation_vi: In-depth Vietnamese pedagogical explanation (dịch câu hỏi + 4 đáp án, phân tích lý do chọn đáp án đúng theo dẫn chứng, bẫy distractor, bí quyết làm bài)

Return a JSON object:
{{
  "groups": [
    {{
      "id": "test1-p3-g56-58",
      "q_start": 56,
      "q_end": 58,
      "dialogue": [...],
      "questions": [...]
    }}
  ]
}}
"""

for model_name in ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro"]:
    try:
        print(f"Calling {model_name}...")
        res = client.models.generate_content(
            model=model_name,
            contents=[f_book, f_t16, f_t17, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        data = json.loads(res.text)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved Group 56-58 to {out_file}")
        break
    except Exception as e:
        print(f"Error with {model_name}: {e}")
        time.sleep(3)
