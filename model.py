from dataclasses import dataclass


@dataclass
class Line:
    file_number: int
    line_number: int
    original_text: str
    canonical_text: str


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int