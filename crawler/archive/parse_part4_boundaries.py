import json

with open("raw_data/TEST 1 - ETS 2023/part4_whisper_raw.json", "r", encoding="utf-8") as f:
    segs = json.load(f)

print("=== SEGMENTS BETWEEN 1880s and 2170s ===")
for s in segs:
    if 1880.0 <= s["start"] <= 2170.0:
        print(f"[{s['start']:06.1f}s - {s['end']:06.1f}s]: {s['text']}")
