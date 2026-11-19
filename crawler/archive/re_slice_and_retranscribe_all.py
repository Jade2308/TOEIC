import os
import sys
import json
import time
import av
from pathlib import Path
from faster_whisper import WhisperModel

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def slice_audio(in_path, out_path, start_sec, end_sec):
    in_container = av.open(in_path)
    in_stream = in_container.streams.audio[0]
    out_container = av.open(out_path, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    out_stream.bit_rate = in_stream.bit_rate or 128000

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

def main():
    audio_path = "raw_data/TEST 2 - ETS 2023/Test 02 Audio.mp3"
    out_dir = Path("public/audio/test2")
    out_dir.mkdir(parents=True, exist_ok=True)

    segments_dir = Path("processed_data/TEST 2 - ETS 2023/intermediate/segments")
    segments_dir.mkdir(parents=True, exist_ok=True)

    with open("scripts/exact_audio_ranges.json", "r", encoding="utf-8") as f:
        ranges = json.load(f)

    p1_ranges = ranges["part1"]
    p2_ranges = ranges["part2"]
    p3_ranges = ranges["part3"]
    p4_ranges = ranges["part4"]

    print("[1/2] Slicing all 54 audio clips with exact timestamps...")
    t0 = time.time()
    
    # Part 1
    for q_str, (s, e) in p1_ranges.items():
        dst = out_dir / f"part1_q{q_str}.mp3"
        slice_audio(audio_path, str(dst), s, e)
    print(f"  [✓] Part 1 (6 clips) sliced.")

    # Part 2
    for q_str, (s, e) in p2_ranges.items():
        dst = out_dir / f"part2_q{q_str}.mp3"
        slice_audio(audio_path, str(dst), s, e)
    print(f"  [✓] Part 2 (25 clips) sliced.")

    # Part 3
    for g_key, (s, e) in p3_ranges.items():
        dst = out_dir / f"part3_{g_key}.mp3"
        slice_audio(audio_path, str(dst), s, e)
    print(f"  [✓] Part 3 (13 clips) sliced.")

    # Part 4
    for g_key, (s, e) in p4_ranges.items():
        dst = out_dir / f"part4_{g_key}.mp3"
        slice_audio(audio_path, str(dst), s, e)
    print(f"  [✓] Part 4 (10 clips) sliced.")

    print(f"  --> All 54 clips re-sliced in {time.time()-t0:.1f}s.")

    print("\n[2/2] Transcribing slices with faster-whisper (base.en, cpu, int8)...")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")

    sliced_segments_data = {
        "part1": {},
        "part2": {},
        "part3": {},
        "part4": {},
    }

    # Transcribe Part 1
    print("  [-] Transcribing Part 1 (Q1-Q6)...")
    for q in range(1, 7):
        clip = str(out_dir / f"part1_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        q_segs = []
        for s in raw:
            t = s.text.strip()
            is_trap = "is being" in t.lower() or "are being" in t.lower()
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": t,
                "text_vi": "",
                "is_trap": is_trap,
            })
        sliced_segments_data["part1"][str(q)] = q_segs

    # Transcribe Part 2
    print("  [-] Transcribing Part 2 (Q7-Q31)...")
    for q in range(7, 32):
        clip = str(out_dir / f"part2_q{q}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        q_segs = []
        for s in raw:
            q_segs.append({
                "id": f"seg-q{q}-{len(q_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part2"][str(q)] = q_segs

    # Transcribe Part 3
    print("  [-] Transcribing Part 3 (13 groups)...")
    for g_key in p3_ranges.keys():
        clip = str(out_dir / f"part3_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        g_segs = []
        for s in raw:
            g_segs.append({
                "id": f"seg-p3-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part3"][g_key] = g_segs

    # Transcribe Part 4
    print("  [-] Transcribing Part 4 (10 groups)...")
    for g_key in p4_ranges.keys():
        clip = str(out_dir / f"part4_{g_key}.mp3")
        segs_gen, _ = model.transcribe(clip, beam_size=5)
        raw = list(segs_gen)
        g_segs = []
        for s in raw:
            g_segs.append({
                "id": f"seg-p4-{g_key}-{len(g_segs)+1}",
                "speaker": "Speaker",
                "start_time": round(s.start, 2),
                "end_time": round(s.end, 2),
                "text_en": s.text.strip(),
                "text_vi": "",
                "is_trap": False,
            })
        sliced_segments_data["part4"][g_key] = g_segs

    out_json = segments_dir / "sliced_audio_segments.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(sliced_segments_data, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Audio processing complete! All 54 clips sliced & transcribed into {out_dir}")
    print(f"  ➔ Saved segment metadata to {out_json}")

if __name__ == "__main__":
    main()
