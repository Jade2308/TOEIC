# TOEIC Adaptive Coaching - Python Data Pipeline

Thư mục này chứa bộ công cụ tự động hóa xử lý dữ liệu đề thi TOEIC:
1. **`process_audio.py`**: Nhận diện âm thanh bài nghe TOEIC bằng **faster-whisper** trên GPU NVIDIA CUDA `float16` (tối ưu hóa cho RTX 3060) và xuất mảng `transcript_segments` có mốc thời gian `start_time` và `end_time` chính xác.
2. **`extract_pdf.py`**: Trích xuất đề thi và đáp án từ file PDF bằng **Google GenAI SDK (Gemini 2.5 Flash)** với tính năng **Structured Outputs (JSON Schema)**, tự động viết giải thích tiếng Việt (`explanation_vi`), phân loại dạng câu (`question_type_tag`), trích dẫn bằng chứng (`evidence_quote`) và cặp từ đồng nghĩa (`paraphrase_pair`).

---

## 1. Môi Trường Conda (`toeic-pipeline`)

Toàn bộ thư viện đã được cài đặt sẵn trong môi trường conda `toeic-pipeline`.

### Kích hoạt môi trường:
```powershell
conda activate toeic-pipeline
```

### Kiểm tra GPU CUDA (RTX 3060):
```powershell
python -c "import ctranslate2; print('CUDA Devices:', ctranslate2.get_cuda_device_count())"
```
> Kết quả: `CUDA Devices: 1` (Đã sẵn sàng tăng tốc phần cứng với Tensor Cores float16).

### Cấu hình API Key cho Gemini:
Tạo hoặc bổ sung vào file `.env` ở thư mục gốc:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 2. Xử Lý Âm Thanh: `process_audio.py`

Đọc file âm thanh MP3/WAV, cắt lọc khoảng lặng với VAD (Voice Activity Detection), nhận diện lời thoại và xuất mảng JSON `transcript_segments` đúng chuẩn `SPECIFICATION.md`.

### Cú pháp:
```powershell
python scripts/process_audio.py <đường_dẫn_file_mp3> [tùy_chọn]
```

### Các tham số chính:
| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `input_audio` | Đường dẫn file MP3/WAV cần phiên âm | *(Bắt buộc)* |
| `-o`, `--output` | Đường dẫn file JSON xuất ra | `<tên_file>_transcript.json` |
| `-m`, `--model-size` | Kích thước mô hình Whisper (`tiny.en`, `base.en`, `small.en`, `medium.en`) | `base.en` |
| `-d`, `--device` | Thiết bị xử lý (`cuda` hoặc `cpu`) | Tự động phát hiện `cuda` |
| `-c`, `--compute-type` | Kiểu tính toán (`float16`, `int8`, `float32`) | `float16` (RTX 3060) |
| `-p`, `--part` | Part thi nghe TOEIC (1, 2, 3, hoặc 4) để kích hoạt heuristic nhận diện bẫy | Không giới hạn |
| `--no-vad` | Tắt bộ lọc khoảng lặng Silero VAD | Mặc định bật VAD |

### Ví dụ thực tế:

#### Ví dụ 1: Phiên âm audio Part 1 (nhận diện bẫy thì "being V3")
```powershell
python scripts/process_audio.py audio/part1_test1.mp3 -o audio/part1_transcript.json -p 1 -m small.en
```

#### Ví dụ 2: Phiên âm audio Part 2 (nhận diện câu hỏi WH và bẫy lặp âm)
```powershell
python scripts/process_audio.py audio/part2_test1.mp3 -o audio/part2_transcript.json -p 2
```

#### Ví dụ 3: Phiên âm đoạn hội thoại Part 3 / Part 4 (luân phiên Man / Woman)
```powershell
python scripts/process_audio.py audio/part3_test1.mp3 -o audio/part3_transcript.json -p 3 -m small.en
```

