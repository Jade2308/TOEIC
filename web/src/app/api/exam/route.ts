import { NextRequest, NextResponse } from 'next/server';
import {
  findExamByIdentifier,
  getFilteredExamPayload,
  listExamSummaries,
  resolveExamsDir,
} from '@/lib/exam-repository';
import { ToeicPart } from '@/types/toeic';

export const dynamic = 'force-dynamic';

const NO_STORE_HEADERS = {
  'Cache-Control': 'no-store, max-age=0',
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const isOverview = searchParams.get('overview') === 'true';

    if (isOverview) {
      const tests = listExamSummaries();
      return NextResponse.json(
        {
          success: true,
          source: 'local_filesystem',
          dataDir: resolveExamsDir(),
          tests,
        },
        { headers: NO_STORE_HEADERS }
      );
    }

    const partParam = searchParams.get('part');
    const parsedPart =
      partParam && partParam !== 'all' ? parseInt(partParam, 10) : undefined;
    const partFilter =
      parsedPart && parsedPart >= 1 && parsedPart <= 7
        ? (parsedPart as ToeicPart)
        : undefined;

    const testIdentifier =
      searchParams.get('test') ||
      searchParams.get('test_id') ||
      searchParams.get('test_name');

    const dataset = findExamByIdentifier(testIdentifier);
    if (!dataset) {
      const available = listExamSummaries();
      return NextResponse.json(
        {
          success: false,
          error:
            available.length === 0
              ? `Chưa tìm thấy đề thi nào trong thư mục dữ liệu (${resolveExamsDir()}).`
              : `Không tìm thấy đề thi "${testIdentifier}".`,
          availableTests: available.map((t) => ({ id: t.id, name: t.name })),
          groups: [],
          questions: [],
        },
        { status: 404, headers: NO_STORE_HEADERS }
      );
    }

    const payload = getFilteredExamPayload(dataset, partFilter);

    return NextResponse.json(
      {
        success: true,
        source: 'local_filesystem',
        exam: payload.summary,
        test_name: payload.summary.name,
        groups: payload.groups,
        questions: payload.questions,
      },
      { headers: NO_STORE_HEADERS }
    );
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Lỗi đọc dữ liệu đề thi';
    console.error('[api/exam] Error:', error);
    return NextResponse.json(
      { success: false, error: message, groups: [], questions: [] },
      { status: 500, headers: NO_STORE_HEADERS }
    );
  }
}
