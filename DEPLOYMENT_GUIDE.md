# HƯỚNG DẪN TRIỂN KHAI TOEIC ADAPTIVE COACH LÊN PROXMOX VE (UBUNTU SERVER — 100% LOCAL STORAGE)

Tài liệu này hướng dẫn từng bước đưa toàn bộ hệ thống **TOEIC L&R Adaptive Coach** lên **Mini PC chạy Proxmox VE** (máy ảo **Ubuntu Server + Docker Compose**), chạy **100% cục bộ không dùng Supabase**, tách bạch hoàn toàn mã nguồn và thư mục dữ liệu `data/`.

---

## 1. Cấu Trúc Thư Mục Tách Bạch Code & Data

```text
/opt/toeic/
├── docker-compose.yml       # Mount sạch sẽ chỉ từ ./data/*
├── web/                     # Mã nguồn Next.js (Build context ~1MB nhờ .dockerignore)
├── crawler/                 # Mã nguồn Python Crawler
├── nginx/                   # Reverse Proxy + Serve thẳng /audio và /images
├── scripts/                 # setup_ubuntu_server.sh, backup_data.sh
└── data/                    # ⭐ TOÀN BỘ DỮ LIỆU Ở 1 NƠI DUY NHẤT (Dễ backup / mount disk)
    ├── raw/                 # Đề gốc (PDF, MP3, Đáp án) — chia sẻ qua Samba
    ├── exams/               # Đề đã crawl JSON — Web tự động quét động, không cần restart!
    ├── media/               # Audio & Ảnh (1 bản duy nhất) — Nginx serve trực tiếp
    └── user/                # Dữ liệu cá nhân: mistakes.json, vocab_srs.json, progress.json
```

---

## 2. Thông Số Khuyến Nghị Cho Máy Ảo Trên Proxmox

| Thành phần | Giá trị khuyến nghị | Lưu ý quan trọng |
| :--- | :--- | :--- |
| **Hệ điều hành** | Ubuntu Server 22.04 LTS hoặc 24.04 LTS | Bản Minimal hoặc Standard |
| **CPU Type** | **`host`** *(Rất quan trọng)* | Bắt buộc chọn `host` để bật AVX2/AVX-512, giúp AI Whisper chạy nhanh gấp 3 lần |
| **Số lõi (Cores)** | 2 đến 4 vCPUs | Phù hợp mọi Mini PC (Intel N100, AMD Ryzen) |
| **Bộ nhớ (RAM)** | **3072 MB – 4096 MB** | Bình thường Docker stack tốn **< 80 MB**; khi chạy Whisper bóc tách đề tạm dùng ~1.5 GB |
| **Ổ cứng (Disk)** | 32 GB – 50 GB (VirtIO SCSI) | Bật `Discard` (Trim SSD). Có thể mount riêng ổ dữ liệu vào `/opt/toeic/data` |
| **Card mạng** | VirtIO (paravirtualized) | Mạng LAN nội bộ tốc độ cao |

---

## 3. Đưa Mã Nguồn & Dữ Liệu Lên Máy Chủ Ubuntu

Từ máy tính Windows (PowerShell):

```powershell
# Giả sử IP máy ảo Ubuntu là 192.168.1.150, user là ubuntu
scp -r d:\DATA\TOEIC ubuntu@192.168.1.150:/opt/toeic
```

*(Lưu ý: không cần copy `web/node_modules` và `web/.next` để truyền nhanh hơn)*

---

## 4. Cài Đặt Tự Động 1-Click

Trên máy chủ Ubuntu Server:

```bash
cd /opt/toeic
chmod +x scripts/setup_ubuntu_server.sh scripts/backup_data.sh crawler/run_crawler.sh
sudo ./scripts/setup_ubuntu_server.sh
```

**Script sẽ tự động:**
- Cài `docker`, `docker compose`, `ffmpeg`, `samba`, `python3-venv`, `ufw`.
- Tạo cấu trúc `/opt/toeic/data/{raw,exams,media,user}` và phân quyền chuẩn cho container `toeic-web` (**UID/GID 1001**) cùng user Ubuntu đều ghi được an toàn (không gặp lỗi `EACCES`).
- Cấu hình Samba Share `[toeic-tests]` trỏ thẳng tới `/opt/toeic/data/raw`.
- Cài sẵn Python venv `/opt/toeic/venv` với đầy đủ thư viện (`faster-whisper`, `google-genai`, `pymupdf`, `pillow`...).

---

## 5. Khởi Động Ứng Dụng Với Docker Compose

```bash
cd /opt/toeic
docker compose up -d --build
```

- **Kiểm tra trạng thái sức khỏe hệ thống:**
  Truy cập `http://<IP_MÁY_ẢO>` → Thanh điều hướng trên cùng hiển thị chấm xanh **`Local • X đề`** (xác nhận đọc được kho đề và ghi tốt vào `data/user/`).
- Hoặc kiểm tra qua terminal:
  ```bash
  curl http://localhost/api/health
  ```

---

## 6. Quy Trình Thêm & Bóc Tách Đề Thi Mới (Không Cần Restart Docker!)

### Bước 1: Đưa đề gốc vào `data/raw/` (chọn 1 trong 2 cách)
- **Cách 1 (Samba trên Windows):** Nhấn `Win + R` → gõ `\\<IP_MÁY_ẢO>\toeic-tests` → kéo thả cả thư mục đề (vd `TEST 5 - ETS 2023`) vào.
- **Cách 2 (Giao diện Web):** Mở `http://<IP_MÁY_ẢO>/admin` → tải lên PDF, MP3, Đáp án.

### Bước 2: Chạy Crawler trên Ubuntu Server VM
```bash
cd /opt/toeic
./crawler/run_crawler.sh "data/raw/TEST 5 - ETS 2023" --device cpu
```

### Bước 3: Mở web và làm bài ngay!
- Crawler tự xuất kết quả vào `data/exams/TEST 5 - ETS 2023/final/...` và media vào `data/media/{audio,images}/...`.
- Bạn chỉ cần bấm **F5** trên trình duyệt (hoặc nút **Làm mới** trong Kho Đề) → **đề mới tự động hiện ngay lập tức, KHÔNG cần rebuild hay restart Docker!**

---

## 7. Sao Lưu (Backup) Dữ Liệu Học Tập Cá Nhân

Toàn bộ lỗi sai, từ vựng SRS và tiến độ làm bài nằm gọn trong `/opt/toeic/data/user/` (chỉ vài trăm KB):

- **Tải nhanh từ trình duyệt:** Bấm biểu tượng **Download** trên thanh Navbar để tải về 1 file `toeic-backup-YYYY-MM-DD.json`.
- **Tự động backup hàng ngày trên Ubuntu VM (crontab):**
  ```bash
  crontab -e
  # Thêm dòng sau để tự backup lúc 02:00 mỗi ngày (giữ 14 bản gần nhất):
  0 2 * * * /opt/toeic/scripts/backup_data.sh
  ```

---

## 8. Các Lệnh Quản Trị Nhanh

```bash
docker compose logs -f web        # Xem log Next.js
docker compose restart            # Khởi động lại stack
docker compose up -d --build      # Cập nhật sau khi sửa code (dữ liệu trong ./data giữ nguyên 100%)
docker stats                      # Kiểm tra RAM/CPU (thường < 80MB RAM khi nhàn rỗi)
```
