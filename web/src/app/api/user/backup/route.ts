import { NextResponse } from 'next/server';
import { exportFullUserBackup, getTodayDateKey } from '@/lib/user-store';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const backup = exportFullUserBackup();
    const filename = `toeic-backup-${getTodayDateKey()}.json`;

    return new Response(JSON.stringify(backup, null, 2), {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Không thể xuất file sao lưu';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
