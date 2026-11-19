import json
import os
import sys
from PIL import Image
from dotenv import load_dotenv

load_dotenv(".env.local")
from google import genai
client = genai.Client()

im9 = Image.open("tmp_pages/booklet_p9.png")
im10 = Image.open("tmp_pages/booklet_p10.png")

f9 = client.files.upload(file="tmp_pages/booklet_p9.png")
f10 = client.files.upload(file="tmp_pages/booklet_p10.png")

prompt = """
Examine the two test booklet pages:
1. In booklet_p9.png (Questions 56-64), find the schedule graphic table for Questions 62-64.
Provide bounding box in pixel coordinates [ymin, xmin, ymax, xmax] for the 1275x1650 image.
2. In booklet_p10.png (Questions 65-70):
a) Find the map graphic for Questions 65-67.
Provide bounding box [ymin, xmin, ymax, xmax] for the 1275x1650 image.
b) Find the catalog / table graphic for Questions 68-70.
Provide bounding box [ymin, xmin, ymax, xmax] for the 1275x1650 image.

Return valid JSON strictly in this format:
{
  "g62_64": [ymin, xmin, ymax, xmax],
  "g65_67": [ymin, xmin, ymax, xmax],
  "g68_70": [ymin, xmin, ymax, xmax]
}
"""

for model_name in ["gemini-2.5-flash", "gemini-2.0-flash"]:
    try:
        print(f"Calling {model_name}...")
        res = client.models.generate_content(
            model=model_name,
            contents=[f9, f10, prompt],
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(res.text)
        print("Received boxes:", data)
        break
    except Exception as e:
        print(f"Error with {model_name}: {e}")

# Crop images
b62 = data["g62_64"]
crop62 = im9.crop((b62[1], b62[0], b62[3], b62[2]))
crop62.save("public/images/test1/part3_g62_64.png")
print("Saved public/images/test1/part3_g62_64.png")

b65 = data["g65_67"]
crop65 = im10.crop((b65[1], b65[0], b65[3], b65[2]))
crop65.save("public/images/test1/part3_g65_67.png")
print("Saved public/images/test1/part3_g65_67.png")

b68 = data["g68_70"]
crop68 = im10.crop((b68[1], b68[0], b68[3], b68[2]))
crop68.save("public/images/test1/part3_g68_70.png")
print("Saved public/images/test1/part3_g68_70.png")
