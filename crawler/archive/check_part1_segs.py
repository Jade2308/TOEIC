import json

with open("raw_data/TEST 1 - ETS 2023/test1_part1_segments.json", "r", encoding="utf-8") as f:
    segs = json.load(f)

for idx, s in enumerate(segs):
    start = s.get("start_time", 0)
    end = s.get("end_time", 0)
    text = s.get("text_en", "")
    print(f"[{idx:02d}] {start:6.2f}s - {end:6.2f}s | {text}")
