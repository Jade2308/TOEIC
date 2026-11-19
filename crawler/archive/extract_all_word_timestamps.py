import sys
import time
import json
from faster_whisper import WhisperModel

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

audio_path = "raw_data/TEST 2 - ETS 2023/Test 02 Audio.mp3"
output_path = "scripts/all_audio_words.json"

print(f"Loading WhisperModel base.en...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")

t0 = time.time()
print(f"Transcribing full audio with word-level timestamps: {audio_path}")
segments, info = model.transcribe(
    audio_path,
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
)

all_words = []
seg_count = 0
for seg in segments:
    seg_count += 1
    if seg.words:
        for w in seg.words:
            all_words.append({
                "word": w.word.strip(),
                "start": round(w.start, 2),
                "end": round(w.end, 2),
                "probability": round(w.probability, 2)
            })
    if seg_count % 50 == 0:
        print(f"  Processed {seg_count} segments (at {seg.end:.1f}s)...")

t1 = time.time()
print(f"Transcription complete in {t1 - t0:.1f}s. Total words collected: {len(all_words)}")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_words, f, indent=2, ensure_ascii=False)

print(f"Saved all word timestamps to {output_path}")
