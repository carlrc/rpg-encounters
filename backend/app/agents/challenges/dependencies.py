from pydantic import BaseModel


class ChallengeAgentDeps(BaseModel):
    encounter_description: str
