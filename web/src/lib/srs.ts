// ==============================================================================
// SuperMemo SM-2 Spaced Repetition Algorithm Implementation
// Reference: SPECIFICATION.md Table 4 (vocab_srs)
// ==============================================================================

export interface SM2Result {
  interval: number;    // Days until next review
  repetition: number;  // Count of consecutive successful recalls
  ease_factor: number; // Ease multiplier (minimum 1.3)
  due_date: string;    // Next review timestamp ISO string
}

/**
 * Calculates new SM-2 parameters based on recall quality.
 * @param quality Recall grade:
 *   5 - Perfect recall with no hesitation
 *   4 - Correct response after a hesitation
 *   3 - Correct response with serious difficulty
 *   2 - Incorrect response, but remembered after seeing answer
 *   1 - Incorrect response, familiar word
 *   0 - Complete blackout
 * @param prevRepetition Current consecutive repetition count
 * @param prevInterval Current interval in days
 * @param prevEaseFactor Current ease factor (default 2.5)
 */
export function calculateSM2(
  quality: number,
  prevRepetition: number = 0,
  prevInterval: number = 1,
  prevEaseFactor: number = 2.5
): SM2Result {
  let repetition = prevRepetition;
  let interval = prevInterval;
  let easeFactor = prevEaseFactor;

  // Grade must be clamped between 0 and 5
  const q = Math.max(0, Math.min(5, Math.round(quality)));

  if (q >= 3) {
    // Successful recall
    if (repetition === 0) {
      interval = 1;
    } else if (repetition === 1) {
      interval = 6;
    } else {
      interval = Math.round(prevInterval * easeFactor);
    }
    repetition += 1;
  } else {
    // Failed recall (reset interval and repetitions)
    repetition = 0;
    interval = 1;
  }

  // Calculate new Ease Factor (EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
  easeFactor = easeFactor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
  if (easeFactor < 1.3) {
    easeFactor = 1.3;
  }

  // Calculate new due date
  const now = new Date();
  const due = new Date(now.getTime() + interval * 24 * 60 * 60 * 1000);

  return {
    interval,
    repetition,
    ease_factor: Number(easeFactor.toFixed(2)),
    due_date: due.toISOString(),
  };
}
