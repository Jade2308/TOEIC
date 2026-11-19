import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import {
  findCanonicalFullJson,
  resolveExamsDir,
  resolveRawDir,
  slugifyFolderName,
} from '@/lib/exam-repository';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const rawDataDir = resolveRawDir();
    const examsDataDir = resolveExamsDir();

    const rawTests: Array<{
      id: string;
      name: string;
      hasPdf: boolean;
      hasAudio: boolean;
      hasKey: boolean;
      hasTranscript: boolean;
      isProcessed: boolean;
    }> = [];

    if (fs.existsSync(rawDataDir)) {
      const dirs = fs
        .readdirSync(rawDataDir, { withFileTypes: true })
        .filter((d) => d.isDirectory() && !d.name.startsWith('.'))
        .map((d) => d.name);

      dirs.sort((a, b) => {
        const numA = parseInt(a.match(/\d+/)?.[0] || '999999', 10);
        const numB = parseInt(b.match(/\d+/)?.[0] || '999999', 10);
        if (numA !== numB) return numA - numB;
        return a.localeCompare(b, undefined, { numeric: true });
      });

      for (const d of dirs) {
        const fullDirPath = path.join(rawDataDir, d);
        const files = fs.readdirSync(fullDirPath).map((f) => f.toLowerCase());

        const hasPdf = files.some(
          (f) =>
            f.endsWith('.pdf') &&
            !f.includes('transcript') &&
            !f.includes('dap-an') &&
            !f.includes('answer')
        );
        const hasAudio = files.some(
          (f) => f.endsWith('.mp3') || f.endsWith('.wav') || f.endsWith('.m4a')
        );
        const hasKey = files.some(
          (f) =>
            (f.includes('dap-an') || f.includes('key') || f.includes('answer')) &&
            (f.endsWith('.jpg') || f.endsWith('.png') || f.endsWith('.jpeg') || f.endsWith('.pdf'))
        );
        const hasTranscript = files.some((f) => f.includes('transcript') && f.endsWith('.pdf'));

        const processedDir = path.join(examsDataDir, d);
        const isProcessed = Boolean(findCanonicalFullJson(processedDir));

        rawTests.push({
          id: slugifyFolderName(d),
          name: d,
          hasPdf,
          hasAudio,
          hasKey,
          hasTranscript,
          isProcessed,
        });
      }
    }

    return NextResponse.json(
      {
        success: true,
        rawDir: rawDataDir,
        examsDir: examsDataDir,
        tests: rawTests,
      },
      { headers: { 'Cache-Control': 'no-store, max-age=0' } }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Lỗi quét kho đề gốc';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
