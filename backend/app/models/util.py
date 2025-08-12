from typing import List


def validate_character_count(text: str, max_characters: int, field_name: str) -> str:
    """Validate character count for text fields."""
    if text:
        character_count = len(text)
        if character_count > max_characters:
            raise ValueError(
                f"{field_name} must be {max_characters} characters or less"
            )
    return text


def validate_choice(value: str, valid_choices: List[str], field_name: str) -> str:
    """Validate that a value is in the list of valid choices."""
    if value not in valid_choices:
        raise ValueError(f'{field_name} must be one of: {", ".join(valid_choices)}')
    return value
