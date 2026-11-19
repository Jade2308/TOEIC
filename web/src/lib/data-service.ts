// ==============================================================================
// Unified Local-First Data Service Layer (100% Server Filesystem Backed)
// Communicates directly with Next.js API Routes (/api/exam, /api/user/*, /api/health)
// Zero cloud/Supabase dependencies; localStorage acts only as an emergency read cache.
// ==============================================================================

import {
  ExamSummary,
  Question,
  QuestionGroup,
  QuestionOptionKey,
  SystemHealthStatus,
  ToeicPart,
  UserMistake,
  UserProgressData,
  VocabSRS,
} from '@/types/toeic';
import {
  getCachedMistakes,
  getCachedProgress,
  getCachedVocab,
  setCachedMistakes,
  setCachedProgress,
  setCachedVocab,
} from '@/lib/storage';

const NO_CACHE_INIT: RequestInit = {
  cache: 'no-store',
};

export const ToeicDataService = {
  /**
   * Check local storage & exam repository health on the server
   */
  async getSystemHealth(): Promise<SystemHealthStatus | null> {
    if (typeof window === 'undefined') return null;
    try {
      const res = await fetch('/api/health', NO_CACHE_INIT);
      const json = await res.json();
      return json as SystemHealthStatus;
    } catch (err) {
      console.warn('Health check failed:', err);
      return null;
    }
  },

  /**
   * Dynamically discover all processed exams from server filesystem (data/exams/)
   */
  async getExamOverview(): Promise<ExamSummary[]> {
    if (typeof window === 'undefined') return [];
    try {
      const res = await fetch('/api/exam?overview=true', NO_CACHE_INIT);
      if (!res.ok) return [];
      const json = await res.json();
      if (json.success && Array.isArray(json.tests)) {
        return json.tests as ExamSummary[];
      }
    } catch (err) {
      console.warn('Failed to fetch exam overview from /api/exam:', err);
    }
    return [];
  },

  /**
   * Load groups and questions for a specific test (by slug id, name, or test number)
   */
  async getExamData(
    part?: ToeicPart,
    testIdentifier?: string
  ): Promise<{ exam: ExamSummary | null; groups: QuestionGroup[]; questions: Question[]; error?: string }> {
    if (typeof window === 'undefined') {
      return { exam: null, groups: [], questions: [] };
    }

    try {
      const queryParams = new URLSearchParams();
      queryParams.set('part', part ? String(part) : 'all');
      if (testIdentifier) {
        queryParams.set('test', testIdentifier);
      }

      const res = await fetch(`/api/exam?${queryParams.toString()}`, NO_CACHE_INIT);
      const json = await res.json();

      if (res.ok && json.success) {
        return {
          exam: (json.exam as ExamSummary) || null,
          groups: Array.isArray(json.groups) ? (json.groups as QuestionGroup[]) : [],
          questions: Array.isArray(json.questions) ? (json.questions as Question[]) : [],
        };
      }

      return {
        exam: null,
        groups: [],
        questions: [],
        error: json.error || 'Không tìm thấy dữ liệu đề thi.',
      };
    } catch (err) {
      console.warn('API /api/exam fetch failed:', err);
      return {
        exam: null,
        groups: [],
        questions: [],
        error: 'Không thể kết nối tới máy chủ cục bộ để tải đề thi.',
      };
    }
  },

  // ============================================================================
  // USER MISTAKES (data/user/mistakes.json)
  // ============================================================================

  async getMistakes(): Promise<UserMistake[]> {
    if (typeof window === 'undefined') return [];
    try {
      const res = await fetch('/api/user/mistakes', NO_CACHE_INIT);
      if (res.ok) {
        const json = await res.json();
        if (json.success && Array.isArray(json.mistakes)) {
          setCachedMistakes(json.mistakes);
          return json.mistakes as UserMistake[];
        }
      }
    } catch (err) {
      console.warn('Failed to fetch mistakes from server, using cache:', err);
    }
    return getCachedMistakes();
  },

  async recordMistake(
    questionId: string,
    wrongAnswer: QuestionOptionKey
  ): Promise<UserMistake | null> {
    try {
      const res = await fetch('/api/user/mistakes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
        body: JSON.stringify({ question_id: questionId, wrong_answer: wrongAnswer }),
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.mistake) {
          return json.mistake as UserMistake;
        }
      }
    } catch (err) {
      console.warn('Failed to persist mistake on server:', err);
    }
    return null;
  },

  async resolveMistake(mistakeId: string): Promise<void> {
    await this.toggleMistakeResolved(mistakeId, true);
  },

  async toggleMistakeResolved(mistakeId: string, resolved?: boolean): Promise<void> {
    try {
      await fetch('/api/user/mistakes', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
        body: JSON.stringify({ id: mistakeId, resolved }),
      });
    } catch (err) {
      console.warn('Failed to toggle mistake resolved state:', err);
    }
  },

  // ============================================================================
  // VOCAB SRS (data/user/vocab_srs.json)
  // ============================================================================

  async getVocabSRS(): Promise<VocabSRS[]> {
    if (typeof window === 'undefined') return [];
    try {
      const res = await fetch('/api/user/vocab', NO_CACHE_INIT);
      if (res.ok) {
        const json = await res.json();
        if (json.success && Array.isArray(json.vocab)) {
          setCachedVocab(json.vocab);
          return json.vocab as VocabSRS[];
        }
      }
    } catch (err) {
      console.warn('Failed to fetch vocab SRS from server, using cache:', err);
    }
    return getCachedVocab();
  },

  async saveWordToSRS(
    word: string,
    meaningVi: string,
    contextSentence: string,
    partOfSpeech: string = 'vocabulary',
    phonetic?: string
  ): Promise<VocabSRS> {
    const res = await fetch('/api/user/vocab', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
      body: JSON.stringify({
        word,
        meaning_vi: meaningVi,
        context_sentence: contextSentence,
        part_of_speech: partOfSpeech,
        phonetic,
      }),
    });

    const json = await res.json();
    if (!res.ok || !json.success || !json.item) {
      throw new Error(json.error || 'Không thể lưu từ vựng lên máy chủ');
    }
    return json.item as VocabSRS;
  },

  async reviewVocabItem(vocabId: string, qualityScore: number): Promise<VocabSRS | null> {
    try {
      const res = await fetch('/api/user/vocab', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
        body: JSON.stringify({ id: vocabId, qualityScore }),
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.item) {
          return json.item as VocabSRS;
        }
      }
    } catch (err) {
      console.warn('Failed to update vocab SM-2 on server:', err);
    }
    return null;
  },

  // ============================================================================
  // USER PROGRESS & STREAK (data/user/progress.json)
  // ============================================================================

  async getUserProgress(): Promise<UserProgressData> {
    const fallback: UserProgressData = getCachedProgress() || {
      selectedTestId: null,
      selectedTestName: null,
      answersByTest: {},
      studyDates: [],
      updatedAt: new Date().toISOString(),
    };

    if (typeof window === 'undefined') return fallback;

    try {
      const res = await fetch('/api/user/progress', NO_CACHE_INIT);
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.progress) {
          setCachedProgress(json.progress);
          return json.progress as UserProgressData;
        }
      }
    } catch (err) {
      console.warn('Failed to fetch user progress, using cache:', err);
    }
    return fallback;
  },

  async saveAnswerProgress(
    testKey: string,
    testName: string,
    questionId?: string,
    answer?: QuestionOptionKey
  ): Promise<UserProgressData | null> {
    try {
      const res = await fetch('/api/user/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
        body: JSON.stringify({ testKey, testName, questionId, answer }),
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.progress) {
          setCachedProgress(json.progress);
          return json.progress as UserProgressData;
        }
      }
    } catch (err) {
      console.warn('Failed to save user progress:', err);
    }
    return null;
  },

  async resetTestProgress(testKey: string): Promise<void> {
    try {
      const res = await fetch(`/api/user/progress?test=${encodeURIComponent(testKey)}`, {
        method: 'DELETE',
        cache: 'no-store',
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.progress) {
          setCachedProgress(json.progress);
        }
      }
    } catch (err) {
      console.warn('Failed to reset test progress:', err);
    }
  },
};
