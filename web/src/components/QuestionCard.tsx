'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  ArrowRightLeft,
  BookmarkPlus,
  Clock,
  Search,
} from 'lucide-react';
import { Question, QuestionOptionKey, QuestionGroup } from '@/types/toeic';
import { useExamStore } from '@/stores/useExamStore';
import { useVocabStore } from '@/stores/useVocabStore';

interface QuestionCardProps {
  question: Question;
  group?: QuestionGroup | null;
  onHighlightEvidence?: (quote: string) => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  group,
  onHighlightEvidence,
}) => {
  const { userAnswers, selectAnswer } = useExamStore();
  const { addWord } = useVocabStore();
  const [srsToast, setSrsToast] = useState<string | null>(null);

  const selectedAnswer = userAnswers[question.id];
  const isAnswered = Boolean(selectedAnswer);
  const isCorrect = selectedAnswer === question.correct_answer;

  const handleSelect = (key: QuestionOptionKey) => {
    if (isAnswered) return;
    selectAnswer(question.id, key);
  };

  const handleAddEvidenceToSRS = async () => {
    if (question.paraphrase_pair) {
      await addWord(
        question.paraphrase_pair.original,
        `Nghĩa tương đương: "${question.paraphrase_pair.paraphrased}"`,
        question.evidence_quote || question.question_text || '',
        'paraphrase'
      );
      setSrsToast(`Đã lưu cặp diễn đạt vào Sổ tay SRS!`);
      setTimeout(() => setSrsToast(null), 2500);
    } else if (question.evidence_quote) {
      await addWord(
        question.evidence_quote.slice(0, 30),
        'Trích đoạn chứng cứ quan trọng',
        question.evidence_quote,
        'evidence'
      );
      setSrsToast(`Đã lưu dẫn chứng vào SRS!`);
      setTimeout(() => setSrsToast(null), 2500);
    }
  };

  const getPacerTag = (tag: string) => {
    switch (tag) {
      case 'word_form':
        return { label: 'Từ loại: Mục tiêu 10s', color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' };
      case 'conjunction':
        return { label: 'Liên từ vs Giới từ: 15s', color: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300' };
      case 'verb_tense':
        return { label: 'Hòa hợp thì: 15s', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300' };
      case 'preposition':
        return { label: 'Giới từ: 15s', color: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-950/60 dark:text-cyan-300' };
      case 'vocabulary':
      case 'vocabulary_collocation':
        return { label: 'Từ vựng & Cụm từ: 25s', color: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300' };
      case 'passive_being_trap':
        return { label: 'Bẫy Being Passive', color: 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300' };
      case 'wh_where':
      case 'wh_when':
        return { label: 'WH-Question Drill', color: 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300' };
      case 'indirect_answer':
        return { label: 'Đáp án gián tiếp', color: 'bg-teal-100 text-teal-800 dark:bg-teal-950/60 dark:text-teal-300' };
      default:
        return { label: tag.replace(/_/g, ' '), color: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300' };
    }
  };

  const pacer = getPacerTag(question.question_type_tag);
  const optionsKeys: QuestionOptionKey[] = question.part === 2 ? ['A', 'B', 'C'] : ['A', 'B', 'C', 'D'];

  return (
    <div className="bg-white dark:bg-[#111a14] border border-emerald-950/10 dark:border-emerald-900/30 rounded-2xl p-5 shadow-xs space-y-4 transition-colors">
      {srsToast && (
        <div className="bg-emerald-600 text-white text-xs px-3 py-1.5 rounded-lg shadow-md animate-fade-in flex items-center justify-between">
          <span>{srsToast}</span>
        </div>
      )}

      {/* Header: Question Number and Strategy Tag */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
            {question.question_number}
          </span>
          <span className="text-xs text-neutral-500 font-medium">Part {question.part}</span>
        </div>

        <div className="flex items-center gap-1.5">
          <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border border-black/5 dark:border-white/5 ${pacer.color}`}>
            {pacer.label}
          </span>
        </div>
      </div>

      {/* Question Text (if applicable) */}
      {question.question_text && (
        <div className="text-base font-semibold text-neutral-900 dark:text-neutral-100 leading-snug">
          {question.question_text}
        </div>
      )}

      {/* Answer Options */}
      <div className="space-y-2 pt-1">
        {optionsKeys.map((key) => {
          const optionText = question.options[key];
          if (!optionText) return null;

          const isThisSelected = selectedAnswer === key;
          const isThisCorrect = question.correct_answer === key;

          let btnStyle = 'border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/40 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-800 dark:text-neutral-200';
          let badgeStyle = 'bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300';

          if (isAnswered) {
            if (isThisCorrect) {
              btnStyle = 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-950 dark:text-emerald-100 ring-2 ring-emerald-500/30';
              badgeStyle = 'bg-emerald-500 text-white font-bold';
            } else if (isThisSelected && !isThisCorrect) {
              btnStyle = 'border-rose-500 bg-rose-50 dark:bg-rose-950/40 text-rose-950 dark:text-rose-100 ring-2 ring-rose-500/30';
              badgeStyle = 'bg-rose-500 text-white font-bold';
            } else {
              btnStyle = 'opacity-60 border-neutral-200 dark:border-neutral-800 text-neutral-500';
            }
          }

          return (
            <button
              key={key}
              disabled={isAnswered}
              onClick={() => handleSelect(key)}
              className={`w-full text-left p-3.5 rounded-xl border transition flex items-center justify-between gap-3 text-sm font-medium ${btnStyle} ${
                isAnswered ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition ${badgeStyle}`}>
                  {key}
                </span>
                <span className="leading-relaxed">{optionText}</span>
              </div>

              {isAnswered && (
                <div className="shrink-0">
                  {isThisCorrect && <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />}
                  {isThisSelected && !isThisCorrect && <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Immediate Coaching & Explanation Section (Shown once answered) */}
      {isAnswered && (
        <div className="pt-2 space-y-3 animate-fade-in">
          {/* Result Banner */}
          <div
            className={`p-3 rounded-xl flex items-center justify-between text-xs font-semibold ${
              isCorrect
                ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/60 dark:text-emerald-200'
                : 'bg-rose-100 text-rose-900 dark:bg-rose-950/60 dark:text-rose-200'
            }`}
          >
            <div className="flex items-center gap-2">
              {isCorrect ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Chính xác! Đáp án đúng là {question.correct_answer}</span>
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>Chưa đúng! Đáp án đúng là {question.correct_answer} (Bạn chọn {selectedAnswer}) - Đã lưu vào Sổ tay lỗi sai</span>
                </>
              )}
            </div>
          </div>

          {/* Evidence quote & Paraphrase Pair */}
          {(question.evidence_quote || question.paraphrase_pair) && (
            <div className="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 rounded-xl p-3.5 text-xs space-y-2">
              {question.evidence_quote && (
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                      <Search className="w-3.5 h-3.5 text-amber-600" />
                      Dẫn chứng trực tiếp (Evidence Quote):
                    </span>
                    <p className="mt-1 font-mono text-[11px] text-amber-800 dark:text-amber-300 bg-amber-100/60 dark:bg-amber-900/40 p-2 rounded-lg">
                      &quot;{question.evidence_quote}&quot;
                    </p>
                  </div>
                  {onHighlightEvidence && (
                    <button
                      onClick={() => onHighlightEvidence(question.evidence_quote!)}
                      className="px-2.5 py-1 rounded bg-amber-200 dark:bg-amber-800 text-amber-900 dark:text-amber-100 font-semibold text-[11px] hover:bg-amber-300 transition shrink-0"
                    >
                      Soi vị trí bài đọc
                    </button>
                  )}
                </div>
              )}

              {question.paraphrase_pair && (
                <div className="pt-1.5 border-t border-amber-200/60 dark:border-amber-900/40">
                  <span className="font-semibold text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                    <ArrowRightLeft className="w-3.5 h-3.5 text-amber-600" />
                    Cặp từ diễn đạt lại (Paraphrase Pair):
                  </span>
                  <div className="mt-1 grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2 rounded bg-white dark:bg-neutral-900 border border-amber-200/80 dark:border-neutral-800">
                      <span className="text-neutral-500 block text-[10px] uppercase font-bold">Lời thoại / Bài đọc</span>
                      <strong className="text-neutral-800 dark:text-neutral-200">{question.paraphrase_pair.original}</strong>
                    </div>
                    <div className="p-2 rounded bg-white dark:bg-neutral-900 border border-amber-200/80 dark:border-neutral-800">
                      <span className="text-emerald-600 block text-[10px] uppercase font-bold">Đáp án trong đề</span>
                      <strong className="text-emerald-700 dark:text-emerald-400">{question.paraphrase_pair.paraphrased}</strong>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end pt-1">
                <button
                  onClick={handleAddEvidenceToSRS}
                  className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 hover:underline"
                >
                  <BookmarkPlus className="w-3.5 h-3.5" />
                  + Lưu cặp từ vựng này vào Sổ tay SRS
                </button>
              </div>
            </div>
          )}

          {/* Detailed Explanation */}
          <div className="bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-800 rounded-xl p-3.5 text-xs space-y-1.5">
            <div className="font-bold text-neutral-800 dark:text-neutral-200">
              Giải thích:
            </div>
            <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed whitespace-pre-line">
              {question.explanation_vi}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
