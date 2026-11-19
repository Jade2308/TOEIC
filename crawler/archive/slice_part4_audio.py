import os
import sys
import json
import av

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

audio_path = "raw_data/TEST 1 - ETS 2023/AUDIO Test 01.mp3"
output_dir = "public/audio/test1"
os.makedirs(output_dir, exist_ok=True)

# Precise timestamp boundaries for 10 talks in Part 4
group_ranges = {
    "g71_73": (1921.0, 2001.0),
    "g74_76": (2001.0, 2081.0),
    "g77_79": (2081.0, 2165.0),
    "g80_82": (2165.0, 2243.0),
    "g83_85": (2243.0, 2325.0),
    "g86_88": (2325.0, 2408.0),
    "g89_91": (2408.0, 2496.0),
    "g92_94": (2496.0, 2579.0),
    "g95_97": (2579.0, 2658.0),
    "g98_100": (2658.0, 2758.0),
}

print(f"Slicing 10 Part 4 audio files from {audio_path}...")

for g_key, (start_sec, end_sec) in group_ranges.items():
    out_file = os.path.join(output_dir, f"part4_{g_key}.mp3")
    print(f"[{g_key}] {start_sec:.1f}s -> {end_sec:.1f}s (dur {end_sec-start_sec:.1f}s) -> {out_file}...")

    in_container = av.open(audio_path)
    in_stream = in_container.streams.audio[0]

    out_container = av.open(out_file, mode="w")
    out_stream = out_container.add_stream("mp3", rate=in_stream.rate)
    out_stream.bit_rate = in_stream.bit_rate or 128000

    seek_target = int(max(0, start_sec - 1.0) / in_stream.time_base)
    in_container.seek(seek_target, stream=in_stream)

    for frame in in_container.decode(in_stream):
        curr_time = float(frame.pts * in_stream.time_base)
        if curr_time < start_sec:
            continue
        if curr_time > end_sec:
            break
        frame.pts = None
        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    for packet in out_stream.encode():
        out_container.mux(packet)

    out_container.close()
    in_container.close()
    size_kb = os.path.getsize(out_file) / 1024
    print(f"  [OK] Saved {out_file} ({size_kb:.1f} KB)")

print("\nAll 10 Part 4 audio files sliced successfully!")
