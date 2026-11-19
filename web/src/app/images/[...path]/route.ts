import { NextRequest } from 'next/server';
import fs from 'fs';
import path from 'path';
import { resolveMediaDir } from '@/lib/exam-repository';

export const dynamic = 'force-dynamic';

const MIME_TYPES: Record<string, string> = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
};

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await context.params;
  if (!segments || segments.length === 0) {
    return new Response('Not found', { status: 404 });
  }

  const imagesRoot = path.resolve(resolveMediaDir(), 'images');
  const targetPath = path.resolve(imagesRoot, ...segments);

  // Guard against path traversal
  if (!targetPath.startsWith(imagesRoot + path.sep)) {
    return new Response('Forbidden', { status: 403 });
  }

  if (!fs.existsSync(targetPath) || !fs.statSync(targetPath).isFile()) {
    return new Response('Image not found', { status: 404 });
  }

  const ext = path.extname(targetPath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  const fileBuffer = fs.readFileSync(targetPath);

  return new Response(fileBuffer, {
    status: 200,
    headers: {
      'Content-Type': contentType,
      'Content-Length': String(fileBuffer.length),
      'Cache-Control': 'public, max-age=2592000',
    },
  });
}
