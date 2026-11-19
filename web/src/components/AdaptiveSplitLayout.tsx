'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Headphones,
  CheckCircle2,
  XCircle,
  Search,
  ArrowRightLeft,
  BookmarkPlus,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Timer,
  FastForward,
  Eye,
  EyeOff,
  Play,
  Pause,
  Columns,
} from 'lucide-react';
import { Question, QuestionGroup, QuestionOptionKey } from '@/types/toeic';
import { useExamStore } from '@/stores/useExamStore';
import { useVocabStore } from '@/stores/useVocabStore';
import { SmartAudioPlayer } from '@/components/SmartAudioPlayer';
import { InteractiveTranscript } from '@/components/InteractiveTranscript';

interface AdaptiveSplitLayoutProps {
  group: QuestionGroup;
  questions: Question[];
  onFinishGroup?: () => void;
  onPrevGroup?: () => void;
  hasNextGroup?: boolean;
  hasPrevGroup?: boolean;
}

export const AdaptiveSplitLayout: React.FC<AdaptiveSplitLayoutProps> = ({
  group,
  questions,
  onFinishGroup,
  onPrevGroup,
  hasNextGroup = true,
  hasPrevGroup = false,
}) => {
  const { userAnswers, selectAnswer, setAudioPlaying, audioState } = useExamStore();
  const { addWord } = useVocabStore();

  const [highlightedEvidence, setHighlightedEvidence] = useState<string | null>(null);
  const [fontSizeClass, setFontSizeClass] = useState<'text-sm' | 'text-base' | 'text-lg'>('text-sm');
  const [readingDisplayMode, setReadingDisplayMode] = useState<'text' | 'image'>('text');
  const [srsToast, setSrsToast] = useState<string | null>(null);
  
  // Transcript visibility: Hidden by default for active test taking
  const [showTranscript, setShowTranscript] = useState(false);

  // Floating text selection to SRS state
  const [selectedText, setSelectedText] = useState<{ text: string; x: number; y: number } | null>(null);
  const passageRef = useRef<HTMLDivElement | null>(null);

  // ----------------------------------------------------------------------------
  // Part 3 & 4: 8-Second Pre-Read Countdown Timer & Answers Status
  // ----------------------------------------------------------------------------
  const isListening = [3, 4].includes(group.part);
  const [preReadTimer, setPreReadTimer] = useState<number | null>(isListening ? 8 : null);

  const anyQuestionAnswered = questions.some((q) => Boolean(userAnswers[q.id]));
  const allGroupAnswered = questions.length > 0 && questions.every((q) => Boolean(userAnswers[q.id]));
  const answeredCount = questions.filter((q) => Boolean(userAnswers[q.id])).length;
  const [mobileActiveTab, setMobileActiveTab] = useState<'content' | 'questions'>('questions');

  useEffect(() => {
    // Reset timer & hide transcript whenever group changes
    setShowTranscript(false);
    setHighlightedEvidence(null);
    setReadingDisplayMode('text');
    setMobileActiveTab(isListening ? 'questions' : 'content');
    if (isListening) {
      setPreReadTimer(8);
      setAudioPlaying(false);
    } else {
      setPreReadTimer(null);
    }
  }, [group.id, isListening, setAudioPlaying]);

  useEffect(() => {
    if (isListening && preReadTimer !== null && preReadTimer > 0) {
      const timer = setTimeout(() => {
        setPreReadTimer((prev) => (prev !== null && prev > 0 ? prev - 1 : null));
      }, 1000);
      return () => clearTimeout(timer);
    } else if (isListening && preReadTimer === 0) {
      // Countdown finished -> Auto play audio
      setAudioPlaying(true);
      setPreReadTimer(null);
    }
  }, [isListening, preReadTimer, setAudioPlaying]);

  const handleSkipPreRead = () => {
    setPreReadTimer(null);
    setAudioPlaying(true);
  };

  // ----------------------------------------------------------------------------
  // Text selection in passage to save to SRS
  // ----------------------------------------------------------------------------
  const handleMouseUp = () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      setSelectedText(null);
      return;
    }
    const text = selection.toString().trim();
    if (text.length > 2 && text.length < 50) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelectedText({
        text,
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
      });
    } else {
      setSelectedText(null);
    }
  };

  const handleSaveSelectedText = async () => {
    if (!selectedText) return;
    await addWord(
      selectedText.text,
      'Từ vựng lưu từ bài đọc TOEIC',
      group.passage_text?.slice(0, 100) || selectedText.text,
      'reading_vocab'
    );
    setSelectedText(null);
    setSrsToast(`Đã thêm "${selectedText.text}" vào Sổ tay SRS!`);
    setTimeout(() => setSrsToast(null), 2500);
  };

  const scrollToEvidence = (quote: string) => {
    setHighlightedEvidence(quote);
    setReadingDisplayMode('text');
    if (!showTranscript && isListening) {
      setShowTranscript(true);
    }
    setTimeout(() => {
      const markElement = passageRef.current?.querySelector('#auto-highlighted-evidence');
      if (markElement) {
        markElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 150);
  };

  const renderPassageWithEvidence = (rawHtml: string) => {
    if (!highlightedEvidence) {
      return <div dangerouslySetInnerHTML={{ __html: rawHtml }} />;
    }
    const quote = highlightedEvidence.trim();
    if (rawHtml.includes(quote)) {
      const highlighted = rawHtml.replace(
        quote,
        `<mark id="auto-highlighted-evidence" class="bg-amber-300 dark:bg-amber-400 text-neutral-950 font-bold px-1.5 py-0.5 rounded-md ring-4 ring-amber-400/50 shadow-md animate-pulse">${quote}</mark>`
      );
      return <div dangerouslySetInnerHTML={{ __html: highlighted }} />;
    }
    return <div dangerouslySetInnerHTML={{ __html: rawHtml }} />;
  };

  const handleSaveParaphraseToSRS = async (pair: { original: string; paraphrased: string }) => {
    await addWord(
      pair.original,
      `Nghĩa tương đương trong đề: "${pair.paraphrased}"`,
      pair.original,
      'paraphrase'
    );
    setSrsToast(`Đã lưu cặp từ "${pair.original} ➔ ${pair.paraphrased}" vào SRS!`);
    setTimeout(() => setSrsToast(null), 2500);
  };

  const optionsKeys: QuestionOptionKey[] = ['A', 'B', 'C', 'D'];

  // ----------------------------------------------------------------------------
  // Question Card Renderer (Renders all questions in the group simultaneously)
  // ----------------------------------------------------------------------------
  const renderSingleQuestion = (q: Question, index: number, isMobile = false) => {
    const qAnswer = userAnswers[q.id];
    const isQAnswered = Boolean(qAnswer);
    const isQCorrect = qAnswer === q.correct_answer;

    return (
      <div
        key={q.id}
        id={`${isMobile ? 'mobile-' : ''}q-card-${q.id}`}
        className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 shadow-2xs space-y-3.5 scroll-mt-3 transition-colors"
      >
        {/* Header: Question Number & Type */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-lg bg-emerald-600 text-white font-bold text-xs flex items-center gap-1 shadow-xs">
              Câu {q.question_number}
            </span>
            <span className="text-[11px] text-neutral-400 font-medium">({index + 1}/{questions.length})</span>
          </div>

          <div className="flex items-center gap-1.5">
            {isQAnswered && (
              <span
                className={`text-[11px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 ${
                  isQCorrect
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                    : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                }`}
              >
                {isQCorrect ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> : <XCircle className="w-3.5 h-3.5 text-rose-600" />}
                {isQCorrect ? 'Chính xác' : 'Chưa đúng'}
              </span>
            )}
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400">
              {q.question_type_tag}
            </span>
          </div>
        </div>

        {/* Question Text */}
        <h4 className="text-sm sm:text-base font-bold text-neutral-900 dark:text-neutral-100 leading-snug">
          {q.question_text}
        </h4>

        {/* Question Graphic (placed specifically on graphic questions like Q63, Q66, Q69) */}
        {(q.image_url || ((q.question_type_tag === 'graphic' || q.question_text?.toLowerCase().includes('graphic')) && group.image_url)) && (
          <div className="rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-neutral-50/70 dark:bg-neutral-950/50 p-2.5 sm:p-3 space-y-1.5 my-2 animate-fade-in shadow-2xs">
            <div className="text-[10px] sm:text-[11px] font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5 text-indigo-500" />
                <span>Hình ảnh / Biểu đồ (Graphic cho Câu {q.question_number})</span>
              </div>
            </div>
            <img
              src={q.image_url || group.image_url!}
              alt={`Graphic for Question ${q.question_number}`}
              className="w-full max-h-72 sm:max-h-80 object-contain rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 mx-auto"
            />
          </div>
        )}

        {/* Options List */}
        <div className="space-y-1.5 sm:space-y-2">
          {optionsKeys.map((key) => {
            const optionText = q.options[key];
            if (!optionText) return null;

            const isThisSelected = qAnswer === key;
            const isThisCorrect = q.correct_answer === key;

            let btnStyle =
              'border-neutral-200 dark:border-neutral-800 bg-neutral-50/70 dark:bg-neutral-950/40 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200';
            let badgeStyle = 'bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300';

            if (isQAnswered) {
              if (isThisCorrect) {
                btnStyle =
                  'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-950 dark:text-emerald-100 ring-2 ring-emerald-500/30';
                badgeStyle = 'bg-emerald-500 text-white font-bold';
              } else if (isThisSelected && !isThisCorrect) {
                btnStyle =
                  'border-rose-500 bg-rose-50 dark:bg-rose-950/50 text-rose-950 dark:text-rose-100 ring-2 ring-rose-500/30';
                badgeStyle = 'bg-rose-500 text-white font-bold';
              } else {
                btnStyle = 'opacity-50 border-neutral-200 dark:border-neutral-800 text-neutral-400';
              }
            }

            return (
              <button
                key={key}
                disabled={isQAnswered}
                onClick={() => !isQAnswered && selectAnswer(q.id, key)}
                className={`w-full text-left p-2.5 sm:p-3 rounded-xl border transition flex items-center justify-between gap-2 text-xs font-medium ${
                  isQAnswered ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'
                } ${btnStyle}`}
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className={`w-5 h-5 sm:w-6 sm:h-6 rounded-md flex items-center justify-center text-xs font-bold shrink-0 transition ${badgeStyle}`}
                  >
                    {key}
                  </span>
                  <span className="leading-snug">{optionText}</span>
                </div>
                {isQAnswered && (
                  <div className="shrink-0">
                    {isThisCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                    {isThisSelected && !isThisCorrect && <XCircle className="w-4 h-4 text-rose-600" />}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* ------------------------------------------------------------ */}
        {/* REVIEW MODE: Evidence Quote, Paraphrase, Detailed Solution   */}
        {/* ------------------------------------------------------------ */}
        {isQAnswered && (
          <div className="space-y-2.5 pt-2 text-xs animate-fade-in border-t border-neutral-100 dark:border-neutral-800">
            {/* Evidence Quote Button with Auto-Scroll */}
            {q.evidence_quote && (
              <div className="p-3 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-900 dark:text-amber-200 flex items-center gap-1 text-[11px]">
                    <Search className="w-3.5 h-3.5 text-amber-600" />
                    Dẫn chứng trong bài:
                  </span>
                  <button
                    onClick={() => scrollToEvidence(q.evidence_quote!)}
                    className="text-[10px] font-bold px-2 py-0.5 rounded-lg bg-amber-200 dark:bg-amber-800 text-amber-950 dark:text-amber-100 hover:bg-amber-300 transition shadow-2xs flex items-center gap-1"
                  >
                    <Eye className="w-3 h-3" />
                    Soi vị trí &rarr;
                  </button>
                </div>
                <p className="font-mono text-[11px] text-amber-900 dark:text-amber-300 bg-amber-100/60 dark:bg-amber-900/40 p-2 rounded-lg leading-relaxed">
                  &ldquo;{q.evidence_quote}&rdquo;
                </p>
              </div>
            )}

            {/* Paraphrase Comparison Card */}
            {q.paraphrase_pair && (
              <div className="p-2.5 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-500/20 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-neutral-800 dark:text-neutral-200 flex items-center gap-1 text-[11px]">
                    <ArrowRightLeft className="w-3.5 h-3.5 text-emerald-500" />
                    Cặp từ diễn đạt lại (Paraphrase):
                  </span>
                  <button
                    onClick={() => handleSaveParaphraseToSRS(q.paraphrase_pair!)}
                    className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 hover:underline flex items-center gap-1"
                  >
                    <BookmarkPlus className="w-3 h-3" />
                    + Lưu vào SRS
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                  <div className="p-2 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800">
                    <span className="text-neutral-400 block text-[9px] uppercase font-bold">Trong bài:</span>
                    <strong className="text-neutral-800 dark:text-neutral-200 block mt-0.5 leading-snug">
                      {q.paraphrase_pair.original}
                    </strong>
                  </div>
                  <div className="p-2 bg-white dark:bg-neutral-900 rounded-lg border border-emerald-200 dark:border-emerald-900">
                    <span className="text-emerald-600 block text-[9px] uppercase font-bold">Trong đáp án:</span>
                    <strong className="text-emerald-700 dark:text-emerald-400 block mt-0.5 leading-snug">
                      {q.paraphrase_pair.paraphrased}
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* Detailed Explanation */}
            <div className="p-3 rounded-xl bg-neutral-50 dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-neutral-800 dark:text-neutral-200 text-[11px]">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                Giải thích chi tiết:
              </div>
              <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed whitespace-pre-line text-[11px]">
                {q.explanation_vi}
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full relative">
      {/* Toast Alert */}
      {srsToast && (
        <div className="fixed top-16 right-4 z-50 bg-emerald-600 text-white text-xs px-4 py-2 rounded-xl shadow-lg animate-bounce">
          {srsToast}
        </div>
      )}

      {/* Floating Selection Tooltip: "+ Save to SRS Vocab" */}
      {selectedText && (
        <div
          style={{
            position: 'fixed',
            left: `${selectedText.x}px`,
            top: `${selectedText.y}px`,
            transform: 'translate(-50%, -100%)',
          }}
          className="z-50 bg-neutral-900 text-white text-xs py-1.5 px-3 rounded-xl shadow-2xl flex items-center gap-1.5 border border-neutral-700 animate-fade-in"
        >
          <button
            onClick={handleSaveSelectedText}
            className="flex items-center gap-1.5 hover:text-emerald-400 font-semibold"
          >
            <BookmarkPlus className="w-3.5 h-3.5 text-emerald-400" />
            + Lưu &ldquo;{selectedText.text.slice(0, 15)}...&rdquo; vào SRS
          </button>
        </div>
      )}

      {/* ==================================================================== */}
      {/* DESKTOP SPLIT-VIEW (>= 768px): 2 Independent Scroll Columns          */}
      {/* ==================================================================== */}
      <div className="hidden md:grid md:grid-cols-12 gap-6 h-[calc(100vh-8.5rem)] min-h-[550px]">
        {/* LEFT COLUMN (6 COLS): Audio + Graphic + Collapsible Transcript */}
        <div className="md:col-span-6 h-full flex flex-col bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs overflow-hidden transition-colors">
          {/* Header Bar */}
          <div className="p-3.5 border-b border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-between bg-neutral-50/70 dark:bg-neutral-950/40">
            <div className="flex items-center gap-2">
              {isListening ? (
                <Headphones className="w-4 h-4 text-emerald-500" />
              ) : (
                <FileText className="w-4 h-4 text-indigo-500" />
              )}
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-700 dark:text-neutral-300">
                {isListening ? `Listening Part ${group.part} Audio Context` : `Reading Part ${group.part} Passage`}
              </span>
              <span className="text-[11px] text-neutral-400 font-normal">({group.test_name})</span>
            </div>

            {/* Reading controls: Toggle between interactive text and authentic scan image + font size */}
            {!isListening && (
              <div className="flex items-center gap-2">
                {group.image_url && (
                  <div className="flex items-center bg-neutral-200/70 dark:bg-neutral-800 p-0.5 rounded-lg text-[11px] font-semibold">
                    <button
                      type="button"
                      onClick={() => setReadingDisplayMode('text')}
                      className={`px-2 py-0.5 rounded-md transition ${
                        readingDisplayMode === 'text'
                          ? 'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-xs'
                          : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-200'
                      }`}
                    >
                      Văn bản
                    </button>
                    <button
                      type="button"
                      onClick={() => setReadingDisplayMode('image')}
                      className={`px-2 py-0.5 rounded-md transition flex items-center gap-1 ${
                        readingDisplayMode === 'image'
                          ? 'bg-white dark:bg-neutral-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                          : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-200'
                      }`}
                    >
                      Ảnh scan
                    </button>
                  </div>
                )}

                {readingDisplayMode === 'text' && (
                  <div className="flex items-center gap-1 text-xs border-l border-neutral-200 dark:border-neutral-800 pl-2">
                    <button
                      onClick={() => setFontSizeClass('text-sm')}
                      className={`px-2 py-0.5 rounded ${fontSizeClass === 'text-sm' ? 'bg-neutral-200 dark:bg-neutral-800 font-bold' : 'text-neutral-400'}`}
                    >
                      A-
                    </button>
                    <button
                      onClick={() => setFontSizeClass('text-base')}
                      className={`px-2 py-0.5 rounded ${fontSizeClass === 'text-base' ? 'bg-neutral-200 dark:bg-neutral-800 font-bold' : 'text-neutral-400'}`}
                    >
                      A
                    </button>
                    <button
                      onClick={() => setFontSizeClass('text-lg')}
                      className={`px-2 py-0.5 rounded ${fontSizeClass === 'text-lg' ? 'bg-neutral-200 dark:bg-neutral-800 font-bold' : 'text-neutral-400'}`}
                    >
                      A+
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Left Scrollable Content */}
          <div
            ref={passageRef}
            onMouseUp={handleMouseUp}
            className="flex-1 overflow-y-auto p-5 space-y-4"
          >
            {/* 8s PRE-READ COUNTDOWN TIMER BANNER */}
            {isListening && preReadTimer !== null && (
              <div className="p-4 rounded-2xl bg-amber-500/10 border-2 border-amber-500/30 text-amber-950 dark:text-amber-200 space-y-2.5 animate-pulse">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-xs sm:text-sm">
                    <Timer className="w-5 h-5 text-amber-600 animate-spin" />
                    <span>8s Đọc Trước Câu Hỏi (Pre-Read Countdown)</span>
                  </div>
                  <span className="text-xl font-mono font-black text-amber-600 dark:text-amber-400">
                    {preReadTimer}s
                  </span>
                </div>

                <p className="text-xs text-amber-900/80 dark:text-amber-300/80 leading-relaxed">
                  Audio đang tạm dừng trong 8 giây để bạn <strong>quét nhanh từ khóa của cả 3 câu hỏi bên phải</strong> trước khi bài nói bắt đầu!
                </p>

                <div className="flex justify-end pt-1">
                  <button
                    onClick={handleSkipPreRead}
                    className="px-3.5 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-neutral-950 text-xs font-bold transition shadow-xs flex items-center gap-1.5"
                  >
                    <FastForward className="w-3.5 h-3.5" />
                    Bỏ qua đếm ngược & Nghe ngay
                  </button>
                </div>
              </div>
            )}

            {/* Listening Section */}
            {isListening && (
              <div className="space-y-4">
                {/* Audio Player */}
                <SmartAudioPlayer
                  audioUrl={group.audio_url}
                  title={`Part ${group.part} Audio Dialogue`}
                  segments={group.transcript_segments}
                  hideSubtitles={!anyQuestionAnswered || !showTranscript}
                />

                {/* Graphic image if present */}
                {group.image_url && (
                  <div className="rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-neutral-50/70 dark:bg-neutral-950/50 p-3 space-y-2">
                    <div className="text-[11px] font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Eye className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Hình ảnh / Biểu đồ đính kèm (Graphic)</span>
                    </div>
                    <img
                      src={group.image_url}
                      alt="Graphic reference"
                      className="w-full max-h-80 object-contain rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800"
                    />
                  </div>
                )}

                {/* Collapsible Transcript: Locked until at least one question is answered */}
                <div className="border-t border-neutral-100 dark:border-neutral-800 pt-3 space-y-2">
                  {!anyQuestionAnswered ? (
                    <div className="p-3 rounded-2xl bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-800 text-xs text-neutral-500 dark:text-neutral-400 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <EyeOff className="w-4 h-4 text-neutral-400 shrink-0" />
                        <span>Lời thoại & bản dịch được ẩn trong lúc làm bài</span>
                      </div>
                      <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-md">
                        Mở khóa sau khi chọn đáp án
                      </span>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={() => setShowTranscript((prev) => !prev)}
                        className="w-full py-2.5 px-4 rounded-2xl border border-emerald-500/30 bg-emerald-50/70 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:hover:bg-emerald-950/70 text-xs font-semibold text-emerald-950 dark:text-emerald-200 transition flex items-center justify-between shadow-2xs"
                      >
                        <div className="flex items-center gap-2">
                          {showTranscript ? (
                            <EyeOff className="w-4 h-4 text-emerald-600" />
                          ) : (
                            <Eye className="w-4 h-4 text-emerald-600" />
                          )}
                          <span>
                            {showTranscript ? 'Thu gọn lời thoại (Transcript)' : 'Xem lời thoại (Transcript) & Dịch nghĩa (Đã mở khóa)'}
                          </span>
                        </div>
                        <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold">
                          {showTranscript ? 'Đang mở' : 'Bấm để xem'}
                        </span>
                      </button>

                      {showTranscript && (
                        <div className="pt-2 animate-fade-in">
                          <InteractiveTranscript segments={group.transcript_segments} />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Reading: Formatted passage with Evidence Auto-Highlighter OR Authentic ETS Scan Image */}
            {!isListening && (
              <div>
                {readingDisplayMode === 'image' && group.image_url ? (
                  <div className="space-y-2 animate-fade-in">
                    <div className="flex items-center justify-between text-xs text-neutral-500 pb-1">
                      <span className="font-semibold flex items-center gap-1.5">
                        <Eye className="w-3.5 h-3.5 text-indigo-500" />
                        Bản scan đề thi gốc ETS (Part {group.part})
                      </span>
                      <button
                        onClick={() => setReadingDisplayMode('text')}
                        className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
                      >
                        Chuyển sang văn bản để soi dẫn chứng & lưu từ
                      </button>
                    </div>
                    <div className="rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-white dark:bg-neutral-950 p-2 shadow-xs">
                      <img
                        src={group.image_url}
                        alt={`Passage scan Part ${group.part}`}
                        className="w-full object-contain rounded-xl border border-neutral-100 dark:border-neutral-800 bg-white"
                      />
                    </div>
                  </div>
                ) : (
                  group.passage_text && (
                    <div
                      className={`prose dark:prose-invert max-w-none text-neutral-800 dark:text-neutral-200 leading-relaxed ${fontSizeClass}`}
                    >
                      {renderPassageWithEvidence(group.passage_text)}
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN (6 COLS): All 3 Linked Questions Displayed Together */}
        <div className="md:col-span-6 h-full flex flex-col bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs overflow-hidden transition-colors">
          {/* Header Bar */}
          <div className="p-3 border-b border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-between bg-neutral-50/70 dark:bg-neutral-950/40 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-neutral-900 dark:text-neutral-100">
                {questions.length > 1
                  ? `Nhóm câu: ${questions[0]?.question_number} - ${questions[questions.length - 1]?.question_number}`
                  : `Câu ${questions[0]?.question_number}`}
              </span>
              <span className="text-[11px] text-neutral-400 font-medium">
                ({answeredCount}/{questions.length} đã trả lời)
              </span>
            </div>

            {/* Quick scroll pills */}
            <div className="flex items-center gap-1.5">
              {questions.map((q) => {
                const ans = userAnswers[q.id];
                const isCor = ans === q.correct_answer;
                let badge =
                  'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200';
                if (ans) {
                  badge = isCor
                    ? 'bg-emerald-500 text-white font-bold'
                    : 'bg-rose-500 text-white font-bold';
                }
                return (
                  <button
                    key={q.id}
                    onClick={() => {
                      const el = document.getElementById(`q-card-${q.id}`);
                      el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition ${badge}`}
                  >
                    Q{q.question_number}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Scrollable Content: All Questions Stacked */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
            {questions.map((q, idx) => renderSingleQuestion(q, idx, false))}
          </div>

          {/* Footer Group Navigation */}
          <div className="p-3 border-t border-emerald-950/10 dark:border-emerald-900/30 flex items-center justify-between bg-neutral-50/70 dark:bg-neutral-950/40">
            <button
              onClick={onPrevGroup}
              disabled={!hasPrevGroup}
              className="px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 text-xs font-semibold disabled:opacity-30 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition flex items-center gap-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Đoạn trước</span>
            </button>

            <span className="text-xs font-medium text-neutral-400">
              {allGroupAnswered ? '✓ Đã xong nhóm này' : `${answeredCount}/${questions.length}`}
            </span>

            <button
              onClick={onFinishGroup}
              disabled={!hasNextGroup}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm ${
                allGroupAnswered
                  ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                  : 'bg-emerald-600/80 hover:bg-emerald-600 text-white'
              }`}
            >
              <span>Sang đoạn tiếp theo</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* MOBILE ADAPTIVE VIEW (< 768px): Responsive Tab-Based Experience      */}
      {/* ==================================================================== */}
      <div className="md:hidden flex flex-col min-h-[calc(100vh-8rem)]">
        {/* Mobile View Switcher Tabs */}
        <div className="bg-white dark:bg-[#111a14] p-1.5 rounded-2xl border border-emerald-950/10 dark:border-emerald-900/30 flex items-center gap-1 shadow-2xs mb-2">
          <button
            type="button"
            onClick={() => setMobileActiveTab('content')}
            className={`flex-1 py-1.5 px-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              mobileActiveTab === 'content'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
            }`}
          >
            {isListening ? (
              <>
                <Headphones className="w-3.5 h-3.5" />
                <span>Audio bài nghe</span>
              </>
            ) : (
              <>
                <FileText className="w-3.5 h-3.5" />
                <span>Bài đọc (Passage)</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => setMobileActiveTab('questions')}
            className={`flex-1 py-1.5 px-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
              mobileActiveTab === 'questions'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Câu hỏi ({answeredCount}/{questions.length})</span>
          </button>
        </div>

        {/* TAB 1: PASSAGE & AUDIO CONTENT */}
        {mobileActiveTab === 'content' && (
          <div
            ref={passageRef}
            onMouseUp={handleMouseUp}
            className="flex-1 overflow-y-auto p-4 bg-white dark:bg-[#111a14] rounded-2xl border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs space-y-3.5"
          >
            <div className="flex items-center justify-between text-xs font-bold text-neutral-500 uppercase tracking-wider pb-1 border-b dark:border-neutral-800">
              <span>{isListening ? `Part ${group.part} Audio Context` : `Part ${group.part} Bài đọc`}</span>
              {!isListening && group.image_url ? (
                <div className="flex items-center bg-neutral-200/80 dark:bg-neutral-800 p-0.5 rounded-lg text-[10px] font-semibold">
                  <button
                    type="button"
                    onClick={() => setReadingDisplayMode('text')}
                    className={`px-2 py-0.5 rounded ${
                      readingDisplayMode === 'text'
                        ? 'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 shadow-xs'
                        : 'text-neutral-500'
                    }`}
                  >
                    Văn bản
                  </button>
                  <button
                    type="button"
                    onClick={() => setReadingDisplayMode('image')}
                    className={`px-2 py-0.5 rounded ${
                      readingDisplayMode === 'image'
                        ? 'bg-white dark:bg-neutral-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                        : 'text-neutral-500'
                    }`}
                  >
                    Ảnh scan
                  </button>
                </div>
              ) : null}
            </div>

            {/* 8s Countdown on Mobile */}
            {isListening && preReadTimer !== null && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs flex items-center justify-between">
                <span className="font-bold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                  <Timer className="w-3.5 h-3.5 text-amber-600 animate-spin" />
                  8s Đọc trước câu hỏi:
                </span>
                <button
                  onClick={handleSkipPreRead}
                  className="text-[11px] font-bold text-amber-700 dark:text-amber-400 underline"
                >
                  Nghe ngay ({preReadTimer}s)
                </button>
              </div>
            )}

            {/* Listening in Mobile */}
            {isListening && (
              <div className="space-y-3">
                <SmartAudioPlayer
                  audioUrl={group.audio_url}
                  title={`Part ${group.part} Dialogue`}
                  segments={group.transcript_segments}
                  hideSubtitles={!anyQuestionAnswered || !showTranscript}
                />

                {group.image_url && (
                  <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-neutral-50/70 dark:bg-neutral-950/50 p-2 space-y-1.5">
                    <div className="text-[10px] font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider flex items-center gap-1">
                      <Eye className="w-3 h-3 text-indigo-500" />
                      <span>Hình ảnh / Biểu đồ đính kèm (Graphic)</span>
                    </div>
                    <img
                      src={group.image_url}
                      alt="Graphic reference"
                      className="w-full max-h-56 object-contain rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800"
                    />
                  </div>
                )}

                {/* Collapsible Transcript on Mobile - Locked until answered */}
                <div className="border-t border-neutral-100 dark:border-neutral-800 pt-2 space-y-2">
                  {!anyQuestionAnswered ? (
                    <div className="p-3 rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-xs text-neutral-500 dark:text-neutral-400 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <EyeOff className="w-4 h-4 text-neutral-400 shrink-0" />
                        <span>Lời thoại & bản dịch được ẩn khi đang làm bài</span>
                      </div>
                      <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-md">
                        Mở khóa sau khi chọn
                      </span>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={() => setShowTranscript((prev) => !prev)}
                        className="w-full py-2 px-3 rounded-xl border border-emerald-500/30 bg-emerald-50/70 dark:bg-emerald-950/40 text-xs font-semibold text-emerald-900 dark:text-emerald-200 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-1.5">
                          {showTranscript ? (
                            <EyeOff className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <Eye className="w-3.5 h-3.5 text-emerald-600" />
                          )}
                          <span>{showTranscript ? 'Thu gọn Transcript' : 'Xem Transcript & Dịch (Đã mở khóa)'}</span>
                        </div>
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">
                          {showTranscript ? 'Đang mở' : 'Bấm xem'}
                        </span>
                      </button>

                      {showTranscript && (
                        <div className="pt-1 animate-fade-in">
                          <InteractiveTranscript segments={group.transcript_segments} />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Reading in Mobile */}
            {!isListening && (
              <div>
                {readingDisplayMode === 'image' && group.image_url ? (
                  <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-white dark:bg-neutral-950 p-1.5 shadow-2xs">
                    <img
                      src={group.image_url}
                      alt={`Passage scan Part ${group.part}`}
                      className="w-full object-contain rounded-lg border border-neutral-100 dark:border-neutral-800 bg-white"
                    />
                  </div>
                ) : (
                  group.passage_text && (
                    <div className="prose dark:prose-invert text-xs text-neutral-800 dark:text-neutral-200 leading-relaxed">
                      {renderPassageWithEvidence(group.passage_text)}
                    </div>
                  )
                )}
              </div>
            )}

            {/* Quick Button to Jump to Questions */}
            <div className="pt-2">
              <button
                type="button"
                onClick={() => setMobileActiveTab('questions')}
                className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-xs"
              >
                <span>Chuyển sang làm câu hỏi ({answeredCount}/{questions.length})</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: QUESTIONS LIST */}
        {mobileActiveTab === 'questions' && (
          <div className="flex-1 flex flex-col bg-white dark:bg-[#111a14] rounded-2xl border border-emerald-950/10 dark:border-emerald-900/30 shadow-xs overflow-hidden">
            {/* Sticky Compact Audio Bar for Listening on Mobile */}
            {isListening && (
              <div className="p-2.5 bg-neutral-900 text-white border-b border-neutral-800 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <button
                    type="button"
                    onClick={() => setAudioPlaying(!audioState.isPlaying)}
                    className="w-8 h-8 rounded-full bg-emerald-500 text-neutral-950 flex items-center justify-center font-bold shrink-0 active:scale-95 transition"
                    title="Phát/Dừng Audio"
                  >
                    {audioState.isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
                  </button>
                  <div className="truncate text-xs">
                    <span className="font-semibold block truncate text-neutral-200">Part {group.part} Audio</span>
                    <span className="text-[10px] text-neutral-400 font-mono">
                      {Math.floor(audioState.currentTime / 60)}:{String(Math.floor(audioState.currentTime % 60)).padStart(2, '0')} / {Math.floor((audioState.duration || 30) / 60)}:{String(Math.floor((audioState.duration || 30) % 60)).padStart(2, '0')}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setMobileActiveTab('content')}
                  className="px-2.5 py-1 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-semibold shrink-0 transition flex items-center gap-1"
                >
                  <FileText className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Xem ngữ cảnh</span>
                </button>
              </div>
            )}

            {/* Reading Context Link for Reading Parts */}
            {!isListening && (
              <div className="p-2 bg-neutral-50 dark:bg-neutral-900/60 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between text-xs">
                <span className="text-neutral-500 font-medium">Đang trả lời câu hỏi bài đọc</span>
                <button
                  type="button"
                  onClick={() => setMobileActiveTab('content')}
                  className="text-emerald-600 dark:text-emerald-400 font-bold hover:underline flex items-center gap-1"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Mở lại bài đọc ➔</span>
                </button>
              </div>
            )}

            {/* Jump Pills Header */}
            <div className="p-2 border-b border-neutral-100 dark:border-neutral-800 flex items-center justify-between bg-neutral-50/70 dark:bg-neutral-950/40">
              <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                Câu {questions[0]?.question_number} - {questions[questions.length - 1]?.question_number} ({answeredCount}/{questions.length})
              </span>

              <div className="flex items-center gap-1.5">
                {questions.map((q) => {
                  const ans = userAnswers[q.id];
                  const isCor = ans === q.correct_answer;
                  let tabStyle = 'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300';
                  if (ans) {
                    tabStyle = isCor
                      ? 'bg-emerald-500 text-white font-bold'
                      : 'bg-rose-500 text-white font-bold';
                  }
                  return (
                    <button
                      key={q.id}
                      onClick={() => {
                        const el = document.getElementById(`mobile-q-card-${q.id}`);
                        el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      }}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${tabStyle}`}
                    >
                      Q{q.question_number}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Scrollable Questions Content */}
            <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5">
              {questions.map((q, idx) => renderSingleQuestion(q, idx, true))}
            </div>

            {/* Mobile Footer Navigation */}
            <div className="p-3 border-t border-neutral-200 dark:border-neutral-800 flex items-center justify-between bg-neutral-50 dark:bg-neutral-950">
              <button
                onClick={onPrevGroup}
                disabled={!hasPrevGroup}
                className="px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 text-xs font-semibold disabled:opacity-30 flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Đoạn trước</span>
              </button>

              <button
                onClick={onFinishGroup}
                disabled={!hasNextGroup}
                className={`px-4 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                  allGroupAnswered
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900'
                }`}
              >
                <span>Sang đoạn tiếp</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
