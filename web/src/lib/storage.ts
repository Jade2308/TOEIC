// ==============================================================================
// Lightweight Browser LocalStorage Emergency Cache
// Server filesystem (data/user/*.json) is the authoritative source of truth.
// LocalStorage is only used as a read-through cache when offline/restarting.
// ==============================================================================

import { UserMistake, UserProgressData, VocabSRS } from '@/types/toeic';

const STORAGE_KEYS = {
  MISTAKES: 'toeic_local_mistakes_v2',
  VOCAB: 'toeic_local_vocab_v2',
  PROGRESS: 'toeic_local_progress_v2',
};

export const safeLocalStorage = {
  getItem<T>(key: string, defaultValue: T): T {
    if (typeof window === 'undefined') {
      return defaultValue;
    }
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  },

  setItem<T>(key: string, value: T): void {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn(`Error writing to localStorage key "${key}":`, error);
    }
  },

  removeItem(key: string): void {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  },
};

export const getCachedMistakes = (): UserMistake[] =>
  safeLocalStorage.getItem<UserMistake[]>(STORAGE_KEYS.MISTAKES, []);

export const setCachedMistakes = (mistakes: UserMistake[]): void =>
  safeLocalStorage.setItem(STORAGE_KEYS.MISTAKES, mistakes);

export const getCachedVocab = (): VocabSRS[] =>
  safeLocalStorage.getItem<VocabSRS[]>(STORAGE_KEYS.VOCAB, []);

export const setCachedVocab = (vocabList: VocabSRS[]): void =>
  safeLocalStorage.setItem(STORAGE_KEYS.VOCAB, vocabList);

export const getCachedProgress = (): UserProgressData | null =>
  safeLocalStorage.getItem<UserProgressData | null>(STORAGE_KEYS.PROGRESS, null);

export const setCachedProgress = (progress: UserProgressData): void =>
  safeLocalStorage.setItem(STORAGE_KEYS.PROGRESS, progress);
