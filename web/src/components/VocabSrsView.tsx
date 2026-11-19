'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { BookOpen, Plus, ChevronRight } from 'lucide-react';
import { useVocabStore } from '@/stores/useVocabStore';
import { VocabSRS } from '@/types/toeic';

export const VocabSrsView: React.FC = () => {
  const { vocabList, isLoading, loadVocab, rateCard } = useVocabStore();
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  useEffect(() => {
    loadVocab();
  }, [loadVocab]);

  const currentCard: VocabSRS | undefined = vocabList[activeCardIndex];

  const handleRate = async (quality: number) => {
    if (!currentCard) return;
    await rateCard(currentCard.id, quality);
    setIsFlipped(false);
    if (activeCardIndex < vocabList.length - 1) {
      setActiveCardIndex(activeCardIndex + 1);
    } else {
      setActiveCardIndex(0);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3 pb-2 border-b border-emerald-950/10 dark:border-emerald-900/30">
        <div>
          <h2 className="text-base sm:text-lg font-black text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <span>Ôn Tập Từ Vựng SRS</span>
          </h2>
          <p className="text-xs text-neutral-500">
            {vocabList.length} từ vựng trong kho &bull; Thẻ {activeCardIndex + 1}/{vocabList.length}
          </p>
        </div>

        <Link
          href="/vocab-srs"
          className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1 shadow-xs"
        >
          <span>Mở kho từ vựng đầy đủ ➔</span>
        </Link>
      </div>

      {/* Flashcard */}
      {currentCard ? (
        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-3xl p-6 sm:p-8 shadow-xs space-y-5 text-center max-w-xl mx-auto transition-colors">
          <div className="flex items-center justify-between text-xs text-neutral-400">
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              {currentCard.part_of_speech || 'Vocabulary'}
            </span>
            <div className="flex items-center gap-2 font-mono text-[11px]">
              <span className="bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-md">
                Lần nhớ: {currentCard.repetition}
              </span>
              <span className="bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-md">
                {currentCard.interval} ngày
              </span>
            </div>
          </div>

          <div className="space-y-2 py-2">
            <h3 className="text-3xl font-extrabold text-neutral-900 dark:text-white tracking-tight">
              {currentCard.word}
            </h3>
            {currentCard.phonetic && (
              <p className="text-sm font-mono text-emerald-600 dark:text-emerald-400">{currentCard.phonetic}</p>
            )}

            {currentCard.context_sentence && (
              <blockquote className="mt-3 text-xs italic text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-900/60 p-3 rounded-xl border border-neutral-100 dark:border-neutral-800 text-left">
                &ldquo;{currentCard.context_sentence}&rdquo;
              </blockquote>
            )}
          </div>

          {!isFlipped ? (
            <button
              onClick={() => setIsFlipped(true)}
              className="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs transition shadow-sm active:scale-[0.99]"
            >
              Lật thẻ xem nghĩa tiếng Việt
            </button>
          ) : (
            <div className="space-y-3 pt-2 border-t border-emerald-950/10 dark:border-emerald-900/30 animate-fade-in">
              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 rounded-xl border border-emerald-200 dark:border-emerald-800 text-left">
                <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 block mb-0.5">
                  Nghĩa:
                </span>
                <p className="text-base font-bold text-emerald-950 dark:text-emerald-100">
                  {currentCard.meaning_vi}
                </p>
              </div>

              <div className="grid grid-cols-4 gap-2 pt-1">
                <button
                  onClick={() => handleRate(1)}
                  className="p-2 rounded-xl bg-rose-100 hover:bg-rose-200 text-rose-900 dark:bg-rose-950 dark:text-rose-200 text-xs font-bold transition"
                >
                  <span>Quên</span>
                </button>
                <button
                  onClick={() => handleRate(3)}
                  className="p-2 rounded-xl bg-amber-100 hover:bg-amber-200 text-amber-900 dark:bg-amber-950 dark:text-amber-200 text-xs font-bold transition"
                >
                  <span>Khó</span>
                </button>
                <button
                  onClick={() => handleRate(4)}
                  className="p-2 rounded-xl bg-emerald-100 hover:bg-emerald-200 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200 text-xs font-bold transition"
                >
                  <span>Tốt</span>
                </button>
                <button
                  onClick={() => handleRate(5)}
                  className="p-2 rounded-xl bg-teal-100 hover:bg-teal-200 text-teal-900 dark:bg-teal-950 dark:text-teal-200 text-xs font-bold transition"
                >
                  <span>Dễ</span>
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-8 text-center text-sm text-neutral-500">Chưa có từ vựng nào trong kho.</div>
      )}
    </div>
  );
};
