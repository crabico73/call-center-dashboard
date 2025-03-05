from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AgentPersonality(BaseModel):
    voice_style: str = "natural"  # natural, professional, friendly
    speech_rate: str = "medium"   # slow, medium, fast
    energy_level: str = "high"    # low, medium, high
    conversation_style: Dict[str, Any] = {
        "formal_level": "semi-formal",
        "friendliness": 8,        # Scale of 1-10
        "empathy": 8,            # Scale of 1-10
        "enthusiasm": 7          # Scale of 1-10
    }
    language_preferences: Dict[str, Any] = {
        "use_contractions": True,
        "conversational_fillers": True,
        "active_listening": True
    }

class AIAgentBase(BaseModel):
    name: str
    description: str
    personality: AgentPersonality
    prompt_template: str
    initial_greeting: str
    fallback_responses: List[str]
    closing_statements: List[str]

class AIAgentCreate(AIAgentBase):
    pass

class AIAgent(AIAgentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 