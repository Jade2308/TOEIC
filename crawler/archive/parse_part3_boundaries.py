import json

with open('raw_data/TEST 1 - ETS 2023/part3_whisper_raw.json', 'r', encoding='utf-8') as f:
    segs = json.load(f)

print(f"Total segments: {len(segs)}")
for i, s in enumerate(segs):
    t = s['text']
    if any(k in t.lower() for k in ['question', 'questions', 'refer to', 'part 4', 'go on to']):
        print(f"[{i:03d}] {s['start']:06.1f}s -> {s['end']:06.1f}s: {t}")
