'use client';

import React, { useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, RotateCw, Volume2, FastForward } from 'lucide-react';
import { useExamStore } from '@/stores/useExamStore';

interface AudioPlayerProps {
  audioUrl?: string | null;
  title?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl, title = 'Audio Trích Đoạn' }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { audioState, setAudioPlaying, setAudioCurrentTime, setAudioDuration, setPlaybackSpeed } =
    useExamStore();

  const fallbackAudio = audioUrl || 'https://cdn.freesound.org/previews/320/320655_5260872-lq.mp3';

  // Sync audio element with store state
  useEffect(() => {
    if (!audioRef.current) return;
    if (audioState.isPlaying) {
      audioRef.current.play().catch(() => {
        // Autoplay may be blocked by browser until user interacts
      });
    } else {
      audioRef.current.pause();
    }
  }, [audioState.isPlaying]);

  // Sync playback speed
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = audioState.playbackSpeed;
    }
  }, [audioState.playbackSpeed]);

  // Handle jump from external store trigger
  useEffect(() => {
    if (audioRef.current && Math.abs(audioRef.current.currentTime - audioState.currentTime) > 0.4) {
      audioRef.current.currentTime = audioState.currentTime;
    }
  }, [audioState.currentTime]);

  const togglePlay = () => {
    setAudioPlaying(!audioState.isPlaying);
  };

  const skipTime = (seconds: number) => {
    if (!audioRef.current) return;
    const newTime = Math.max(0, Math.min(audioRef.current.duration || 30, audioRef.current.currentTime + seconds));
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

  const speedOptions = [0.8, 1.0, 1.1, 1.25];

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remaining = Math.floor(secs % 60);
    return `${mins}:${remaining < 10 ? '0' : ''}${remaining}`;
  };

  return (
    <div className="bg-neutral-900 text-white rounded-xl p-3.5 shadow-md border border-neutral-800">
      <audio
        ref={audioRef}
        src={fallbackAudio}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setAudioPlaying(false)}
        preload="metadata"
      />

      <div className="flex items-center justify-between mb-2 text-xs text-neutral-400">
        <span className="flex items-center gap-1.5 font-medium text-neutral-200">
          <Volume2 className="w-4 h-4 text-emerald-400" />
          {title}
        </span>
        <span className="font-mono">
          {formatTime(audioState.currentTime)} / {formatTime(audioState.duration || 30)}
        </span>
      </div>

      {/* Progress slider */}
      <div className="mb-3">
        <input
          type="range"
          min="0"
          max={audioState.duration || 30}
          step="0.1"
          value={audioState.currentTime}
          onChange={handleSeek}
          className="w-full h-1.5 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
        />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => skipTime(-5)}
            className="p-1.5 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800 transition"
            title="Tua lùi 5 giây"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={togglePlay}
            className="w-9 h-9 rounded-full bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold flex items-center justify-center transition shadow-lg shadow-emerald-500/20"
            title={audioState.isPlaying ? 'Tạm dừng' : 'Phát âm thanh'}
          >
            {audioState.isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
          </button>

          <button
            onClick={() => skipTime(5)}
            className="p-1.5 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800 transition"
            title="Tua tới 5 giây"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>

        {/* Playback speed buttons */}
        <div className="flex items-center gap-1 bg-neutral-800/80 p-0.5 rounded-lg text-xs">
          <FastForward className="w-3.5 h-3.5 text-neutral-400 ml-1.5 mr-0.5" />
          {speedOptions.map((speed) => (
            <button
              key={speed}
              onClick={() => setPlaybackSpeed(speed)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition ${
                audioState.playbackSpeed === speed
                  ? 'bg-emerald-500 text-neutral-950 font-bold'
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
