'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  CheckCircle2,
  Play,
  RotateCcw,
  ArrowRight,
  ShieldCheck,
  Headphones,
  Search,
  ChevronLeft,
  Target,
  Layers,
} from 'lucide-react';
import { useMistakeStore } from '@/stores/useMistakeStore';
import { UserMistake, QuestionOptionKey } from '@/types/toeic';

export default function ErrorLogPage() {
  const { mistakes, isLoading, loadMistakes, resolveMistake, toggleResolveMistake, recordMistake } =
    useMistakeStore();

  const [activeTab, setActiveTab] = useState<'unresolved' | 'resolved' | 'all'>('unresolved');
  const [selectedPartFilter, setSelectedPartFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Drill Mode State
  const [isDrillMode, setIsDrillMode] = useState(false);
  const [drillIndex, setDrillIndex] = useState(0);
  const [drillSelectedAnswer, setDrillSelectedAnswer] = useState<QuestionOptionKey | null>(null);
  const [drillAnswerSubmitted, setDrillAnswerSubmitted] = useState(false);
  const [drillIsCorrect, setDrillIsCorrect] = useState<boolean | null>(null);

  useEffect(() => {
    loadMistakes();
  }, [loadMistakes]);

  // Derived filtered mistakes for list view
  const filteredMistakes = useMemo(() => {
    return mistakes.filter((m) => {
      if (activeTab === 'unresolved' && m.resolved) return false;
      if (activeTab === 'resolved' && !m.resolved) return false;

      if (selectedPartFilter !== 'all') {
        const partNum = parseInt(selectedPartFilter, 10);
        if (m.question?.part !== partNum) return false;
      }

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const textMatch = m.question?.question_text?.toLowerCase().includes(q);
        const explMatch = m.question?.explanation_vi?.toLowerCase().includes(q);
        if (!textMatch && !explMatch) return false;
      }

      return true;
    });
  }, [mistakes, activeTab, selectedPartFilter, searchQuery]);

  // Mistakes for drill mode
  const drillPool = useMemo(() => {
    if (activeTab === 'resolved') {
      return mistakes.filter((m) => m.resolved);
    }
    const unres = mistakes.filter((m) => !m.resolved);
    return unres.length > 0 ? unres : mistakes;
  }, [mistakes, activeTab]);

  const currentDrillMistake = drillPool[drillIndex] || drillPool[0];

  const handleStartDrill = () => {
    setDrillIndex(0);
    setDrillSelectedAnswer(null);
    setDrillAnswerSubmitted(false);
    setDrillIsCorrect(null);
    setIsDrillMode(true);
  };

  const handleExitDrill = () => {
    setIsDrillMode(false);
    setDrillSelectedAnswer(null);
    setDrillAnswerSubmitted(false);
    setDrillIsCorrect(null);
    loadMistakes();
  };

  const handleSelectDrillAnswer = async (key: QuestionOptionKey) => {
    if (drillAnswerSubmitted || !currentDrillMistake?.question) return;

    setDrillSelectedAnswer(key);
    setDrillAnswerSubmitted(true);

    const correct = currentDrillMistake.question.correct_answer === key;
    setDrillIsCorrect(correct);

    if (correct) {
      await resolveMistake(currentDrillMistake.id);
    } else {
      await recordMistake(currentDrillMistake.question_id, key);
    }
  };

  const handleNextDrillQuestion = () => {
    if (drillIndex < drillPool.length - 1) {
      setDrillIndex(drillIndex + 1);
    } else {
      setDrillIndex(0);
    }
    setDrillSelectedAnswer(null);
    setDrillAnswerSubmitted(false);
    setDrillIsCorrect(null);
  };

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isDrillMode || drillAnswerSubmitted) return;
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;

      if (['1', 'A'].includes(e.key.toUpperCase())) handleSelectDrillAnswer('A');
      else if (['2', 'B'].includes(e.key.toUpperCase())) handleSelectDrillAnswer('B');
      else if (['3', 'C'].includes(e.key.toUpperCase())) handleSelectDrillAnswer('C');
      else if (['4', 'D'].includes(e.key.toUpperCase())) handleSelectDrillAnswer('D');
    },
    [isDrillMode, drillAnswerSubmitted, currentDrillMistake]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const unresolvedCount = mistakes.filter((m) => !m.resolved).length;
  const resolvedCount = mistakes.filter((m) => m.resolved).length;
  const resolutionRate =
    mistakes.length > 0 ? Math.round((resolvedCount / mistakes.length) * 100) : 0;

  return (
    <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 md:p-8 space-y-6">
      {/* Subheader */}
      <div className="flex items-center justify-between flex-wrap gap-3 pb-2 border-b border-emerald-950/10 dark:border-emerald-900/30">
        <div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-rose-500" />
            <span>Sổ Tay Lỗi Sai (Error Log)</span>
          </h1>
          <p className="text-xs text-neutral-500">Tự động lưu câu sai và phân loại để luyện tập khắc phục</p>
        </div>

        {!isDrillMode && unresolvedCount > 0 && (
          <button
            onClick={handleStartDrill}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Luyện lại câu sai ({unresolvedCount})</span>
          </button>
        )}
      </div>

      {/* ================================================================== */}
      {/* DRILL MODE VIEW                                                    */}
      {/* ================================================================== */}
      {isDrillMode ? (
        <section className="bg-white dark:bg-[#111a14] rounded-3xl p-6 sm:p-8 border border-emerald-950/10 dark:border-emerald-900/30 shadow-md space-y-6 animate-fade-in">
          {/* Top Drill Controls */}
          <div className="flex items-center justify-between pb-3 border-b border-neutral-100 dark:border-neutral-800">
            <button
              onClick={handleExitDrill}
              className="px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-700 text-xs font-bold hover:bg-neutral-100 dark:hover:bg-neutral-800 transition flex items-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Dừng luyện tập</span>
            </button>

            <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
              Câu {drillIndex + 1} / {drillPool.length}
            </span>
          </div>

          {currentDrillMistake && currentDrillMistake.question ? (
            (() => {
              const q = currentDrillMistake.question;
              return (
                <div className="space-y-5 max-w-3xl mx-auto">
                  {/* Listening audio if applicable */}
                  {currentDrillMistake.group?.audio_url && (
                    <div className="p-3.5 rounded-2xl bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-800 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2.5">
                        <Headphones className="w-4 h-4 text-emerald-600" />
                        <span className="text-xs font-bold">Audio Part {q.part}</span>
                      </div>
                      <audio controls src={currentDrillMistake.group.audio_url} className="h-9 w-64" />
                    </div>
                  )}

                  {/* Question Prompt */}
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-neutral-400 uppercase tracking-wider">
                      Part {q.part} &bull; Câu {q.question_number}
                    </span>
                    <h3 className="text-base sm:text-lg font-bold text-neutral-900 dark:text-neutral-100">
                      {q.question_text || '(Nghe audio để chọn đáp án)'}
                    </h3>
                  </div>

                  {/* Options */}
                  <div className="grid grid-cols-1 gap-2.5">
                    {(['A', 'B', 'C', 'D'] as QuestionOptionKey[]).map((key) => {
                      const text = q.options[key];
                      if (!text) return null;

                      const isSelected = drillSelectedAnswer === key;
                      const isCorrectOption = q.correct_answer === key;

                      let btnStyle =
                        'border-neutral-200 dark:border-neutral-800 hover:border-emerald-500 hover:bg-neutral-50 dark:hover:bg-neutral-800/60';

                      if (drillAnswerSubmitted) {
                        if (isCorrectOption) {
                          btnStyle =
                            'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-950 dark:text-emerald-100 font-bold ring-2 ring-emerald-500';
                        } else if (isSelected && !drillIsCorrect) {
                          btnStyle =
                            'border-rose-500 bg-rose-50 dark:bg-rose-950/60 text-rose-950 dark:text-rose-100 font-bold ring-2 ring-rose-500';
                        } else {
                          btnStyle = 'opacity-40 border-neutral-200 dark:border-neutral-800';
                        }
                      }

                      return (
                        <button
                          key={key}
                          disabled={drillAnswerSubmitted}
                          onClick={() => handleSelectDrillAnswer(key)}
                          className={`w-full p-3.5 rounded-2xl border text-left transition flex items-center justify-between ${btnStyle}`}
                        >
                          <div className="flex items-center gap-3">
                            <span
                              className={`w-7 h-7 rounded-xl flex items-center justify-center font-bold text-xs ${
                                drillAnswerSubmitted && isCorrectOption
                                  ? 'bg-emerald-600 text-white'
                                  : drillAnswerSubmitted && isSelected && !drillIsCorrect
                                  ? 'bg-rose-600 text-white'
                                  : 'bg-neutral-100 dark:bg-neutral-800'
                              }`}
                            >
                              {key}
                            </span>
                            <span className="text-sm font-medium">{text}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Answer Feedback */}
                  {drillAnswerSubmitted && (
                    <div className="space-y-3 pt-2 animate-fade-in">
                      <div
                        className={`p-3.5 rounded-xl border flex items-center justify-between text-xs font-bold ${
                          drillIsCorrect
                            ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                            : 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200'
                        }`}
                      >
                        <span>
                          {drillIsCorrect
                            ? '✓ Chính xác! Câu này đã được đánh dấu là đã hiểu.'
                            : `✗ Chưa đúng! Đáp án chuẩn là (${q.correct_answer}).`}
                        </span>

                        <button
                          onClick={handleNextDrillQuestion}
                          className="px-4 py-1.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 text-xs font-bold transition flex items-center gap-1 shadow-sm"
                        >
                          <span>Câu tiếp theo</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {q.explanation_vi && (
                        <div className="p-3.5 rounded-xl bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-800 text-xs space-y-1">
                          <strong className="block text-neutral-800 dark:text-neutral-200">Giải thích:</strong>
                          <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed whitespace-pre-line">
                            {q.explanation_vi}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })()
          ) : (
            <div className="p-8 text-center text-sm text-neutral-500">
              Không có câu hỏi trong hàng đợi.
            </div>
          )}
        </section>
      ) : null}

      {/* ================================================================== */}
      {/* STATS & LIST VIEW                                                  */}
      {/* ================================================================== */}
      {!isDrillMode && (
        <>
          {/* 4 Stats Cards */}
          <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
              <span className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider block">
                Tổng lỗi sai
              </span>
              <div className="text-2xl sm:text-3xl font-black text-neutral-900 dark:text-neutral-100 mt-1">
                {mistakes.length}
              </div>
            </div>

            <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
              <span className="text-[11px] font-semibold text-rose-600 dark:text-rose-400 uppercase tracking-wider block">
                Cần sửa
              </span>
              <div className="text-2xl sm:text-3xl font-black text-rose-600 dark:text-rose-400 mt-1">
                {unresolvedCount}
              </div>
            </div>

            <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
              <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                Đã hiểu rõ
              </span>
              <div className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
                {resolvedCount}
              </div>
            </div>

            <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-4 shadow-xs">
              <span className="text-[11px] font-semibold text-teal-600 dark:text-teal-400 uppercase tracking-wider block">
                Tỉ lệ khắc phục
              </span>
              <div className="text-2xl sm:text-3xl font-black text-teal-600 dark:text-teal-400 mt-1">
                {resolutionRate}%
              </div>
            </div>
          </section>

          {/* Filter Bar */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-1 bg-emerald-950/5 dark:bg-emerald-950/30 p-1 rounded-2xl border border-emerald-900/10 dark:border-emerald-800/30 text-xs font-bold">
              <button
                onClick={() => setActiveTab('unresolved')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  activeTab === 'unresolved'
                    ? 'bg-rose-500 text-white shadow-xs'
                    : 'text-neutral-600 dark:text-neutral-400 hover:text-rose-600'
                }`}
              >
                Cần sửa ({unresolvedCount})
              </button>
              <button
                onClick={() => setActiveTab('resolved')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  activeTab === 'resolved'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'text-neutral-600 dark:text-neutral-400 hover:text-emerald-600'
                }`}
              >
                Đã hiểu ({resolvedCount})
              </button>
              <button
                onClick={() => setActiveTab('all')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  activeTab === 'all'
                    ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 shadow-xs'
                    : 'text-neutral-600 dark:text-neutral-400'
                }`}
              >
                Tất cả ({mistakes.length})
              </button>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={selectedPartFilter}
                onChange={(e) => setSelectedPartFilter(e.target.value)}
                className="text-xs px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-[#111a14] font-medium focus:outline-emerald-500"
              >
                <option value="all">Tất cả Part</option>
                <option value="1">Part 1</option>
                <option value="2">Part 2</option>
                <option value="3">Part 3</option>
                <option value="4">Part 4</option>
                <option value="5">Part 5</option>
                <option value="6">Part 6</option>
                <option value="7">Part 7</option>
              </select>

              <div className="relative w-44 sm:w-56">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
                <input
                  type="text"
                  placeholder="Tìm câu hỏi..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full text-xs pl-8 pr-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-[#111a14] focus:outline-emerald-500"
                />
              </div>
            </div>
          </div>

          {/* Mistakes Cards List */}
          {isLoading ? (
            <div className="p-12 text-center text-sm text-neutral-500">Đang tải...</div>
          ) : filteredMistakes.length === 0 ? (
            <div className="p-12 rounded-3xl border border-dashed border-emerald-950/20 dark:border-emerald-900/30 text-center space-y-3 bg-white dark:bg-[#111a14]">
              <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto" />
              <h4 className="font-bold text-neutral-800 dark:text-neutral-200 text-base">
                {activeTab === 'unresolved' ? 'Không có câu sai nào cần sửa!' : 'Không có câu hỏi nào.'}
              </h4>
            </div>
          ) : (
            <div className="space-y-3.5">
              {filteredMistakes.map((mistake) => {
                const q = mistake.question;
                return (
                  <div
                    key={mistake.id}
                    className={`rounded-2xl border p-4 sm:p-5 transition shadow-xs space-y-3 ${
                      mistake.resolved
                        ? 'bg-white/60 dark:bg-[#111a14]/60 border-neutral-200 dark:border-neutral-800/80 opacity-75'
                        : 'bg-white dark:bg-[#111a14] border-emerald-950/10 dark:border-emerald-900/30'
                    }`}
                  >
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        <span className="w-7 h-7 rounded-lg bg-emerald-600 text-white font-bold text-xs flex items-center justify-center">
                          {q?.question_number || '?'}
                        </span>
                        <span className="text-xs font-semibold text-neutral-500">Part {q?.part}</span>
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                          Sai {mistake.wrong_count || 1} lần
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleResolveMistake(mistake.id, !mistake.resolved)}
                          className={`text-xs font-bold px-3 py-1.5 rounded-xl transition flex items-center gap-1 ${
                            mistake.resolved
                              ? 'bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300'
                              : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                          }`}
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>{mistake.resolved ? 'Cần ôn lại' : 'Đã hiểu'}</span>
                        </button>
                      </div>
                    </div>

                    {q?.question_text && (
                      <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                        {q.question_text}
                      </p>
                    )}

                    {/* Wrong vs Correct Answer Pill */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-center gap-2 text-rose-900 dark:text-rose-200">
                        <span className="w-5 h-5 rounded bg-rose-500 text-white flex items-center justify-center font-bold text-[11px] shrink-0">
                          {mistake.selected_wrong_answer}
                        </span>
                        <span className="truncate">{q?.options[mistake.selected_wrong_answer] || 'Bạn đã chọn'}</span>
                      </div>

                      <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/60 flex items-center gap-2 text-emerald-900 dark:text-emerald-200">
                        <span className="w-5 h-5 rounded bg-emerald-500 text-white flex items-center justify-center font-bold text-[11px] shrink-0">
                          {q?.correct_answer}
                        </span>
                        <span className="truncate">{q?.options[q.correct_answer] || 'Đáp án đúng'}</span>
                      </div>
                    </div>

                    {/* Explanation */}
                    {q?.explanation_vi && (
                      <div className="p-3 rounded-xl bg-neutral-50 dark:bg-neutral-900/50 text-xs text-neutral-600 dark:text-neutral-400 whitespace-pre-line leading-relaxed">
                        {q.explanation_vi}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </main>
  );
}
