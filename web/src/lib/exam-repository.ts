// ==============================================================================
// Server-Side Dynamic Exam Repository (Single Source of Truth on Filesystem)
// Scans data/exams/ dynamically so newly crawled tests appear immediately
// without restarting or rebuilding Next.js / Docker.
// ==============================================================================

import fs from 'fs';
import path from 'path';
import { ExamSummary, Question, QuestionGroup, ToeicPart } from '@/types/toeic';

export interface LoadedExamDataset {
  summary: ExamSummary;
  filePath: string;
  mtimeMs: number;
  groups: QuestionGroup[];
  questions: Question[];
}

// mtime-validated in-memory cache (auto-invalidates immediately if file changes)
const datasetCache = new Map<string, LoadedExamDataset>();

function pickFirstExistingDir(candidates: Array<string | undefined>): string | null {
  for (const candidate of candidates) {
    if (!candidate) continue;
    const resolved = path.resolve(candidate);
    if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) {
      return resolved;
    }
  }
  return null;
}

export function resolveDataRootDir(): string {
  const envDataDir = process.env.DATA_DIR;
  if (envDataDir) {
    return path.resolve(envDataDir);
  }
  const existing = pickFirstExistingDir([
    path.join(process.cwd(), 'data'),
    path.join(process.cwd(), '..', 'data'),
  ]);
  return existing || path.resolve(process.cwd(), '..', 'data');
}

export function resolveExamsDir(): string {
  const existing = pickFirstExistingDir([
    process.env.PROCESSED_DATA_DIR,
    process.env.EXAMS_DATA_DIR,
    path.join(resolveDataRootDir(), 'exams'),
    path.join(process.cwd(), 'data', 'exams'),
    path.join(process.cwd(), '..', 'data', 'exams'),
    // Backward compatibility fallback for legacy crawler/processed_data layout
    path.join(process.cwd(), 'crawler', 'processed_data'),
    path.join(process.cwd(), '..', 'crawler', 'processed_data'),
  ]);
  return existing || path.join(resolveDataRootDir(), 'exams');
}

export function resolveRawDir(): string {
  const existing = pickFirstExistingDir([
    process.env.RAW_DATA_DIR,
    path.join(resolveDataRootDir(), 'raw'),
    path.join(process.cwd(), 'data', 'raw'),
    path.join(process.cwd(), '..', 'data', 'raw'),
    // Backward compatibility fallback for legacy crawler/raw_data layout
    path.join(process.cwd(), 'crawler', 'raw_data'),
    path.join(process.cwd(), '..', 'crawler', 'raw_data'),
  ]);
  return existing || path.join(resolveDataRootDir(), 'raw');
}

export function resolveMediaDir(): string {
  const existing = pickFirstExistingDir([
    process.env.MEDIA_DATA_DIR,
    path.join(resolveDataRootDir(), 'media'),
    path.join(process.cwd(), 'data', 'media'),
    path.join(process.cwd(), '..', 'data', 'media'),
    // Backward compatibility fallback
    path.join(process.cwd(), 'public'),
  ]);
  return existing || path.join(resolveDataRootDir(), 'media');
}

export function resolveUserDataDir(): string {
  if (process.env.USER_DATA_DIR) {
    return path.resolve(process.env.USER_DATA_DIR);
  }
  const existing = pickFirstExistingDir([
    path.join(resolveDataRootDir(), 'user'),
    path.join(process.cwd(), 'data', 'user'),
    path.join(process.cwd(), '..', 'data', 'user'),
    path.join(process.cwd(), 'user_data'),
    path.join(process.cwd(), '..', 'user_data'),
  ]);
  return existing || path.join(resolveDataRootDir(), 'user');
}

export function slugifyFolderName(folderName: string): string {
  return folderName
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'exam';
}

