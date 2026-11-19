'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  UploadCloud,
  FileText,
  Headphones,
  Key,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
  Terminal,
  RefreshCw,
  FolderOpen,
  ArrowRight,
  Layers,
  Sparkles,
  Cpu,
  StopCircle,
} from 'lucide-react';

interface RawTestItem {
  id?: string;
  name: string;
  hasPdf: boolean;
  hasAudio: boolean;
  hasKey: boolean;
  hasTranscript: boolean;
  isProcessed: boolean;
}

export default function AdminPage() {
  const [tests, setTests] = useState<RawTestItem[]>([]);
  const [loadingTests, setLoadingTests] = useState(true);

  // Upload state
  const [testName, setTestName] = useState('');
  const [testPdf, setTestPdf] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [answerFile, setAnswerFile] = useState<File | null>(null);
  const [transcriptPdf, setTranscriptPdf] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Pipeline execution state
  const [isRunning, setIsRunning] = useState(false);
  const [activeTestDir, setActiveTestDir] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [device, setDevice] = useState<'cpu' | 'cuda'>('cpu');
  const [skipAudio, setSkipAudio] = useState(false);

  const logEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const fetchTests = async () => {
    setLoadingTests(true);
    try {
      const res = await fetch('/api/admin/tests');
      const data = await res.json();
      if (data.success && Array.isArray(data.tests)) {
        setTests(data.tests);
      }
    } catch (e) {
      console.error('Failed to load tests list:', e);
    } finally {
      setLoadingTests(false);
    }
  };

  useEffect(() => {
    fetchTests();
  }, []);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const handleStartPipeline = (targetDir: string) => {
    if (isRunning) return;

    setIsRunning(true);
    setActiveTestDir(targetDir);
    setLogs([`[*] Khởi chạy kết nối Pipeline cho thư mục: ${targetDir}...`]);

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const queryParams = new URLSearchParams({
      test_dir: targetDir,
      device,
      skip_audio: String(skipAudio),
    });

    const es = new EventSource(`/api/admin/pipeline?${queryParams.toString()}`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'stdout' || payload.type === 'info' || payload.type === 'start') {
          setLogs((prev) => [...prev, payload.message]);
        } else if (payload.type === 'stderr') {
          setLogs((prev) => [...prev, `[STDERR] ${payload.message}`]);
        } else if (payload.type === 'end') {
          setLogs((prev) => [...prev, `\n${payload.message}`]);
          setIsRunning(false);
          es.close();
          fetchTests();
        } else if (payload.type === 'error') {
          setLogs((prev) => [...prev, `[ERROR] ${payload.message}`]);
          setIsRunning(false);
          es.close();
        }
      } catch (err) {
        setLogs((prev) => [...prev, event.data]);
      }
    };

    es.onerror = () => {
      setLogs((prev) => [...prev, '[SYSTEM] Luồng kết nối log đã đóng.']);
      setIsRunning(false);
      es.close();
      fetchTests();
    };
  };

  const handleStopPipeline = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsRunning(false);
    setLogs((prev) => [...prev, '[!] Người dùng đã chủ động ngắt theo dõi tiến trình.']);
  };

  const handleUploadAndRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testName.trim() || !testPdf || !audioFile || !answerFile) {
      setUploadMessage({ type: 'error', text: 'Vui lòng điền tên đề và chọn đủ 3 file bắt buộc (PDF, MP3, Đáp án).' });
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('test_name', testName.trim());
    formData.append('test_pdf', testPdf);
    formData.append('audio_file', audioFile);
    formData.append('answer_file', answerFile);
    if (transcriptPdf) {
      formData.append('transcript_pdf', transcriptPdf);
    }

    try {
      const res = await fetch('/api/admin/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Upload failed');
      }

      setUploadMessage({ type: 'success', text: `Tải lên thành công! Đang tự động khởi chạy bóc tách đề "${testName.trim()}"...` });
      await fetchTests();
      // Auto run pipeline
      handleStartPipeline(testName.trim());
    } catch (err: any) {
      setUploadMessage({ type: 'error', text: err.message || 'Lỗi trong quá trình upload' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 md:p-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-emerald-950/10 dark:border-emerald-900/30">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
              <FolderOpen className="w-5 h-5" />
            </span>
            <h1 className="text-xl sm:text-2xl font-black text-neutral-900 dark:text-neutral-100 tracking-tight">
              Quản Trị & Tải Đề Thi Mới
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 mt-1">
            Gửi file đề mới trực tiếp lên máy chủ hoặc kích hoạt pipeline bóc tách AI cho các bộ đề sẵn có.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            href="/"
            className="px-3.5 py-2 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-[#111a14] hover:bg-neutral-50 text-neutral-700 dark:text-neutral-200 text-xs font-bold transition shadow-2xs"
          >
            Về Trang Chủ
          </Link>
          <button
            onClick={fetchTests}
            disabled={loadingTests}
            className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingTests ? 'animate-spin' : ''}`} />
            Làm mới danh sách
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload Form & Existing Raw Tests */}
        <div className="lg:col-span-6 space-y-6">
          {/* Box 1: Upload Form */}
          <section className="bg-white dark:bg-[#111a14] border border-emerald-950/15 dark:border-emerald-900/30 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h2 className="text-base font-black text-neutral-900 dark:text-neutral-100">
                Tải Đề Thi Mới Lên Máy Chủ
              </h2>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed">
              Kéo thả các file của bộ đề. Hệ thống sẽ lưu vào kho lưu trữ và sẵn sàng kích hoạt bóc tách tự động.
            </p>

            {uploadMessage && (
              <div
                className={`p-3 rounded-2xl text-xs flex items-center gap-2 ${
                  uploadMessage.type === 'success'
                    ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-800'
                    : 'bg-rose-50 dark:bg-rose-950/50 text-rose-800 dark:text-rose-200 border border-rose-300 dark:border-rose-800'
                }`}
              >
                {uploadMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
                <span>{uploadMessage.text}</span>
              </div>
            )}

            <form onSubmit={handleUploadAndRun} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Tên thư mục đề thi (Folder name) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: TEST 5 - ETS 2023"
                  value={testName}
                  onChange={(e) => setTestName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-50/50 dark:bg-[#0c1410] text-sm focus:outline-hidden focus:ring-2 focus:ring-emerald-500 font-medium"
                  required
                />
              </div>

              {/* 3 Main Files Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* PDF Test */}
                <div className="p-3 rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-700 bg-neutral-50/50 dark:bg-[#0c1410] space-y-1">
                  <span className="text-[11px] font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-rose-500" />
                    Đề thi (PDF) *
                  </span>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setTestPdf(e.target.files?.[0] || null)}
                    className="text-xs text-neutral-500 file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-100 file:text-emerald-800 dark:file:bg-emerald-950 dark:file:text-emerald-300"
                    required
                  />
                  {testPdf && <p className="text-[10px] text-emerald-600 truncate">{testPdf.name}</p>}
                </div>

                {/* Audio MP3 */}
                <div className="p-3 rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-700 bg-neutral-50/50 dark:bg-[#0c1410] space-y-1">
                  <span className="text-[11px] font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                    <Headphones className="w-3.5 h-3.5 text-amber-500" />
                    File Audio (MP3/WAV) *
                  </span>
                  <input
                    type="file"
                    accept=".mp3,.wav,.m4a"
                    onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                    className="text-xs text-neutral-500 file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-100 file:text-emerald-800 dark:file:bg-emerald-950 dark:file:text-emerald-300"
                    required
                  />
                  {audioFile && <p className="text-[10px] text-emerald-600 truncate">{audioFile.name}</p>}
                </div>

                {/* Answer Key */}
                <div className="p-3 rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-700 bg-neutral-50/50 dark:bg-[#0c1410] space-y-1">
                  <span className="text-[11px] font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5 text-emerald-500" />
                    Bảng Đáp Án (Ảnh/PDF) *
                  </span>
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={(e) => setAnswerFile(e.target.files?.[0] || null)}
                    className="text-xs text-neutral-500 file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-100 file:text-emerald-800 dark:file:bg-emerald-950 dark:file:text-emerald-300"
                    required
                  />
                  {answerFile && <p className="text-[10px] text-emerald-600 truncate">{answerFile.name}</p>}
                </div>

                {/* Transcript PDF */}
                <div className="p-3 rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-700 bg-neutral-50/50 dark:bg-[#0c1410] space-y-1">
                  <span className="text-[11px] font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-indigo-500" />
                    Transcript (Tùy chọn)
                  </span>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setTranscriptPdf(e.target.files?.[0] || null)}
                    className="text-xs text-neutral-500 file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-100 file:text-emerald-800 dark:file:bg-emerald-950 dark:file:text-emerald-300"
                  />
                  {transcriptPdf && <p className="text-[10px] text-emerald-600 truncate">{transcriptPdf.name}</p>}
                </div>
              </div>

              {/* Advanced execution options */}
              <div className="p-3.5 rounded-2xl bg-neutral-100/70 dark:bg-[#0c1410] border border-neutral-200 dark:border-neutral-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-neutral-500" />
                  <span className="font-semibold text-neutral-700 dark:text-neutral-300">Thiết bị AI Whisper:</span>
                  <select
                    value={device}
                    onChange={(e) => setDevice(e.target.value as 'cpu' | 'cuda')}
                    className="px-2 py-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-[#111a14] font-bold text-xs"
                  >
                    <option value="cpu">CPU (Tối ưu cho Mini PC)</option>
                    <option value="cuda">CUDA GPU</option>
                  </select>
                </div>

                <label className="flex items-center gap-1.5 cursor-pointer font-medium text-neutral-600 dark:text-neutral-400">
                  <input
                    type="checkbox"
                    checked={skipAudio}
                    onChange={(e) => setSkipAudio(e.target.checked)}
                    className="rounded text-emerald-600"
                  />
                  Bỏ qua cắt audio (--skip-audio)
                </label>
              </div>

              <button
                type="submit"
                disabled={uploading || isRunning}
                className="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-black text-sm transition shadow-md flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Đang tải file lên máy chủ...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    Tải Lên & Khởi Chạy Xử Lý Tự Động
                  </>
                )}
              </button>
            </form>
          </section>

          {/* Box 2: Existing Raw Tests Library */}
          <section className="bg-white dark:bg-[#111a14] border border-emerald-950/15 dark:border-emerald-900/30 rounded-3xl p-5 sm:p-6 shadow-xs space-y-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                <h2 className="text-base font-black text-neutral-900 dark:text-neutral-100">
                  Kho Đề Trong Máy Chủ ({tests.length} Đề)
                </h2>
              </div>
              <span className="text-[11px] font-bold text-neutral-400">data/raw</span>
            </div>

            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Các bộ đề đã được copy lên server (qua Samba/SMB hoặc upload). Bạn có thể bấm nút để kích hoạt bóc tách ngay:
            </p>

            <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
              {tests.map((item) => (
                <div
                  key={item.name}
                  className={`p-3 rounded-2xl border transition flex items-center justify-between gap-3 ${
                    item.isProcessed
                      ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-900/20'
                      : 'bg-neutral-50/80 dark:bg-[#0c1410] border-neutral-200 dark:border-neutral-800'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black text-neutral-900 dark:text-neutral-100">
                        {item.name}
                      </span>
                      {item.isProcessed ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Đã hoàn tất (200 câu)
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Chờ bóc tách
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-[10px] text-neutral-400 mt-1">
                      <span className={item.hasPdf ? 'text-emerald-600 dark:text-emerald-400' : 'text-neutral-400 line-through'}>
                        PDF
                      </span>
                      &bull;
                      <span className={item.hasAudio ? 'text-emerald-600 dark:text-emerald-400' : 'text-neutral-400 line-through'}>
                        MP3
                      </span>
                      &bull;
                      <span className={item.hasKey ? 'text-emerald-600 dark:text-emerald-400' : 'text-neutral-400 line-through'}>
                        Key Đáp án
                      </span>
                    </div>
                  </div>

                  <div>
                    {item.isProcessed ? (
                      <Link
                        href={`/practice?part=all&test=${encodeURIComponent(item.id || item.name)}`}
                        className="px-3 py-1.5 rounded-xl border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100/50 text-xs font-bold transition flex items-center gap-1"
                      >
                        Làm đề
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    ) : (
                      <button
                        onClick={() => handleStartPipeline(item.name)}
                        disabled={isRunning}
                        className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs transition shadow-2xs flex items-center gap-1"
                      >
                        <Play className="w-3 h-3 fill-current" />
                        Xử lý ngay
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column: Real-time Live Log Console */}
        <div className="lg:col-span-6 space-y-4">
          <section className="bg-neutral-900 border border-neutral-800 rounded-3xl p-5 sm:p-6 shadow-xl flex flex-col h-[640px]">
            <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
              <div className="flex items-center gap-2 text-white">
                <Terminal className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-black">
                  Terminal Trực Tiếp (Live Pipeline Console)
                </h3>
              </div>

              <div className="flex items-center gap-2">
                {isRunning && (
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    Đang chạy...
                  </span>
                )}

                {isRunning && (
                  <button
                    onClick={handleStopPipeline}
                    className="p-1 rounded-lg text-neutral-400 hover:text-rose-400 transition"
                    title="Ngắt theo dõi"
                  >
                    <StopCircle className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Terminal Body */}
            <div className="flex-1 overflow-y-auto mt-3 p-3 rounded-2xl bg-black/60 font-mono text-xs text-neutral-300 space-y-1 select-text">
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-neutral-500 text-center space-y-2">
                  <Terminal className="w-8 h-8 opacity-40" />
                  <p>Chưa có tiến trình nào đang chạy.</p>
                  <p className="text-[11px] text-neutral-600">
                    Bấm "Xử lý ngay" hoặc "Tải lên & Khởi chạy" để bắt đầu theo dõi log bóc tách AI theo thời gian thực.
                  </p>
                </div>
              ) : (
                logs.map((line, idx) => (
                  <div key={idx} className="whitespace-pre-wrap leading-relaxed break-all">
                    {line.startsWith('[ERROR]') || line.includes('[!]') ? (
                      <span className="text-rose-400">{line}</span>
                    ) : line.startsWith('[✓]') || line.includes('HOÀN TẤT') ? (
                      <span className="text-emerald-400 font-bold">{line}</span>
                    ) : line.startsWith('[*]') ? (
                      <span className="text-teal-300">{line}</span>
                    ) : (
                      line
                    )}
                  </div>
                ))
              )}
              <div ref={logEndRef} />
            </div>

            {/* Terminal Footer */}
            <div className="pt-3 border-t border-neutral-800 text-[11px] text-neutral-400 flex items-center justify-between">
              <span>Đề đang xử lý: <strong>{activeTestDir || 'Không có'}</strong></span>
              <button
                onClick={() => setLogs([])}
                className="hover:text-neutral-200 transition font-semibold"
              >
                Xóa màn hình log
              </button>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
