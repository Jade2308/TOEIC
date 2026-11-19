import json

with open('raw_data/TEST 1 - ETS 2023/test1_audio_segments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total segments: {len(data)}")
for i, s in enumerate(data[:45]):
    text = s.get('text_en', '')
    start = s.get('start_time', 0)
    end = s.get('end_time', 0)
    print(f"[{start:6.2f}s - {end:6.2f}s] {text}")
