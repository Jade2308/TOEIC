import { NextRequest, NextResponse } from 'next/server';
import { getTodayDateKey, mutateUserProgress, readUserProgress } from '@/lib/user-store';
import { QuestionOptionKey } from '@/types/toeic';

export const dynamic = 'force-dynamic';

const NO_STORE_HEADERS = {
  'Cache-Control': 'no-store, max-age=0',
};

const VALID_OPTIONS = new Set<QuestionOptionKey>(['A', 'B', 'C', 'D']);

export async function GET() {
  try {
    const progress = readUserProgress();
    return NextResponse.json(
      { success: true, progress },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể đọc tiến độ học tập';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const testKey = typeof body.testKey === 'string' ? body.testKey.trim() : '';
    const testName = typeof body.testName === 'string' ? body.testName.trim() : undefined;
    const questionId = typeof body.questionId === 'string' ? body.questionId.trim() : '';
    const answer = body.answer as QuestionOptionKey | undefined;

    const updated = await mutateUserProgress((current) => {
      const next = {
        ...current,
        answersByTest: { ...current.answersByTest },
        studyDates: [...current.studyDates],
      };

      if (testKey) {
        next.selectedTestId = testKey;
      }
      if (testName) {
        next.selectedTestName = testName;
      }

      if (testKey && questionId && answer && VALID_OPTIONS.has(answer)) {
        next.answersByTest[testKey] = {
          ...(next.answersByTest[testKey] || {}),
          [questionId]: answer,
        };

        const today = getTodayDateKey();
        if (!next.studyDates.includes(today)) {
          next.studyDates.push(today);
          next.studyDates.sort();
        }
      }

      return { next, result: next };
    });

    return NextResponse.json(
      { success: true, progress: updated },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể lưu tiến độ';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const testKey = searchParams.get('test');

    const updated = await mutateUserProgress((current) => {
      const nextAnswers = { ...current.answersByTest };
      if (testKey) {
        delete nextAnswers[testKey];
      } else {
        for (const k of Object.keys(nextAnswers)) {
          delete nextAnswers[k];
        }
      }
      const next = { ...current, answersByTest: nextAnswers };
      return { next, result: next };
    });

    return NextResponse.json(
      { success: true, progress: updated },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể đặt lại tiến độ';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}
