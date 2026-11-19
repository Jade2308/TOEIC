import { create } from 'zustand';
import { VocabSRS } from '@/types/toeic';
import { ToeicDataService } from '@/lib/data-service';

export interface VocabStoreState {
  vocabList: VocabSRS[];
  isLoading: boolean;
  loadVocab: () => Promise<void>;
  addWord: (
    word: string,
    meaningVi: string,
    contextSentence: string,
    partOfSpeech?: string,
    phonetic?: string
  ) => Promise<VocabSRS>;
  rateCard: (vocabId: string, quality: number) => Promise<void>;
}

export const useVocabStore = create<VocabStoreState>((set, get) => ({
  vocabList: [],
  isLoading: false,

  loadVocab: async () => {
    set({ isLoading: true });
    try {
      const data = await ToeicDataService.getVocabSRS();
      set({ vocabList: data, isLoading: false });
    } catch (err) {
      console.error('Failed to load vocab:', err);
      set({ isLoading: false });
    }
  },

  addWord: async (word, meaningVi, contextSentence, partOfSpeech = 'vocabulary', phonetic) => {
    const newWord = await ToeicDataService.saveWordToSRS(
      word,
      meaningVi,
      contextSentence,
      partOfSpeech,
      phonetic
    );
    await get().loadVocab();
    return newWord;
  },

  rateCard: async (vocabId: string, quality: number) => {
    await ToeicDataService.reviewVocabItem(vocabId, quality);
    await get().loadVocab();
  },
}));
