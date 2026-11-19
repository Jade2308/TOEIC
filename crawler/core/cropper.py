from __future__ import annotations

"""
PDF Image and Reading Passage Cropping Module using PyMuPDF (fitz) and Pillow.
Supports dynamic page-offset discovery across different ETS TOEIC book editions.
"""

import shutil
from pathlib import Path
from typing import Optional

try:
    import pymupdf
    from PIL import Image
except ImportError:
    pymupdf = None
    Image = None


def detect_base_offset(doc: pymupdf.Document) -> int:
    """Calculates page index offset based on total document pages and cover layout."""
    total_pages = len(doc)
    if total_pages >= 41:
        return 1
    elif total_pages == 40:
        return 0
    else:
        # Fallback for other scans
        return max(0, total_pages - 40)


def process_images_pipeline(
    test_pdf_path: Path,
    output_image_dir: Path,
    secondary_image_dir: Optional[Path] = None,
):
    """Crops Part 1 photos, Part 3/4 graphics, and Part 6/7 passages from the test PDF."""
    if pymupdf is None or Image is None:
        raise ImportError("Packages 'pymupdf' and 'pillow' are required for image cropping.")

    output_image_dir.mkdir(parents=True, exist_ok=True)
    if secondary_image_dir:
        secondary_image_dir.mkdir(parents=True, exist_ok=True)

    # Check if images already exist
    q1_img = output_image_dir / "part1_q1.jpg"
    p7_end_img = output_image_dir / "part7_196_200.png"
    p7_check = output_image_dir / "part7_173_175.png"
    if q1_img.exists() and p7_end_img.exists() and p7_check.exists():
        print(f"  [✓] All cropped images already present in {output_image_dir}")
        if secondary_image_dir:
            for f in output_image_dir.glob("*.*"):
                sec_f = secondary_image_dir / f.name
                if not sec_f.exists():
                    shutil.copy2(f, sec_f)
        return

    doc = pymupdf.open(str(test_pdf_path))
    offset = detect_base_offset(doc)
    print(f"  [➔] Cropping images from test PDF ({len(doc)} pages, page offset: +{offset})...")

    # 1. Part 1 Photos (Q1 to Q6)
    idx_p1 = 1 + offset
    pix_a = doc[idx_p1].get_pixmap(dpi=150)
    im_a = Image.frombytes("RGB", [pix_a.width, pix_a.height], pix_a.samples)
    im_a.crop((180, 95, 1000, 780)).save(output_image_dir / "part1_q1.jpg", "JPEG", quality=92)
    im_a.crop((180, 870, 1025, 1450)).save(output_image_dir / "part1_q2.jpg", "JPEG", quality=92)

    pix_b = doc[idx_p1 + 1].get_pixmap(dpi=150)
    im_b = Image.frombytes("RGB", [pix_b.width, pix_b.height], pix_b.samples)
    im_b.crop((180, 95, 1000, 680)).save(output_image_dir / "part1_q3.jpg", "JPEG", quality=92)
    im_b.crop((180, 770, 1000, 1340)).save(output_image_dir / "part1_q4.jpg", "JPEG", quality=92)

    pix_c = doc[idx_p1 + 2].get_pixmap(dpi=150)
    im_c = Image.frombytes("RGB", [pix_c.width, pix_c.height], pix_c.samples)
    im_c.crop((180, 95, 1010, 680)).save(output_image_dir / "part1_q5.jpg", "JPEG", quality=92)
    im_c.crop((180, 770, 1010, 1340)).save(output_image_dir / "part1_q6.jpg", "JPEG", quality=92)

    # 2. Part 3 Graphics
    idx_p3_1 = 7 + offset
    idx_p3_2 = 8 + offset
    pix_p3_1 = doc[idx_p3_1].get_pixmap(dpi=150)
    im_p3_1 = Image.frombytes("RGB", [pix_p3_1.width, pix_p3_1.height], pix_p3_1.samples)
    g62 = im_p3_1.crop((550, 90, 1080, 420))
    g62.save(output_image_dir / "part3_g62_64.png")
    g62.save(output_image_dir / "part3_q64.png")

    pix_p3_2 = doc[idx_p3_2].get_pixmap(dpi=150)
    im_p3_2 = Image.frombytes("RGB", [pix_p3_2.width, pix_p3_2.height], pix_p3_2.samples)
    g65 = im_p3_2.crop((110, 90, 560, 480))
    g65.save(output_image_dir / "part3_g65_67.png")
    g65.save(output_image_dir / "part3_q66.png")

    g68 = im_p3_2.crop((600, 90, 1080, 420))
    g68.save(output_image_dir / "part3_g68_70.png")
    g68.save(output_image_dir / "part3_q70.png")

    # 3. Part 4 Graphics
    idx_p4 = 11 + offset
    pix_p4 = doc[idx_p4].get_pixmap(dpi=150)
    im_p4 = Image.frombytes("RGB", [pix_p4.width, pix_p4.height], pix_p4.samples)
    g95 = im_p4.crop((60, 90, 560, 480))
    g95.save(output_image_dir / "part4_g95_97.png")
    g95.save(output_image_dir / "part4_q97.png")

    g98 = im_p4.crop((560, 90, 1100, 480))
    g98.save(output_image_dir / "part4_g98_100.png")
    g98.save(output_image_dir / "part4_q100.png")

    # 4. Part 6 Passages (Pages 16-19 in 41-page book)
    p6_ranges = [
        ("part6_131_134.png", 15 + offset),
        ("part6_135_138.png", 16 + offset),
        ("part6_139_142.png", 17 + offset),
        ("part6_143_146.png", 18 + offset),
    ]
    for fn, idx in p6_ranges:
        if idx < len(doc):
            pix = doc[idx].get_pixmap(dpi=150)
            im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            im.crop((80, 80, im.width - 80, int(im.height * 0.58))).save(output_image_dir / fn)

    # 5. Part 7 Passages (Pages 20-40 in 41-page book)
    p7_ranges = [
        ("part7_147_148.png", 19 + offset, False),
        ("part7_149_150.png", 20 + offset, False),
        ("part7_151_152.png", 21 + offset, False),
        ("part7_153_154.png", 22 + offset, False),
        ("part7_155_157.png", 23 + offset, False),
        ("part7_158_160.png", 24 + offset, False),
        ("part7_158_161.png", 24 + offset, False),
        ("part7_161_164.png", 25 + offset, False),
        ("part7_161_163.png", 25 + offset, False),
        ("part7_162_165.png", 25 + offset, False),
        ("part7_164_167.png", 26 + offset, False),
        ("part7_165_167.png", 26 + offset, False),
        ("part7_166_168.png", 26 + offset, False),
        ("part7_168_171.png", 27 + offset, False),
        ("part7_169_172.png", 27 + offset, False),
        ("part7_172_175.png", 28 + offset, False),
        ("part7_173_175.png", 28 + offset, False),
        ("part7_176_180.png", 30 + offset, True),
        ("part7_181_185.png", 32 + offset, True),
        ("part7_186_190.png", 34 + offset, True),
        ("part7_191_195.png", 36 + offset, True),
        ("part7_196_200.png", 38 + offset, True),
    ]
    for fn, idx, is_multi in p7_ranges:
        if idx >= len(doc):
            continue
        if not is_multi:
            pix = doc[idx].get_pixmap(dpi=150)
            im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            im.crop((80, 80, im.width - 80, int(im.height * 0.62))).save(output_image_dir / fn)
        else:
            if idx + 1 < len(doc):
                pix1 = doc[idx].get_pixmap(dpi=130)
                pix2 = doc[idx + 1].get_pixmap(dpi=130)
                im1 = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)
                im2 = Image.frombytes("RGB", [pix2.width, pix2.height], pix2.samples)
                comb = Image.new("RGB", (im1.width + im2.width, max(im1.height, im2.height)), (255, 255, 255))
                comb.paste(im1, (0, 0))
                comb.paste(im2, (im1.width, 0))
                comb.save(output_image_dir / fn)

    # Sync to secondary dir
    if secondary_image_dir:
        for f in output_image_dir.glob("*.*"):
            sec_f = secondary_image_dir / f.name
            shutil.copy2(f, sec_f)

    print(f"  [✓] All images cropped successfully into {output_image_dir}")
