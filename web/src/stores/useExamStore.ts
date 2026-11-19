import { create } from 'zustand';
import {
  ExamSummary,
  Question,
  QuestionGroup,
  QuestionOptionKey,
  ToeicPart,
  TranscriptSegment,
} from '@/types/toeic';
import { ToeicDataService } from '@/lib/data-service';

export type ExamMode = 'practice' | 'review';

export interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  playbackSpeed: number; // 0.8, 1.0, 1.1, 1.25
  activeSegmentId: string | number | null;
}

export interface ExamStoreState {
  // Dynamic Exam Registry
  availableExams: ExamSummary[];
  isLoadingExams: boolean;
  hasLoadedExams: boolean;

  // Active Exam Data
  groups: QuestionGroup[];
  questions: Question[];
  selectedPart: ToeicPart | 'all';
  selectedTestId: string;
  selectedTest: string;
  currentQuestionIndex: number;
  userAnswers: Record<string, QuestionOptionKey>;
  answersByTest: Record<string, Record<string, QuestionOptionKey>>;
  studyDates: string[];
  mode: ExamMode;
  isLoading: boolean;
  loadError: string | null;

  // Audio State
  audioState: AudioPlayerState;

  // Drill & Pacer States
  pacerSeconds: number;
  whDrillSelection: string | null;
  hidePart2Text: boolean;

  // Actions
  loadAvailableExams: (force?: boolean) => Promise<ExamSummary[]>;
  loadUserProgress: () => Promise<void>;
  setSelectedPart: (part: ToeicPart | 'all') => Promise<void>;
  setSelectedTest: (testIdentifier: string) => Promise<void>;
  loadExamData: (part?: ToeicPart | 'all', testIdentifier?: string) => Promise<void>;
  selectAnswer: (questionId: string, answer: QuestionOptionKey) => Promise<void>;
  goToQuestion: (index: number) => void;
  nextQuestion: () => void;
  prevQuestion: () => void;
  setMode: (mode: ExamMode) => void;
  resetProgress: () => Promise<void>;

  // Pacer & Drill actions
  setPacerSeconds: (seconds: number) => void;
  resetPacer: () => void;
  setWhDrillSelection: (type: string | null) => void;
  toggleHidePart2Text: () => void;

  // Audio actions
  setAudioPlaying: (isPlaying: boolean) => void;
  setAudioCurrentTime: (time: number) => void;
  setAudioDuration: (duration: number) => void;
  setPlaybackSpeed: (speed: number) => void;
  setActiveSegment: (segmentId: string | number | null) => void;
  jumpToSegment: (segment: TranscriptSegment) => void;
}

