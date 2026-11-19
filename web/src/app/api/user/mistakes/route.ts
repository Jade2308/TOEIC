import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { findQuestionAcrossAllExams } from '@/lib/exam-repository';
import { mutateMistakes, readMistakes } from '@/lib/user-store';
import { QuestionOptionKey, UserMistake } from '@/types/toeic';

export const dynamic = 'force-dynamic';

const NO_STORE_HEADERS = {
  'Cache-Control': 'no-store, max-age=0',
};

const VALID_OPTIONS = new Set<QuestionOptionKey>(['A', 'B', 'C', 'D']);

function hydrateMistake(mistake: UserMistake): UserMistake {
  const found = findQuestionAcrossAllExams(mistake.question_id);
  if (found) {
    return {
      ...mistake,
      question: found.question,
      group: found.group,
    };
  }
  return mistake;
}

export async function GET() {
  try {
    const raw = readMistakes();
    const hydrated = raw
      .map(hydrateMistake)
      .sort((a, b) => (b.updated_at || b.created_at || '').localeCompare(a.updated_at || a.created_at || ''));

    return NextResponse.json(
      { success: true, mistakes: hydrated },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể đọc sổ lỗi sai';
    return NextResponse.json(
      { success: false, error: message, mistakes: [] },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const questionId = typeof body.question_id === 'string' ? body.question_id.trim() : '';
    const wrongAnswer = body.wrong_answer as QuestionOptionKey;

    if (!questionId || !VALID_OPTIONS.has(wrongAnswer)) {
      return NextResponse.json(
        { success: false, error: 'Thiếu question_id hoặc đáp án sai không hợp lệ.' },
        { status: 400, headers: NO_STORE_HEADERS }
      );
    }

    const found = findQuestionAcrossAllExams(questionId);
    const now = new Date().toISOString();

    const saved = await mutateMistakes((current) => {
      const idx = current.findIndex((m) => m.question_id === questionId);
      if (idx >= 0) {
        const existing = current[idx];
        const updated: UserMistake = {
          ...existing,
          selected_wrong_answer: wrongAnswer,
          wrong_count: (existing.wrong_count || 1) + 1,
          next_review_date: now,
          resolved: false,
          question: found?.question ?? existing.question,
          group: found?.group ?? existing.group,
          updated_at: now,
        };
        const next = [...current];
        next[idx] = updated;
        return { next, result: updated };
      }

      const created: UserMistake = {
        id: crypto.randomUUID(),
        question_id: questionId,
        selected_wrong_answer: wrongAnswer,
        wrong_count: 1,
        next_review_date: now,
        resolved: false,
        question: found?.question,
        group: found?.group,
        created_at: now,
        updated_at: now,
      };
      return { next: [created, ...current], result: created };
    });

    return NextResponse.json(
      { success: true, mistake: hydrateMistake(saved) },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể lưu lỗi sai';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const id = typeof body.id === 'string' ? body.id.trim() : '';
    const resolved = typeof body.resolved === 'boolean' ? body.resolved : undefined;

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Thiếu id lỗi sai.' },
        { status: 400, headers: NO_STORE_HEADERS }
      );
    }

    const now = new Date().toISOString();
    const updatedItem = await mutateMistakes((current) => {
      let target: UserMistake | null = null;
      const next = current.map((m) => {
        if (m.id === id) {
          target = {
            ...m,
            resolved: resolved !== undefined ? resolved : !m.resolved,
            updated_at: now,
          };
          return target;
        }
        return m;
      });
      return { next, result: target };
    });

    if (!updatedItem) {
      return NextResponse.json(
        { success: false, error: 'Không tìm thấy lỗi sai cần cập nhật.' },
        { status: 404, headers: NO_STORE_HEADERS }
      );
    }

    return NextResponse.json(
      { success: true, mistake: hydrateMistake(updatedItem) },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể cập nhật lỗi sai';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    await mutateMistakes((current) => {
      if (!id) return { next: [], result: true };
      return { next: current.filter((m) => m.id !== id), result: true };
    });

    return NextResponse.json({ success: true }, { headers: NO_STORE_HEADERS });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể xóa lỗi sai';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}
