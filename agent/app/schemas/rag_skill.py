''' RAG Skill Schema '''

from pydantic import BaseModel

class RagSkillConfig(BaseModel):
    model: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float