'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { AlertCircle, CheckCircle2, ArrowRight, ShieldCheck } from 'lucide-react';
import { useMistakeStore } from '@/stores/useMistakeStore';
import { useExamStore } from '@/stores/useExamStore';

export const ErrorLogView: React.FC = () => {
  const { mistakes, isLoading, loadMistakes, resolveMistake } = useMistakeStore();
  const { goToQuestion, questions } = useExamStore();

  useEffect(() => {
    loadMistakes();
  }, [loadMistakes]);

  const unresolved = mistakes.filter((m) => !m.resolved);
  const resolved = mistakes.filter((m) => m.resolved);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3 pb-2 border-b border-emerald-950/10 dark:border-emerald-900/30">
        <div>
          <h2 className="text-base sm:text-lg font-black text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-rose-500" />
            <span>Sổ Tay Lỗi Sai</span>
          </h2>
          <p className="text-xs text-neutral-500">
            {unresolved.length} câu cần khắc phục &bull; {resolved.length} câu đã hiểu
          </p>
        </div>

        <Link
          href="/error-log"
          className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1 shadow-xs"
        >
          <span>Mở trang phân tích lỗi ➔</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-neutral-500">Đang tải...</div>
      ) : mistakes.length === 0 ? (
        <div className="p-10 border border-dashed border-emerald-950/20 dark:border-emerald-900/30 rounded-2xl text-center space-y-2 bg-white dark:bg-[#111a14]">
          <ShieldCheck className="w-10 h-10 text-emerald-500 mx-auto" />
          <p className="font-semibold text-neutral-700 dark:text-neutral-300">Không có câu sai nào!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {unresolved.map((mistake) => {
            const q = mistake.question;
            return (
              <div
                key={mistake.id}
                className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs space-y-2.5 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 text-xs font-bold rounded-lg bg-emerald-600 text-white">
                      Câu {q?.question_number || '?'}
                    </span>
                    <span className="text-xs font-medium text-neutral-500">Part {q?.part}</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 font-semibold">
                      Sai {mistake.wrong_count} lần
                    </span>
                  </div>

                  <button
                    onClick={() => resolveMistake(mistake.id)}
                    className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950 dark:text-emerald-300 transition"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Đã hiểu
                  </button>
                </div>

                {q?.question_text && (
                  <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
                    {q.question_text}
                  </p>
                )}

                <div className="flex items-center gap-3 text-xs font-medium p-2 rounded-xl bg-neutral-50 dark:bg-neutral-900/60">
                  <div className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
                    <span className="w-5 h-5 rounded bg-rose-100 dark:bg-rose-950 flex items-center justify-center font-bold">
                      {mistake.selected_wrong_answer}
                    </span>
                    <span className="truncate">Đã chọn</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-neutral-400 shrink-0" />
                  <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                    <span className="w-5 h-5 rounded bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center font-bold">
                      {q?.correct_answer}
                    </span>
                    <span className="truncate">Đúng</span>
                  </div>
                </div>

                {q?.explanation_vi && (
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed border-t border-neutral-100 dark:border-neutral-800 pt-2">
                    {q.explanation_vi}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
