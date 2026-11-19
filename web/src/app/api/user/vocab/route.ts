import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { calculateSM2 } from '@/lib/srs';
import { mutateVocabList, readVocabList } from '@/lib/user-store';
import { VocabSRS } from '@/types/toeic';

export const dynamic = 'force-dynamic';

const NO_STORE_HEADERS = {
  'Cache-Control': 'no-store, max-age=0',
};

export async function GET() {
  try {
    const list = readVocabList().sort(
      (a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
    );
    return NextResponse.json(
      { success: true, vocab: list },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể đọc kho từ vựng';
    return NextResponse.json(
      { success: false, error: message, vocab: [] },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const word = typeof body.word === 'string' ? body.word.trim() : '';
    const meaningVi = typeof body.meaning_vi === 'string' ? body.meaning_vi.trim() : '';
    const contextSentence =
      typeof body.context_sentence === 'string' ? body.context_sentence.trim() : '';
    const partOfSpeech =
      typeof body.part_of_speech === 'string' && body.part_of_speech.trim()
        ? body.part_of_speech.trim()
        : 'vocabulary';
    const phonetic =
      typeof body.phonetic === 'string' && body.phonetic.trim()
        ? body.phonetic.trim()
        : undefined;

    if (!word || !meaningVi) {
      return NextResponse.json(
        { success: false, error: 'Thiếu từ vựng hoặc nghĩa tiếng Việt.' },
        { status: 400, headers: NO_STORE_HEADERS }
      );
    }

    const now = new Date().toISOString();
    const saved = await mutateVocabList((current) => {
      const existing = current.find((v) => v.word.toLowerCase() === word.toLowerCase());
      if (existing) {
        return { next: current, result: existing };
      }

      const item: VocabSRS = {
        id: crypto.randomUUID(),
        word,
        phonetic,
        meaning_vi: meaningVi,
        context_sentence: contextSentence || word,
        part_of_speech: partOfSpeech,
        interval: 1,
        repetition: 0,
        ease_factor: 2.5,
        due_date: now,
        created_at: now,
        updated_at: now,
      };
      return { next: [item, ...current], result: item };
    });

    return NextResponse.json(
      { success: true, item: saved },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể lưu từ vựng';
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
    const qualityScore = Number(body.qualityScore ?? body.quality);

    if (!id || Number.isNaN(qualityScore)) {
      return NextResponse.json(
        { success: false, error: 'Thiếu id hoặc điểm đánh giá SM-2.' },
        { status: 400, headers: NO_STORE_HEADERS }
      );
    }

    const now = new Date().toISOString();
    const updatedItem = await mutateVocabList((current) => {
      let target: VocabSRS | null = null;
      const next = current.map((v) => {
        if (v.id === id) {
          const sm2 = calculateSM2(qualityScore, v.repetition, v.interval, v.ease_factor);
          target = {
            ...v,
            interval: sm2.interval,
            repetition: sm2.repetition,
            ease_factor: sm2.ease_factor,
            due_date: sm2.due_date,
            updated_at: now,
          };
          return target;
        }
        return v;
      });
      return { next, result: target };
    });

    if (!updatedItem) {
      return NextResponse.json(
        { success: false, error: 'Không tìm thấy từ vựng cần ôn.' },
        { status: 404, headers: NO_STORE_HEADERS }
      );
    }

    return NextResponse.json(
      { success: true, item: updatedItem },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể cập nhật từ vựng';
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

    if (!id) {
      return NextResponse.json(
        { success: false, error: 'Thiếu id từ vựng cần xóa.' },
        { status: 400, headers: NO_STORE_HEADERS }
      );
    }

    await mutateVocabList((current) => ({
      next: current.filter((v) => v.id !== id),
      result: true,
    }));

    return NextResponse.json({ success: true }, { headers: NO_STORE_HEADERS });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể xóa từ vựng';
    return NextResponse.json(
      { success: false, error: message },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}
