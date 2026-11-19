import { NextRequest } from 'next/server';
import fs from 'fs';
import path from 'path';
import { resolveMediaDir } from '@/lib/exam-repository';

export const dynamic = 'force-dynamic';

const MIME_TYPES: Record<string, string> = {
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.m4a': 'audio/mp4',
  '.ogg': 'audio/ogg',
};

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await context.params;
  if (!segments || segments.length === 0) {
    return new Response('Not found', { status: 404 });
  }

  const audioRoot = path.resolve(resolveMediaDir(), 'audio');
  const targetPath = path.resolve(audioRoot, ...segments);

  // Guard against path traversal
  if (!targetPath.startsWith(audioRoot + path.sep)) {
    return new Response('Forbidden', { status: 403 });
  }

  if (!fs.existsSync(targetPath) || !fs.statSync(targetPath).isFile()) {
    return new Response('Audio not found', { status: 404 });
  }

  const stat = fs.statSync(targetPath);
  const fileSize = stat.size;
  const ext = path.extname(targetPath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  const range = request.headers.get('range');

  if (range) {
    const match = range.match(/bytes=(\d*)-(\d*)/);
    const start = match && match[1] ? parseInt(match[1], 10) : 0;
    const end = match && match[2] ? Math.min(parseInt(match[2], 10), fileSize - 1) : fileSize - 1;

    if (isNaN(start) || isNaN(end) || start > end || start >= fileSize) {
      return new Response(null, {
        status: 416,
        headers: { 'Content-Range': `bytes */${fileSize}` },
      });
    }

    const chunkSize = end - start + 1;
    const buffer = Buffer.alloc(chunkSize);
    const fd = fs.openSync(targetPath, 'r');
    try {
      fs.readSync(fd, buffer, 0, chunkSize, start);
    } finally {
      fs.closeSync(fd);
    }

    return new Response(buffer, {
      status: 206,
      headers: {
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': String(chunkSize),
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=2592000',
      },
    });
  }

  const fileBuffer = fs.readFileSync(targetPath);
  return new Response(fileBuffer, {
    status: 200,
    headers: {
      'Accept-Ranges': 'bytes',
      'Content-Length': String(fileSize),
      'Content-Type': contentType,
      'Cache-Control': 'public, max-age=2592000',
    },
  });
}
