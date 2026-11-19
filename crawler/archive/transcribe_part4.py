import os
import sys
import json
import time
from faster_whisper import WhisperModel
import av
import numpy as np

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

audio_path = "raw_data/TEST 1 - ETS 2023/AUDIO Test 01.mp3"
output_json = "processed_data/TEST 1 - ETS 2023/intermediate/whisper/part4_whisper_raw.json"
os.makedirs(os.path.dirname(output_json), exist_ok=True)

print("Loading Whisper model (base.en on cpu)...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")

print(f"Transcribing Part 4 audio from {audio_path}...")
start_time = time.time()

container = av.open(audio_path)
stream = container.streams.audio[0]

resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)

audio_frames = []
start_sec = 1850.0
end_sec = 2760.0

target_pts = int(start_sec / stream.time_base)
container.seek(target_pts, stream=stream)

for frame in container.decode(stream):
    frame_time = float(frame.pts * stream.time_base)
    if frame_time < start_sec:
        continue
    if frame_time > end_sec:
        break
    resampled = resampler.resample(frame)
    for r in resampled:
        audio_frames.append(r.to_ndarray())

if not audio_frames:
    print("No audio frames decoded!")
    sys.exit(1)

audio_data = np.concatenate(audio_frames, axis=1).squeeze()
audio_float = audio_data.astype(np.float32) / 32768.0

print(f"Decoded {len(audio_float)/16000:.2f} seconds of audio. Running Whisper...")

segments, info = model.transcribe(audio_float, language="en", beam_size=5, word_timestamps=True)

results = []
for seg in segments:
    abs_start = round(start_sec + seg.start, 2)
    abs_end = round(start_sec + seg.end, 2)
    words = []
    if seg.words:
        for w in seg.words:
            words.append({
                "word": w.word,
                "start": round(start_sec + w.start, 2),
                "end": round(start_sec + w.end, 2),
                "probability": round(w.probability, 2)
            })
    results.append({
        "id": seg.id,
        "start": abs_start,
        "end": abs_end,
        "text": seg.text.strip(),
        "words": words
    })
    print(f"[{abs_start:06.1f}s -> {abs_end:06.1f}s]: {seg.text.strip()[:60]}")

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Done in {time.time()-start_time:.1f}s. Saved {len(results)} segments to {output_json}.")
