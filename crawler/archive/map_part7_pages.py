import os
import json
import time
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env.local")
from google import genai
from google.genai import types

client = genai.Client()

def get_page_info(page_num):
    img_path = f"tmp_pages/p7_pages/page_{page_num}.png"
    if not os.path.exists(img_path):
        return None
    
    img = Image.open(img_path)
    prompt = """Analyze this TOEIC test booklet page.
List all reading passage question sets on this page (e.g. Questions 147-148, Questions 149-150).
Format response strictly as JSON:
{
  "page": int,
  "groups": [
    {
      "q_range": "147-148",
      "doc_type": "Advertisement / Email / Notice / Article / Text Message / Form / Schedule",
      "title": "Short title or subject line",
      "questions_on_this_page": [147, 148]
    }
  ]
}
"""
    try:
        res = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        data = json.loads(res.text)
        data["page"] = page_num
        return data
    except Exception as e:
        print(f"Error on page {page_num}: {e}")
        return None

all_page_info = []
for p in range(21, 44):
    info = get_page_info(p)
    if info:
        print(f"Page {p}: {info.get('groups')}")
        all_page_info.append(info)
    time.sleep(1)

with open("tmp_pages/p7_page_mapping.json", "w", encoding="utf-8") as f:
    json.dump(all_page_info, f, indent=2, ensure_ascii=False)

print("\nSaved mapping to tmp_pages/p7_page_mapping.json")
