'use client';

import React, { useRef, useEffect, useState } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  RotateCw,
  Volume2,
  VolumeX,
  FastForward,
  Repeat,
  Radio,
  Sparkles,
} from 'lucide-react';
import { useExamStore } from '@/stores/useExamStore';
import { TranscriptSegment } from '@/types/toeic';

interface SmartAudioPlayerProps {
  audioUrl?: string | null;
  title?: string;
  segments?: TranscriptSegment[] | null;
  isSticky?: boolean;
  hideSubtitles?: boolean;
}

export const SmartAudioPlayer: React.FC<SmartAudioPlayerProps> = ({
  audioUrl,
  title = 'Trình phát âm thanh bài thi TOEIC',
  segments,
  isSticky = false,
  hideSubtitles = false,
}) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const {
    audioState,
    setAudioPlaying,
    setAudioCurrentTime,
    setAudioDuration,
    setPlaybackSpeed,
    jumpToSegment,
  } = useExamStore();

  const [isMuted, setIsMuted] = useState(false);
  const [isLoopingSegment, setIsLoopingSegment] = useState(false);

  const fallbackAudio = audioUrl || 'https://cdn.freesound.org/previews/320/320655_5260872-lq.mp3';

  // Find currently active segment
  const activeSegment = segments?.find(
    (seg) => audioState.currentTime >= seg.start_time && audioState.currentTime <= seg.end_time
  );

  // Sync audio play/pause with Zustand store
  useEffect(() => {
    if (!audioRef.current) return;
    if (audioState.isPlaying) {
      audioRef.current.play().catch(() => {
        // Prevent uncaught play error if browser requires user gesture
        setAudioPlaying(false);
      });
    } else {
      audioRef.current.pause();
    }
  }, [audioState.isPlaying, setAudioPlaying]);

  // Sync playback speed
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = audioState.playbackSpeed;
    }
  }, [audioState.playbackSpeed]);

  // Sync external seek jumps
  useEffect(() => {
    if (audioRef.current && Math.abs(audioRef.current.currentTime - audioState.currentTime) > 0.4) {
      audioRef.current.currentTime = audioState.currentTime;
    }
  }, [audioState.currentTime]);

  // Loop segment if active
  useEffect(() => {
    if (isLoopingSegment && activeSegment && audioRef.current) {
      if (audioState.currentTime >= activeSegment.end_time) {
        audioRef.current.currentTime = activeSegment.start_time;
        setAudioCurrentTime(activeSegment.start_time);
      }
    }
  }, [audioState.currentTime, isLoopingSegment, activeSegment, setAudioCurrentTime]);

  const togglePlay = () => {
    setAudioPlaying(!audioState.isPlaying);
  };

  const skipSeconds = (seconds: number) => {
    if (!audioRef.current) return;
    const maxDur = audioRef.current.duration || 30;
    const newTime = Math.max(0, Math.min(maxDur, audioRef.current.currentTime + seconds));
    audioRef.current.currentTime = newTime;
    setAudioCurrentTime(newTime);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setAudioCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setAudioDuration(audioRef.current.duration || 30);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
    setAudioCurrentTime(time);
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '0:00';
    const mins = Math.floor(secs / 60);
    const remaining = Math.floor(secs % 60);
    return `${mins}:${remaining < 10 ? '0' : ''}${remaining}`;
  };

  const speedOptions = [0.8, 1.0, 1.1, 1.25];

  return (
    <div
      className={`rounded-2xl transition-all shadow-lg ${
        isSticky
          ? 'sticky bottom-3 z-30 bg-neutral-900/95 text-white backdrop-blur-md border border-neutral-700/80 p-3 sm:p-4 mx-auto max-w-3xl'
          : 'bg-neutral-900 text-white border border-neutral-800 p-4'
      }`}
    >
      <audio
        ref={audioRef}
        src={fallbackAudio}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setAudioPlaying(false)}
        preload="metadata"
      />

      {/* Top Header & Live Transcript Banner */}
      <div className="flex items-center justify-between gap-2 mb-2 text-xs">
        <div className="flex items-center gap-2 truncate">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
          <span className="font-semibold text-neutral-200 truncate">{title}</span>
        </div>

        <div className="flex items-center gap-2 shrink-0 font-mono text-neutral-400 text-[11px]">
          <span>{formatTime(audioState.currentTime)}</span>
          <span>/</span>
          <span>{formatTime(audioState.duration || 30)}</span>
        </div>
      </div>

      {/* Real-time Subtitle Snippet */}
      {activeSegment && !hideSubtitles && (
        <div className="mb-2.5 px-3 py-1.5 rounded-xl bg-neutral-800/90 border border-neutral-700 text-xs flex items-center justify-between gap-2 animate-fade-in">
          <div className="flex items-center gap-2 truncate text-emerald-300">
            <Radio className="w-3.5 h-3.5 shrink-0 text-emerald-400 animate-pulse" />
            <span className="truncate">
              <strong>{activeSegment.speaker || 'Voice'}:</strong> {activeSegment.text_en}
            </span>
          </div>
          <span className="text-[10px] text-neutral-400 font-mono shrink-0">
            {activeSegment.start_time.toFixed(1)}s
          </span>
        </div>
      )}

      {/* Progress Bar (Scrubber) */}
      <div className="relative mb-3 group">
        <input
          type="range"
          min="0"
          max={audioState.duration || 30}
          step="0.05"
          value={audioState.currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400 transition"
        />
        {/* Segment Markers on Scrubber */}
        {segments && segments.length > 0 && audioState.duration > 0 && (
          <div className="absolute inset-0 pointer-events-none flex items-center">
            {segments.map((seg) => {
              const leftPercent = (seg.start_time / audioState.duration) * 100;
              return (
                <div
                  key={seg.id}
                  style={{ left: `${leftPercent}%` }}
                  className={`absolute w-1 h-2 rounded-full ${
                    seg.is_trap ? 'bg-rose-500' : 'bg-emerald-400/70'
                  }`}
                  title={`${seg.speaker || 'Seg'}: ${seg.start_time}s`}
                />
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom Controls */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        {/* Play/Pause & Skip buttons */}
        <div className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => skipSeconds(-5)}
            className="p-2 rounded-xl text-neutral-300 hover:text-white hover:bg-neutral-800 transition"
            title="Tua lại 5 giây"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={togglePlay}
            className="w-11 h-11 rounded-full bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold flex items-center justify-center transition shadow-lg shadow-emerald-500/25 active:scale-95"
            title={audioState.isPlaying ? 'Tạm dừng (Space)' : 'Phát âm thanh (Space)'}
          >
            {audioState.isPlaying ? (
              <Pause className="w-5 h-5 fill-current" />
            ) : (
              <Play className="w-5 h-5 fill-current ml-0.5" />
            )}
          </button>

          <button
            onClick={() => skipSeconds(5)}
            className="p-2 rounded-xl text-neutral-300 hover:text-white hover:bg-neutral-800 transition"
            title="Tua tới 5 giây"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          {/* Loop current segment toggle */}
          <button
            onClick={() => setIsLoopingSegment(!isLoopingSegment)}
            className={`p-2 rounded-xl transition text-xs flex items-center gap-1 ${
              isLoopingSegment
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800'
            }`}
            title="Lặp lại câu hội thoại hiện tại"
          >
            <Repeat className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[11px]">Lặp câu</span>
          </button>

          <button
            onClick={toggleMute}
            className="p-2 rounded-xl text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 transition"
            title={isMuted ? 'Bật âm' : 'Tắt tiếng'}
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4" />}
          </button>
        </div>

        {/* Speed Controls (0.8x - 1.25x) */}
        <div className="flex items-center gap-1 bg-neutral-800/90 p-1 rounded-xl border border-neutral-700/60">
          <FastForward className="w-3 h-3 text-neutral-400 ml-1.5 mr-0.5" />
          {speedOptions.map((speed) => (
            <button
              key={speed}
              onClick={() => setPlaybackSpeed(speed)}
              className={`px-2 py-1 rounded-lg text-[11px] font-semibold transition ${
                audioState.playbackSpeed === speed
                  ? 'bg-emerald-500 text-neutral-950 font-bold shadow-sm'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
