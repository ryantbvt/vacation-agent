'''
Intent Skill Module

This module is responsible for determining the intent of a user's message.
'''

from python_utils.logging.logging import init_logger
from app.schemas.config import AgentConfig

from app.paths import SERVICE_CONFIG_PATH

config = AgentConfig.from_yaml(SERVICE_CONFIG_PATH)

# Initialize logger
logger = init_logger()

class IntentSkill:
    def __init__(self):
        logger.info(f"Initialize intent skill module")
        
        # Simple keyword classification
        self.kb_indicators = config.intent_skills.kb_indicators
        self.kb_patterns = config.intent_skills.kb_patterns
        self.realtime_indicators = config.intent_skills.realtime_indicators
        self.realtime_patterns = config.intent_skills.realtime_patterns
        self.question_words = config.intent_skills.question_words
        self.command_patterns = config.intent_skills.command_patterns
        self.thresholds = config.intent_skills.thresholds
        self.scoring_weights = config.intent_skills.scoring_weights

    def classify_intent(self, user_query: str):
        '''
        Description: Classify the intent of the user's query

        Args:
            user_query (str): The user's query

        Returns:
            intent (str): The classified intent ("kb", "realtime", or "general")
        '''
        logger.info(f"Classifying intent for query: '{user_query}'")
        
        # Step 1: Score KB and realtime indicators
        kb_score = self._score_kb_indicators(user_query)
        realtime_score = self._score_realtime_indicators(user_query)
        
        # Step 2: Return winning intent
        intent = self._determine_winning_intent(kb_score, realtime_score)
        
        logger.info(f"Intent classification result: {intent} (KB: {kb_score}, Realtime: {realtime_score})")
        
        return intent
        

    def _score_kb_indicators(self, user_query: str) -> int:
        '''
        Description: Score the KB indicators. Indicators includes:
        - Camping
        - Reservations
        - Dinner plans
        - Itinerary

        Args:
            user_query (str): The user's query

        Returns:
            kb_score (int): The score of the KB indicators
        '''
        
        # convert query to lowercase
        user_query = user_query.lower()

        # Start scoring
        kb_score = 0.0

        # Score query against direct indicators + patterns
        for indicator in self.kb_indicators:
            if indicator in user_query:
                kb_score += 1.0

        for pattern_word, pattern_value in self.kb_patterns.items():
            if pattern_word in user_query:
                kb_score += pattern_value

        for question_word in self.question_words:
            if question_word in user_query:
                kb_score += 0.25

        # Short query bonus - shorter queries often need KB info
        query_length = len(user_query.split())
        if query_length <= 3:
            kb_score += 0.5

        # Cross-penalty: penalize when realtime indicators appear
        for realtime_indicator in self.realtime_indicators:
            if realtime_indicator in user_query:
                kb_score -= 0.5

        # Ensure non-negative score
        kb_score = max(0.0, kb_score)

        return kb_score     
        

    def _score_realtime_indicators(self, user_query: str) -> int:
        '''
        Description: Score the realtime indicators. Indicators includes:
        - Time Sensitivity
        - Status
        - Weather
        - Traffic
        - Live data

        Args:
            user_query (str): The user's query

        Returns:
            realtime_score (int): The score of the realtime indicators
        '''
        
        # convert query to lowercase
        user_query = user_query.lower()

        # Start scoring
        realtime_score = 0.0

        # Score query against direct indicators
        for indicator in self.realtime_indicators:
            if indicator in user_query:
                realtime_score += 1.0

        # Score query against realtime patterns
        for pattern_word, pattern_value in self.realtime_patterns.items():
            if pattern_word in user_query:
                realtime_score += pattern_value

        # Command pattern bonus - commands often need realtime data
        for command_pattern in self.command_patterns:
            if command_pattern in user_query:
                realtime_score += 0.5

        # Very short query bonus - very short queries might be status checks
        query_length = len(user_query.split())
        if query_length <= 2:
            realtime_score += 0.5

        # Cross-penalty: penalize when KB indicators appear
        for kb_indicator in self.kb_indicators:
            if kb_indicator in user_query:
                realtime_score -= 0.5

        # Ensure non-negative score
        realtime_score = max(0.0, realtime_score)

        return realtime_score

    def _determine_winning_intent(self, kb_score: int, realtime_score: int) -> str:
        '''
        Description: Determine the winning intent based on the scores of the KB and realtime indicators.
        Winning intent can be KB, realtime, or general questions.

        Winning score will do the following:
        If KB score wins, then we will route the query to RAG skill to access the KB.
        If realtime score wins, we we route query to LLM + web search.
        If general wins, we will route query to LLM with no web search.

        Args:
            kb_score (int): The score of the KB indicators
            realtime_score (int): The score of the realtime indicators

        Returns:
            winning_intent (str): The winning intent
        '''
        
        # Get thresholds from config
        kb_threshold = self.thresholds.kb_threshold
        realtime_threshold = self.thresholds.realtime_threshold
        
        # Rule 1: Realtime wins if it's higher and meets threshold
        if realtime_score > kb_score and realtime_score >= realtime_threshold:
            return "realtime"
        
        # Rule 2: KB wins if it's higher and meets threshold
        if kb_score > realtime_score and kb_score >= kb_threshold:
            return "kb"
        
        # Rule 3: If scores are equal and both meet thresholds, prefer realtime (more urgent)
        if kb_score == realtime_score and kb_score >= kb_threshold and realtime_score >= realtime_threshold:
            return "realtime"
        
        # Rule 4: If one meets threshold and the other doesn't, choose the one that meets threshold
        if kb_score >= kb_threshold and realtime_score < realtime_threshold:
            return "kb"
        if realtime_score >= realtime_threshold and kb_score < kb_threshold:
            return "realtime"
        
        # Rule 5: Fallback to general if neither meets threshold
        return "general"