function extractTestNumber(text: string): number | null {
  const testMatch = text.match(/test\s*[-_#]?\s*(\d+)/i);
  if (testMatch) return parseInt(testMatch[1], 10);
  const firstNum = text.match(/\b(\d+)\b/);
  return firstNum ? parseInt(firstNum[1], 10) : null;
}

/**
 * Selects the canonical compiled full-test JSON file inside an exam directory.
 * Explicitly excludes partial files like `test1_part5_full.json` which previously
 * caused nondeterministic failures on Linux ext4 filesystems.
 */
export function findCanonicalFullJson(examDirPath: string): string | null {
  const searchDirs = [path.join(examDirPath, 'final'), examDirPath];

  for (const dir of searchDirs) {
    if (!fs.existsSync(/*turbopackIgnore: true*/ dir) || !fs.statSync(/*turbopackIgnore: true*/ dir).isDirectory()) continue;

    const jsonFiles = fs
      .readdirSync(/*turbopackIgnore: true*/ dir)
      .filter((name) => name.toLowerCase().endsWith('.json'))
      .sort((a, b) => a.localeCompare(b));

    if (jsonFiles.length === 0) continue;

    // Priority 1: *full.json files that are NOT single-part files (exclude part1..part7)
    const fullCandidates = jsonFiles.filter((name) => {
      const lower = name.toLowerCase();
      return lower.includes('full.json') && !/part\s*\d+/i.test(lower);
    });

    if (fullCandidates.length === 1) {
      return path.join(dir, fullCandidates[0]);
    }

    if (fullCandidates.length > 1) {
      // Pick the largest full JSON file (most complete dataset)
      fullCandidates.sort((a, b) => {
        const sizeA = fs.statSync(path.join(dir, a)).size;
        const sizeB = fs.statSync(path.join(dir, b)).size;
        return sizeB - sizeA;
      });
      return path.join(dir, fullCandidates[0]);
    }

    // Priority 2: any full.json if no non-part full.json exists
    const anyFull = jsonFiles.filter((name) => name.toLowerCase().includes('full.json'));
    if (anyFull.length > 0) {
      anyFull.sort((a, b) => {
        const sizeA = fs.statSync(path.join(dir, a)).size;
        const sizeB = fs.statSync(path.join(dir, b)).size;
        return sizeB - sizeA;
      });
      return path.join(dir, anyFull[0]);
    }
  }

  return null;
}

function loadExamDatasetFromFile(folderName: string, filePath: string): LoadedExamDataset | null {
  try {
    const stat = fs.statSync(filePath);
    const cached = datasetCache.get(filePath);
    if (cached && cached.mtimeMs === stat.mtimeMs) {
      return cached;
    }

    const raw = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
    const parsed = JSON.parse(raw);

    const groups: QuestionGroup[] = Array.isArray(parsed.question_groups)
      ? parsed.question_groups
      : [];
    const questions: Question[] = Array.isArray(parsed.questions)
      ? parsed.questions
      : [];

    if (questions.length === 0 && groups.length === 0) {
      return null;
    }

    // Sort questions stably by question_number
    questions.sort((a, b) => (a.question_number || 0) - (b.question_number || 0));

    const testName: string =
      parsed.metadata?.test_name ||
      groups[0]?.test_name ||
      folderName;

    const testNumber = extractTestNumber(testName) ?? extractTestNumber(folderName);
    const shortTitle =
      testNumber !== null
        ? `Test ${String(testNumber).padStart(2, '0')}`
        : folderName.slice(0, 12);

    const parts: Record<number, number> = {};
    for (const q of questions) {
      if (q.part) {
        parts[q.part] = (parts[q.part] || 0) + 1;
      }
    }

    const summary: ExamSummary = {
      id: slugifyFolderName(folderName),
      folderName,
      testNumber,
      name: testName,
      shortTitle,
      totalQuestions: questions.length,
      totalGroups: groups.length,
      parts,
      updatedAt: stat.mtime.toISOString(),
    };

    const dataset: LoadedExamDataset = {
      summary,
      filePath,
      mtimeMs: stat.mtimeMs,
      groups,
      questions,
    };

    datasetCache.set(filePath, dataset);
    return dataset;
  } catch (err) {
    console.error(`[exam-repository] Failed to parse exam file "${filePath}":`, err);
    return null;
  }
}

/**
 * Dynamically discovers and loads all processed exams from disk.
 * Never hardcoded; naturally sorted by testNumber then name.
 */
export function loadAllExams(): LoadedExamDataset[] {
  const examsDir = resolveExamsDir();
  if (!fs.existsSync(/*turbopackIgnore: true*/ examsDir)) {
    return [];
  }

  const entries = fs.readdirSync(/*turbopackIgnore: true*/ examsDir, { withFileTypes: true });
  const datasets: LoadedExamDataset[] = [];
  const activeFilePaths = new Set<string>();

  for (const entry of entries) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) {
      continue;
    }
    const dirPath = path.join(/*turbopackIgnore: true*/ examsDir, entry.name);
    const fullJsonPath = findCanonicalFullJson(dirPath);
    if (!fullJsonPath) continue;

    activeFilePaths.add(fullJsonPath);
    const dataset = loadExamDatasetFromFile(entry.name, fullJsonPath);
    if (dataset) {
      datasets.push(dataset);
    }
  }

  // Prune stale cache entries for deleted exams
  for (const cachedPath of datasetCache.keys()) {
    if (!activeFilePaths.has(cachedPath)) {
      datasetCache.delete(cachedPath);
    }
  }

  // Natural sort: group by testNumber when present, then alphabetical name
  datasets.sort((a, b) => {
    const numA = a.summary.testNumber ?? Number.MAX_SAFE_INTEGER;
    const numB = b.summary.testNumber ?? Number.MAX_SAFE_INTEGER;
    if (numA !== numB) return numA - numB;
    return a.summary.name.localeCompare(b.summary.name, undefined, { numeric: true });
  });

  return datasets;
}

