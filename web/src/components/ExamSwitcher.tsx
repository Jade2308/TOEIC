'use client';

import React, { useEffect, useId, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  BookOpen,
  ChevronDown,
  Check,
  Layers,
  X,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { useExamStore } from '@/stores/useExamStore';
import { ExamSummary } from '@/types/toeic';

export function ExamSwitcher({ className = '' }: { className?: string }) {
  const router = useRouter();
  const titleId = useId();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const {
    availableExams,
    isLoadingExams,
    hasLoadedExams,
    selectedTestId,
    selectedTest,
    loadAvailableExams,
    setSelectedTest,
  } = useExamStore();

  useEffect(() => {
    if (!hasLoadedExams) {
      loadAvailableExams();
    }
  }, [hasLoadedExams, loadAvailableExams]);

  // Fallback light-dismiss for browsers without native <dialog closedby="any"> support
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog || typeof HTMLDialogElement === 'undefined') return;
    if ('closedBy' in HTMLDialogElement.prototype) return;

    const isOutside = (e: PointerEvent) => {
      const r = dialog.getBoundingClientRect();
      return (
        e.clientX < r.left ||
        e.clientX > r.right ||
        e.clientY < r.top ||
        e.clientY > r.bottom
      );
    };

    let pressedOutside = false;
    const onPointerDown = (e: PointerEvent) => {
      pressedOutside = isOutside(e);
    };
    const onPointerUp = (e: PointerEvent) => {
      if (pressedOutside && isOutside(e)) {
        dialog.close();
      }
      pressedOutside = false;
    };

    dialog.addEventListener('pointerdown', onPointerDown);
    dialog.addEventListener('pointerup', onPointerUp);
    return () => {
      dialog.removeEventListener('pointerdown', onPointerDown);
      dialog.removeEventListener('pointerup', onPointerUp);
    };
  }, []);

  const handleOpen = () => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
    // Always re-scan server filesystem when opening modal so newly crawled tests show immediately
    loadAvailableExams(true);
  };

  const handleClose = () => {
    const dialog = dialogRef.current;
    if (dialog?.open) {
      dialog.close();
    }
  };

  const handleDialogClose = () => {
    const dialog = dialogRef.current;
    if (dialog) {
      dialog.returnValue = '';
    }
  };

  const currentExam =
    availableExams.find(
      (t) =>
        t.id === selectedTestId ||
        t.name.toLowerCase() === selectedTest.toLowerCase()
    ) || availableExams[0];

  const handleSelectExam = async (exam: ExamSummary) => {
    await setSelectedTest(exam.id);
    handleClose();

    if (typeof window !== 'undefined' && window.location.pathname.startsWith('/practice')) {
      const currentParams = new URLSearchParams(window.location.search);
      const part = currentParams.get('part') || 'all';
      router.push(`/practice?part=${part}&test=${encodeURIComponent(exam.id)}`);
    }
  };

  const triggerLabel = currentExam
    ? currentExam.name
    : isLoadingExams
    ? 'Đang tải đề...'
    : 'Chưa có đề thi';

  return (
    <>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={handleOpen}
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-emerald-950/15 dark:border-emerald-800/40 bg-emerald-50/60 dark:bg-emerald-950/30 hover:bg-emerald-100/80 dark:hover:bg-emerald-950/60 text-emerald-900 dark:text-emerald-200 text-xs font-bold transition shadow-2xs group ${className}`}
        title="Chọn đề thi khác"
      >
        <BookOpen className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
        <span className="truncate max-w-[160px] sm:max-w-[220px]">{triggerLabel}</span>
        <ChevronDown className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 group-hover:translate-y-0.5 transition shrink-0" />
      </button>

      {/* Native Top-Layer Modal Dialog */}
      <dialog
        ref={dialogRef}
        aria-labelledby={titleId}
        onClose={handleDialogClose}
        {...({ closedby: 'any' } as Record<string, string>)}
        className="m-auto w-[calc(100%-2rem)] max-w-xl max-h-[90vh] open:flex flex-col gap-4 overflow-hidden bg-white dark:bg-[#111a14] text-neutral-900 dark:text-neutral-100 border border-emerald-950/20 dark:border-emerald-900/40 rounded-3xl p-5 sm:p-6 shadow-2xl backdrop:bg-black/60 backdrop:backdrop-blur-xs"
      >
        {/* Header */}
        <div className="flex items-center justify-between gap-3 pb-3 border-b border-emerald-950/10 dark:border-emerald-900/30 shrink-0">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
              <Layers className="w-4 h-4" />
            </div>
            <h2
              id={titleId}
              className="text-base font-black text-neutral-900 dark:text-neutral-100 truncate"
            >
              Chọn Đề Thi ({availableExams.length} Đề)
            </h2>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            <button
              type="button"
              onClick={() => loadAvailableExams(true)}
              disabled={isLoadingExams}
              className="p-1.5 rounded-xl text-neutral-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition"
              title="Làm mới danh sách đề"
              aria-label="Làm mới danh sách đề"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingExams ? 'animate-spin' : ''}`} />
            </button>
            <button
              type="button"
              onClick={handleClose}
              className="p-1.5 rounded-xl text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 transition"
              aria-label="Đóng"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Dynamic List of Processed Tests */}
        <div className="space-y-2.5 overflow-y-auto overscroll-contain p-0.5 pr-1.5 flex-1 min-h-0">
          {availableExams.length === 0 ? (
            <div className="p-8 text-center rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-700 text-xs text-neutral-500 space-y-2">
              <p className="font-bold text-neutral-700 dark:text-neutral-300">
                {isLoadingExams ? 'Đang tải danh sách đề thi...' : 'Chưa có đề thi nào.'}
              </p>
              <p>
                Hãy tải thêm đề ở mục Tải đề rồi bấm làm mới phía trên.
              </p>
            </div>
          ) : (
            availableExams.map((exam) => {
              const isSelected =
                currentExam?.id === exam.id ||
                selectedTest.toLowerCase() === exam.name.toLowerCase();

              return (
                <button
                  key={exam.id}
                  type="button"
                  onClick={() => handleSelectExam(exam)}
                  className={`w-full text-left p-3.5 rounded-2xl border transition flex items-center justify-between gap-3 cursor-pointer ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-50/70 dark:bg-emerald-950/40 text-emerald-950 dark:text-emerald-100 ring-2 ring-emerald-500/30'
                      : 'border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#111a14] hover:border-emerald-500/60'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span
                      className={`px-2.5 h-9 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                        isSelected
                          ? 'bg-emerald-600 text-white'
                          : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                      }`}
                    >
                      {exam.shortTitle}
                    </span>

                    <div className="min-w-0 flex items-center gap-2 flex-wrap">
                      <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100 truncate">
                        {exam.name}
                      </h3>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1 shrink-0">
                        <CheckCircle2 className="w-3 h-3" /> {exam.totalQuestions} câu
                      </span>
                    </div>
                  </div>

                  <div className="shrink-0">
                    {isSelected ? (
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                        <Check className="w-4 h-4" />
                        <span className="hidden sm:inline">Đang luyện</span>
                      </span>
                    ) : (
                      <span className="inline-block px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-2xs">
                        Chọn đề này
                      </span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="pt-2 border-t border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-end shrink-0">
          <button
            type="button"
            onClick={handleClose}
            className="text-xs font-semibold text-neutral-600 dark:text-neutral-300 hover:underline shrink-0"
          >
            Đóng
          </button>
        </div>
      </dialog>
    </>
  );
}
