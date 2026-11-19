import { NextResponse } from 'next/server';
import {
  listExamSummaries,
  resolveExamsDir,
  resolveMediaDir,
  resolveRawDir,
  resolveUserDataDir,
} from '@/lib/exam-repository';
import { checkUserDataWritable } from '@/lib/user-store';

export const dynamic = 'force-dynamic';

export async function GET() {
  const exams = listExamSummaries();
  const writeCheck = checkUserDataWritable();

  const status = {
    ok: writeCheck.writable,
    storageMode: 'local_filesystem' as const,
    examCount: exams.length,
    userDataWritable: writeCheck.writable,
    paths: {
      examsDir: resolveExamsDir(),
      rawDir: resolveRawDir(),
      mediaDir: resolveMediaDir(),
      userDataDir: resolveUserDataDir(),
    },
    ...(writeCheck.error ? { error: writeCheck.error } : {}),
  };

  return NextResponse.json(status, {
    status: writeCheck.writable ? 200 : 503,
    headers: { 'Cache-Control': 'no-store, max-age=0' },
  });
}
