from typing import List, Optional
from pydantic import BaseModel, Field


class ParaphrasePairSchema(BaseModel):
    original: str = Field(description="Exact phrase or expression from the passage or listening script")
    paraphrased: str = Field(description="Equivalent synonym or paraphrased phrase in the correct answer choice")


class OptionsSchema(BaseModel):
    A: str = Field(description="Option A text")
    B: str = Field(description="Option B text")
    C: str = Field(description="Option C text")
    D: Optional[str] = Field(default=None, description="Option D text (null/omitted for Part 2)")


class QuestionSchema(BaseModel):
    question_number: int = Field(description="Question number in the test (1 to 200)")
    part: int = Field(description="TOEIC Part number (1 to 7)")
    question_type_tag: str = Field(
        description=(
            "Standard coaching tag: word_form, conjunction, verb_tense, preposition, "
            "vocabulary, wh_where, wh_when, homophone_trap, passive_being_trap, "
            "indirect_response, inference, detail_lookup, graphic, instruction_action"
        )
    )
    question_text: Optional[str] = Field(
        default=None,
        description="The question prompt"
    )
    options: OptionsSchema = Field(description="Options object containing choices A, B, C, and D")
    correct_answer: str = Field(description="Single capital letter corresponding to correct choice: 'A', 'B', 'C', or 'D'")
    explanation_vi: str = Field(
        description=(
            "Comprehensive Vietnamese pedagogical explanation: grammar/vocab rule, "
            "why correct answer is right, ETS distractor trap breakdown, and coaching tactic tip"
        )
    )
    evidence_quote: Optional[str] = Field(
        default=None,
        description="Exact substring from passage or transcript that proves the correct answer"
    )
    paraphrase_pair: Optional[ParaphrasePairSchema] = Field(
        default=None,
        description="Pair of original wording vs paraphrased wording in correct answer"
    )


class QuestionGroupSchema(BaseModel):
    part: int = Field(description="TOEIC Part number (1 to 7)")
    passage_text: Optional[str] = Field(
        default=None,
        description="Full reading passage text in clean Markdown or HTML for Part 6 and 7; null for Part 1-5"
    )
    audio_script: Optional[str] = Field(
        default=None,
        description="Transcript of the audio dialogue or short talk if provided in the key"
    )
    questions: List[QuestionSchema] = Field(description="List of questions linked to this context")


class ToeicExtractionPayload(BaseModel):
    test_name: str = Field(description="Name of the test, e.g. 'ETS TOEIC 2023 - Test 2'")
    groups: List[QuestionGroupSchema] = Field(description="Extracted question groups with linked questions")
