import fitz
import os

doc_trans = fitz.open("raw_data/TEST 1 - ETS 2023/Transcript Test 1.pdf")
doc_test = fitz.open("raw_data/TEST 1 - ETS 2023/ETS 2023 Test 1.pdf")

os.makedirs("tmp_p3", exist_ok=True)

# Booklet pages:
# page index 6 (booklet p7): Q32-43
# page index 7 (booklet p8): Q44-55
# page index 8 (booklet p9): Q56-64
# page index 9 (booklet p10): Q65-70
for p in range(6, 10):
    pix = doc_test[p].get_pixmap(dpi=150)
    pix.save(f"tmp_p3/booklet_p{p+1}.png")
    print(f"Saved booklet_p{p+1}.png")

# Transcript pages:
# page index 6 (trans p7) to page index 20 (trans p21)
for p in range(6, 21):
    pix = doc_trans[p].get_pixmap(dpi=150)
    pix.save(f"tmp_p3/trans_p{p+1}.png")
    print(f"Saved trans_p{p+1}.png")

print("All Part 3 pages prepared!")
