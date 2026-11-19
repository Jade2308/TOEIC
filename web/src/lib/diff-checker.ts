// Word-by-word diff checker for TOEIC Part 2 Micro-Dictation Drill

export interface DiffWordResult {
  expectedWord: string;
  userWord?: string;
  status: 'correct' | 'missing' | 'incorrect';
}

export interface DictationDiffResult {
  tokens: DiffWordResult[];
  accuracy: number; // 0 to 100%
  totalWords: number;
  correctWords: number;
}

export function checkDictation(userText: string, expectedText: string): DictationDiffResult {
  const clean = (str: string) =>
    str
      .toLowerCase()
      .replace(/[.,/#!$%^&*;:{}=\-_`~()?'""]/g, '')
      .replace(/\s+/g, ' ')
      .trim();

  const expectedWords = clean(expectedText).split(' ').filter(Boolean);
  const userWords = clean(userText).split(' ').filter(Boolean);

  const tokens: DiffWordResult[] = [];
  let correctCount = 0;

  for (let i = 0; i < expectedWords.length; i++) {
    const expected = expectedWords[i];
    const user = userWords[i];

    if (!user) {
      tokens.push({
        expectedWord: expected,
        status: 'missing',
      });
    } else if (user === expected) {
      tokens.push({
        expectedWord: expected,
        userWord: user,
        status: 'correct',
      });
      correctCount++;
    } else {
      // Check if word appears nearby (transposition / small omission)
      const foundNearby = userWords.slice(Math.max(0, i - 1), i + 2).includes(expected);
      if (foundNearby) {
        tokens.push({
          expectedWord: expected,
          userWord: user,
          status: 'correct',
        });
        correctCount++;
      } else {
        tokens.push({
          expectedWord: expected,
          userWord: user,
          status: 'incorrect',
        });
      }
    }
  }

  const accuracy = expectedWords.length > 0
    ? Math.round((correctCount / expectedWords.length) * 100)
    : 0;

  return {
    tokens,
    accuracy,
    totalWords: expectedWords.length,
    correctWords: correctCount,
  };
}
