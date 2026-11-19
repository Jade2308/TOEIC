import os
import sys
import json
import av
from faster_whisper import WhisperModel

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

def slice_audio(in_path, out_path, start_sec, end_sec):
    in_container = av.open(in_path)
    in_stream = in_container.streams.audio[0]
    
    out_container = av.open(out_path, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    
    start_pts = int(start_sec / in_stream.time_base)
    end_pts = int(end_sec / in_stream.time_base)
    in_container.seek(start_pts, stream=in_stream)
    
    for frame in in_container.decode(in_stream):
        if frame.pts < start_pts:
            continue
        if frame.pts > end_pts:
            break
        for packet in out_stream.encode(frame):
            out_container.mux(packet)
            
    for packet in out_stream.encode(None):
        out_container.mux(packet)
        
    out_container.close()
    in_container.close()

# Time ranges for Q1-Q6 in test 1 audio
ranges = {
    1: (96.0, 124.0),
    2: (124.0, 153.0),
    3: (153.0, 183.0),
    4: (183.0, 208.0),
    5: (208.0, 234.0),
    6: (234.0, 261.0),
}

audio_src = "public/audio/test1/audio_test01.mp3"
os.makedirs("public/audio/test1", exist_ok=True)

print("[-] Slicing audio files for Questions 1-6...")
for q_num, (start_t, end_t) in ranges.items():
    out_file = f"public/audio/test1/part1_q{q_num}.mp3"
    slice_audio(audio_src, out_file, start_t, end_t)
    print(f"  [✓] Q{q_num}: {out_file} ({start_t}s - {end_t}s, size: {os.path.getsize(out_file)} bytes)")

print("\n[-] Transcribing individual slices with faster-whisper (CPU int8)...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")

q_segments = {}
for q_num in range(1, 7):
    clip_path = f"public/audio/test1/part1_q{q_num}.mp3"
    segments_gen, _ = model.transcribe(clip_path, beam_size=5, vad_filter=False)
    segs = []
    for s in segments_gen:
        text = s.text.strip()
        is_trap = "is being" in text.lower() or "are being" in text.lower()
        segs.append({
            "id": f"seg-q{q_num}-{len(segs)+1}",
            "speaker": "Speaker",
            "start_time": round(s.start, 2),
            "end_time": round(s.end, 2),
            "text_en": text,
            "text_vi": "",
            "is_trap": is_trap
        })
    q_segments[q_num] = segs
    print(f"  [✓] Q{q_num}: {len(segs)} segments extracted")
    for s in segs:
        trap = " [TRAP CANDIDATE]" if s["is_trap"] else ""
        print(f"      [{s['start_time']:04.1f}s - {s['end_time']:04.1f}s] {s['text_en']}{trap}")

with open("raw_data/TEST 1 - ETS 2023/part1_sliced_segments.json", "w", encoding="utf-8") as f:
    json.dump(q_segments, f, ensure_ascii=False, indent=2)

print("\n[DONE] Saved sliced segments to raw_data/TEST 1 - ETS 2023/part1_sliced_segments.json")
