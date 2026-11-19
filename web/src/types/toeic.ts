// Type Definitions for TOEIC L&R Adaptive Coaching Platform
// Strictly aligns with SPECIFICATION.md Section 3

export type ToeicPart = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export type QuestionOptionKey = 'A' | 'B' | 'C' | 'D';

export interface QuestionOptions {
  A: string;
  B: string;
  C: string;
  D?: string; // Part 2 only has A, B, C
}

export interface ParaphrasePair {
  original: string;
  paraphrased: string;
}

export interface TranscriptSegment {
  id: string | number;
  speaker?: string; // e.g. "Woman", "Man", "Speaker", "Question 1"
  start_time: number; // in seconds (e.g. 1.25)
  end_time: number;   // in seconds (e.g. 4.80)
  text_en: string;
  text_vi?: string;
  is_trap?: boolean;  // highlighted if this segment contains a distractor/trap
}

export interface QuestionGroup {
  id: string;
  test_name: string;
  part: ToeicPart;
  passage_text?: string | null; // HTML/Markdown for Part 6, 7 reading passages
  image_url?: string | null;    // Part 1 photos, Part 3/4/7 graphics
  audio_url?: string | null;    // Part 1, 2, 3, 4 MP3 link
  transcript_segments?: TranscriptSegment[] | null;
  questions?: Question[];
  created_at?: string;
  updated_at?: string;
}

export interface Question {
  id: string;
  group_id: string;
  part: ToeicPart;
  question_number: number;
  question_type_tag: string; // e.g., 'word_form', 'verb_tense', 'wh_where', 'passive_being_trap'
  question_text?: string | null; // Nullable for Part 1 & 2
  options: QuestionOptions;
  correct_answer: QuestionOptionKey;
  explanation_vi: string; // Detailed Vietnamese explanation + strategy tip
  evidence_quote?: string | null; // Substring in passage_text or transcript_segments
  paraphrase_pair?: ParaphrasePair | null;
  image_url?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface UserMistake {
  id: string;
  question_id: string;
  selected_wrong_answer: QuestionOptionKey;
  wrong_count: number;
  next_review_date: string;
  resolved: boolean;
  question?: Question;
  group?: QuestionGroup;
  created_at?: string;
  updated_at?: string;
}

export interface VocabSRS {
  id: string;
  word: string;
  phonetic?: string;
  meaning_vi: string;
  context_sentence: string; // Captured from question where user highlighted it
  part_of_speech?: string;  // e.g. 'noun', 'verb', 'adjective', 'adverb', 'collocation'
  interval: number;         // Days until next review (SM-2)
  repetition: number;       // Count of successful recalls
  ease_factor: number;      // Default 2.5
  due_date: string;         // ISO timestamp
  created_at?: string;
  updated_at?: string;
}

export interface ExamSummary {
  id: string;                 // Stable slug derived from folder name (e.g. 'test-1-ets-2023')
  folderName: string;         // Exact folder name in data/exams/
  testNumber: number | null;  // Parsed numeric test index if present
  name: string;               // Display title from metadata.test_name
  shortTitle: string;         // Compact badge label (e.g. 'Test 01')
  totalQuestions: number;
  totalGroups: number;
  parts: Record<number, number>;
  updatedAt: string;
}

export interface UserProgressData {
  selectedTestId: string | null;
  selectedTestName: string | null;
  answersByTest: Record<string, Record<string, QuestionOptionKey>>;
  studyDates: string[]; // YYYY-MM-DD strings
  updatedAt: string;
}

export interface SystemHealthStatus {
  ok: boolean;
  storageMode: 'local_filesystem';
  examCount: number;
  userDataWritable: boolean;
  paths: {
    examsDir: string;
    rawDir: string;
    mediaDir: string;
    userDataDir: string;
  };
  error?: string;
}
