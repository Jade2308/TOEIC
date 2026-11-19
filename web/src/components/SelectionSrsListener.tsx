'use client';

import React, { useState, useEffect, useRef } from 'react';
import { BookmarkPlus, Sparkles, X, Check, BookOpen, Volume2 } from 'lucide-react';
import { useVocabStore } from '@/stores/useVocabStore';

export const SelectionSrsListener: React.FC = () => {
  const { addWord } = useVocabStore();

  const [selectionRange, setSelectionRange] = useState<{
    text: string;
    context: string;
    x: number;
    y: number;
  } | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Form states
  const [word, setWord] = useState('');
  const [phonetic, setPhonetic] = useState('');
  const [meaningVi, setMeaningVi] = useState('');
  const [partOfSpeech, setPartOfSpeech] = useState('vocabulary');
  const [contextSentence, setContextSentence] = useState('');

  // Listen to mouseup / touchend for text selection
  useEffect(() => {
    const handleSelection = () => {
      // Don't trigger if modal is already open
      if (isModalOpen) return;

      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        setSelectionRange(null);
        return;
      }

      const selectedStr = selection.toString().trim();
      // Only trigger for meaningful selections (2 to 60 characters)
      if (selectedStr.length < 2 || selectedStr.length > 70) {
        setSelectionRange(null);
        return;
      }

      // Check if selection is inside an interactive input or button
      const anchorNode = selection.anchorNode;
      const element = anchorNode?.parentElement;
      if (element?.closest('input, textarea, button, select')) {
        setSelectionRange(null);
        return;
      }

      try {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Extract surrounding sentence context
        const parentBlock = element?.closest('p, div, li, span, blockquote');
        let fullContext = parentBlock?.textContent?.trim() || selectedStr;
        // Clean multiple whitespaces
        fullContext = fullContext.replace(/\s+/g, ' ');

        setSelectionRange({
          text: selectedStr,
          context: fullContext,
          x: rect.left + rect.width / 2,
          y: Math.max(10, rect.top - 8),
        });
      } catch (e) {
        setSelectionRange(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, [isModalOpen]);

  // Open modal with pre-filled fields
  const handleOpenModal = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!selectionRange) return;

    setWord(selectionRange.text);
    setContextSentence(selectionRange.context);
    setPhonetic('');
    setMeaningVi('');
    setPartOfSpeech('vocabulary');

    setIsModalOpen(true);
    setSelectionRange(null);
    window.getSelection()?.removeAllRanges();
  };

  const handleSaveVocab = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!word.trim() || !meaningVi.trim()) return;

    await addWord(word.trim(), meaningVi.trim(), contextSentence.trim(), partOfSpeech, phonetic.trim());

    setIsModalOpen(false);
    setToastMessage(`Đã thêm "${word}" vào hàng đợi Spaced Repetition (SRS)!`);
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <>
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-600 text-white text-xs sm:text-sm px-4 py-2.5 rounded-2xl shadow-xl flex items-center gap-2 animate-bounce">
          <Check className="w-4 h-4 text-emerald-200" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Floating Tooltip Button */}
      {selectionRange && !isModalOpen && (
        <div
          style={{
            position: 'fixed',
            left: `${selectionRange.x}px`,
            top: `${selectionRange.y}px`,
            transform: 'translate(-50%, -100%)',
          }}
          className="z-50 animate-fade-in pointer-events-auto"
        >
          <button
            onMouseDown={(e) => {
              // Prevent losing selection before click
              e.preventDefault();
            }}
            onClick={handleOpenModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 text-xs font-bold shadow-2xl hover:scale-105 active:scale-95 transition border border-neutral-700 dark:border-neutral-200"
          >
            <BookmarkPlus className="w-3.5 h-3.5 text-emerald-400 dark:text-emerald-600" />
            <span>+ Lưu vào SRS</span>
          </button>
        </div>
      )}

      {/* Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-neutral-100 dark:border-neutral-800">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                    Lưu Từ Vựng Cần Ôn
                  </h3>
                  <p className="text-[11px] text-neutral-500">
                    Tự động nhắc ôn tập lại theo lịch ngắt quãng
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveVocab} className="space-y-3.5">
              {/* Word & Phonetic */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Từ vựng / Thuật ngữ tiếng Anh *
                  </label>
                  <input
                    type="text"
                    required
                    value={word}
                    onChange={(e) => setWord(e.target.value)}
                    className="w-full text-xs font-semibold px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Phiên âm (Phonetic)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. /kəmˈplɪm.ən.tri/"
                    value={phonetic}
                    onChange={(e) => setPhonetic(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  />
                </div>
              </div>

              {/* Part of Speech & Meaning */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Từ loại
                  </label>
                  <select
                    value={partOfSpeech}
                    onChange={(e) => setPartOfSpeech(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  >
                    <option value="noun">Danh từ (Noun)</option>
                    <option value="verb">Động từ (Verb)</option>
                    <option value="adjective">Tính từ (Adjective)</option>
                    <option value="adverb">Trạng từ (Adverb)</option>
                    <option value="collocation">Cụm từ (Collocation)</option>
                    <option value="idiom">Thành ngữ (Idiom)</option>
                    <option value="vocabulary">Từ vựng chung</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Nghĩa Tiếng Việt *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. miễn phí, tặng kèm"
                    value={meaningVi}
                    onChange={(e) => setMeaningVi(e.target.value)}
                    className="w-full text-xs font-medium px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                    autoFocus
                  />
                </div>
              </div>

              {/* Context Sentence */}
              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Câu ngữ cảnh trích từ bài thi TOEIC
                </label>
                <textarea
                  rows={2}
                  value={contextSentence}
                  onChange={(e) => setContextSentence(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-950 text-neutral-800 dark:text-neutral-200 focus:outline-emerald-500 italic"
                />
              </div>

              {/* Action buttons */}
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-neutral-200 dark:border-neutral-700 text-xs font-semibold hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
                >
                  Hủy
                </button>

                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-sm flex items-center gap-1.5"
                >
                  <BookmarkPlus className="w-3.5 h-3.5" />
                  <span>Lưu vào hệ thống SRS</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
