# PROJECT SPECIFICATION: TOEIC L&R Adaptive Coaching Web App

## 1. Project Overview
A responsive, mobile-first and desktop-optimized Web Application for TOEIC Listening & Reading (L&R) preparation (Target score: 650 to 800+). Unlike standard quiz apps, this app integrates real-exam strategies, trap identification, audio segmentation, and Spaced Repetition (SRS) directly into the practice interface.

## 2. Tech Stack
- **Framework:** Next.js 14+ (App Router), TypeScript
- **Styling & UI:** Tailwind CSS, shadcn/ui, Lucide React icons, Framer Motion (for smooth mobile drawers)
- **Backend / Database:** 100% Local Filesystem JSON Storage (`data/exams` for dynamic exam discovery, `data/media` for Nginx-served MP3/images, `data/user` for atomic `mistakes.json`, `vocab_srs.json`, and `progress.json`)
- **State Management:** Zustand (for exam session, audio player state, and timer)
- **Data Processing (Local Scripts):** Python 3.10+, Faster-Whisper / Pydub (Audio timestamps), Google GenAI SDK (PDF to JSON extraction)

## 3. Database Schema & JSON Data Structure

### Table 1: `question_groups` (Used for shared context in Parts 1, 2, 3, 4, 6, 7)
- `id`: UUID (Primary Key)
- `test_name`: TEXT (e.g., "ETS 2024 - Test 1")
- `part`: INT (1 to 7)
- `passage_text`: TEXT (Nullable - HTML/Markdown for Part 6, 7 reading passages)
- `image_url`: TEXT (Nullable - Part 1 photos, Part 3/4/7 graphics)
- `audio_url`: TEXT (Nullable - Part 1, 2, 3, 4 MP3 link)
- `transcript_segments`: JSONB (Array of `{ id, speaker, start_time, end_time, text_en, text_vi, is_trap }`)

### Table 2: `questions` (Individual questions)
- `id`: UUID (Primary Key)
- `group_id`: UUID (Foreign Key -> `question_groups.id`)
- `part`: INT (1 to 7)
- `question_number`: INT (1 to 200)
- `question_type_tag`: TEXT (e.g., `word_form`, `verb_tense`, `preposition`, `wh_where`, `wh_when`, `yes_no`, `inference`, `graphic`, `passive_being_trap`, `homophone_trap`)
- `question_text`: TEXT (Nullable for Part 1 & 2 during listening)
- `options`: JSONB (`{ "A": "...", "B": "...", "C": "...", "D": "..." }` - Note: Part 2 only has A, B, C)
- `correct_answer`: CHAR(1) ('A', 'B', 'C', or 'D')
- `explanation_vi`: TEXT (Detailed Vietnamese explanation + strategy tip)
- `evidence_quote`: TEXT (Exact substring in `passage_text` or `transcript_segments` that proves the correct answer, used for auto-highlighting)
- `paraphrase_pair`: JSONB (`{ "original": "...", "paraphrased": "..." }`)

### Table 3: `user_mistakes` (Error Log)
- `id`: UUID (Primary Key)
- `question_id`: UUID (Foreign Key -> `questions.id`)
- `selected_wrong_answer`: CHAR(1)
- `wrong_count`: INT (Default 1)
- `next_review_date`: TIMESTAMP
- `resolved`: BOOLEAN (Default false)

### Table 4: `vocab_srs` (Spaced Repetition Vocabulary)
- `id`: UUID (Primary Key)
- `word`: TEXT
- `phonetic`: TEXT
- `meaning_vi`: TEXT
- `context_sentence`: TEXT (Captured from the TOEIC question where user highlighted it)
- `part_of_speech`: TEXT
- `interval`: INT (Days until next review - SM-2 algorithm)
- `repetition`: INT (Count of successful recalls)
- `ease_factor`: FLOAT (Default 2.5)
- `due_date`: TIMESTAMP

## 4. Responsive UI/UX Architecture (CRITICAL)
1. **Single-Card Layout (Parts 1, 2, 5):**
   - Centered card interface.
   - Desktop: Keyboard shortcuts (`1, 2, 3, 4` or `A, B, C, D` to select answer, `Space` to play/pause audio, `Enter` for next question).
   - Mobile: Large thumb-friendly option buttons at the bottom half of the screen.
2. **Adaptive Split-View Layout (Parts 3, 4, 6, 7):**
   - **Desktop (`>= 768px`):** 2-column split screen (`grid-cols-12`). Left column (7 cols, independent scroll) shows Reading Passage / Graphic / Transcript. Right column (5 cols, independent scroll) shows the 3-5 linked questions.
   - **Mobile (`< 768px`):** Top 55% of viewport displays the Reading Passage / Graphic (scrollable). Bottom 45% is a fixed/draggable **Bottom Sheet / Drawer** with horizontal swipe or tab buttons (`Q1 | Q2 | Q3`) so the user NEVER has to scroll up and down the whole page to read and answer.
3. **Sticky Smart Audio Player:**
   - Docked at the bottom (or top of question panel).
   - Features: Play/Pause, `-5s` / `+5s` rewind, Playback speed (`0.8x, 1.0x, 1.1x, 1.25x`), and **Interactive Transcript Sync** (clicking any transcript line jumps `audio.currentTime` to `segment.start_time`).

## 5. Part-Specific Coaching Mechanics
- **Part 1 (Photos):** Before playing audio, show a "Quick Predict" prompt (user mentally notes Verbs & Nouns). In Review mode, highlight `being` passive traps in red.
- **Part 2 (Question-Response):**
  - *Mode A (Standard):* Hide question text & option texts. Only show `A, B, C` buttons.
  - *Mode B (WH-Catcher Drill):* After the question audio plays, pause audio and ask user to tap the heard question type (`Where`, `When`, `Who`, `Why`, `How`, `Statement/Yes-No`) before unlocking A, B, C options.
  - *Mode C (Micro-Dictation):* Input box for user to type the exact sentence heard; diff-check and highlight missed words.
- **Part 3 & 4 (Conversations & Talks):**
  - Include an **8-second Pre-Read Countdown timer** before the audio auto-plays, training the user to scan the 3 questions first.
  - In Review mode, display the `paraphrase_pair` badge (e.g., Audio: *"out of stock"* == Answer: *"unavailable"*).
- **Part 5 (Incomplete Sentences):**
  - **20-Second Pacer:** Visual countdown bar per question (turns yellow at 15s, red at 20s).
  - **Strategy Hint Banner:** Remind user to look at the 4 options first to classify (`[Word Form - 10s]` vs `[Vocabulary - 25s]`).
- **Part 6 & 7 (Reading Comprehension):**
  - **Evidence Auto-Highlighter:** In Review mode, clicking "Show Evidence" on Question X automatically scrolls the left/top passage to `evidence_quote` and highlights it in yellow (`<mark>`).
  - **Text Selection to SRS:** Selecting any word/phrase in the passage or transcript opens a floating popover with a `"+ Save to SRS Vocab"` button.