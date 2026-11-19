'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  BookOpen,
  Calendar,
  Clock,
  CheckCircle2,
  Plus,
  Search,
  Check,
  ChevronRight,
  ChevronLeft,
  Award,
  Sparkles,
} from 'lucide-react';
import { useVocabStore } from '@/stores/useVocabStore';
import { VocabSRS } from '@/types/toeic';

export default function VocabSrsPage() {
  const { vocabList, isLoading, loadVocab, rateCard, addWord } = useVocabStore();

  const [activeTab, setActiveTab] = useState<'due' | 'all' | 'mastered'>('due');
  const [activeCardIndex, setActiveCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // New word form state
  const [newWord, setNewWord] = useState('');
  const [newMeaning, setNewMeaning] = useState('');
  const [newSentence, setNewSentence] = useState('');
  const [newPos, setNewPos] = useState('noun');
  const [newPhonetic, setNewPhonetic] = useState('');

  useEffect(() => {
    loadVocab();
  }, [loadVocab]);

  const now = new Date();

  const filteredCards = vocabList.filter((item) => {
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const match =
        item.word.toLowerCase().includes(q) || item.meaning_vi.toLowerCase().includes(q);
      if (!match) return false;
    }

    if (activeTab === 'due') {
      return new Date(item.due_date) <= now;
    }
    if (activeTab === 'mastered') {
      return item.repetition >= 3;
    }
    return true;
  });

  const currentCard: VocabSRS | undefined = filteredCards[activeCardIndex] || filteredCards[0];

  useEffect(() => {
    setActiveCardIndex(0);
    setIsFlipped(false);
  }, [activeTab]);

  const handleRate = async (quality: number) => {
    if (!currentCard) return;

    await rateCard(currentCard.id, quality);
    setIsFlipped(false);

    let qualityLabel = '';
    if (quality === 1) qualityLabel = 'Quên (Reset 1 ngày)';
    else if (quality === 3) qualityLabel = 'Khó (Tăng chậm)';
    else if (quality === 4) qualityLabel = 'Tốt (Chuẩn SM-2)';
    else if (quality === 5) qualityLabel = 'Dễ (Dài hạn)';

    setToastMsg(`Đã đánh giá [${qualityLabel}] cho "${currentCard.word}"`);
    setTimeout(() => setToastMsg(null), 2500);

    if (activeCardIndex < filteredCards.length - 1) {
      setActiveCardIndex(activeCardIndex + 1);
    } else {
      setActiveCardIndex(0);
    }
  };

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        setIsFlipped((prev) => !prev);
        return;
      }

      if (isFlipped) {
        if (e.key === '1') handleRate(1);
        else if (e.key === '2') handleRate(3);
        else if (e.key === '3') handleRate(4);
        else if (e.key === '4') handleRate(5);
      }

      if (e.key === 'ArrowRight' && activeCardIndex < filteredCards.length - 1) {
        setActiveCardIndex((prev) => prev + 1);
        setIsFlipped(false);
      }
      if (e.key === 'ArrowLeft' && activeCardIndex > 0) {
        setActiveCardIndex((prev) => prev - 1);
        setIsFlipped(false);
      }
    },
    [isFlipped, activeCardIndex, filteredCards.length, handleRate]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleAddNewWord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWord || !newMeaning) return;

    await addWord(newWord, newMeaning, newSentence || newWord, newPos, newPhonetic);
    setNewWord('');
    setNewMeaning('');
    setNewSentence('');
    setNewPhonetic('');
    setShowAddModal(false);
    setToastMsg(`Đã thêm từ "${newWord}" vào kho SRS!`);
    setTimeout(() => setToastMsg(null), 2500);
  };

  const dueCount = vocabList.filter((v) => new Date(v.due_date) <= now).length;
  const masteredCount = vocabList.filter((v) => v.repetition >= 3).length;
  const avgInterval =
    vocabList.length > 0
      ? (vocabList.reduce((acc, curr) => acc + curr.interval, 0) / vocabList.length).toFixed(1)
      : '0';

  return (
    <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 md:p-8 space-y-6">
      {/* Toast */}
      {toastMsg && (
        <div className="fixed top-16 right-4 z-50 bg-emerald-600 text-white text-xs px-4 py-2.5 rounded-2xl shadow-xl flex items-center gap-2 animate-bounce">
          <Check className="w-4 h-4 text-emerald-200" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Subheader */}
      <div className="flex items-center justify-between flex-wrap gap-3 pb-2 border-b border-emerald-950/10 dark:border-emerald-900/30">
        <div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <span>Từ Vựng SRS (Spaced Repetition)</span>
          </h1>
          <p className="text-xs text-neutral-500">Ôn tập ngắt quãng tối ưu theo thuật toán SuperMemo SM-2</p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Thêm từ mới</span>
        </button>
      </div>

      {/* Quick Stats Grid */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-neutral-500 text-xs">
            <span className="font-semibold">Cần ôn hôm nay</span>
            <Clock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400">
              {dueCount}
            </span>
            <span className="text-xs text-neutral-400 font-medium">thẻ</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-neutral-500 text-xs">
            <span className="font-semibold">Tổng từ trong kho</span>
            <BookOpen className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-black text-neutral-900 dark:text-neutral-100">
              {vocabList.length}
            </span>
            <span className="text-xs text-neutral-400 font-medium">từ vựng</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-neutral-500 text-xs">
            <span className="font-semibold">Đã thuộc vững</span>
            <Award className="w-4 h-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-black text-teal-600 dark:text-teal-400">
              {masteredCount}
            </span>
            <span className="text-xs text-neutral-400 font-medium">từ</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-neutral-500 text-xs">
            <span className="font-semibold">Chu kỳ trung bình</span>
            <Calendar className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400">
              {avgInterval}
            </span>
            <span className="text-xs text-neutral-400 font-medium">ngày</span>
          </div>
        </div>
      </section>

      {/* Tabs & Search */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-1 bg-emerald-950/5 dark:bg-emerald-950/30 p-1 rounded-2xl border border-emerald-900/10 dark:border-emerald-800/30 text-xs font-bold">
          <button
            onClick={() => setActiveTab('due')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'due'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:text-emerald-700'
            }`}
          >
            Cần ôn ({dueCount})
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'all'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:text-emerald-700'
            }`}
          >
            Tất cả ({vocabList.length})
          </button>
          <button
            onClick={() => setActiveTab('mastered')}
            className={`px-3 py-1.5 rounded-xl transition ${
              activeTab === 'mastered'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:text-emerald-700'
            }`}
          >
            Đã thuộc ({masteredCount})
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Tìm từ hoặc nghĩa..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#111a14] text-xs focus:outline-emerald-500"
          />
        </div>
      </div>

      {/* Flashcard Arena */}
      {filteredCards.length > 0 && currentCard ? (
        <div className="max-w-2xl mx-auto space-y-4">
          {/* Card Box */}
          <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-3xl p-6 sm:p-10 shadow-md text-center relative overflow-hidden transition-colors">
            {/* Top Card Badge */}
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-4">
              <span className="inline-block text-[11px] uppercase tracking-wider font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/70 px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-900">
                {currentCard.part_of_speech || 'Vocabulary'}
              </span>

              <div className="flex items-center gap-2 font-mono text-[11px]">
                <span className="bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-md">
                  Lần nhớ: {currentCard.repetition}
                </span>
                <span className="bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-md">
                  Chu kỳ: {currentCard.interval} ngày
                </span>
              </div>
            </div>

            {/* Word Front */}
            <div className="py-4 space-y-3">
              <h2 className="text-4xl sm:text-5xl font-black text-neutral-900 dark:text-white tracking-tight">
                {currentCard.word}
              </h2>

              {currentCard.phonetic && (
                <p className="text-sm font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                  {currentCard.phonetic}
                </p>
              )}

              {currentCard.context_sentence && (
                <blockquote className="mt-4 text-xs sm:text-sm italic text-neutral-600 dark:text-neutral-300 bg-neutral-50 dark:bg-neutral-900/60 p-4 rounded-2xl border border-neutral-200/50 dark:border-neutral-800 leading-relaxed text-left">
                  &ldquo;{currentCard.context_sentence}&rdquo;
                </blockquote>
              )}
            </div>

            {/* Action Flip / Rate */}
            {!isFlipped ? (
              <button
                onClick={() => setIsFlipped(true)}
                className="w-full py-3.5 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm transition shadow-md mt-4 active:scale-[0.99]"
              >
                Lật thẻ xem nghĩa (Phím Space)
              </button>
            ) : (
              <div className="space-y-4 pt-4 border-t border-emerald-950/10 dark:border-emerald-900/30 animate-fade-in">
                <div className="p-4 bg-emerald-50 dark:bg-emerald-950/50 rounded-2xl border border-emerald-200 dark:border-emerald-800 text-left">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 block mb-1">
                    Nghĩa Tiếng Việt:
                  </span>
                  <p className="text-lg sm:text-xl font-extrabold text-emerald-950 dark:text-emerald-100 leading-relaxed">
                    {currentCard.meaning_vi}
                  </p>
                </div>

                <div className="grid grid-cols-4 gap-2 pt-1">
                  <button
                    onClick={() => handleRate(1)}
                    className="p-3 rounded-2xl bg-rose-100 hover:bg-rose-200 text-rose-900 dark:bg-rose-950/80 dark:text-rose-200 text-xs font-bold transition flex flex-col items-center justify-center gap-0.5 border border-rose-300 dark:border-rose-900 active:scale-95"
                  >
                    <span className="text-sm font-black">Quên</span>
                    <span className="text-[10px] opacity-75 font-normal">1 ngày</span>
                  </button>

                  <button
                    onClick={() => handleRate(3)}
                    className="p-3 rounded-2xl bg-amber-100 hover:bg-amber-200 text-amber-900 dark:bg-amber-950/80 dark:text-amber-200 text-xs font-bold transition flex flex-col items-center justify-center gap-0.5 border border-amber-300 dark:border-amber-900 active:scale-95"
                  >
                    <span className="text-sm font-black">Khó</span>
                    <span className="text-[10px] opacity-75 font-normal">Tăng chậm</span>
                  </button>

                  <button
                    onClick={() => handleRate(4)}
                    className="p-3 rounded-2xl bg-emerald-100 hover:bg-emerald-200 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200 text-xs font-bold transition flex flex-col items-center justify-center gap-0.5 border border-emerald-300 dark:border-emerald-900 active:scale-95"
                  >
                    <span className="text-sm font-black">Tốt</span>
                    <span className="text-[10px] opacity-75 font-normal">Chuẩn SM-2</span>
                  </button>

                  <button
                    onClick={() => handleRate(5)}
                    className="p-3 rounded-2xl bg-teal-100 hover:bg-teal-200 text-teal-900 dark:bg-teal-950/80 dark:text-teal-200 text-xs font-bold transition flex flex-col items-center justify-center gap-0.5 border border-teal-300 dark:border-teal-900 active:scale-95"
                  >
                    <span className="text-sm font-black">Dễ</span>
                    <span className="text-[10px] opacity-75 font-normal">Dài hạn</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between text-xs font-bold px-1">
            <button
              onClick={() => {
                if (activeCardIndex > 0) {
                  setActiveCardIndex(activeCardIndex - 1);
                  setIsFlipped(false);
                }
              }}
              disabled={activeCardIndex === 0}
              className="px-4 py-2 rounded-xl border border-neutral-300 dark:border-neutral-700 hover:bg-emerald-50 dark:hover:bg-neutral-800 disabled:opacity-30 transition flex items-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Thẻ trước</span>
            </button>

            <span className="text-neutral-400 font-mono">
              {activeCardIndex + 1} / {filteredCards.length}
            </span>

            <button
              onClick={() => {
                if (activeCardIndex < filteredCards.length - 1) {
                  setActiveCardIndex(activeCardIndex + 1);
                  setIsFlipped(false);
                }
              }}
              disabled={activeCardIndex === filteredCards.length - 1}
              className="px-4 py-2 rounded-xl border border-neutral-300 dark:border-neutral-700 hover:bg-emerald-50 dark:hover:bg-neutral-800 disabled:opacity-30 transition flex items-center gap-1"
            >
              <span>Thẻ sau</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 space-y-3">
          <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto" />
          <h3 className="font-extrabold text-base text-neutral-800 dark:text-neutral-200">
            {activeTab === 'due'
              ? 'Bạn đã hoàn thành toàn bộ thẻ cần ôn hôm nay!'
              : 'Không có thẻ từ vựng nào.'}
          </h3>
        </div>
      )}

      {/* Word Deck Grid */}
      <section className="space-y-3 pt-6 border-t border-emerald-950/10 dark:border-emerald-900/30">
        <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
          Danh Sách Từ Vựng ({vocabList.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {vocabList.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                const targetIdx = filteredCards.findIndex((c) => c.id === item.id);
                if (targetIdx !== -1) {
                  setActiveCardIndex(targetIdx);
                } else {
                  setActiveTab('all');
                  setTimeout(() => {
                    const newIdx = vocabList.findIndex((c) => c.id === item.id);
                    if (newIdx !== -1) setActiveCardIndex(newIdx);
                  }, 50);
                }
                setIsFlipped(false);
                window.scrollTo({ top: 120, behavior: 'smooth' });
              }}
              className="p-4 rounded-2xl border border-emerald-950/10 dark:border-emerald-900/30 bg-white dark:bg-[#111a14] hover:border-emerald-500 transition cursor-pointer shadow-xs space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-neutral-900 dark:text-neutral-100 group-hover:text-emerald-600 transition">
                  {item.word}
                </span>
                <span className="text-[10px] font-mono font-semibold bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-full text-neutral-500">
                  {item.interval}d &bull; Rep: {item.repetition}
                </span>
              </div>

              <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate">
                {item.meaning_vi}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Modal: Add Word */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white dark:bg-[#111a14] border border-emerald-950/20 dark:border-emerald-900/40 rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-neutral-100 dark:border-neutral-800">
              <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                Thêm Từ Vựng Mới
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-xs text-neutral-400 hover:text-neutral-600"
              >
                Đóng
              </button>
            </div>

            <form onSubmit={handleAddNewWord} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Từ tiếng Anh *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. negotiation"
                    value={newWord}
                    onChange={(e) => setNewWord(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Phiên âm
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. /nəˌɡoʊ.ʃiˈeɪ.ʃən/"
                    value={newPhonetic}
                    onChange={(e) => setNewPhonetic(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Từ loại
                  </label>
                  <select
                    value={newPos}
                    onChange={(e) => setNewPos(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  >
                    <option value="noun">Danh từ (Noun)</option>
                    <option value="verb">Động từ (Verb)</option>
                    <option value="adjective">Tính từ (Adjective)</option>
                    <option value="adverb">Trạng từ (Adverb)</option>
                    <option value="collocation">Cụm từ (Collocation)</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Nghĩa Tiếng Việt *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. sự đàm phán, thương lượng"
                    value={newMeaning}
                    onChange={(e) => setNewMeaning(e.target.value)}
                    className="w-full text-xs px-3 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Câu ngữ cảnh
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Contract negotiations will resume next Monday."
                  value={newSentence}
                  onChange={(e) => setNewSentence(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-950 focus:outline-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl border text-xs font-bold hover:bg-neutral-100 dark:hover:bg-neutral-800"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-sm"
                >
                  Lưu vào kho
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
