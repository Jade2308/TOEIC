import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { resolveRawDir } from '@/lib/exam-repository';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const testName = formData.get('test_name') as string;
    const testPdf = formData.get('test_pdf') as File | null;
    const audioFile = formData.get('audio_file') as File | null;
    const answerFile = formData.get('answer_file') as File | null;
    const transcriptPdf = formData.get('transcript_pdf') as File | null;

    if (!testName || !testName.trim()) {
      return NextResponse.json(
        { success: false, error: 'Vui lòng cung cấp tên thư mục đề thi (ví dụ: TEST 5 - ETS 2023).' },
        { status: 400 }
      );
    }

    // Sanitize directory name against path traversal
    const safeDirName = testName.trim().replace(/[\\/:*?"<>|]+/g, '-');
    if (!safeDirName || safeDirName === '.' || safeDirName === '..') {
      return NextResponse.json(
        { success: false, error: 'Tên thư mục đề thi không hợp lệ.' },
        { status: 400 }
      );
    }

    if (!testPdf || !audioFile || !answerFile) {
      return NextResponse.json(
        { success: false, error: 'Thiếu file bắt buộc: Cần đầy đủ Đề PDF, Audio MP3 và Đáp án (ảnh hoặc PDF).' },
        { status: 400 }
      );
    }

    const targetBaseDir = resolveRawDir();
    const testDir = path.resolve(targetBaseDir, safeDirName);
    if (!testDir.startsWith(path.resolve(targetBaseDir) + path.sep)) {
      return NextResponse.json(
        { success: false, error: 'Đường dẫn thư mục không hợp lệ.' },
        { status: 400 }
      );
    }

    if (!fs.existsSync(testDir)) {
      fs.mkdirSync(testDir, { recursive: true });
    }

    const saveFile = async (file: File, filename: string) => {
      const cleanFilename = path.basename(filename);
      const buffer = Buffer.from(await file.arrayBuffer());
      fs.writeFileSync(path.join(testDir, cleanFilename), buffer);
    };

    await saveFile(testPdf, testPdf.name);
    await saveFile(audioFile, audioFile.name);
    await saveFile(answerFile, answerFile.name);
    if (transcriptPdf && transcriptPdf.size > 0) {
      await saveFile(transcriptPdf, transcriptPdf.name);
    }

    return NextResponse.json({
      success: true,
      message: `Đã tải lên toàn bộ tài liệu thành công vào thư mục "data/raw/${safeDirName}"!`,
      test_dir: safeDirName,
    });
  } catch (error: unknown) {
    console.error('Upload handler error:', error);
    const message = error instanceof Error ? error.message : 'Lỗi xử lý file tải lên';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
