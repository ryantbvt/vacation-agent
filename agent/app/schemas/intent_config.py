''' Intent Skill Schema '''

from pydantic import BaseModel
from typing import List, Dict

class Thresholds(BaseModel):
    kb_threshold: float
    realtime_threshold: float

class ScoringWeights(BaseModel):
    exact_match_bonus: int
    phrase_bonus: int
    question_bonus: int
    command_bonus: int
    short_query_bonus: int
    cross_penalty: int

class IntentSkill(BaseModel):
    kb_indicators: List[str]
    realtime_indicators: List[str]
    kb_patterns: Dict[str, int]
    realtime_patterns: Dict[str, int]
    question_words: List[str]
    command_patterns: List[str]
    thresholds: Thresholds
    scoring_weights: ScoringWeights