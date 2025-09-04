import logging
import os
from typing import List

import httpx
from langfuse import observe
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Field name aliases for OpenAI's API response format
SELF_HARM = "self-harm"
SEXUAL_MINORS = "sexual/minors"
HATE_THREATENING = "hate/threatening"
VIOLENCE_GRAPHIC = "violence/graphic"
SELF_HARM_INTENT = "self-harm/intent"
SELF_HARM_INSTRUCTIONS = "self-harm/instructions"
HARASSMENT_THREATENING = "harassment/threatening"
ILLICIT_VIOLENT = "illicit/violent"


class Categories(BaseModel):
    """Category flags from moderation API"""

    sexual: bool = Field(
        description="Content meant to arouse sexual excitement or promote sexual services"
    )
    hate: bool = Field(
        description="Content that expresses, incites, or promotes hate based on identity"
    )
    harassment: bool = Field(
        description="Content that harasses or bullies an individual"
    )
    violence: bool = Field(
        description="Content that depicts death, violence, or physical injury"
    )
    self_harm: bool = Field(
        alias=SELF_HARM,
        description="Content that promotes or depicts acts of self-harm",
    )
    sexual_minors: bool = Field(
        alias=SEXUAL_MINORS, description="Sexual content involving individuals under 18"
    )
    hate_threatening: bool = Field(
        alias=HATE_THREATENING,
        description="Hateful content that includes violence or serious harm",
    )
    violence_graphic: bool = Field(
        alias=VIOLENCE_GRAPHIC,
        description="Graphic depictions of death, violence, or injury",
    )
    self_harm_intent: bool = Field(
        alias=SELF_HARM_INTENT,
        description="Content where speaker expresses intent to engage in self-harm",
    )
    self_harm_instructions: bool = Field(
        alias=SELF_HARM_INSTRUCTIONS,
        description="Content that provides instructions for self-harm",
    )
    harassment_threatening: bool = Field(
        alias=HARASSMENT_THREATENING,
        description="Harassment content that includes violence or serious harm",
    )
    illicit: bool = Field(
        default=False, description="Content that promotes or enables illegal activities"
    )
    illicit_violent: bool = Field(
        default=False,
        alias=ILLICIT_VIOLENT,
        description="Illegal violence or weapons-related content",
    )


class CategoryScores(BaseModel):
    """Category scores from moderation API"""

    sexual: float
    hate: float
    harassment: float
    violence: float
    self_harm: float = Field(alias=SELF_HARM)
    sexual_minors: float = Field(alias=SEXUAL_MINORS)
    hate_threatening: float = Field(alias=HATE_THREATENING)
    violence_graphic: float = Field(alias=VIOLENCE_GRAPHIC)
    self_harm_intent: float = Field(alias=SELF_HARM_INTENT)
    self_harm_instructions: float = Field(alias=SELF_HARM_INSTRUCTIONS)
    harassment_threatening: float = Field(alias=HARASSMENT_THREATENING)
    illicit: float = Field(default=0.0)
    illicit_violent: float = Field(default=0.0, alias=ILLICIT_VIOLENT)


class ModerationResult(BaseModel):
    """Individual moderation result matching OpenAI's response structure"""

    flagged: bool
    categories: Categories
    category_scores: CategoryScores


class ModerationResponse(BaseModel):
    """Complete response from OpenAI moderation API"""

    id: str
    model: str
    results: List[ModerationResult]


class ModerationDecision(BaseModel):
    """Decision on whether content should be blocked"""

    should_block: bool
    reasons: List[str]
    triggered_must_block: List[str]
    triggered_should_block: List[str]


def openai_flag(categories: Categories) -> bool:
    must_block = (
        categories.sexual_minors
        | categories.self_harm
        | categories.self_harm_instructions
        | categories.hate_threatening
        | categories.self_harm_intent
    )

    return must_block


class OpenAIModerationClient:
    """Client for OpenAI's content moderation API"""

    # Must block categories - any of these flagged = instant block
    MUST_BLOCK_CATEGORIES = [
        "sexual_minors",
        "self_harm_intent",
        "self_harm_instructions",
        "illicit",
    ]

    # Should block categories - flagged + any one must block = block
    SHOULD_BLOCK_CATEGORIES = [
        "self_harm",
        "harassment_threatening",
        "hate_threatening",
        "illicit_violent",
    ]

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.base_url = "https://api.openai.com/v1"

    @observe(capture_input=False, capture_output=False)
    async def moderate(self, text: str) -> ModerationResponse:
        """Check text for NSFW/harmful content using OpenAI's moderation API"""
        url = f"{self.base_url}/moderations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"input": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=headers, json=payload, timeout=5.0
            )
            response.raise_for_status()

            return ModerationResponse(**response.json())
