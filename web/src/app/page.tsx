'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Layers,
  AlertCircle,
  BookOpen,
  Headphones,
  FileText,
  Clock,
  ArrowRight,
  Sparkles,
  Flame,
  Radio,
  Zap,
  RefreshCw,
  UploadCloud,
  Image as ImageIcon,
  MessageSquareQuote,
  MessagesSquare,
  Mic,
  PenLine,
} from 'lucide-react';
import { useMistakeStore } from '@/stores/useMistakeStore';
import { useVocabStore } from '@/stores/useVocabStore';
import { useExamStore } from '@/stores/useExamStore';
import { ExamSwitcher } from '@/components/ExamSwitcher';

interface PartItem {
  part: number;
  title: string;
  subtitle: string;
  range: string;
  type: 'Listening' | 'Reading';
  count: number;
  icon: React.ComponentType<{ className?: string }>;
}

const PART_ACCENT = {
  Listening: {
    cardHover: 'hover:border-emerald-500/60 dark:hover:border-emerald-600/60',
    iconBox:
      'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white',
    partLabel: 'text-emerald-700 dark:text-emerald-400',
    countPill:
      'bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-200/70 dark:border-emerald-800/40',
    titleHover: 'group-hover:text-emerald-700 dark:group-hover:text-emerald-300',
    cta: 'text-emerald-600 dark:text-emerald-400',
  },
  Reading: {
    cardHover: 'hover:border-teal-500/60 dark:hover:border-teal-600/60',
    iconBox:
      'bg-teal-50 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400 group-hover:bg-teal-600 group-hover:text-white',
    partLabel: 'text-teal-700 dark:text-teal-400',
    countPill:
      'bg-teal-50 dark:bg-teal-950/70 text-teal-700 dark:text-teal-300 border border-teal-200/70 dark:border-teal-800/40',
    titleHover: 'group-hover:text-teal-700 dark:group-hover:text-teal-300',
    cta: 'text-teal-600 dark:text-teal-400',
  },
} as const;

