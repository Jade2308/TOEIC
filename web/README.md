# TOEIC Adaptive Coach - Web Application

Giao diện ứng dụng luyện thi TOEIC Listening & Reading Adaptive Coach được phát triển với Next.js 16 (App Router), React 19, Tailwind CSS v4, Zustand và Lucide icons.

---

## 1. Công Nghệ Sử Dụng

- **Framework**: Next.js 16.4.3 (App Router, Turbopack)
- **UI / Styling**: React 19, Tailwind CSS v4, Framer Motion, Lucide React
- **State Management**: Zustand
- **Database / Backend**: Supabase Client (PostgreSQL) kèm Local JSON Mock Fallback

---

## 2. Cài Đặt & Chạy Ứng Dụng

### Chạy trực tiếp từ thư mục `web/`:
```powershell
cd web
npm install
npm run dev
```

### Hoặc chạy từ thư mục gốc của dự án:
```powershell
npm run dev
```

Mở trình duyệt tại [http://localhost:3000](http://localhost:3000) để bắt đầu luyện thi.

---

## 3. Cấu Trúc Mã Nguồn

```
web/
├── public/                # Tài nguyên tĩnh (audio câu hỏi, ảnh tranh/bài đọc, icons)
│   ├── audio/             # Audio cắt theo câu (part1_q1.mp3, part2_q7.mp3, ...)
│   └── images/            # Tranh ảnh và bài đọc crop độ phân giải cao
├── src/
│   ├── app/               # Next.js App Router (pages, layout, /api/exam)
│   ├── components/        # Các UI Components (SingleCardLayout, AdaptiveSplitLayout, SmartAudioPlayer, ...)
│   ├── lib/               # Data service, storage, SRS spaced repetition, supabase client
│   ├── stores/            # Zustand stores (useExamStore, useMistakeStore, useVocabStore)
│   ├── types/             # TypeScript definitions cho câu hỏi, nhóm đề thi
│   └── data/              # Mock data dự phòng khi chạy offline
├── package.json
└── tsconfig.json
```
