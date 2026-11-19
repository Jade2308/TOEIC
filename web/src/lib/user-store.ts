// ==============================================================================
// Server-Side Atomic JSON User Data Store (Replaces Supabase for Personal Use)
// Persists mistakes.json, vocab_srs.json, and progress.json inside data/user/
// ==============================================================================

import fs from 'fs';
import path from 'path';
import { UserMistake, UserProgressData, VocabSRS } from '@/types/toeic';
import { resolveUserDataDir } from '@/lib/exam-repository';

// Per-file serialized write queue so rapid UI clicks never interleave writes
const writeQueues = new Map<string, Promise<unknown>>();

function enqueueFileOp<T>(fileKey: string, task: () => T | Promise<T>): Promise<T> {
  const prev = writeQueues.get(fileKey) || Promise.resolve();
  const next = prev.then(() => task(), () => task());
  writeQueues.set(
    fileKey,
    next.catch(() => undefined)
  );
  return next;
}

function ensureUserDataDir(): string {
  const dir = resolveUserDataDir();
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  return dir;
}

function getFilePath(filename: string): string {
  return path.join(ensureUserDataDir(), filename);
}

function readJsonFile<T>(filename: string, defaultValue: T): T {
  try {
    const filePath = getFilePath(filename);
    if (!fs.existsSync(filePath)) {
      return defaultValue;
    }
    const content = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '').trim();
    if (!content) return defaultValue;
    return JSON.parse(content) as T;
  } catch (err) {
    console.error(`[user-store] Failed to read ${filename}:`, err);
    return defaultValue;
  }
}

function atomicWriteJsonFile(filename: string, data: unknown): void {
  const filePath = getFilePath(filename);
  const tmpPath = `${filePath}.tmp.${process.pid}.${Date.now()}`;
  const serialized = JSON.stringify(data, null, 2);
  fs.writeFileSync(tmpPath, serialized, 'utf8');
  fs.renameSync(tmpPath, filePath);
}

// ==============================================================================
// HEALTH / WRITABILITY CHECK
// ==============================================================================

export function checkUserDataWritable(): { writable: boolean; dir: string; error?: string } {
  const dir = resolveUserDataDir();
  try {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    const probe = path.join(dir, `.write-test-${process.pid}-${Date.now()}`);
    fs.writeFileSync(probe, 'ok', 'utf8');
    fs.unlinkSync(probe);
    return { writable: true, dir };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return { writable: false, dir, error: message };
  }
}

// ==============================================================================
// 1. MISTAKES STORE (data/user/mistakes.json)
// ==============================================================================

const MISTAKES_FILE = 'mistakes.json';

export function readMistakes(): UserMistake[] {
  const list = readJsonFile<UserMistake[]>(MISTAKES_FILE, []);
  return Array.isArray(list) ? list : [];
}

export async function mutateMistakes<T>(
  updater: (current: UserMistake[]) => { next: UserMistake[]; result: T }
): Promise<T> {
  return enqueueFileOp(MISTAKES_FILE, () => {
    const current = readMistakes();
    const { next, result } = updater(current);
    atomicWriteJsonFile(MISTAKES_FILE, next);
    return result;
  });
}

// ==============================================================================
// 2. VOCAB SRS STORE (data/user/vocab_srs.json)
// ==============================================================================

const VOCAB_FILE = 'vocab_srs.json';

export function readVocabList(): VocabSRS[] {
  const list = readJsonFile<VocabSRS[]>(VOCAB_FILE, []);
  return Array.isArray(list) ? list : [];
}

export async function mutateVocabList<T>(
  updater: (current: VocabSRS[]) => { next: VocabSRS[]; result: T }
): Promise<T> {
  return enqueueFileOp(VOCAB_FILE, () => {
    const current = readVocabList();
    const { next, result } = updater(current);
    atomicWriteJsonFile(VOCAB_FILE, next);
    return result;
  });
}

// ==============================================================================
// 3. USER PROGRESS & STUDY STREAK STORE (data/user/progress.json)
// ==============================================================================

const PROGRESS_FILE = 'progress.json';

function defaultProgress(): UserProgressData {
  return {
    selectedTestId: null,
    selectedTestName: null,
    answersByTest: {},
    studyDates: [],
    updatedAt: new Date().toISOString(),
  };
}

export function readUserProgress(): UserProgressData {
  const raw = readJsonFile<Partial<UserProgressData>>(PROGRESS_FILE, defaultProgress());
  return {
    selectedTestId: raw.selectedTestId ?? null,
    selectedTestName: raw.selectedTestName ?? null,
    answersByTest: raw.answersByTest && typeof raw.answersByTest === 'object' ? raw.answersByTest : {},
    studyDates: Array.isArray(raw.studyDates) ? raw.studyDates : [],
    updatedAt: raw.updatedAt || new Date().toISOString(),
  };
}

export async function mutateUserProgress<T>(
  updater: (current: UserProgressData) => { next: UserProgressData; result: T }
): Promise<T> {
  return enqueueFileOp(PROGRESS_FILE, () => {
    const current = readUserProgress();
    const { next, result } = updater(current);
    next.updatedAt = new Date().toISOString();
    atomicWriteJsonFile(PROGRESS_FILE, next);
    return result;
  });
}

export function getTodayDateKey(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function exportFullUserBackup() {
  return {
    exportedAt: new Date().toISOString(),
    version: 1,
    mistakes: readMistakes(),
    vocab_srs: readVocabList(),
    progress: readUserProgress(),
  };
}
