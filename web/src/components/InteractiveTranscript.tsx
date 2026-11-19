'use client';

import React from 'react';
import { PlayCircle, AlertTriangle, BookmarkPlus } from 'lucide-react';
import { TranscriptSegment } from '@/types/toeic';
import { useExamStore } from '@/stores/useExamStore';
import { useVocabStore } from '@/stores/useVocabStore';

interface InteractiveTranscriptProps {
  segments?: TranscriptSegment[] | null;
  showTrapAnnotations?: boolean;
}

export const InteractiveTranscript: React.FC<InteractiveTranscriptProps> = ({
  segments,
  showTrapAnnotations = true,
}) => {
  const { audioState, jumpToSegment } = useExamStore();
  const { addWord } = useVocabStore();
  const [toastMessage, setToastMessage] = React.useState<string | null>(null);

  if (!segments || segments.length === 0) {
    return (
      <div className="text-center py-6 text-sm text-neutral-400 italic">
        Không có transcript cho phần này.
      </div>
    );
  }

  const handleSaveToSRS = async (e: React.MouseEvent, text: string) => {
    e.stopPropagation();
    const selection = window.getSelection()?.toString().trim();
    const wordToSave = selection && selection.length > 0 && selection.length < 40 ? selection : text.slice(0, 30);
    
    await addWord(wordToSave, 'Từ vựng trích xuất từ transcript bài nghe', text, 'collocation');
    setToastMessage(`Đã lưu "${wordToSave}" vào Sổ tay SRS!`);
    setTimeout(() => setToastMessage(null), 2500);
  };

  return (
    <div className="space-y-2">
      {toastMessage && (
        <div className="bg-emerald-600 text-white text-xs px-3 py-1.5 rounded-md shadow-md animate-fade-in flex items-center justify-between">
          <span>{toastMessage}</span>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-neutral-500 mb-1 font-medium">
        <span>Lời thoại hội thoại (Bấm vào câu để nghe lại đoạn đó):</span>
      </div>

      <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
        {segments.map((seg) => {
          const isActive = audioState.activeSegmentId === seg.id;
          const isTrap = showTrapAnnotations && seg.is_trap;

          return (
            <div
              key={seg.id}
              onClick={() => jumpToSegment(seg)}
              className={`group p-3 rounded-xl border text-sm transition cursor-pointer relative ${
                isActive
                  ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-500 shadow-sm'
                  : 'bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 dark:hover:border-neutral-700'
              } ${isTrap ? 'border-l-4 border-l-rose-500' : ''}`}
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <div className="flex items-center gap-2">
                  <PlayCircle
                    className={`w-4 h-4 transition ${
                      isActive ? 'text-emerald-600 dark:text-emerald-400' : 'text-neutral-400 group-hover:text-emerald-500'
                    }`}
                  />
                  {seg.speaker && (
                    <span className="font-semibold text-xs text-neutral-700 dark:text-neutral-300">
                      {seg.speaker}:
                    </span>
                  )}
                  <span className="text-[11px] font-mono text-neutral-400">
                    {seg.start_time.toFixed(1)}s - {seg.end_time.toFixed(1)}s
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  {isTrap && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/50 px-2 py-0.5 rounded-full border border-rose-200 dark:border-rose-800">
                      <AlertTriangle className="w-3 h-3 text-rose-500" />
                      Bẫy thính giác
                    </span>
                  )}
                  <button
                    onClick={(e) => handleSaveToSRS(e, seg.text_en)}
                    title="Lưu từ/câu vào SRS Vocab"
                    className="p-1 rounded text-neutral-400 hover:text-emerald-600 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
                  >
                    <BookmarkPlus className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <p className={`text-neutral-900 dark:text-neutral-100 ${isActive ? 'font-medium' : ''}`}>
                {seg.text_en}
              </p>

              {seg.text_vi && (
                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 italic">
                  {seg.text_vi}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
