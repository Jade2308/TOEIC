import sys
from faster_whisper import WhisperModel
import json

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

audio_path = "raw_data/TEST 2 - ETS 2023/Test 02 Audio.mp3"

model = WhisperModel("base.en", device="cpu", compute_type="int8")

# Let's transcribe the Part 2 range (approx 280s to 820s)
# faster-whisper doesn't take start/end directly, but we can decode frames or slice a temporary segment,
# OR we can transcribe the whole audio with word_timestamps=True and find every question header!
print("Transcribing audio to find exact word timestamps for Part 2...")
segments, info = model.transcribe(
    audio_path,
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
)

all_words = []
for seg in segments:
    # only keep segments between 270s and 830s (Part 2)
    if seg.start < 270.0:
        continue
    if seg.start > 830.0:
        break
    if seg.words:
        for w in seg.words:
            all_words.append({
                "word": w.word.strip(),
                "start": round(w.start, 2),
                "end": round(w.end, 2),
                "probability": round(w.probability, 2)
            })

print(f"Collected {len(all_words)} words in Part 2 range.")
with open("scripts/part2_words.json", "w", encoding="utf-8") as f:
    json.dump(all_words, f, indent=2, ensure_ascii=False)
print("Saved scripts/part2_words.json")
