'use client';

import React, { Suspense, useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  RotateCcw,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  BookOpen,
  LayoutGrid,
  X,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { useExamStore } from '@/stores/useExamStore';
import { useMistakeStore } from '@/stores/useMistakeStore';
import { useVocabStore } from '@/stores/useVocabStore';
import { ToeicPart, Question } from '@/types/toeic';

import { SingleCardLayout } from '@/components/SingleCardLayout';
import { AdaptiveSplitLayout } from '@/components/AdaptiveSplitLayout';
import { ErrorLogView } from '@/components/ErrorLogView';
import { VocabSrsView } from '@/components/VocabSrsView';
import { ExamSwitcher } from '@/components/ExamSwitcher';

function PracticeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const jumpBarRef = useRef<HTMLDivElement>(null);
  const lastAppliedQueryRef = useRef<string>('');
  const [isPaletteOpen, setIsPaletteOpen] = useState(false);

  const partParam = searchParams.get('part');
  const viewParam = searchParams.get('view');
  const testParam = searchParams.get('test');

  const {
    groups,
    questions,
    selectedPart,
    selectedTestId,
    selectedTest,
    currentQuestionIndex,
    userAnswers,
    isLoading,
    loadError,
    loadAvailableExams,
    loadExamData,
    goToQuestion,
    nextQuestion,
    prevQuestion,
    resetProgress,
  } = useExamStore();

  const { mistakes, loadMistakes } = useMistakeStore();
  const { vocabList, loadVocab } = useVocabStore();

  const [activeView, setActiveView] = useState<'practice' | 'mistakes' | 'vocab'>(
    viewParam === 'mistakes' ? 'mistakes' : viewParam === 'vocab' ? 'vocab' : 'practice'
  );

  // Auto-scroll active question into view in the quick jump bar
  useEffect(() => {
    if (jumpBarRef.current) {
      const activeEl = jumpBarRef.current.querySelector<HTMLElement>('[data-active="true"]');
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }
    }
  }, [currentQuestionIndex]);

  useEffect(() => {
    loadMistakes();
    loadVocab();
    loadAvailableExams();
  }, [loadMistakes, loadVocab, loadAvailableExams]);

  useEffect(() => {
    if (viewParam === 'mistakes') {
      setActiveView('mistakes');
    } else if (viewParam === 'vocab') {
      setActiveView('vocab');
    } else {
      setActiveView('practice');
    }

    const parsedPart =
      partParam && partParam !== 'all' ? (parseInt(partParam, 10) as ToeicPart) : 'all';
    const queryKey = `${testParam || ''}::${parsedPart}`;

    if (lastAppliedQueryRef.current === queryKey) {
      return;
    }
    lastAppliedQueryRef.current = queryKey;

    const requestedTest = testParam?.trim() || selectedTestId || selectedTest || undefined;

    if (parsedPart !== selectedPart) {
      useExamStore.setState({ selectedPart: parsedPart });
    }
    loadExamData(parsedPart, requestedTest);
  }, [partParam, viewParam, testParam, selectedPart, selectedTestId, selectedTest, loadExamData]);

  const currentQuestion = questions[currentQuestionIndex];
  const currentGroup = currentQuestion
    ? groups.find((g) => g.id === currentQuestion.group_id)
    : undefined;

  const linkedQuestions = currentGroup
    ? questions.filter((q) => q.group_id === currentGroup.id)
    : currentQuestion
    ? [currentQuestion]
    : [];

  const handleNextGroup = () => {
    if (!currentGroup) return;
    const nextQIndex = questions.findIndex(
      (q, idx) => idx > currentQuestionIndex && q.group_id !== currentGroup.id
    );
    if (nextQIndex !== -1) {
      goToQuestion(nextQIndex);
    } else if (currentQuestionIndex < questions.length - 1) {
      nextQuestion();
    }
  };

  const handlePrevGroup = () => {
    if (!currentGroup) return;
    const prevQuestions = questions.filter(
      (q, idx) => idx < currentQuestionIndex && q.group_id !== currentGroup.id
    );
    if (prevQuestions.length > 0) {
      const prevGroupId = prevQuestions[prevQuestions.length - 1].group_id;
      const prevGroupFirstQIndex = questions.findIndex((q) => q.group_id === prevGroupId);
      if (prevGroupFirstQIndex !== -1) {
        goToQuestion(prevGroupFirstQIndex);
        return;
      }
    }
    if (currentQuestionIndex > 0) {
      prevQuestion();
    }
  };

  const hasNextGroup = currentGroup
    ? questions.some((q, idx) => idx > currentQuestionIndex && q.group_id !== currentGroup.id)
    : currentQuestionIndex < questions.length - 1;

  const hasPrevGroup = currentGroup
    ? questions.some((q, idx) => idx < currentQuestionIndex && q.group_id !== currentGroup.id)
    : currentQuestionIndex > 0;

  const handleReset = () => {
    if (confirm('Đặt lại bài làm của phiên này?')) {
      resetProgress();
    }
  };

  const partTabs: { id: ToeicPart | 'all'; label: string }[] = [
    { id: 'all', label: 'Tất cả' },
    { id: 1, label: 'Part 1' },
    { id: 2, label: 'Part 2' },
    { id: 3, label: 'Part 3' },
    { id: 4, label: 'Part 4' },
    { id: 5, label: 'Part 5' },
    { id: 6, label: 'Part 6' },
    { id: 7, label: 'Part 7' },
  ];

  const handlePartChange = (part: ToeicPart | 'all') => {
    const test = searchParams.get('test');
    const query = test ? `?part=${part}&test=${test}` : `?part=${part}`;
    router.push(`/practice${query}`);
  };

  const answeredCount = Object.keys(userAnswers).length;
  const correctCount = questions.filter((q) => userAnswers[q.id] && userAnswers[q.id] === q.correct_answer).length;
  const wrongCount = questions.filter((q) => userAnswers[q.id] && userAnswers[q.id] !== q.correct_answer).length;
  const unresolvedMistakesCount = mistakes.filter((m) => !m.resolved).length;

  const partTitles: Record<number, string> = {
    1: 'Part 1: Hình ảnh (Photographs)',
    2: 'Part 2: Hỏi & Đáp (Question - Response)',
    3: 'Part 3: Hội thoại (Conversations)',
    4: 'Part 4: Bài nói ngắn (Short Talks)',
    5: 'Part 5: Điền câu (Incomplete Sentences)',
    6: 'Part 6: Điền đoạn văn (Text Completion)',
    7: 'Part 7: Đọc hiểu (Reading Comprehension)',
  };

  const groupedQuestions = React.useMemo(() => {
    const map: Record<number, { question: Question; index: number }[]> = {};
    questions.forEach((q, idx) => {
      if (!map[q.part]) map[q.part] = [];
      map[q.part].push({ question: q, index: idx });
    });
    return map;
  }, [questions]);

  return (
    <div className="flex-1 flex flex-col">
      {/* Subheader: Exam Switcher & Part Selector */}
      <div className="bg-white/70 dark:bg-[#0c1410]/70 border-b border-emerald-950/10 dark:border-emerald-900/30 backdrop-blur-xs">
        <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between flex-wrap gap-2.5">
          {/* Left: Exam Switcher + Part Selection Pills */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-0.5">
            <ExamSwitcher />

            <div className="h-4 w-px bg-neutral-200 dark:bg-emerald-900/40 hidden sm:block shrink-0" />

            <div className="flex items-center gap-1 shrink-0">
              {partTabs.map((tab) => {
                const isActive = activeView === 'practice' && selectedPart === tab.id;
                return (
                  <button
                    key={String(tab.id)}
                    onClick={() => {
                      setActiveView('practice');
                      handlePartChange(tab.id);
                    }}
                    className={`px-2.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                      isActive
                        ? 'bg-emerald-600 text-white shadow-xs'
                        : 'text-neutral-600 dark:text-neutral-400 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-500/10'
                    }`}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-semibold text-neutral-500 dark:text-neutral-400">
              {answeredCount}/{questions.length} Đã làm
            </span>

            <button
              onClick={handleReset}
              className="p-1.5 rounded-xl border border-neutral-200 dark:border-emerald-950/60 text-neutral-500 dark:text-neutral-400 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/30 transition text-xs flex items-center gap-1"
              title="Đặt lại bài làm"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline text-xs">Làm lại</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-3 sm:p-5 md:p-6 space-y-4">
        {activeView === 'mistakes' ? (
          <div className="max-w-3xl mx-auto py-2">
            <ErrorLogView />
          </div>
        ) : activeView === 'vocab' ? (
          <div className="max-w-3xl mx-auto py-2">
            <VocabSrsView />
          </div>
        ) : (
          /* PRACTICE VIEW */
          <div className="space-y-4">
            {/* Question Quick Jump Bar with Scroll & Palette Controls */}
            {questions.length > 0 && (
              <div className="bg-white dark:bg-[#111a14] p-2 sm:p-2.5 rounded-2xl border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs flex items-center justify-between gap-1.5 sm:gap-2 overflow-hidden">
                {/* Scroll Left Button */}
                <button
                  type="button"
                  onClick={() => jumpBarRef.current?.scrollBy({ left: -220, behavior: 'smooth' })}
                  className="p-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 text-neutral-500 hover:text-emerald-600 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition shrink-0"
                  title="Cuộn sang trái"
                  aria-label="Cuộn sang trái"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                {/* Horizontal Question Buttons */}
                <div
                  ref={jumpBarRef}
                  onWheel={(e) => {
                    if (e.deltaY !== 0 && jumpBarRef.current) {
                      jumpBarRef.current.scrollLeft += e.deltaY;
                    }
                  }}
                  className="flex items-center gap-1 sm:gap-1.5 overflow-x-auto flex-1 py-1 px-1 scroll-smooth"
                >
                  {questions.map((q, idx) => {
                    const isCurrent = idx === currentQuestionIndex;
                    const answer = userAnswers[q.id];
                    const isCorrect = answer === q.correct_answer;

                    let badgeColor =
                      'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/40';
                    if (answer) {
                      badgeColor = isCorrect
                        ? 'bg-emerald-500 text-white font-bold'
                        : 'bg-rose-500 text-white font-bold';
                    }
                    if (isCurrent) {
                      badgeColor +=
                        ' ring-2 ring-emerald-500 ring-offset-2 dark:ring-offset-[#090e0c] font-black scale-105';
                    }

                    return (
                      <button
                        key={q.id}
                        data-active={isCurrent ? 'true' : 'false'}
                        onClick={() => goToQuestion(idx)}
                        className={`w-7 h-7 sm:w-8 sm:h-8 rounded-lg text-xs flex items-center justify-center transition shrink-0 font-medium ${badgeColor}`}
                        title={`Câu ${q.question_number} (Part ${q.part})`}
                      >
                        {q.question_number}
                      </button>
                    );
                  })}
                </div>

                {/* Scroll Right Button */}
                <button
                  type="button"
                  onClick={() => jumpBarRef.current?.scrollBy({ left: 220, behavior: 'smooth' })}
                  className="p-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 text-neutral-500 hover:text-emerald-600 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition shrink-0"
                  title="Cuộn sang phải"
                  aria-label="Cuộn sang phải"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>

                {/* Question Palette Modal Trigger */}
                <button
                  type="button"
                  onClick={() => setIsPaletteOpen(true)}
                  className="px-2.5 sm:px-3 py-1.5 rounded-xl border border-emerald-950/20 dark:border-emerald-800/40 bg-emerald-50/70 dark:bg-emerald-950/40 hover:bg-emerald-100 dark:hover:bg-emerald-950/70 text-emerald-950 dark:text-emerald-200 text-xs font-bold flex items-center gap-1.5 transition shrink-0 shadow-2xs"
                  title="Mở toàn bộ danh sách câu hỏi"
                >
                  <LayoutGrid className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span className="hidden sm:inline">Bảng câu hỏi</span>
                  <span className="font-mono text-[11px] text-emerald-700 dark:text-emerald-300">
                    ({answeredCount}/{questions.length})
                  </span>
                </button>
              </div>
            )}

            {/* Question Palette Modal */}
            {isPaletteOpen && (
              <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 animate-fade-in">
                <div className="bg-white dark:bg-[#111a14] border border-emerald-950/20 dark:border-emerald-900/40 rounded-3xl p-4 sm:p-6 max-w-3xl w-full shadow-2xl space-y-4 max-h-[88vh] flex flex-col">
                  {/* Modal Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-emerald-950/10 dark:border-emerald-900/30">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xs">
                        <LayoutGrid className="w-4 h-4" />
                      </div>
                      <div>
                        <h3 className="text-base font-black text-neutral-900 dark:text-neutral-100">
                          Bảng Điều Hướng Toàn Bộ Câu Hỏi
                        </h3>
                        <p className="text-xs text-neutral-500">
                          {selectedTest} &bull; Bấm vào số câu bất kỳ để nhảy tới ngay
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setIsPaletteOpen(false)}
                      className="p-1.5 rounded-xl text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 transition"
                      aria-label="Đóng"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Summary Stats & Legend Bar */}
                  <div className="flex items-center justify-between flex-wrap gap-2 text-xs p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-950/50 border border-neutral-200/80 dark:border-neutral-800">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1.5 font-medium">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                        <span>Đúng: <strong>{correctCount}</strong></span>
                      </span>
                      <span className="flex items-center gap-1.5 font-medium">
                        <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                        <span>Sai: <strong>{wrongCount}</strong></span>
                      </span>
                      <span className="flex items-center gap-1.5 font-medium text-neutral-500">
                        <span className="w-2.5 h-2.5 rounded-full bg-neutral-300 dark:bg-neutral-700" />
                        <span>Chưa làm: <strong>{questions.length - answeredCount}</strong></span>
                      </span>
                    </div>

                    <span className="font-mono text-emerald-700 dark:text-emerald-400 font-bold">
                      Tiến độ: {Math.round((answeredCount / (questions.length || 1)) * 100)}%
                    </span>
                  </div>

                  {/* Grouped Questions List by Part */}
                  <div className="space-y-4 overflow-y-auto pr-1 flex-1">
                    {Object.entries(groupedQuestions).map(([partStr, partQuestions]) => {
                      const partNum = Number(partStr);
                      return (
                        <div key={partNum} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-emerald-500" />
                              {partTitles[partNum] || `Part ${partNum}`}
                            </span>
                            <span className="text-[11px] text-neutral-400 font-mono">
                              {partQuestions.filter((item) => userAnswers[item.question.id]).length}/{partQuestions.length} đã làm
                            </span>
                          </div>

                          <div className="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-12 gap-1.5">
                            {partQuestions.map(({ question: q, index }) => {
                              const isCurrent = index === currentQuestionIndex;
                              const answer = userAnswers[q.id];
                              const isCorrect = answer === q.correct_answer;

                              let badgeColor =
                                'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40';
                              if (answer) {
                                badgeColor = isCorrect
                                  ? 'bg-emerald-500 text-white font-bold'
                                  : 'bg-rose-500 text-white font-bold';
                              }
                              if (isCurrent) {
                                badgeColor +=
                                  ' ring-2 ring-emerald-500 ring-offset-2 dark:ring-offset-[#111a14] font-black scale-105';
                              }

                              return (
                                <button
                                  key={q.id}
                                  onClick={() => {
                                    goToQuestion(index);
                                    setIsPaletteOpen(false);
                                  }}
                                  className={`h-8 rounded-lg text-xs flex items-center justify-center font-medium transition ${badgeColor}`}
                                  title={`Câu ${q.question_number}`}
                                >
                                  {q.question_number}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Modal Footer */}
                  <div className="pt-2 border-t border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-between text-xs text-neutral-400">
                    <span>Chọn bất kỳ câu hỏi nào để chuyển ngay tới câu đó</span>
                    <button
                      onClick={() => setIsPaletteOpen(false)}
                      className="px-3 py-1 rounded-xl bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-semibold hover:bg-neutral-200"
                    >
                      Đóng
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Layout Render */}
            {isLoading ? (
              <div className="p-16 text-center text-sm text-neutral-500">Đang tải câu hỏi...</div>
            ) : !currentQuestion ? (
              <div className="p-16 text-center text-sm text-neutral-500 space-y-2">
                <p>{loadError || 'Không tìm thấy câu hỏi cho phần này.'}</p>
                <Link
                  href="/"
                  className="inline-block px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-500 transition"
                >
                  Quay lại trang chủ
                </Link>
              </div>
            ) : [1, 2, 5].includes(currentQuestion.part) ? (
              /* SINGLE CARD (PARTS 1, 2, 5) */
              <SingleCardLayout
                question={currentQuestion}
                group={currentGroup}
                onNext={nextQuestion}
                onPrev={prevQuestion}
                hasNext={currentQuestionIndex < questions.length - 1}
                hasPrev={currentQuestionIndex > 0}
              />
            ) : currentGroup ? (
              /* ADAPTIVE SPLIT (PARTS 3, 4, 6, 7) */
              <AdaptiveSplitLayout
                group={currentGroup}
                questions={linkedQuestions}
                onFinishGroup={handleNextGroup}
                onPrevGroup={handlePrevGroup}
                hasNextGroup={hasNextGroup}
                hasPrevGroup={hasPrevGroup}
              />
            ) : null}
          </div>
        )}
      </main>
    </div>
  );
}

export default function PracticePage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-neutral-500">Đang tải phòng luyện đề...</div>}>
      <PracticeContent />
    </Suspense>
  );
}