function PartCard({ item, href }: { item: PartItem; href: string }) {
  const Icon = item.icon;
  const accent = PART_ACCENT[item.type];

  return (
    <Link
      href={href}
      className="group block h-full rounded-2xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600"
    >
      <article
        className={`@container h-full grid grid-rows-[auto_1fr_auto] gap-3.5 rounded-2xl p-4 @[280px]:p-5 bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs transition duration-200 hover:-translate-y-0.5 hover:shadow-md ${accent.cardHover}`}
      >
        <header className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <span
              className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 transition-colors ${accent.iconBox}`}
              aria-hidden="true"
            >
              <Icon className="w-4.5 h-4.5" />
            </span>
            <span className={`text-xs font-extrabold uppercase tracking-wider ${accent.partLabel}`}>
              Part {item.part}
            </span>
          </div>

          <span
            className={`text-[11px] font-bold tabular-nums px-2.5 py-1 rounded-full shrink-0 ${accent.countPill}`}
          >
            {item.count} câu
          </span>
        </header>

        <hgroup className="space-y-0.5">
          <h4
            className={`font-bold text-[15px] leading-snug text-neutral-900 dark:text-neutral-100 transition-colors ${accent.titleHover}`}
          >
            {item.title}
          </h4>
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            {item.subtitle}
          </p>
        </hgroup>

        <footer className="pt-3 border-t border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-between gap-2 text-xs">
          <span className="font-mono text-[11px] text-neutral-400 dark:text-neutral-500 tabular-nums">
            {item.range}
          </span>
          <span className={`inline-flex items-center gap-1 font-bold transition-colors ${accent.cta}`}>
            <span>Luyện ngay</span>
            <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
          </span>
        </footer>
      </article>
    </Link>
  );
}

function calculateStudyStreak(studyDates: string[]): number {
  if (!studyDates || studyDates.length === 0) return 0;
  const dateSet = new Set(studyDates);
  const toKey = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

  const cursor = new Date();
  if (!dateSet.has(toKey(cursor))) {
    cursor.setDate(cursor.getDate() - 1);
    if (!dateSet.has(toKey(cursor))) return 0;
  }

  let streak = 0;
  while (dateSet.has(toKey(cursor))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const { mistakes, loadMistakes } = useMistakeStore();
  const { vocabList, loadVocab } = useVocabStore();
  const {
    availableExams,
    isLoadingExams,
    selectedTestId,
    selectedTest,
    answersByTest,
    studyDates,
    loadAvailableExams,
    loadUserProgress,
    setSelectedTest,
  } = useExamStore();

  useEffect(() => {
    setMounted(true);
    loadMistakes();
    loadVocab();
    loadAvailableExams(true);
    loadUserProgress();
  }, [loadMistakes, loadVocab, loadAvailableExams, loadUserProgress]);

  const currentExam = useMemo(() => {
    return (
      availableExams.find(
        (e) =>
          e.id === selectedTestId ||
          e.name.toLowerCase() === selectedTest.toLowerCase()
      ) || availableExams[0]
    );
  }, [availableExams, selectedTestId, selectedTest]);

  const activeExamId = currentExam?.id || selectedTestId || '';
  const activeExamName = currentExam?.name || selectedTest || 'Chưa có đề thi';

  const getPartCount = (part: number, defaultCount: number) => {
    if (currentExam?.parts && currentExam.parts[part]) {
      return currentExam.parts[part];
    }
    return defaultCount;
  };

  const listeningParts: PartItem[] = [
    {
      part: 1,
      title: 'Mô tả hình ảnh',
      subtitle: 'Photographs',
      range: 'Câu 1–6',
      type: 'Listening',
      count: getPartCount(1, 6),
      icon: ImageIcon,
    },
    {
      part: 2,
      title: 'Hỏi & Đáp',
      subtitle: 'Question–Response',
      range: 'Câu 7–31',
      type: 'Listening',
      count: getPartCount(2, 25),
      icon: MessageSquareQuote,
    },
    {
      part: 3,
      title: 'Hội thoại ngắn',
      subtitle: 'Conversations',
      range: 'Câu 32–70',
      type: 'Listening',
      count: getPartCount(3, 39),
      icon: MessagesSquare,
    },
    {
      part: 4,
      title: 'Bài nói ngắn',
      subtitle: 'Short Talks',
      range: 'Câu 71–100',
      type: 'Listening',
      count: getPartCount(4, 30),
      icon: Mic,
    },
  ];

  const readingParts: PartItem[] = [
    {
      part: 5,
      title: 'Điền vào câu',
      subtitle: 'Incomplete Sentences',
      range: 'Câu 101–130',
      type: 'Reading',
      count: getPartCount(5, 30),
      icon: PenLine,
    },
    {
      part: 6,
      title: 'Điền đoạn văn',
      subtitle: 'Text Completion',
      range: 'Câu 131–146',
      type: 'Reading',
      count: getPartCount(6, 16),
      icon: FileText,
    },
    {
      part: 7,
      title: 'Đọc hiểu',
      subtitle: 'Reading Comprehension',
      range: 'Câu 147–200',
      type: 'Reading',
      count: getPartCount(7, 54),
      icon: BookOpen,
    },
  ];

  const totalListeningQuestions = listeningParts.reduce((sum, p) => sum + p.count, 0);
  const totalReadingQuestions = readingParts.reduce((sum, p) => sum + p.count, 0);

  const unresolvedCount = mounted ? mistakes.filter((m) => !m.resolved).length : 0;
  const now = new Date();
  const dueVocabCount = mounted ? vocabList.filter((v) => new Date(v.due_date) <= now).length : 0;
  const streakDays = mounted ? calculateStudyStreak(studyDates) : 0;

  const practiceHref = (part: string | number) =>
    activeExamId
      ? `/practice?part=${part}&test=${encodeURIComponent(activeExamId)}`
      : `/practice?part=${part}`;

  return (
    <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 md:p-8 space-y-8">
      {/* ================================================================== */}
      {/* 1. TOP QUICK STATS                                                 */}
      {/* ================================================================== */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        {/* Streak */}
        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-neutral-500 dark:text-neutral-400 block uppercase tracking-wider">
              Chuỗi học tập
            </span>
            <div className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              {streakDays} <span className="text-xs font-semibold text-neutral-400">ngày</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <Flame className="w-5 h-5 fill-current" />
          </div>
        </div>

        {/* Selected Exam */}
        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs flex items-center justify-between">
          <div className="overflow-hidden pr-1">
            <span className="text-[11px] font-semibold text-neutral-500 dark:text-neutral-400 block uppercase tracking-wider">
              Đề đang chọn
            </span>
            <div
              className="text-base sm:text-lg font-black text-neutral-900 dark:text-neutral-100 mt-1 truncate"
              title={activeExamName}
            >
              {currentExam?.shortTitle || activeExamName}
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-teal-50 dark:bg-teal-950/50 text-teal-600 dark:text-teal-400 flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
        </div>

        {/* Error log stat */}
        <Link
          href="/error-log"
          className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs flex items-center justify-between hover:border-rose-400/60 dark:hover:border-rose-800/80 transition group"
        >
          <div>
            <span className="text-[11px] font-semibold text-neutral-500 dark:text-neutral-400 block uppercase tracking-wider">
              Câu cần sửa
            </span>
            <div className="text-2xl sm:text-3xl font-black text-rose-600 dark:text-rose-400 mt-1">
              {unresolvedCount} <span className="text-xs font-semibold text-neutral-400">câu</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center group-hover:scale-105 transition">
            <AlertCircle className="w-5 h-5" />
          </div>
        </Link>

        {/* Vocab SRS stat */}
        <Link
          href="/vocab-srs"
          className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs flex items-center justify-between hover:border-emerald-500 dark:hover:border-emerald-600 transition group"
        >
          <div>
            <span className="text-[11px] font-semibold text-neutral-500 dark:text-neutral-400 block uppercase tracking-wider">
              Từ vựng cần ôn
            </span>
            <div className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
              {dueVocabCount} <span className="text-xs font-semibold text-neutral-400">từ</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center group-hover:scale-105 transition">
            <BookOpen className="w-5 h-5" />
          </div>
        </Link>
      </section>

      {/* ================================================================== */}
      {/* 2. CHỨC NĂNG CHÍNH (CORE FUNCTION MODULES)                         */}
      {/* ================================================================== */}
      <section className="space-y-3.5">
        <h2 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          Chức năng chính
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Luyện đề */}
          <Link
            href={practiceHref('all')}
            className="group relative overflow-hidden rounded-3xl p-6 bg-gradient-to-br from-emerald-600 to-teal-700 text-white shadow-md hover:shadow-xl hover:shadow-emerald-900/20 transition flex flex-col justify-between space-y-4"
          >
            <div className="space-y-1.5">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-white text-[11px] font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                {activeExamName}
              </div>
              <h3 className="text-xl font-black tracking-tight pt-1">
                Luyện Toàn Bộ Đề Thi
              </h3>
              <p className="text-xs text-emerald-100/90 leading-relaxed">
                Đầy đủ 7 Part chuẩn ETS, âm thanh bản ngữ và giải thích chi tiết.
              </p>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs font-bold bg-white text-emerald-950 px-3.5 py-1.5 rounded-xl flex items-center gap-1.5 group-hover:bg-emerald-50 transition">
                <span>Vào làm đề ngay</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
              </span>
              <span className="text-xs font-mono font-bold text-emerald-200">
                {currentExam?.totalQuestions || 200} câu
              </span>
            </div>
          </Link>

          {/* Card 2: Sổ tay lỗi sai */}
          <Link
            href="/error-log"
            className="group rounded-3xl p-6 bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 hover:border-rose-400 dark:hover:border-rose-800 shadow-xs hover:shadow-md transition flex flex-col justify-between space-y-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold">
                  <AlertCircle className="w-5 h-5" />
                </span>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300">
                  {unresolvedCount} câu chưa sửa
                </span>
              </div>
              <h3 className="text-lg font-black text-neutral-900 dark:text-neutral-100 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition">
                Sổ Tay Lỗi Sai
              </h3>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed">
                Tự động tổng hợp câu làm sai từ mọi bộ đề để bạn xem lại và khắc phục.
              </p>
            </div>

            <div className="flex items-center text-xs font-bold text-rose-600 dark:text-rose-400 gap-1 pt-2">
              <span>Xem & khắc phục câu sai</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* Card 3: Từ vựng SRS */}
          <Link
            href="/vocab-srs"
            className="group rounded-3xl p-6 bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 hover:border-emerald-500 dark:hover:border-emerald-600 shadow-xs hover:shadow-md transition flex flex-col justify-between space-y-4"
          >
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                  <BookOpen className="w-5 h-5" />
                </span>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                  {vocabList.length} từ trong kho
                </span>
              </div>
              <h3 className="text-lg font-black text-neutral-900 dark:text-neutral-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition">
                Flashcard Từ Vựng (SRS)
              </h3>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed">
                Ôn tập ngắt quãng giúp nhớ lâu từ vựng và các cặp từ đồng nghĩa trong đề.
              </p>
            </div>

            <div className="flex items-center text-xs font-bold text-emerald-600 dark:text-emerald-400 gap-1 pt-2">
              <span>Lật thẻ flashcard ({dueVocabCount} cần ôn)</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
            </div>
          </Link>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 2.5 KHO BỘ ĐỀ THI ĐÃ SẴN SÀNG (100% DYNAMIC TỪ data/exams)         */}
      {/* ================================================================== */}
      <section className="space-y-3.5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Kho Bộ Đề Thi ({availableExams.length} Đề)
          </h2>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => loadAvailableExams(true)}
              disabled={isLoadingExams}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#111a14] hover:border-emerald-500 text-neutral-600 dark:text-neutral-300 text-xs font-semibold transition"
              title="Làm mới danh sách đề thi"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoadingExams ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Làm mới</span>
            </button>
            <ExamSwitcher />
          </div>
        </div>

        {availableExams.length === 0 ? (
          <div className="p-8 rounded-3xl border border-dashed border-emerald-950/20 dark:border-emerald-900/40 bg-white dark:bg-[#111a14] text-center space-y-3">
            <UploadCloud className="w-10 h-10 text-emerald-500 mx-auto" />
            <h3 className="font-bold text-sm text-neutral-800 dark:text-neutral-200">
              {isLoadingExams ? 'Đang tải danh sách đề thi...' : 'Chưa có đề thi nào'}
            </h3>
            <p className="text-xs text-neutral-500 max-w-md mx-auto">
              Hãy tải đề mới tại trang Tải đề để bắt đầu luyện tập.
            </p>
            <Link
              href="/admin"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition"
            >
              <span>Đi tới trang Tải đề</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {availableExams.map((test) => {
              const isSelected = currentExam?.id === test.id;
              const answeredInTest = Object.keys(answersByTest[test.id] || {}).length;

              return (
                <div
                  key={test.id}
                  className={`p-3.5 rounded-2xl border transition flex flex-col justify-between space-y-3 ${
                    isSelected
                      ? 'bg-emerald-500/10 dark:bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/50 shadow-xs'
                      : 'bg-white dark:bg-[#111a14] border-emerald-950/15 dark:border-emerald-900/40 hover:border-emerald-500/60 shadow-xs'
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-black text-emerald-700 dark:text-emerald-300">
                        {test.shortTitle}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {answeredInTest > 0 && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300">
                            Đã làm {answeredInTest}/{test.totalQuestions}
                          </span>
                        )}
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                          {test.totalQuestions} câu
                        </span>
                      </div>
                    </div>
                    <h4 className="font-bold text-xs sm:text-sm text-neutral-900 dark:text-neutral-100 line-clamp-1">
                      {test.name}
                    </h4>
                  </div>

                  <Link
                    href={`/practice?part=all&test=${encodeURIComponent(test.id)}`}
                    onClick={() => setSelectedTest(test.id)}
                    className={`w-full py-1.5 px-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-2xs ${
                      isSelected
                        ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                        : 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-600 hover:text-white'
                    }`}
                  >
                    <span>{isSelected ? 'Tiếp tục luyện' : 'Luyện đề'}</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* ================================================================== */}
      {/* 3. LUYỆN TẬP THEO TỪNG PART (LISTENING & READING)                  */}
      {/* ================================================================== */}
      <section className="space-y-6">
        {/* Listening Parts */}
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
              <Headphones className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              Kỹ năng Nghe (Part 1 – Part 4)
            </h3>
            <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold tabular-nums">
              Listening &bull; {totalListeningQuestions} câu
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {listeningParts.map((item) => (
              <PartCard key={item.part} item={item} href={practiceHref(item.part)} />
            ))}
          </div>
        </div>

        {/* Reading Parts */}
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-teal-600 dark:text-teal-400" />
              Kỹ năng Đọc (Part 5 – Part 7)
            </h3>
            <span className="text-xs font-mono text-teal-600 dark:text-teal-400 font-bold tabular-nums">
              Reading &bull; {totalReadingQuestions} câu
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
            {readingParts.map((item) => (
              <PartCard key={item.part} item={item} href={practiceHref(item.part)} />
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 4. LUYỆN NHANH (MICRO DRILLS)                                      */}
      {/* ================================================================== */}
      <section className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
          <Zap className="w-4 h-4 text-amber-500 fill-amber-500" />
          Luyện nhanh 5 phút
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Link
            href={practiceHref(5)}
            className="p-4 rounded-2xl bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 hover:border-emerald-500 transition flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                <Clock className="w-4.5 h-4.5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-neutral-900 dark:text-neutral-100">
                  Part 5: Tốc độ 20 giây / câu
                </h4>
                <p className="text-[11px] text-neutral-500">Rèn phản xạ từ loại và liên từ</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-neutral-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition" />
          </Link>

          <Link
            href={practiceHref(2)}
            className="p-4 rounded-2xl bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 hover:border-emerald-500 transition flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-teal-50 dark:bg-teal-950 text-teal-600 dark:text-teal-400 flex items-center justify-center font-bold">
                <Radio className="w-4.5 h-4.5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-neutral-900 dark:text-neutral-100">
                  Part 2: Bắt từ hỏi WH-Catcher
                </h4>
                <p className="text-[11px] text-neutral-500">Nghe phản xạ và loại trừ đáp án bẫy</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-neutral-400 group-hover:text-teal-600 group-hover:translate-x-1 transition" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="pt-6 pb-4 border-t border-emerald-950/10 dark:border-emerald-900/30 text-center text-xs text-neutral-400">
        <span>TOEIC L&amp;R Coach</span>
      </footer>
    </main>
  );
}
