import { NextRequest } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { resolveRawDir } from '@/lib/exam-repository';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const testDirName = searchParams.get('test_dir');
  const skipAudio = searchParams.get('skip_audio') === 'true';
  const device = searchParams.get('device') || 'cpu';

  if (!testDirName) {
    return new Response('Missing test_dir parameter', { status: 400 });
  }

  const candidateRoots = [
    path.resolve(/*turbopackIgnore: true*/ process.cwd(), '..'),
    path.resolve(/*turbopackIgnore: true*/ process.cwd()),
  ];

  const rootDir = candidateRoots.find((r) => fs.existsSync(/*turbopackIgnore: true*/ path.join(r, 'crawler', 'main.py')));
  const rawDir = resolveRawDir();
  const testDirPath = path.join(rawDir, path.basename(testDirName));

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      const sendEvent = (data: Record<string, unknown>) => {
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        } catch {
          // Stream closed by client
        }
      };

      // If running inside the ultra-lightweight Docker web container (node:20-alpine without Python/crawler)
      if (!rootDir) {
        sendEvent({
          type: 'info',
          message: `[INFO] Web đang chạy trong Docker container siêu nhẹ (không cài Python/Whisper để tiết kiệm RAM).`,
        });
        sendEvent({
          type: 'info',
          message: `[INFO] Tài liệu đề thi đã sẵn sàng tại: data/raw/${path.basename(testDirName)}`,
        });
        sendEvent({
          type: 'info',
          message: `[HƯỚNG DẪN] Chạy lệnh sau trên terminal Ubuntu Server VM để bóc tách AI:`,
        });
        sendEvent({
          type: 'stdout',
          message: `cd /opt/toeic && ./crawler/run_crawler.sh "data/raw/${path.basename(testDirName)}" --device ${device}${skipAudio ? ' --skip-audio' : ''}\n`,
        });
        sendEvent({
          type: 'info',
          message: `[✓] Sau khi crawler chạy xong, chỉ cần bấm F5 trên web — đề mới sẽ tự động hiện ngay lập tức mà KHÔNG cần restart Docker!`,
        });
        sendEvent({
          type: 'end',
          code: 0,
          message: 'Đã hiển thị lệnh chạy crawler trên máy chủ Ubuntu.',
          timestamp: new Date().toISOString(),
        });
        controller.close();
        return;
      }

      const scriptPath = path.join(rootDir, 'crawler', 'main.py');

      sendEvent({
        type: 'start',
        message: `[START] Bắt đầu khởi chạy pipeline cho đề: ${testDirName}`,
        timestamp: new Date().toISOString(),
      });

      const pythonCmd =
        process.env.PYTHON_PATH ||
        (fs.existsSync('/opt/toeic/venv/bin/python')
          ? '/opt/toeic/venv/bin/python'
          : process.platform === 'win32'
          ? 'python'
          : 'python3');

      const args = [scriptPath, '--test-dir', testDirPath, '--device', device];
      if (skipAudio) {
        args.push('--skip-audio');
      }

      sendEvent({
        type: 'info',
        message: `[EXEC] ${pythonCmd} ${args.join(' ')}`,
      });

      const child = spawn(pythonCmd, args, {
        cwd: rootDir,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1',
        },
      });

      child.stdout.on('data', (chunk) => {
        sendEvent({ type: 'stdout', message: chunk.toString('utf-8') });
      });

      child.stderr.on('data', (chunk) => {
        sendEvent({ type: 'stderr', message: chunk.toString('utf-8') });
      });

      child.on('close', (code) => {
        sendEvent({
          type: 'end',
          code,
          message:
            code === 0
              ? '✓ ĐÃ XỬ LÝ HOÀN TẤT THÀNH CÔNG 100%! Đề thi mới đã tự động sẵn sàng để luyện tập.'
              : `[!] Pipeline kết thúc với mã lỗi: ${code}`,
          timestamp: new Date().toISOString(),
        });
        controller.close();
      });

      child.on('error', (err) => {
        sendEvent({
          type: 'error',
          message: `Không thể thực thi Python (${err.message}). Nếu đang chạy trong Docker, hãy chạy trên Ubuntu host: ./crawler/run_crawler.sh "data/raw/${path.basename(testDirName)}"`,
        });
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}
