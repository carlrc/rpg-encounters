import logging
from typing import Dict, List

from pydantic import BaseModel, Field
from pydantic_ai import UnexpectedModelBehavior

from app.agents.base_agent import BaseAgent
from app.db.limits import CHARACTER_COMMUNICATION_LIMIT
from app.models.character import CommunicationStyle

logger = logging.getLogger(__name__)


class CommunicationStyleAgentOutput(BaseModel):
    examples: List[str] = Field(
        ...,
        description="Examples of the characters communication style",
    )
    style_summary: str = Field(
        ...,
        description="Summary of the characters communication style",
    )


class CommunicationStylePresetProfile(BaseModel):
    style: CommunicationStyle = Field(..., description="The communication style preset")
    style_summary: str = Field(..., description="The style preset summary")
    examples: List[str] = Field(..., description="Style preset examples")


COMMUNICATION_STYLE_PROFILES: Dict[str, CommunicationStylePresetProfile] = {
    CommunicationStyle.NERDY.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.NERDY.value,
        style_summary="Speaks with intellectual enthusiasm, references facts, and uses precise or technical wording. Every reply should include a fact.",
        examples=[
            "Actually, the probability of that happening is only 3.14 percent.",
            "That’s interesting; it aligns with a theory I read about yesterday.",
            "Let me double-check the exact calculation before we continue.",
        ],
    ),
    CommunicationStyle.THEATRICAL.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.THEATRICAL.value,
        style_summary="Speaks with drama and flair, exaggerating tone as if performing for an audience. Every reply is dramatic.",
        examples=[
            "Behold! A revelation unlike any other!",
            "This moment shall be remembered forever.",
            "Step closer, the spotlight is on us now!",
        ],
    ),
    CommunicationStyle.JOKING.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.JOKING.value,
        style_summary="Constantly makes puns, jokes, and sarcastic remarks; rarely serious. Every reply is a joke.",
        examples=[
            "I would help, but I left my bravery in my other jacket.",
            "Guess I’ll just wing it—like a bird.",
            "Relax, I always fall on my face with style.",
        ],
    ),
    CommunicationStyle.PARANOID.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.PARANOID.value,
        style_summary="Nervous, suspicious, always scanning for threats or hidden motives. Every reply should illustrate suspicion.",
        examples=[
            "Did you hear that? Someone’s definitely listening.",
            "I don’t trust this; it feels like a setup.",
            "Everything looks normal, which makes it even scarier.",
        ],
    ),
    CommunicationStyle.PROFANE.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.PROFANE.value,
        style_summary="Blunt, vulgar, and unfiltered; swears (.e.g, fuck off, fuck you) freely and speaks without restraint. Every reply uses harsh language.",
        examples=[
            "That’s a terrible fucking idea, but let’s roll with it.",
            "Move your ass before we waste more time.",
            "Well, shit, nothing ever goes smooth.",
        ],
    ),
    CommunicationStyle.FLIRTATIOUS.value: CommunicationStylePresetProfile(
        style=CommunicationStyle.FLIRTATIOUS.value,
        style_summary="Playful, charming, often teases or flatters in a lighthearted way. Every reply is a flirt.",
        examples=[
            "Careful, keep talking like that and I might start blushing.",
            "You must practice, because nobody stumbles into being that smooth.",
            "Are you always this charming, or am I just lucky today?",
        ],
    ),
}


class CommunicationStyleAgent(BaseAgent):
    def __init__(self, system_prompt: str):
        super().__init__()

        agent = self._generate_agent(
            system_prompt=system_prompt, output_type=CommunicationStyleAgentOutput
        )

        @agent.output_validator
        async def trim_length(
            _, output: CommunicationStyleAgentOutput
        ) -> CommunicationStyleAgentOutput:
            """Trim communication style to character limit if needed"""
            length = len(output.style_summary)
            if length > CHARACTER_COMMUNICATION_LIMIT:
                logger.warning(
                    f"Communication style truncated from {length} to {CHARACTER_COMMUNICATION_LIMIT} characters"
                )
                output.style_summary = output.style_summary[
                    :CHARACTER_COMMUNICATION_LIMIT
                ].rstrip()
            return output

        # Set after decorators
        self.agent = agent

    async def generate(self) -> CommunicationStyleAgentOutput:
        try:
            run_result = await self.agent.run(
                "Generate a communication style summary for this character."
            )

            return run_result.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
