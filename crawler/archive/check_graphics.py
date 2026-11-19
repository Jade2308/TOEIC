import fitz
import os
from PIL import Image

doc_test = fitz.open("raw_data/TEST 1 - ETS 2023/ETS 2023 Test 1.pdf")
os.makedirs("public/images/test1", exist_ok=True)

# Let's render page 8 (0-indexed, booklet page 9) and page 9 (0-indexed, booklet page 10)
p8 = doc_test[8]
p9 = doc_test[9]

# On page 8: Questions 56-64. Questions 62-64 refer to "the following conversation and schedule"
# Let's crop the schedule graphic.
# Let's find images or rects on page 8:
print("Page 8 rect:", p8.rect)
print("Page 9 rect:", p9.rect)

# We can render at 300 DPI (approx 4.16x scale: 72 -> 300)
# Let's save the whole page 8 and page 9 as high-res images and also check layout:
pix8 = p8.get_pixmap(dpi=150)
pix8.save("tmp_pages/booklet_p9.png")
pix9 = p9.get_pixmap(dpi=150)
pix9.save("tmp_pages/booklet_p10.png")

print(f"Saved booklet_p9.png ({pix8.width}x{pix8.height}) and booklet_p10.png ({pix9.width}x{pix9.height})")