export const useExamStore = create<ExamStoreState>((set, get) => ({
  availableExams: [],
  isLoadingExams: false,
  hasLoadedExams: false,

  groups: [],
  questions: [],
  selectedPart: 'all',
  selectedTestId: '',
  selectedTest: '',
  currentQuestionIndex: 0,
  userAnswers: {},
  answersByTest: {},
  studyDates: [],
  mode: 'practice',
  isLoading: false,
  loadError: null,

  audioState: {
    isPlaying: false,
    currentTime: 0,
    duration: 30,
    playbackSpeed: 1.0,
    activeSegmentId: null,
  },

  pacerSeconds: 0,
  whDrillSelection: null,
  hidePart2Text: true,

  loadAvailableExams: async (force = false) => {
    const state = get();
    if (state.isLoadingExams && !force) {
      return state.availableExams;
    }

    set({ isLoadingExams: true });
    try {
      const exams = await ToeicDataService.getExamOverview();
      const current = get();
      let nextTestId = current.selectedTestId;
      let nextTestName = current.selectedTest;

      if (exams.length > 0) {
        const existingMatch = exams.find(
          (e) =>
            e.id === current.selectedTestId ||
            e.name.toLowerCase() === current.selectedTest.toLowerCase()
        );
        if (existingMatch) {
          nextTestId = existingMatch.id;
          nextTestName = existingMatch.name;
        } else {
          nextTestId = exams[0].id;
          nextTestName = exams[0].name;
        }
      }

      set({
        availableExams: exams,
        isLoadingExams: false,
        hasLoadedExams: true,
        selectedTestId: nextTestId,
        selectedTest: nextTestName,
      });
      return exams;
    } catch (err) {
      console.error('Failed to load available exams:', err);
      set({ isLoadingExams: false, hasLoadedExams: true });
      return get().availableExams;
    }
  },

  loadUserProgress: async () => {
    try {
      const progress = await ToeicDataService.getUserProgress();
      const current = get();
      const activeKey = current.selectedTestId || progress.selectedTestId || '';
      const activeAnswers = activeKey ? progress.answersByTest[activeKey] || {} : current.userAnswers;

      set({
        answersByTest: progress.answersByTest || {},
        studyDates: progress.studyDates || [],
        userAnswers: Object.keys(current.userAnswers).length > 0 ? current.userAnswers : activeAnswers,
        ...(current.selectedTestId === '' && progress.selectedTestId
          ? {
              selectedTestId: progress.selectedTestId,
              selectedTest: progress.selectedTestName || current.selectedTest,
            }
          : {}),
      });
    } catch (err) {
      console.warn('Failed to load user progress:', err);
    }
  },

  setSelectedPart: async (part: ToeicPart | 'all') => {
    set({
      selectedPart: part,
      currentQuestionIndex: 0,
      pacerSeconds: 0,
      whDrillSelection: null,
    });
    await get().loadExamData(part, get().selectedTestId || get().selectedTest || undefined);
  },

  setSelectedTest: async (testIdentifier: string) => {
    const exams = get().availableExams;
    const match = exams.find(
      (e) =>
        e.id === testIdentifier ||
        e.name.toLowerCase() === testIdentifier.toLowerCase() ||
        e.folderName.toLowerCase() === testIdentifier.toLowerCase()
    );

    const nextKey = match?.id || testIdentifier;
    const nextName = match?.name || testIdentifier;
    const savedAnswers = get().answersByTest[nextKey] || {};

    set({
      selectedTestId: nextKey,
      selectedTest: nextName,
      currentQuestionIndex: 0,
      userAnswers: savedAnswers,
      pacerSeconds: 0,
      whDrillSelection: null,
    });

    // Persist last selected test in background
    ToeicDataService.saveAnswerProgress(nextKey, nextName).catch(() => undefined);

    await get().loadExamData(get().selectedPart, nextKey);
  },

  loadExamData: async (part, testIdentifier) => {
    set({ isLoading: true, loadError: null });
    try {
      const state = get();
      const targetPart = part !== undefined ? part : state.selectedPart;
      const targetTest =
        testIdentifier !== undefined
          ? testIdentifier
          : state.selectedTestId || state.selectedTest || undefined;
      const partFilter = targetPart === 'all' ? undefined : targetPart;

      const [examResult, progress] = await Promise.all([
        ToeicDataService.getExamData(partFilter, targetTest),
        ToeicDataService.getUserProgress(),
      ]);

      const resolvedId = examResult.exam?.id || state.selectedTestId || targetTest || '';
      const resolvedName = examResult.exam?.name || state.selectedTest || targetTest || '';
      const savedAnswers = resolvedId ? progress.answersByTest[resolvedId] || {} : {};

      set({
        groups: examResult.groups,
        questions: examResult.questions,
        selectedTestId: resolvedId,
        selectedTest: resolvedName,
        answersByTest: progress.answersByTest || {},
        studyDates: progress.studyDates || [],
        userAnswers: savedAnswers,
        isLoading: false,
        loadError: examResult.error || null,
        currentQuestionIndex: 0,
        pacerSeconds: 0,
        whDrillSelection: null,
      });
    } catch (err) {
      console.error('Failed to load exam data:', err);
      set({
        isLoading: false,
        loadError: 'Không thể tải dữ liệu đề thi từ máy chủ cục bộ.',
      });
    }
  },

  selectAnswer: async (questionId: string, answer: QuestionOptionKey) => {
    const { questions, userAnswers, answersByTest, selectedTestId, selectedTest } = get();
    if (userAnswers[questionId]) {
      return;
    }

    const updatedAnswers = { ...userAnswers, [questionId]: answer };
    const testKey = selectedTestId || selectedTest || 'default';
    const updatedByTest = {
      ...answersByTest,
      [testKey]: updatedAnswers,
    };

    set({
      userAnswers: updatedAnswers,
      answersByTest: updatedByTest,
    });

    // Persist answer & study date on local server in background
    ToeicDataService.saveAnswerProgress(testKey, selectedTest || testKey, questionId, answer)
      .then((progress) => {
        if (progress?.studyDates) {
          set({ studyDates: progress.studyDates });
        }
      })
      .catch((err) => {
        console.warn('Background save progress failed:', err);
      });

    const currentQ = questions.find((q) => q.id === questionId);
    if (currentQ && answer !== currentQ.correct_answer) {
      ToeicDataService.recordMistake(questionId, answer).catch((err) => {
        console.warn('Background record mistake failed:', err);
      });
    }
  },

  goToQuestion: (index: number) => {
    const { questions } = get();
    if (index >= 0 && index < questions.length) {
      set({ currentQuestionIndex: index, pacerSeconds: 0, whDrillSelection: null });
    }
  },

  nextQuestion: () => {
    const { currentQuestionIndex, questions } = get();
    if (currentQuestionIndex < questions.length - 1) {
      set({ currentQuestionIndex: currentQuestionIndex + 1, pacerSeconds: 0, whDrillSelection: null });
    }
  },

  prevQuestion: () => {
    const { currentQuestionIndex } = get();
    if (currentQuestionIndex > 0) {
      set({ currentQuestionIndex: currentQuestionIndex - 1, pacerSeconds: 0, whDrillSelection: null });
    }
  },

  setMode: (mode: ExamMode) => {
    set({ mode });
  },

  resetProgress: async () => {
    const { selectedTestId, selectedTest, answersByTest } = get();
    const testKey = selectedTestId || selectedTest;
    const nextByTest = { ...answersByTest };
    if (testKey) {
      delete nextByTest[testKey];
    }

    set({
      userAnswers: {},
      answersByTest: nextByTest,
      currentQuestionIndex: 0,
      mode: 'practice',
      pacerSeconds: 0,
      whDrillSelection: null,
    });

    if (testKey) {
      await ToeicDataService.resetTestProgress(testKey);
    }
  },

  setPacerSeconds: (seconds: number) => {
    set({ pacerSeconds: seconds });
  },

  resetPacer: () => {
    set({ pacerSeconds: 0 });
  },

  setWhDrillSelection: (type: string | null) => {
    set({ whDrillSelection: type });
  },

  toggleHidePart2Text: () => {
    set((state) => ({ hidePart2Text: !state.hidePart2Text }));
  },

  setAudioPlaying: (isPlaying: boolean) => {
    set((state) => ({
      audioState: { ...state.audioState, isPlaying },
    }));
  },

  setAudioCurrentTime: (currentTime: number) => {
    const { groups, currentQuestionIndex, questions } = get();
    const currentQ = questions[currentQuestionIndex];
    const group = currentQ ? groups.find((g) => g.id === currentQ.group_id) : null;

    let activeSegmentId: string | number | null = null;
    if (group?.transcript_segments) {
      const match = group.transcript_segments.find(
        (seg) => currentTime >= seg.start_time && currentTime <= seg.end_time
      );
      if (match) activeSegmentId = match.id;
    }

    set((state) => ({
      audioState: { ...state.audioState, currentTime, activeSegmentId },
    }));
  },

  setAudioDuration: (duration: number) => {
    set((state) => ({
      audioState: { ...state.audioState, duration },
    }));
  },

  setPlaybackSpeed: (playbackSpeed: number) => {
    set((state) => ({
      audioState: { ...state.audioState, playbackSpeed },
    }));
  },

  setActiveSegment: (activeSegmentId: string | number | null) => {
    set((state) => ({
      audioState: { ...state.audioState, activeSegmentId },
    }));
  },

  jumpToSegment: (segment: TranscriptSegment) => {
    set((state) => ({
      audioState: {
        ...state.audioState,
        currentTime: segment.start_time,
        activeSegmentId: segment.id,
        isPlaying: true,
      },
    }));
  },
}));
