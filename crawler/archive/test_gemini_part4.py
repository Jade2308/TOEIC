import os
import sys
import json
from dotenv import load_dotenv
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
load_dotenv(".env.local")
from google import genai
from google.genai import types

client = genai.Client()

print("Opening images...", flush=True)
im_book = Image.open("tmp_p3/booklet_p11.png")
im_t20 = Image.open("tmp_p4/trans_p20.png")
im_t21 = Image.open("tmp_p4/trans_p21.png")
print("Images opened. Calling Gemini 2.5-flash...", flush=True)

prompt = "Transcribe Questions 71-73 text, options, and transcript from the images. Return short JSON."
res = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[im_book, im_t20, im_t21, prompt],
    config=types.GenerateContentConfig(response_mime_type="application/json")
)
print("Response received!", flush=True)
print(res.text[:300], flush=True)