### Cấu trúc file JSON xuất ra:
```json
[
  {
    "id": "seg-001",
    "speaker": "Speaker",
    "start_time": 0.0,
    "end_time": 3.45,
    "text_en": "A laptop is being repaired on the desk.",
    "text_vi": "",
    "is_trap": true
  },
  {
    "id": "seg-002",
    "speaker": "Speaker",
    "start_time": 4.1,
    "end_time": 7.3,
    "text_en": "A woman is typing on a computer keyboard.",
    "text_vi": "",
    "is_trap": false
  }
]
```

---

## 3. Trích Xuất Đề Thi PDF: `extract_pdf.py`

Sử dụng **Google GenAI SDK (Gemini 2.5 Flash)** với **Structured Outputs (Pydantic JSON Schema)** để đọc trực tiếp file PDF đề thi và file PDF đáp án, tự động:
- Trích xuất toàn bộ câu hỏi và 4 phương án lựa chọn.
- So khớp với file đáp án để xác định `correct_answer`.
- Viết giải thích tiếng Việt chuyên sâu (`explanation_vi`) bao gồm: cấu trúc ngữ pháp, lý do chọn, phân tích bẫy đề thi ETS và mẹo phản xạ 10s.
- Gắn nhãn phân loại dạng câu (`question_type_tag`).
- Bóc tách dẫn chứng gốc (`evidence_quote`) và cặp từ đồng nghĩa (`paraphrase_pair`).
- Định dạng sẵn cho 2 bảng Supabase: `question_groups` và `questions`.

### Cú pháp:
```powershell
python scripts/extract_pdf.py --test-pdf <file_de_thi.pdf> [tùy_chọn]
```

### Các tham số chính:
| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `--test-pdf` | File PDF đề bài (câu hỏi, hình ảnh, bài đọc) | *(Bắt buộc)* |
| `--answer-pdf` | File PDF đáp án (nếu tách rời đề bài) | `None` |
| `-o`, `--output` | Đường dẫn file JSON xuất ra | `toeic_extracted.json` |
| `-m`, `--model` | Model Gemini sử dụng | `gemini-2.5-flash` |
| `-p`, `--part` | Chỉ trích xuất Part cụ thể (1 đến 7) | Trích xuất toàn bộ |
| `--test-name` | Tên đề thi (ví dụ: "ETS 2024 - Test 1") | `ETS TOEIC Test` |
| `--audio-transcript` | Ghép file JSON kết quả từ `process_audio.py` vào `transcript_segments` | `None` |
| `--import-supabase` | Tự động chèn trực tiếp vào database Supabase nếu có `.env` | `False` |

### Ví dụ thực tế:

#### Ví dụ 1: Trích xuất trọn vẹn đề thi kèm đáp án
```powershell
python scripts/extract_pdf.py --test-pdf data/ETS_2024_Test01.pdf --answer-pdf data/ETS_2024_Key01.pdf -o data/test01_full.json --test-name "ETS 2024 - Test 1"
```

#### Ví dụ 2: Trích xuất riêng Part 5 (Luyện 20-Second Pacer)
```powershell
python scripts/extract_pdf.py --test-pdf data/ETS_2024_Test01.pdf --answer-pdf data/ETS_2024_Key01.pdf -p 5 -o data/part5_extracted.json
```

#### Ví dụ 3: Trích xuất Part 3 kèm ghép đồng bộ mốc âm thanh từ `process_audio.py`
```powershell
python scripts/extract_pdf.py --test-pdf data/ETS_2024_Test01.pdf --answer-pdf data/ETS_2024_Key01.pdf -p 3 --audio-transcript audio/part3_transcript.json -o data/part3_ready.json
```

#### Ví dụ 4: Trích xuất và đẩy thẳng vào Supabase
```powershell
python scripts/extract_pdf.py --test-pdf data/ETS_2024_Test01.pdf --answer-pdf data/ETS_2024_Key01.pdf --import-supabase
```

