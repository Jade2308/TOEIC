'use client';

import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  Search,
  ArrowRightLeft,
  BookmarkPlus,
  HelpCircle,
  Eye,
  EyeOff,
  Radio,
  Keyboard,
  ArrowRight,
  ArrowLeft,
  AlertTriangle,
  FileEdit,
  RotateCcw,
  Volume2,
  Check,
  Flame,
  Award,
  Headphones,
} from 'lucide-react';
import { Question, QuestionGroup, QuestionOptionKey } from '@/types/toeic';
import { useExamStore } from '@/stores/useExamStore';
import { useVocabStore } from '@/stores/useVocabStore';
import { SmartAudioPlayer } from '@/components/SmartAudioPlayer';
import { InteractiveTranscript } from '@/components/InteractiveTranscript';
import { checkDictation, DictationDiffResult } from '@/lib/diff-checker';

interface SingleCardLayoutProps {
  question: Question;
  group?: QuestionGroup | null;
  onNext?: () => void;
  onPrev?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
}

export type Part2CoachingMode = 'standard' | 'wh_catcher' | 'micro_dictation';

export const SingleCardLayout: React.FC<SingleCardLayoutProps> = ({
  question,
  group,
  onNext,
  onPrev,
  hasPrev = false,
  hasNext = false,
}) => {
  const {
    userAnswers,
    selectAnswer,
    audioState,
    setAudioPlaying,
    jumpToSegment,
  } = useExamStore();

  const { addWord } = useVocabStore();
  const [srsToast, setSrsToast] = useState<string | null>(null);

  // ----------------------------------------------------------------------------
  // Part 2 Coaching States
  // ----------------------------------------------------------------------------
  const [part2Mode, setPart2Mode] = useState<Part2CoachingMode>('standard');
  const [selectedWhTag, setSelectedWhTag] = useState<string | null>(null);
  const [whValidation, setWhValidation] = useState<{ isCorrect: boolean; message: string } | null>(null);
  const [isWhUnlocked, setIsWhUnlocked] = useState(false);

  // Micro-Dictation States
  const [dictationInput, setDictationInput] = useState('');
  const [dictationResult, setDictationResult] = useState<DictationDiffResult | null>(null);
  const [isDictationChecked, setIsDictationChecked] = useState(false);

  // ----------------------------------------------------------------------------
  // Part 5 20-Second Pacer State (Independent 20s Countdown per Question)
  // ----------------------------------------------------------------------------
  const [pacerElapsed, setPacerElapsed] = useState(0);
  const [pacerCompletedTime, setPacerCompletedTime] = useState<number | null>(null);

  // ----------------------------------------------------------------------------
  const selectedAnswer = userAnswers[question.id];
  const isAnswered = Boolean(selectedAnswer);
  const isCorrect = selectedAnswer === question.correct_answer;

  const handleSelect = (key: QuestionOptionKey) => {
    if (isAnswered) return;
    selectAnswer(question.id, key);
  };

  // Reset states when moving to another question
  useEffect(() => {
    setSelectedWhTag(null);
    setWhValidation(null);
    setIsWhUnlocked(false);
    setDictationInput('');
    setDictationResult(null);
    setIsDictationChecked(false);
    setPacerElapsed(0);
    setPacerCompletedTime(null);
  }, [question.id]);

  // ----------------------------------------------------------------------------
  // Part 5 20-Second Pacer Timer Logic
  // ----------------------------------------------------------------------------
  useEffect(() => {
    if (question.part === 5 && !isAnswered) {
      const timer = setInterval(() => {
        setPacerElapsed((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    } else if (question.part === 5 && isAnswered && pacerCompletedTime === null) {
      setPacerCompletedTime(pacerElapsed);
    }
  }, [question.id, question.part, isAnswered, pacerElapsed, pacerCompletedTime]);

  // ----------------------------------------------------------------------------
  // Keyboard Shortcuts (Desktop: 1..4, A..D, Space, Enter, Arrows)
  // ----------------------------------------------------------------------------
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      // Space: Toggle Audio
      if (e.code === 'Space') {
        e.preventDefault();
        setAudioPlaying(!audioState.isPlaying);
        return;
      }

      // Enter: Next question if answered
      if (e.key === 'Enter') {
        e.preventDefault();
        if (onNext && hasNext) onNext();
        return;
      }

      // Arrows
      if (e.key === 'ArrowRight' && onNext && hasNext) {
        onNext();
        return;
      }
      if (e.key === 'ArrowLeft' && onPrev && hasPrev) {
        onPrev();
        return;
      }

      // In Part 2 WH-Catcher mode, block options until unlocked
      if (question.part === 2 && part2Mode === 'wh_catcher' && !isWhUnlocked && !isAnswered) {
        return;
      }

      // Option Keys (1, 2, 3, 4 or A, B, C, D) - Only allowed if not answered yet
      if (!isAnswered) {
        const keyUpper = e.key.toUpperCase();
        let chosenKey: QuestionOptionKey | null = null;

        if (['1', 'A'].includes(keyUpper)) chosenKey = 'A';
        else if (['2', 'B'].includes(keyUpper)) chosenKey = 'B';
        else if (['3', 'C'].includes(keyUpper)) chosenKey = 'C';
        else if (['4', 'D'].includes(keyUpper) && question.part !== 2) chosenKey = 'D';

        if (chosenKey) {
          handleSelect(chosenKey);
        }
      }
    },
    [audioState.isPlaying, selectAnswer, question.id, question.part, part2Mode, isWhUnlocked, isAnswered, onNext, onPrev, hasNext, hasPrev, setAudioPlaying]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // ----------------------------------------------------------------------------
  // Part 2 WH-Catcher Logic
  // ----------------------------------------------------------------------------
  const whOptions = ['What', 'Where', 'When', 'Who', 'Why', 'How', 'Statement / Yes-No'];

  const getExpectedWhTag = (tag: string, text?: string | null): string => {
    if (tag.includes('what')) return 'What';
    if (tag.includes('where')) return 'Where';
    if (tag.includes('when')) return 'When';
    if (tag.includes('who')) return 'Who';
    if (tag.includes('why')) return 'Why';
    if (tag.includes('how')) return 'How';
    return 'Statement / Yes-No';
  };

  const handleSelectWhTag = (tag: string) => {
    setSelectedWhTag(tag);
    const expected = getExpectedWhTag(question.question_type_tag, question.question_text);

    if (tag === expected) {
      setWhValidation({
        isCorrect: true,
        message: `Chính xác! Câu hỏi bắt đầu bằng dạng [${tag}]. Đã mở khóa đáp án A, B, C! Hãy loại trừ bẫy Yes/No để chọn đáp án đúng.`,
      });
      setIsWhUnlocked(true);
    } else {
      setWhValidation({
        isCorrect: false,
        message: `Chưa đúng! Lời thoại câu hỏi không bắt đầu bằng [${tag}]. Hãy bấm nghe lại và chú ý kỹ từ đầu tiên.`,
      });
      setIsWhUnlocked(false);
    }
  };

  // ----------------------------------------------------------------------------
  // Part 2 Micro-Dictation Logic
  // ----------------------------------------------------------------------------
  const handleCheckDictation = () => {
    const targetText = question.question_text || group?.transcript_segments?.[0]?.text_en || '';
    if (!targetText || !dictationInput.trim()) return;

    const result = checkDictation(dictationInput, targetText);
    setDictationResult(result);
    setIsDictationChecked(true);
  };

  const handleReplayQuestionAudio = () => {
    const questionSegment = group?.transcript_segments?.find((s) => !s.id.toString().includes('-a') && !s.id.toString().includes('-b') && !s.id.toString().includes('-c'));
    if (questionSegment) {
      jumpToSegment(questionSegment);
    } else {
      setAudioPlaying(true);
    }
  };

  // ----------------------------------------------------------------------------
  // Handlers for SRS saving
  // ----------------------------------------------------------------------------
  const handleSaveToSRS = async () => {
    if (question.paraphrase_pair) {
      await addWord(
        question.paraphrase_pair.original,
        `Nghĩa tương đương: "${question.paraphrase_pair.paraphrased}"`,
        question.evidence_quote || question.question_text || '',
        'paraphrase'
      );
      setSrsToast('Đã lưu cặp từ diễn đạt vào Sổ tay SRS!');
    } else if (question.evidence_quote) {
      await addWord(
        question.evidence_quote.slice(0, 32),
        'Trích dẫn then chốt trong đề',
        question.evidence_quote,
        'evidence'
      );
      setSrsToast('Đã lưu dẫn chứng vào Sổ tay SRS!');
    }
    setTimeout(() => setSrsToast(null), 2500);
  };

  // ----------------------------------------------------------------------------
  // Question Classification & Pacer Helpers (Part 5)
  // ----------------------------------------------------------------------------
  const getQuestionTypeDetails = (tag: string) => {
    switch (tag) {
      case 'word_form':
        return {
          label: 'Từ Loại (Word Form)',
          targetTime: 10,
          tip: 'Nhìn lướt 4 phương án: Cùng gốc từ -> giải quyết dưới 10s dựa vào vị trí ngữ pháp.',
          color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300 border-emerald-300',
        };
      case 'conjunction':
        return {
          label: 'Liên Từ vs Giới Từ (Conjunction)',
          targetTime: 15,
          tip: 'Kiểm tra vế sau chỗ trống là Mệnh đề (S + V) hay Cụm danh từ (Noun Phrase).',
          color: 'bg-blue-100 text-blue-800 dark:bg-blue-950/70 dark:text-blue-300 border-blue-300',
        };
      case 'verb_tense':
        return {
          label: 'Hòa Hợp Thì Động Từ (Verb Tense)',
          targetTime: 15,
          tip: 'Mệnh đề trạng ngữ chỉ thời gian (Once, As soon as) dùng thì hiện tại thay cho tương lai.',
          color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/70 dark:text-indigo-300 border-indigo-300',
        };
      case 'preposition':
        return {
          label: 'Giới Từ Đi Kèm (Preposition)',
          targetTime: 15,
          tip: 'Xác định giới từ chỉ phương tiện, kênh phân phối ("through authorized dealers").',
          color: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-950/70 dark:text-cyan-300 border-cyan-300',
        };
      case 'vocabulary':
      case 'vocabulary_collocation':
        return {
          label: 'Từ Vựng & Collocation Công Sở',
          targetTime: 25,
          tip: 'Cụm từ thường gặp: "submit an estimate / budget proposal" (nộp bản kế hoạch).',
          color: 'bg-purple-100 text-purple-800 dark:bg-purple-950/70 dark:text-purple-300 border-purple-300',
        };
      default:
        return {
          label: tag.replace(/_/g, ' '),
          targetTime: 20,
          tip: 'Nhìn nhanh 4 phương án để định hình cấu trúc câu.',
          color: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300 border-neutral-300',
        };
    }
  };

  const typeDetails = getQuestionTypeDetails(question.question_type_tag);

  // Pacer bar logic
  const pacerCurrentTime = isAnswered && pacerCompletedTime !== null ? pacerCompletedTime : pacerElapsed;
  const pacerPercent = Math.min(100, (pacerCurrentTime / 20) * 100);
  let pacerColor = 'bg-emerald-500';
  let pacerTextColor = 'text-emerald-600 dark:text-emerald-400';

  if (pacerCurrentTime >= 15 && pacerCurrentTime < 20) {
    pacerColor = 'bg-amber-500';
    pacerTextColor = 'text-amber-600 dark:text-amber-400';
  } else if (pacerCurrentTime >= 20) {
    pacerColor = 'bg-rose-500';
    pacerTextColor = 'text-rose-600 dark:text-rose-400';
  }

  // Determine if options should be locked in Part 2 WH-Catcher mode
  const areOptionsLockedInPart2 =
    question.part === 2 && part2Mode === 'wh_catcher' && !isWhUnlocked && !isAnswered;

  const optionsKeys: QuestionOptionKey[] = question.part === 2 ? ['A', 'B', 'C'] : ['A', 'B', 'C', 'D'];

  return (
    <div className="max-w-2xl mx-auto space-y-4 animate-fade-in">
      {/* Toast */}
      {srsToast && (
        <div className="bg-emerald-600 text-white text-xs px-4 py-2 rounded-xl shadow-lg flex items-center justify-between animate-bounce">
          <span>{srsToast}</span>
        </div>
      )}

      {/* Keyboard Shortcuts Hint Bar (Desktop only) */}
      <div className="hidden md:flex items-center justify-between text-[11px] text-neutral-400 px-3 py-1.5 bg-neutral-200/50 dark:bg-neutral-800/40 rounded-xl">
        <span className="flex items-center gap-1.5 font-medium">
          <Keyboard className="w-3.5 h-3.5 text-neutral-500" />
          Phím tắt: <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-neutral-700 font-mono shadow-xs">1..4</kbd> Chọn đáp án &bull;{' '}
          <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-neutral-700 font-mono shadow-xs">Space</kbd> Play/Pause &bull;{' '}
          <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-neutral-700 font-mono shadow-xs">Enter</kbd> Câu tiếp theo
        </span>
        <span className="font-mono">Part {question.part} &bull; Câu {question.question_number}</span>
      </div>

      {/* ==================================================================== */}
      {/* PART 1: PHOTO & AUDIO                                                */}
      {/* ==================================================================== */}
      {question.part === 1 && (
        <div className="bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 p-4 shadow-xs space-y-3 overflow-hidden">
          {/* Photo Display with robust object-contain and fallback */}
          <div className="relative w-full rounded-2xl overflow-hidden bg-neutral-950 border border-neutral-200 dark:border-neutral-800 flex items-center justify-center p-2 min-h-[260px]">
            <img
              src={group?.image_url || `/images/test1/part1_q${question.question_number}.jpg`}
              alt={`TOEIC Part 1 Photo #${question.question_number}`}
              className="max-h-[300px] sm:max-h-[420px] w-auto max-w-full object-contain rounded-xl shadow-md transition duration-300"
              onError={(e) => {
                const target = e.currentTarget;
                const fallback = `/images/test1/part1_q${question.question_number}.jpg`;
                if (target.src !== fallback) {
                  target.src = fallback;
                }
              }}
            />
            <div className="absolute top-3 left-3 bg-neutral-900/85 backdrop-blur-md text-white text-[11px] font-bold px-3 py-1 rounded-full shadow-sm flex items-center gap-1.5 border border-white/10">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>Part 1 &bull; Câu {question.question_number}</span>
            </div>
          </div>

          <SmartAudioPlayer
            audioUrl={group?.audio_url || `/audio/test1/part1_q${question.question_number}.mp3`}
            title={`Audio Part 1 - Câu ${question.question_number}`}
            segments={group?.transcript_segments}
            hideSubtitles={!isAnswered}
          />
        </div>
      )}

      {/* ==================================================================== */}
      {/* PART 2: 3 MODES (STANDARD, WH-CATCHER, MICRO-DICTATION)              */}
      {/* ==================================================================== */}
      {question.part === 2 && (
        <div className="bg-white dark:bg-neutral-900 rounded-3xl border border-neutral-200 dark:border-neutral-800 p-4 sm:p-5 shadow-sm space-y-4">
          {/* Header & Mode Switcher */}
          <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-neutral-100 dark:border-neutral-800">
            <div>
              <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider block">
                Part 2: Question - Response Coaching
              </span>
              <span className="text-[11px] text-neutral-400">
                Luyện phản xạ thính giác không nhìn chữ (3 đáp án A, B, C)
              </span>
            </div>

            {/* 3 Modes Switcher */}
            <div className="flex items-center gap-1 bg-neutral-100 dark:bg-neutral-800 p-1 rounded-2xl text-xs font-semibold">
              <button
                onClick={() => setPart2Mode('standard')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  part2Mode === 'standard'
                    ? 'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white shadow-xs font-bold'
                    : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-300'
                }`}
              >
                1. Standard
              </button>
              <button
                onClick={() => setPart2Mode('wh_catcher')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  part2Mode === 'wh_catcher'
                    ? 'bg-amber-500 text-neutral-950 font-bold shadow-xs'
                    : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-300'
                }`}
              >
                2. WH-Catcher
              </button>
              <button
                onClick={() => setPart2Mode('micro_dictation')}
                className={`px-3 py-1.5 rounded-xl transition ${
                  part2Mode === 'micro_dictation'
                    ? 'bg-indigo-600 text-white font-bold shadow-xs'
                    : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-300'
                }`}
              >
                3. Micro-Dictation
              </button>
            </div>
          </div>

          {/* Smart Audio Player */}
          <SmartAudioPlayer
            audioUrl={group?.audio_url || `/audio/test1/part2_q${question.question_number}.mp3`}
            title={`Audio Part 2 - Câu ${question.question_number}`}
            segments={group?.transcript_segments}
            hideSubtitles={!isAnswered}
          />

          {/* ---------------------------------------------------------------- */}
          {/* MODE 1: STANDARD MODE (Mask text during listening)              */}
          {/* ---------------------------------------------------------------- */}
          {part2Mode === 'standard' && (
            <div className="p-3 rounded-2xl bg-neutral-50 dark:bg-neutral-950/60 border border-neutral-200/80 dark:border-neutral-800 text-xs flex items-center justify-between">
              <span className="text-neutral-600 dark:text-neutral-400">
                {isAnswered
                  ? 'Đã mở khóa lời thoại câu hỏi và các phương án bên dưới.'
                  : 'Chế độ tiêu chuẩn: Ẩn toàn bộ chữ câu hỏi và phương án A, B, C cho đến khi bạn chọn xong.'}
              </span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 text-[11px] shrink-0">
                {isAnswered ? 'Đã mở khóa' : 'Đang ẩn text'}
              </span>
            </div>
          )}

          {/* ---------------------------------------------------------------- */}
          {/* MODE 2: WH-CATCHER DRILL (Must choose WH type to unlock options) */}
          {/* ---------------------------------------------------------------- */}
          {part2Mode === 'wh_catcher' && (
            <div className="p-4 rounded-2xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-950 dark:text-amber-200 flex items-center gap-1.5">
                  <Radio className="w-4 h-4 text-amber-600 animate-pulse" />
                  Bước 1: Bắt từ để hỏi đầu câu (WH-Catcher Drill)
                </span>
                <span className="text-[11px] text-amber-800 dark:text-amber-300 font-semibold">
                  {isWhUnlocked ? '✓ Đã mở khóa A, B, C' : 'Chưa mở khóa'}
                </span>
              </div>

              <p className="text-xs text-amber-900/80 dark:text-amber-300/80">
                Hãy nghe kỹ từ đầu tiên trong câu hỏi và chọn dạng từ tương ứng để mở khóa đáp án:
              </p>

              {/* WH Options Buttons */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {whOptions.map((tag) => {
                  const isSelected = selectedWhTag === tag;
                  return (
                    <button
                      key={tag}
                      onClick={() => handleSelectWhTag(tag)}
                      className={`p-2 rounded-xl text-xs font-bold transition border flex items-center justify-between ${
                        isSelected
                          ? isWhUnlocked
                            ? 'bg-emerald-500 text-white border-emerald-600 shadow-xs'
                            : 'bg-rose-500 text-white border-rose-600 shadow-xs'
                          : 'bg-white dark:bg-neutral-900 text-neutral-800 dark:text-neutral-200 border-neutral-200 dark:border-neutral-700 hover:border-amber-400'
                      }`}
                    >
                      <span>{tag}</span>
                      {isSelected && (isWhUnlocked ? <Check className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />)}
                    </button>
                  );
                })}
              </div>

              {/* Feedback Alert */}
              {whValidation && (
                <div
                  className={`p-3 rounded-xl text-xs font-medium border flex items-start gap-2 animate-fade-in ${
                    whValidation.isCorrect
                      ? 'bg-emerald-100/90 text-emerald-950 border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-200 dark:border-emerald-800'
                      : 'bg-rose-100/90 text-rose-950 border-rose-300 dark:bg-rose-950/70 dark:text-rose-200 dark:border-rose-800'
                  }`}
                >
                  {whValidation.isCorrect ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  )}
                  <span>{whValidation.message}</span>
                </div>
              )}
            </div>
          )}

          {/* ---------------------------------------------------------------- */}
          {/* MODE 3: MICRO-DICTATION (Word-by-word diff check)                */}
          {/* ---------------------------------------------------------------- */}
          {part2Mode === 'micro_dictation' && (
            <div className="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-900/60 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <FileEdit className="w-4 h-4 text-indigo-600" />
                  Chế Độ Micro-Dictation: Nghe & Gõ Lại Câu Hỏi
                </span>
                <button
                  onClick={handleReplayQuestionAudio}
                  className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  <RotateCcw className="w-3 h-3" />
                  Nghe lại câu hỏi
                </button>
              </div>

              <textarea
                rows={2}
                value={dictationInput}
                onChange={(e) => setDictationInput(e.target.value)}
                placeholder="Gõ lại chính xác câu hỏi bạn vừa nghe được tại đây..."
                className="w-full text-xs sm:text-sm p-3 rounded-xl border border-indigo-200 dark:border-indigo-800 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 focus:outline-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />

              <div className="flex items-center justify-between gap-2">
                <button
                  onClick={handleCheckDictation}
                  disabled={!dictationInput.trim()}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition disabled:opacity-40 shadow-sm"
                >
                  Kiểm tra chính tả (Diff-Check)
                </button>

                <button
                  onClick={() => {
                    const ans = question.question_text || group?.transcript_segments?.[0]?.text_en || '';
                    setDictationInput(ans);
                  }}
                  className="text-xs text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200 underline"
                >
                  Hiện gợi ý câu gốc
                </button>
              </div>

              {/* Dictation Diff-Check Result */}
              {isDictationChecked && dictationResult && (
                <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-indigo-200 dark:border-indigo-800 space-y-2.5 animate-fade-in">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-neutral-700 dark:text-neutral-300">
                      Kết quả so khớp từ vựng (Word Diff):
                    </span>
                    <span
                      className={`font-mono font-bold px-2 py-0.5 rounded-full ${
                        dictationResult.accuracy >= 80
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                      }`}
                    >
                      Độ chính xác: {dictationResult.accuracy}% ({dictationResult.correctWords}/{dictationResult.totalWords} từ)
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {dictationResult.tokens.map((token, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded-lg text-xs font-mono font-medium border ${
                          token.status === 'correct'
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800'
                            : 'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800 line-through'
                        }`}
                        title={token.status === 'correct' ? 'Đúng' : `Sai/Thiếu (Câu gốc: ${token.expectedWord})`}
                      >
                        {token.userWord || token.expectedWord}
                      </span>
                    ))}
                  </div>

                  <p className="text-[11px] text-neutral-500 pt-1">
                    <strong>Câu chuẩn:</strong> &ldquo;{question.question_text || group?.transcript_segments?.[0]?.text_en}&rdquo;
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Question Text (Revealed after answering or toggled) */}
          {isAnswered && question.question_text && (
            <div className="p-3.5 rounded-2xl bg-neutral-50 dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 text-sm font-semibold text-neutral-800 dark:text-neutral-200 animate-fade-in">
              &ldquo;{question.question_text}&rdquo;
            </div>
          )}
        </div>
      )}

      {/* ==================================================================== */}
      {/* PART 5: 20-SECOND PACER                                              */}
      {/* ==================================================================== */}
      {question.part === 5 && (
        <div className="bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 p-4 sm:p-5 shadow-xs space-y-3.5">
          {/* Target Time Badge & Clock */}
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold px-3 py-1 rounded-xl border ${typeDetails.color}`}>
                {typeDetails.label}
              </span>
              <span className="text-xs font-mono text-neutral-500 font-semibold">
                Mục tiêu: &le; {typeDetails.targetTime}s
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-xs font-mono font-bold">
              <Clock className="w-3.5 h-3.5 text-emerald-500" />
              <span className={pacerTextColor}>
                {pacerCurrentTime}s / 20s
              </span>
            </div>
          </div>

          {/* 20-Second Pacer Progress Bar */}
          <div className="space-y-1">
            <div className="w-full h-2 rounded-full bg-neutral-100 dark:bg-neutral-800 overflow-hidden relative">
              <div
                style={{ width: `${pacerPercent}%` }}
                className={`h-full transition-all duration-300 rounded-full ${pacerColor}`}
              />
              <div className="absolute top-0 bottom-0 left-[75%] w-0.5 bg-neutral-400 dark:bg-neutral-600 opacity-60" title="15s" />
            </div>

            <div className="flex items-center justify-between text-[10px] text-neutral-400 font-mono px-0.5">
              <span>0s</span>
              <span>15s</span>
              <span>20s</span>
            </div>
          </div>

          {/* Time Exceeded Warning Banner */}
          {pacerCurrentTime >= 20 && !isAnswered && (
            <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-300 dark:border-rose-800 text-xs text-rose-900 dark:text-rose-200 flex items-center gap-2 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
              <span>
                <strong>Quá 20s:</strong> Hãy chốt đáp án ngay để chuyển sang câu tiếp theo.
              </span>
            </div>
          )}
        </div>
      )}

      {/* ==================================================================== */}
      {/* MAIN QUESTION CARD (OPTIONS A, B, C, D)                              */}
      {/* ==================================================================== */}
      <div className="bg-white dark:bg-[#111a14] rounded-3xl border border-emerald-950/10 dark:border-emerald-900/30 p-5 sm:p-6 shadow-xs space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              {question.question_number}
            </span>
            <span className="text-xs font-medium text-neutral-500">Part {question.part}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300">
              Tag: {question.question_type_tag}
            </span>
          </div>
        </div>

        {/* Question text (Part 1, 5) */}
        {question.question_text && question.part !== 2 && (
          <div className="text-base sm:text-lg font-bold text-neutral-900 dark:text-neutral-100 leading-snug">
            {question.question_text}
          </div>
        )}

        {/* Question Graphic (for questions with graphic e.g. Q63, Q66, Q69) */}
        {(question.image_url || ((question.question_type_tag === 'graphic' || question.question_text?.toLowerCase().includes('graphic')) && group?.image_url)) && (
          <div className="rounded-2xl border border-neutral-200 dark:border-neutral-800 overflow-hidden bg-neutral-50/70 dark:bg-neutral-950/50 p-3 space-y-1.5 animate-fade-in shadow-2xs">
            <div className="text-[11px] font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider flex items-center gap-1.5">
              <Eye className="w-3.5 h-3.5 text-indigo-500" />
              <span>Hình ảnh / Biểu đồ (Graphic cho Câu {question.question_number})</span>
            </div>
            <img
              src={question.image_url || group?.image_url!}
              alt={`Graphic for Question ${question.question_number}`}
              className="w-full max-h-80 object-contain rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 mx-auto"
            />
          </div>
        )}

        {/* Locked Overlay for Part 2 WH-Catcher Drill */}
        {areOptionsLockedInPart2 && (
          <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 text-center space-y-1">
            <p className="text-xs font-bold text-amber-900 dark:text-amber-200">
              Đáp án A, B, C đang bị khóa
            </p>
            <p className="text-[11px] text-amber-800 dark:text-amber-300">
              Vui lòng chọn đúng từ để hỏi đầu câu ở bảng trên để mở khóa các lựa chọn!
            </p>
          </div>
        )}

        {/* Options Buttons Grid */}
        <div className={`space-y-2.5 pt-1 ${areOptionsLockedInPart2 ? 'opacity-40 pointer-events-none' : ''}`}>
          {optionsKeys.map((key) => {
            const rawText = question.options[key];
            if (!rawText) return null;

            // In Part 1 and Part 2, mask text until answered (authentic exam simulation)
            const isTextMasked = (question.part === 1 || question.part === 2) && !isAnswered;

            const isThisSelected = selectedAnswer === key;
            const isThisCorrect = question.correct_answer === key;

            let btnStyle =
              'border-neutral-200 dark:border-neutral-800 bg-neutral-50/70 dark:bg-neutral-950/40 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200';
            let badgeStyle = 'bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300';

            if (isAnswered) {
              if (isThisCorrect) {
                btnStyle =
                  'border-emerald-500 bg-emerald-50/90 dark:bg-emerald-950/50 text-emerald-950 dark:text-emerald-100 ring-2 ring-emerald-500/40';
                badgeStyle = 'bg-emerald-500 text-white font-bold';
              } else if (isThisSelected && !isThisCorrect) {
                btnStyle =
                  'border-rose-500 bg-rose-50/90 dark:bg-rose-950/50 text-rose-950 dark:text-rose-100 ring-2 ring-rose-500/40';
                badgeStyle = 'bg-rose-500 text-white font-bold';
              } else {
                btnStyle = 'opacity-50 border-neutral-200 dark:border-neutral-800 text-neutral-400';
              }
            }

            return (
              <button
                key={key}
                disabled={isAnswered}
                onClick={() => handleSelect(key)}
                className={`w-full min-h-[58px] text-left p-3.5 sm:p-4 rounded-2xl border transition-all flex items-center justify-between gap-3 text-sm sm:text-base font-medium ${
                  isAnswered ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'
                } ${btnStyle}`}
              >
                <div className="flex items-center gap-3.5 flex-1 min-w-0">
                  <span
                    className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold shrink-0 shadow-xs transition ${badgeStyle}`}
                  >
                    {key}
                  </span>
                  {isTextMasked ? (
                    <div className="flex items-center justify-between flex-1 gap-2">
                      <span className="font-semibold text-neutral-700 dark:text-neutral-300">
                        Phương án ({key})
                      </span>
                      <span className="text-xs text-neutral-400 font-normal italic flex items-center gap-1.5 shrink-0">
                        <Headphones className="w-3.5 h-3.5 opacity-60 text-emerald-500" />
                        <span>Nghe audio</span>
                      </span>
                    </div>
                  ) : (
                    <span className="leading-relaxed flex-1">{rawText}</span>
                  )}
                </div>

                {isAnswered && (
                  <div className="shrink-0">
                    {isThisCorrect && (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                    )}
                    {isThisSelected && !isThisCorrect && (
                      <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Post-Answer Detailed Review & Coaching */}
        {isAnswered && (
          <div className="pt-3 space-y-3.5 animate-fade-in border-t border-neutral-100 dark:border-neutral-800">
            {/* Status Feedback */}
            <div
              className={`p-3.5 rounded-2xl flex items-center justify-between text-xs font-semibold ${
                isCorrect
                  ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/70 dark:text-emerald-200'
                  : 'bg-rose-100 text-rose-900 dark:bg-rose-950/70 dark:text-rose-200'
              }`}
            >
              <div className="flex items-center gap-2">
                {isCorrect ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Xuất sắc! Đáp án chính xác là {question.correct_answer}</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-rose-600" />
                    <span>Chưa chính xác! Đáp án đúng là {question.correct_answer} (Bạn đã chọn {selectedAnswer}) - Đã ghi nhận vào Sổ tay lỗi sai</span>
                  </>
                )}
              </div>

              {pacerCompletedTime !== null && question.part === 5 && (
                <span className="text-[11px] font-mono font-bold">
                  Hoàn thành: {pacerCompletedTime}s
                </span>
              )}
            </div>

            {/* Paraphrase & Evidence Section */}
            {(question.evidence_quote || question.paraphrase_pair) && (
              <div className="p-4 rounded-2xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 text-xs space-y-2.5">
                {question.evidence_quote && (
                  <div>
                    <span className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                      <Search className="w-3.5 h-3.5 text-amber-600" />
                      Dẫn chứng cốt lõi (Evidence Quote):
                    </span>
                    <p className="mt-1 font-mono text-[11px] text-amber-800 dark:text-amber-300 bg-amber-100/60 dark:bg-amber-900/40 p-2 rounded-xl">
                      &ldquo;{question.evidence_quote}&rdquo;
                    </p>
                  </div>
                )}

                {question.paraphrase_pair && (
                  <div className="pt-1.5 border-t border-amber-200/60 dark:border-amber-900/40">
                    <span className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                      <ArrowRightLeft className="w-3.5 h-3.5 text-amber-600" />
                      Cặp từ diễn đạt lại (Paraphrase Pair):
                    </span>
                    <div className="mt-1.5 grid grid-cols-2 gap-2 text-[11px]">
                      <div className="p-2.5 rounded-xl bg-white dark:bg-neutral-900 border border-amber-200/80 dark:border-neutral-800">
                        <span className="text-neutral-400 block text-[10px] uppercase font-bold">Bài nghe / Đọc</span>
                        <strong className="text-neutral-800 dark:text-neutral-200">{question.paraphrase_pair.original}</strong>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white dark:bg-neutral-900 border border-amber-200/80 dark:border-neutral-800">
                        <span className="text-emerald-600 block text-[10px] uppercase font-bold">Đáp án trong đề</span>
                        <strong className="text-emerald-700 dark:text-emerald-400">{question.paraphrase_pair.paraphrased}</strong>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex justify-end pt-1">
                  <button
                    onClick={handleSaveToSRS}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-400 hover:underline"
                  >
                    <BookmarkPlus className="w-3.5 h-3.5" />
                    + Lưu vào Sổ tay từ vựng Spaced Repetition (SRS)
                  </button>
                </div>
              </div>
            )}

            {/* Detailed Vietnamese Explanation */}
            <div className="p-4 rounded-2xl bg-neutral-50 dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 text-xs space-y-2">
              <div className="flex items-center gap-1.5 font-bold text-neutral-800 dark:text-neutral-200">
                <Sparkles className="w-4 h-4 text-amber-500" />
                Chiến thuật & Giải thích chi tiết:
              </div>
              <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed whitespace-pre-line">
                {question.explanation_vi}
              </p>
            </div>

            {/* Transcript Sync Accordion for Part 1 & 2 */}
            {group?.transcript_segments && group.transcript_segments.length > 0 && (
              <div className="pt-2">
                <InteractiveTranscript segments={group.transcript_segments} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={onPrev}
          disabled={!hasPrev}
          className="px-4 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 text-xs font-semibold hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-30 transition flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Câu trước</span>
        </button>

        <button
          onClick={onNext}
          disabled={!hasNext}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold disabled:opacity-30 transition flex items-center gap-1.5 shadow-sm"
        >
          <span>Câu tiếp theo</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
