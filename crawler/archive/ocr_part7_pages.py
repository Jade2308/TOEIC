import os
import json
import asyncio
from PIL import Image
import winocr

async def process_all_pages():
    results = {}
    for p in range(21, 44):
        img_path = f"tmp_pages/p7_pages/page_{p}.png"
        if not os.path.exists(img_path):
            print(f"File {img_path} not found.")
            continue
        
        img = Image.open(img_path)
        res = await winocr.recognize_pil(img)
        lines = [line.text for line in res.lines]
        results[p] = {
            "page": p,
            "lines": lines,
            "raw_text": "\n".join(lines)
        }
        print(f"Page {p}: extracted {len(lines)} lines")

    with open("tmp_pages/p7_ocr_all.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nSaved all OCR results to tmp_pages/p7_ocr_all.json")

if __name__ == "__main__":
    asyncio.run(process_all_pages())
