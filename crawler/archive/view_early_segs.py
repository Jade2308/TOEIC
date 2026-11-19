import json

with open('raw_data/TEST 1 - ETS 2023/part3_whisper_raw.json', 'r', encoding='utf-8') as f:
    segs = json.load(f)

for i in range(50):
    s = segs[i]
    print(f"[{i:02d}] {s['start']:06.1f}s - {s['end']:06.1f}s: {s['text'][:70]}")
