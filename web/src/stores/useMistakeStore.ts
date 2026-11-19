import { create } from 'zustand';
import { UserMistake, QuestionOptionKey } from '@/types/toeic';
import { ToeicDataService } from '@/lib/data-service';

export interface MistakeStoreState {
  mistakes: UserMistake[];
  isLoading: boolean;
  loadMistakes: () => Promise<void>;
  recordMistake: (questionId: string, wrongAnswer: QuestionOptionKey) => Promise<void>;
  resolveMistake: (mistakeId: string) => Promise<void>;
  toggleResolveMistake: (mistakeId: string, resolved?: boolean) => Promise<void>;
}

export const useMistakeStore = create<MistakeStoreState>((set, get) => ({
  mistakes: [],
  isLoading: false,

  loadMistakes: async () => {
    set({ isLoading: true });
    try {
      const data = await ToeicDataService.getMistakes();
      set({ mistakes: data, isLoading: false });
    } catch (err) {
      console.error('Failed to load mistakes:', err);
      set({ isLoading: false });
    }
  },

  recordMistake: async (questionId: string, wrongAnswer: QuestionOptionKey) => {
    await ToeicDataService.recordMistake(questionId, wrongAnswer);
    await get().loadMistakes();
  },

  resolveMistake: async (mistakeId: string) => {
    await ToeicDataService.resolveMistake(mistakeId);
    await get().loadMistakes();
  },

  toggleResolveMistake: async (mistakeId: string, resolved?: boolean) => {
    await ToeicDataService.toggleMistakeResolved(mistakeId, resolved);
    await get().loadMistakes();
  },
}));
