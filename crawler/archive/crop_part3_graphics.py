import fitz
import os

doc_test = fitz.open("raw_data/TEST 1 - ETS 2023/ETS 2023 Test 1.pdf")
os.makedirs("public/images/test1", exist_ok=True)

# p9 (index 8): has Questions 56-64. Questions 62-64 has a graphic (table or schedule or map)
# Let's render page 8 and page 9 at 200 DPI
page8 = doc_test[8]
pix8 = page8.get_pixmap(dpi=200)
pix8.save("tmp_pages/p9_200dpi.png")

page9 = doc_test[9]
pix9 = page9.get_pixmap(dpi=200)
pix9.save("tmp_pages/p10_200dpi.png")

from PIL import Image

im8 = Image.open("tmp_pages/p9_200dpi.png")
w8, h8 = im8.size

im9 = Image.open("tmp_pages/p10_200dpi.png")
w9, h9 = im9.size

# Let's inspect the positions of the graphics using Gemini Flash
from dotenv import load_dotenv
load_dotenv(".env.local")
from google import genai
client = genai.Client()

f8 = client.files.upload(file="tmp_pages/p9_200dpi.png")
f9 = client.files.upload(file="tmp_pages/p10_200dpi.png")

prompt = """
Look at the two pages:
1. In the first image (page 9 of booklet, Questions 56-64), find the graphic accompanying Questions 62-64.
Give the exact bounding box [ymin, xmin, ymax, xmax] normalized to 1000.
2. In the second image (page 10 of booklet, Questions 65-70):
a) Graphic for Questions 65-67: bounding box [ymin, xmin, ymax, xmax] normalized to 1000.
b) Graphic for Questions 68-70: bounding box [ymin, xmin, ymax, xmax] normalized to 1000.

Return JSON in this format:
{
  "g62_64": [ymin, xmin, ymax, xmax],
  "g65_67": [ymin, xmin, ymax, xmax],
  "g68_70": [ymin, xmin, ymax, xmax]
}
"""

res = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[f8, f9, prompt],
    config={"response_mime_type": "application/json"}
)

import json
data = json.loads(res.text)
print("Detected boxes:", data)

# Crop and save
b62 = data["g62_64"]
box62 = (int(b62[1]*w8/1000), int(b62[0]*h8/1000), int(b62[3]*w8/1000), int(b62[2]*h8/1000))
crop62 = im8.crop(box62)
crop62.save("public/images/test1/part3_g62_64.png")
print("Saved public/images/test1/part3_g62_64.png")

b65 = data["g65_67"]
box65 = (int(b65[1]*w9/1000), int(b65[0]*h9/1000), int(b65[3]*w9/1000), int(b65[2]*h9/1000))
crop65 = im9.crop(box65)
crop65.save("public/images/test1/part3_g65_67.png")
print("Saved public/images/test1/part3_g65_67.png")

b68 = data["g68_70"]
box68 = (int(b68[1]*w9/1000), int(b68[0]*h9/1000), int(b68[3]*w9/1000), int(b68[2]*h9/1000))
crop68 = im9.crop(box68)
crop68.save("public/images/test1/part3_g68_70.png")
print("Saved public/images/test1/part3_g68_70.png")
