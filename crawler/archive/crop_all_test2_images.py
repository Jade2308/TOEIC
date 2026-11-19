import os
import sys
import pymupdf
from PIL import Image
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    doc_path = "raw_data/TEST 2 - ETS 2023/Test 02 ETS 2023 Reading _ Listening.pdf"
    doc = pymupdf.open(doc_path)
    out_dir = Path("public/images/test2")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[-] Extracting images from {doc_path} into {out_dir}...")

    # --- 1. PART 1 PHOTOS (Q1 to Q6) ---
    print("  [1/4] Cropping Part 1 Photos (Q1-Q6)...")
    # Page 2 (idx 1): Q1 top, Q2 bottom
    pix2 = doc[1].get_pixmap(dpi=150)
    im2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)
    # Q1
    q1_crop = im2.crop((230, 95, 960, 780))
    q1_crop.save(out_dir / "part1_q1.jpg", "JPEG", quality=90)
    # Q2
    q2_crop = im2.crop((180, 875, 1025, 1445))
    q2_crop.save(out_dir / "part1_q2.jpg", "JPEG", quality=90)

    # Page 3 (idx 2): Q3 top, Q4 bottom
    pix3 = doc[2].get_pixmap(dpi=150)
    im3 = Image.frombytes("RGB", [pix3.width, pix3.height], pix3.samples)
    # Q3
    q3_crop = im3.crop((200, 95, 1000, 680))
    q3_crop.save(out_dir / "part1_q3.jpg", "JPEG", quality=90)
    # Q4
    q4_crop = im3.crop((200, 775, 1000, 1340))
    q4_crop.save(out_dir / "part1_q4.jpg", "JPEG", quality=90)

    # Page 4 (idx 3): Q5 top, Q6 bottom
    pix4 = doc[3].get_pixmap(dpi=150)
    im4 = Image.frombytes("RGB", [pix4.width, pix4.height], pix4.samples)
    # Q5
    q5_crop = im4.crop((185, 95, 1010, 670))
    q5_crop.save(out_dir / "part1_q5.jpg", "JPEG", quality=90)
    # Q6
    q6_crop = im4.crop((185, 770, 1010, 1340))
    q6_crop.save(out_dir / "part1_q6.jpg", "JPEG", quality=90)
    print("    [✓] Saved part1_q1.jpg through part1_q6.jpg")

    # --- 2. PART 3 GRAPHICS ---
    print("  [2/4] Cropping Part 3 Graphics...")
    # Q62-64 on Page 8 (idx 7)
    pix8 = doc[7].get_pixmap(dpi=150)
    im8 = Image.frombytes("RGB", [pix8.width, pix8.height], pix8.samples)
    g62 = im8.crop((650, 90, 1060, 410))
    g62.save(out_dir / "part3_g62_64.png")
    g62.save(out_dir / "part3_q64.png")

    # Q65-67 & Q68-70 on Page 9 (idx 8)
    pix9 = doc[8].get_pixmap(dpi=150)
    im9 = Image.frombytes("RGB", [pix9.width, pix9.height], pix9.samples)
    g65 = im9.crop((150, 90, 550, 360))
    g65.save(out_dir / "part3_g65_67.png")
    g65.save(out_dir / "part3_q66.png")

    g68 = im9.crop((650, 90, 1060, 410))
    g68.save(out_dir / "part3_g68_70.png")
    g68.save(out_dir / "part3_q70.png")
    print("    [✓] Saved part3 graphics: g62_64, g65_67, g68_70")

    # --- 3. PART 4 GRAPHICS ---
    print("  [3/4] Cropping Part 4 Graphics...")
    # Page 12 (idx 11): Q95-97 left, Q98-100 right
    pix12 = doc[11].get_pixmap(dpi=150)
    im12 = Image.frombytes("RGB", [pix12.width, pix12.height], pix12.samples)
    g95 = im12.crop((140, 95, 570, 345))
    g95.save(out_dir / "part4_g95_97.png")
    g95.save(out_dir / "part4_q97.png")

    g98 = im12.crop((630, 95, 1100, 245))
    g98.save(out_dir / "part4_g98_100.png")
    g98.save(out_dir / "part4_q100.png")
    print("    [✓] Saved part4 graphics: g95_97, g98_100")

    # --- 4. PART 6 & 7 PASSAGE IMAGES ---
    print("  [4/4] Rendering Part 6 & 7 Passages...")
    # Part 6 (pages 16-19, idx 15-18)
    p6_ranges = [
        ("part6_131_134.png", 15),
        ("part6_135_138.png", 16),
        ("part6_139_142.png", 17),
        ("part6_143_146.png", 18),
    ]
    for filename, p_idx in p6_ranges:
        pix = doc[p_idx].get_pixmap(dpi=150)
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        # Crop upper passage region
        passage = im.crop((80, 80, im.width - 80, int(im.height * 0.55)))
        passage.save(out_dir / filename)

    # Part 7 (pages 20 to 39, idx 19 to 38)
    p7_ranges = [
        ("part7_147_148.png", 19, False),
        ("part7_149_150.png", 20, False),
        ("part7_151_152.png", 21, False),
        ("part7_153_154.png", 22, False),
        ("part7_155_157.png", 23, False),
        ("part7_158_160.png", 24, False),
        ("part7_161_164.png", 25, False),
        ("part7_165_167.png", 26, False),
        ("part7_168_171.png", 27, False),
        ("part7_172_175.png", 28, False),
        ("part7_176_180.png", 29, True),   # multi-page
        ("part7_181_185.png", 31, True),
        ("part7_186_190.png", 33, True),
        ("part7_191_195.png", 35, True),
        ("part7_196_200.png", 37, True),
    ]

    for filename, p_idx, is_multi in p7_ranges:
        if not is_multi:
            pix = doc[p_idx].get_pixmap(dpi=150)
            im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Crop passage area (left column or top half)
            passage = im.crop((80, 80, im.width - 80, int(im.height * 0.6)))
            passage.save(out_dir / filename)
        else:
            # Combine 2 pages
            pix1 = doc[p_idx].get_pixmap(dpi=120)
            pix2 = doc[p_idx+1].get_pixmap(dpi=120)
            im1 = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)
            im2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)
            # stitch horizontally or take first page passage
            comb = Image.new("RGB", (im1.width + im2.width, max(im1.height, im2.height)), (255, 255, 255))
            comb.paste(im1, (0, 0))
            comb.paste(im2, (im1.width, 0))
            comb.save(out_dir / filename)

    print("    [✓] Saved all Part 6 & Part 7 passage images")
    print(f"\n[DONE] Image cropping complete! All files in {out_dir}")

if __name__ == "__main__":
    main()
