# TOEIC L&R Adaptive Coach & Data Pipeline

Hệ thống luyện thi TOEIC Listening & Reading thông minh được tổ chức thành 2 module độc lập:
1. **`web/`**: Ứng dụng Web TOEIC Adaptive Coach (Next.js 16 App Router, React 19, Tailwind CSS v4, Zustand).
2. **`crawler/`**: Module cào, bóc tách đề thi PDF và Audio MP3 tự động (Python 3.10+, Faster-Whisper CUDA, Gemini 2.5/3.8 Flash Structured Outputs).

---

## 1. Cấu Trúc Tổng Quan Dự Án

```
TOEIC/
├── package.json         # Root scripts ủy quyền (npm run dev, npm run crawler, ...)
├── .gitignore           # Cấu hình ignore cho cả Next.js và Python
├── SPECIFICATION.md     # Đặc tả kiến trúc sản phẩm
├── supabase/            # Database schema & migrations Supabase
│   └── schema.sql
│
├── web/                 # [MODULE 1] Ứng dụng Web TOEIC
│   ├── src/             # Next.js App Router, components, lib, stores
│   ├── public/          # Audio cắt theo câu & ảnh bài đọc crop
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
└── crawler/             # [MODULE 2] Module Cào & Xử Lý Dữ Liệu
    ├── main.py          # Master CLI cào và trích xuất đề thi
    ├── requirements.txt # Thư viện Python
    ├── core/            # audio, cropper, extractor, schema, seeder
    ├── raw_data/        # Kho tài liệu gốc (PDFs, full Audio MP3, Keys)
    ├── processed_data/  # Dữ liệu JSON bóc tách hoàn chỉnh
    ├── archive/         # Lưu trữ an toàn các script lịch sử
    └── README.md
```

---

## 2. Bắt Đầu Nhanh

### 💻 Khởi Động Web App:
```powershell
# Chạy trực tiếp từ thư mục gốc:
npm run dev

# Hoặc:
cd web
npm run dev
```
Mở trình duyệt tại [http://localhost:3000](http://localhost:3000).

---

### 🤖 Chạy Module Cào Đề Thi (Crawler):
```powershell
# Kích hoạt conda:
conda activate toeic-pipeline

# Chạy trích xuất đề thi (tự động xuất audio & ảnh vào web/public):
python crawler/main.py --test-dir "crawler/raw_data/TEST 2 - ETS 2023"

# Hoặc từ thư mục gốc thông qua npm script:
npm run crawler -- --test-dir "crawler/raw_data/TEST 2 - ETS 2023"
```

---

## 3. Liên Kết Dữ Liệu Giữa 2 Module

- **Dữ liệu bài tập & câu hỏi**: Web App đọc từ CSDL Supabase (khi có kết nối) hoặc tự động nạp từ `crawler/processed_data/` khi chạy local offline.
- **Tài nguyên âm thanh & hình ảnh**: Pipeline cào đề tự động xuất các file âm thanh cắt nhỏ (`/audio/test1/`) và hình ảnh (`/images/test1/`) trực tiếp vào thư mục `web/public/`, sẵn sàng phục vụ người học trên giao diện web ngay lập tức.
