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
        description="Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness)."
    )
    hate: bool = Field(
        description="Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste."
    )
    harassment: bool = Field(
        description="Content that expresses, incites, or promotes harassing language towards any target."
    )
    violence: bool = Field(
        description="Content that depicts death, violence, or physical injury."
    )
    self_harm: bool = Field(
        alias=SELF_HARM,
        description="Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
    )
    sexual_minors: bool = Field(
        alias=SEXUAL_MINORS,
        description="Sexual content that includes an individual who is under 18 years old.",
    )
    hate_threatening: bool = Field(
        alias=HATE_THREATENING,
        description="Hateful content that also includes violence or serious harm towards the targeted group based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
    )
    violence_graphic: bool = Field(
        alias=VIOLENCE_GRAPHIC,
        description="Content that depicts death, violence, or physical injury in graphic detail.",
    )
    self_harm_intent: bool = Field(
        alias=SELF_HARM_INTENT,
        description="Content where the speaker expresses that they are engaging or intend to engage in acts of self-harm, such as suicide, cutting, and eating disorders.",
    )
    self_harm_instructions: bool = Field(
        alias=SELF_HARM_INSTRUCTIONS,
        description="Content that encourages performing acts of self-harm, such as suicide, cutting, and eating disorders, or that gives instructions or advice on how to commit such acts.",
    )
    harassment_threatening: bool = Field(
        alias=HARASSMENT_THREATENING,
        description="Harassment content that also includes violence or serious harm towards any target.",
    )
    illicit: bool = Field(
        default=False,
        description="Content that gives advice or instruction on how to commit illicit acts. A phrase like 'how to shoplift' would fit this category.",
    )
    illicit_violent: bool = Field(
        default=False,
        alias=ILLICIT_VIOLENT,
        description="The same types of content flagged by the illicit category, but also includes references to violence or procuring a weapon.",
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


def openai_flag(categories: Categories) -> bool:
    is_illegal = (
        categories.sexual_minors
        or categories.self_harm
        or categories.self_harm_instructions
        or categories.hate_threatening
        or categories.self_harm_intent
    )

    is_sexually_violent = (
        categories.violence and categories.harassment and categories.sexual
    )

    return is_illegal or is_sexually_violent


def openai_scores(scores: CategoryScores, breach_threshold: float) -> bool:
    # Enforce lower threshold than OpenAI flags
    def breach(score: float) -> bool:
        return score > breach_threshold

    should_block = breach(scores.violence) and (
        breach(scores.hate)
        or breach(scores.harassment_threatening)
        or breach(scores.self_harm)
        or breach(scores.self_harm_intent)
        or breach(scores.self_harm_instructions)
    )

    return should_block


def openai_scores_minors(score: float) -> bool:
    # Enforce extremely low threshold on this category in case OpenAI flags don't
    return score > 0.1


class OpenAIModerationClient:
    """Client for OpenAI's content moderation API"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.base_url = "https://api.openai.com/v1"

    @observe()
    async def check(self, text: str) -> ModerationResponse:
        """Check text for NSFW/harmful content using OpenAI's moderation API"""
        url = f"{self.base_url}/moderations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"input": text}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=payload, timeout=5.0
                )
                response.raise_for_status()

                return ModerationResponse(**response.json())
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI Moderation HTTP {e.response.status_code} error: {e}")
            raise
        except httpx.ConnectTimeout as e:
            logger.error(
                f"OpenAI Moderation connection timeout: Failed to connect to {url}. Error: {e}"
            )
            raise
        except httpx.TimeoutException as e:
            logger.error(f"OpenAI Moderation request timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI Moderation check failed: {type(e).__name__}: {e}")
            raise