export function listExamSummaries(): ExamSummary[] {
  return loadAllExams().map((d) => d.summary);
}

/**
 * Resolves an exam by flexible identifier:
 * 1. Exact slug `id` (e.g. 'test-5-ets-2023')
 * 2. Exact `folderName` (e.g. 'TEST 5 - ETS 2023')
 * 3. Exact `name` (case-insensitive, e.g. 'ETS TOEIC 2023 - Test 5')
 * 4. Numeric test index (e.g. '5', 'test-5', 'test 5')
 */
export function findExamByIdentifier(identifier?: string | null): LoadedExamDataset | null {
  const all = loadAllExams();
  if (all.length === 0) return null;

  if (!identifier || !identifier.trim()) {
    return all[0];
  }

  const trimmed = identifier.trim();
  const lower = trimmed.toLowerCase();
  const slugified = slugifyFolderName(trimmed);

  // 1. Exact id or folderName
  const byId = all.find(
    (d) =>
      d.summary.id === lower ||
      d.summary.id === slugified ||
      d.summary.folderName.toLowerCase() === lower
  );
  if (byId) return byId;

  // 2. Exact test display name
  const byName = all.find((d) => d.summary.name.toLowerCase() === lower);
  if (byName) return byName;

  // 3. Match by test number if user passed '5', 'test 5', 'test-5'
  const num = extractTestNumber(trimmed);
  if (num !== null) {
    // Prefer matching both year/book hint if provided in identifier
    const yearMatch = trimmed.match(/\b(20\d{2})\b/);
    if (yearMatch) {
      const year = yearMatch[1];
      const byYearAndNum = all.find(
        (d) =>
          d.summary.testNumber === num &&
          (d.summary.name.includes(year) || d.summary.folderName.includes(year))
      );
      if (byYearAndNum) return byYearAndNum;
    }

    const byNum = all.find((d) => d.summary.testNumber === num);
    if (byNum) return byNum;
  }

  // 4. Substring fallback
  const bySubstring = all.find(
    (d) =>
      d.summary.name.toLowerCase().includes(lower) ||
      d.summary.folderName.toLowerCase().includes(lower)
  );
  if (bySubstring) return bySubstring;

  return null;
}

export function getFilteredExamPayload(
  dataset: LoadedExamDataset,
  partFilter?: ToeicPart
): { summary: ExamSummary; groups: QuestionGroup[]; questions: Question[] } {
  const groups = partFilter
    ? dataset.groups.filter((g) => g.part === partFilter)
    : dataset.groups;
  const questions = partFilter
    ? dataset.questions.filter((q) => q.part === partFilter)
    : dataset.questions;

  const questionsByGroup = new Map<string, Question[]>();
  for (const q of questions) {
    const list = questionsByGroup.get(q.group_id);
    if (list) list.push(q);
    else questionsByGroup.set(q.group_id, [q]);
  }

  const enrichedGroups = groups.map((g) => ({
    ...g,
    questions: questionsByGroup.get(g.id) || [],
  }));

  return {
    summary: dataset.summary,
    groups: enrichedGroups,
    questions,
  };
}

/**
 * Looks up a question and its parent group across ALL crawled exams on disk.
 * Ensures Error Log mistakes from ANY test (Test 1, 2, 3, 4, 5...) hydrate cleanly.
 */
export function findQuestionAcrossAllExams(
  questionId: string
): { question: Question; group?: QuestionGroup; examSummary: ExamSummary } | null {
  const all = loadAllExams();
  for (const dataset of all) {
    const question = dataset.questions.find((q) => q.id === questionId);
    if (question) {
      const group = dataset.groups.find((g) => g.id === question.group_id);
      return { question, group, examSummary: dataset.summary };
    }
  }
  return null;
}
