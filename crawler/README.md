# TOEIC Crawler & Data Extraction Module

Module chuyên trách cào, trích xuất, bóc tách và chuẩn hóa dữ liệu đề thi TOEIC từ tài liệu thô (PDF & Audio MP3) thành cơ sở dữ liệu có cấu trúc phục vụ trực tiếp cho Web App và Supabase.

---

## 1. Cấu Trúc Thư Mục

```
crawler/
├── main.py              # CLI Master điều phối trọn vẹn quy trình
├── requirements.txt     # Danh sách thư viện Python
├── .env.example         # Mẫu biến môi trường
├── core/                # Các package module hóa
│   ├── schema.py        # Pydantic Schemas cho Structured Outputs
│   ├── audio.py         # Cắt audio MP3 & phiên âm faster-whisper (CUDA/CPU)
│   ├── cropper.py       # Cắt ảnh Part 1, Part 3/4 graphics, Part 6/7 passages
│   ├── extractor.py     # Gọi Gemini 2.5/3.8 Flash bóc tách câu hỏi & giải thích
│   └── seeder.py        # Import dữ liệu vào CSDL Supabase
├── raw_data/            # Tài liệu gốc người dùng nạp vào (PDF, Audio full, Đáp án)
├── processed_data/      # Kết quả trích xuất JSON (intermediate & final)
├── archive/             # Lưu trữ an toàn toàn bộ script lịch sử
└── .temp/               # Bộ nhớ đệm trang PDF tạm thời
```

---

## 2. Cài Đặt Môi Trường

Kích hoạt môi trường conda đã chuẩn bị sẵn:
```powershell
conda activate toeic-pipeline
```

Hoặc cài đặt qua pip:
```powershell
pip install -r crawler/requirements.txt
```

Kiểm tra GPU NVIDIA CUDA (nếu có card RTX 3060):
```powershell
python -c "import ctranslate2; print('CUDA Devices:', ctranslate2.get_cuda_device_count())"
```

---

## 3. Cấu Hình Biến Môi Trường (`.env`)

Sao chép `.env.example` thành `.env` bên trong thư mục `crawler/` (hoặc đặt ở thư mục gốc):
```env
GEMINI_API_KEY=your_gemini_api_key_here
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

---

## 4. Hướng Dẫn Sử Dụng

### Trích xuất trọn vẹn 1 đề thi (One-Click Master Pipeline):
```powershell
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023"
```

### Chạy tăng tốc trên GPU NVIDIA CUDA:
```powershell
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023" --device cuda
```

### Bỏ qua trích xuất audio (nếu đã cắt xong trước đó):
```powershell
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023" --skip-audio
```

### Chỉ trích xuất riêng một số Part cụ thể (ví dụ Part 5 và Part 7):
```powershell
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023" --parts 5,7
```

### Tự động nạp dữ liệu trích xuất vào Supabase:
```powershell
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023" --import-supabase
```
