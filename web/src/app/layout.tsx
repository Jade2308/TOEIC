import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/Navbar';
import { ThemeInitializer } from '@/components/ThemeInitializer';
import { SelectionSrsListener } from '@/components/SelectionSrsListener';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'TOEIC L&R Coach - Nền Tảng Luyện Thi TOEIC Tinh Gọn',
  description: 'Luyện thi TOEIC L&R chuẩn ETS 2023, sổ tay câu sai và học từ vựng Spaced Repetition (SRS)',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="vi"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#f8faf8] dark:bg-[#090e0c] text-neutral-900 dark:text-neutral-100 transition-colors selection:bg-emerald-500/30 selection:text-emerald-900 dark:selection:text-emerald-100">
        <ThemeInitializer />
        <Navbar />
        <div className="flex-1 flex flex-col">
          {children}
        </div>
        <SelectionSrsListener />
      </body>
    </html>
  );
}