### Cấu trúc file JSON xuất ra chuẩn Supabase:
```json
{
  "metadata": {
    "test_name": "ETS 2024 - Test 1",
    "extracted_at": "2026-10-28 21:00:00",
    "model_used": "gemini-2.5-flash",
    "total_groups": 10,
    "total_questions": 30
  },
  "question_groups": [
    {
      "id": "c1f7b093-6b32-4a0b-9df2-51c34a2f8d81",
      "test_name": "ETS 2024 - Test 1",
      "part": 7,
      "passage_text": "...",
      "image_url": null,
      "audio_url": null,
      "transcript_segments": null
    }
  ],
  "questions": [
    {
      "id": "e2a1b942-8c11-4f1b-a5d3-82b1c34a2e99",
      "group_id": "c1f7b093-6b32-4a0b-9df2-51c34a2f8d81",
      "part": 7,
      "question_number": 147,
      "question_type_tag": "inference",
      "question_text": "What is indicated about the company?",
      "options": {
        "A": "It previously completed an award-winning project.",
        "B": "It was recently relocated."
      },
      "correct_answer": "A",
      "explanation_vi": "Phân tích câu hỏi suy luận...",
      "evidence_quote": "Having closely followed your acclaimed, award-winning work...",
      "paraphrase_pair": {
        "original": "award-winning work",
        "paraphrased": "completed an award-winning project"
      }
    }
  ]
}
```

---

## 4. Quy Trình Trọn Vẹn (End-to-End Pipeline)

```
[Audio MP3]  ➔  process_audio.py (RTX 3060 GPU float16)  ➔  [transcript.json]
                                                                  ↓
[Test PDF]   ➔  extract_pdf.py (Gemini 2.5 Flash)        ➔  [toeic_dataset.json]
[Answer PDF] ↗                                                    ↓
                                                         [Supabase Database]
                                                    (question_groups & questions)
```

---

## 5. Quy Chuẩn Phân Loại Thư Mục Dữ Liệu (Data Architecture)

Hệ thống tuân thủ nghiêm ngặt nguyên tắc phân tách **Dữ liệu thô (Bronze)** và **Dữ liệu đã qua xử lý (Silver/Gold)**:

### 1. `raw_data/` (Chỉ chứa tài liệu gốc người dùng nạp vào)
- **Tuyệt đối không lưu dữ liệu xử lý, file json hay file tạm vào thư mục này.**
- Mỗi đề thi là một thư mục riêng: `raw_data/TEST X - ETS 2023/`
- Chỉ chứa 4 loại tệp nguồn:
  - `Audio Test XX.mp3` (File audio trọn vẹn)
  - `ETS 2023 Test X.pdf` (Đề thi nguyên bản)
  - `Transcript Test X.pdf` (Transcript lời thoại)
  - `Dap-an-test-X-ets-2023.png` hoặc `.pdf` (Bảng đáp án chính thức)

### 2. `processed_data/` (Toàn bộ dữ liệu bóc tách của Pipeline)
- Cấu trúc theo từng đề: `processed_data/TEST X - ETS 2023/`
  - **`final/`**: Dữ liệu chuẩn hóa hoàn chỉnh:
    - `test1_part1.json` -> `test1_part7.json` (Từng part độc lập)
    - `test1_full.json` (Đầy đủ 200 câu hỏi và question groups sẵn sàng nạp Supabase)
  - **`intermediate/`**: Dữ liệu trung gian hỗ trợ kiểm tra và debug:
    - `whisper/`: Nhận diện giọng nói gốc (`*_whisper_raw.json`)
    - `batches/`: Kết quả trích xuất từng đợt từ Gemini
    - `segments/`: Mốc thời gian cắt audio câu hỏi
    - `answers/`: Bảng đáp án JSON bóc tách từ ảnh/PDF

### 3. `public/` (Tài nguyên phục vụ Web App)
- `public/audio/test1/`: Các file audio nhỏ đã cắt theo từng câu / cụm câu (`part1_q1.mp3`, `part2_q7.mp3`, v.v.).
- `public/images/test1/`: Các hình ảnh tranh vẽ, tài liệu đọc đã cắt crop độ phân giải cao.

### 4. `.temp/` (Bộ nhớ đệm tạm thời - Đã đưa vào `.gitignore`)
- Chứa các file ảnh PDF trang render tạm thời phục vụ OCR/Cropping, tự động dọn dẹp không đẩy lên Git.

