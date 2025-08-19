from typing import List

from app.models.memory import Memory
from app.models.player import Player
from app.models.reveal import Reveal, RevealLayer


def structure_reveals(reveals: List[Reveal]):
    if not reveals:
        return """**IMPORTANT**: No reveals available for this character. Refer to memories and character background."""

    instruction_parts = []
    instruction_parts.append("\n# Available Reveals")
    instruction_parts.append(
        "**IMPORTANT**: Select the reveal which is most relevant to the players message."
    )

    for reveal in reveals:
        instruction_parts.append(
            f"""
            \n## ID {reveal.id} - {reveal.title}
            **{RevealLayer.STANDARD.name}:** {reveal.level_1_content}
            **{RevealLayer.PRIVILEGED.name}:** {reveal.level_2_content or 'NONE'}
            **{RevealLayer.EXCLUSIVE.name}:** {reveal.level_3_content or 'NONE'}
            """
        )

    return "".join(instruction_parts)


def structure_filtered_reveal_content(reveals: List[str]):
    reveal_context = """# Reveals
    The following information should be used in your response.
    """

    if reveals:
        for reveal in reveals:
            reveal_context += f"""
        - {reveal}
        """

    return reveal_context


def structure_encounter(encounter_description: str):
    if encounter_description:
        return f"""# Physical Location Context
            Your character is currently in the following encounter. Use this information as your physical world context.
            {encounter_description}
            """
    else:
        return ""


def structure_character_memories(memories: List[Memory], player: Player):
    """Build base instruction with world context and player information."""
    base_instruction = """
        # World Context
        The following are memories that shape your understanding of the world:
        """

    if memories:
        for memory in memories:
            base_instruction += f"""
        - {memory.content}
        """

    base_instruction += f"""
        # Current Interaction Context
        You are speaking with a {player.race}, {player.gender}, {player.class_name} who looks like {player.appearance}."""

    return base_instruction
