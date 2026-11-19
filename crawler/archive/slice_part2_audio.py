import os
import sys
import json
import av
from faster_whisper import WhisperModel

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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
        frame.pts = None
        for packet in out_stream.encode(frame):
            out_container.mux(packet)
            
    for packet in out_stream.encode(None):
        out_container.mux(packet)
        
    out_container.close()
    in_container.close()

# Time ranges for Q7-Q31 in test 1 audio
ranges = {
    7:  (293.8, 310.8),
    8:  (313.1, 330.9),
    9:  (332.6, 350.4),
    10: (352.0, 370.2),
    11: (370.3, 390.0),
    12: (391.0, 410.2),
    13: (410.3, 427.4),
    14: (429.5, 446.4),
    15: (448.1, 466.9),
    16: (468.6, 487.9),
    17: (488.0, 506.9),
    18: (507.0, 526.1),
    19: (528.1, 546.2),
    20: (547.9, 566.4),
    21: (568.0, 585.3),
    22: (587.1, 607.8),
    23: (608.7, 628.5),
    24: (630.6, 650.8),
    25: (652.5, 672.4),
    26: (673.9, 692.9),
    27: (694.6, 715.1),
    28: (716.2, 736.9),
    29: (738.6, 758.6),
    30: (760.4, 779.6),
    31: (781.3, 801.8),
}

audio_src = "public/audio/test1/audio_test01.mp3"
os.makedirs("public/audio/test1", exist_ok=True)

print("[-] Slicing audio files for Questions 7-31...")
for q_num, (start_t, end_t) in ranges.items():
    out_file = f"public/audio/test1/part2_q{q_num}.mp3"
    slice_audio(audio_src, out_file, start_t, end_t)
    size = os.path.getsize(out_file)
    print(f"  [✓] Q{q_num:2d}: {out_file} ({start_t:6.1f}s - {end_t:6.1f}s, size: {size} bytes)")

print("\n[-] Transcribing individual slices with faster-whisper to get relative segment timestamps...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")

q_segments = {}
for q_num in range(7, 32):
    clip_path = f"public/audio/test1/part2_q{q_num}.mp3"
    segments_gen, _ = model.transcribe(clip_path, beam_size=5, vad_filter=False)
    raw_segs = list(segments_gen)
    
    # Store raw segments per question slice
    slice_segs = []
    for s in raw_segs:
        slice_segs.append({
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": s.text.strip()
        })
    q_segments[q_num] = slice_segs
    print(f"  [✓] Q{q_num:2d}: {len(slice_segs)} segments extracted")
    for s in slice_segs:
        print(f"      [{s['start']:04.1f}s - {s['end']:04.1f}s] {s['text']}")

os.makedirs("raw_data/TEST 1 - ETS 2023", exist_ok=True)
with open("raw_data/TEST 1 - ETS 2023/part2_sliced_raw_segments.json", "w", encoding="utf-8") as f:
    json.dump(q_segments, f, ensure_ascii=False, indent=2)

print("\n[DONE] Slicing and per-clip transcription complete!")
