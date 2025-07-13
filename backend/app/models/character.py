from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class CharacterBase(BaseModel):
    name: str
    avatar: Optional[str] = Field(None, description="Character avatar image (base64 or URL)")
    race: str = Field(..., description="Character race")
    size: str = Field(..., description="Character size")
    alignment: str = Field(..., description="Character alignment")
    profession: str = Field(..., description="Character profession")
    background: str = Field(..., description="Character background (max 80 words)")
    communication_style: str = Field(..., description="Character communication style (max 30 words)")
    tags: List[str] = Field(default_factory=list, description="Character tags")

    @field_validator('background')
    @classmethod
    def validate_background_word_count(cls, background_text):
        if background_text:
            word_count = len(background_text.split())
            if word_count > 80:
                raise ValueError('Background must be 80 words or less')
        return background_text

    @field_validator('communication_style')
    @classmethod
    def validate_communication_style_word_count(cls, communication_style_text):
        if communication_style_text:
            word_count = len(communication_style_text.split())
            if word_count > 30:
                raise ValueError('Communication style must be 30 words or less')
        return communication_style_text

    @field_validator('race')
    @classmethod
    def validate_race(cls, race_value):
        valid_races = [
            'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
            'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
        ]
        if race_value not in valid_races:
            raise ValueError(f'Race must be one of: {", ".join(valid_races)}')
        return race_value

    @field_validator('size')
    @classmethod
    def validate_size(cls, size_value):
        valid_sizes = ['Small', 'Medium', 'Large']
        if size_value not in valid_sizes:
            raise ValueError(f'Size must be one of: {", ".join(valid_sizes)}')
        return size_value

    @field_validator('alignment')
    @classmethod
    def validate_alignment(cls, alignment_value):
        valid_alignments = [
            'Lawful Good', 'Neutral Good', 'Chaotic Good',
            'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
            'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
        ]
        if alignment_value not in valid_alignments:
            raise ValueError(f'Alignment must be one of: {", ".join(valid_alignments)}')
        return alignment_value

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, tags_list):
        if tags_list:
            processed_tags = []
            for tag in tags_list:
                if tag and not tag.startswith('#'):
                    # Auto-add hash prefix and convert to kebab-case
                    kebab_case = tag.lower().replace(' ', '-').replace('_', '-')
                    processed_tags.append(f'#{kebab_case}')
                else:
                    processed_tags.append(tag)
            return processed_tags
        return tags_list

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    race: Optional[str] = None
    size: Optional[str] = None
    alignment: Optional[str] = None
    profession: Optional[str] = None
    background: Optional[str] = None
    communication_style: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator('background')
    @classmethod
    def validate_background_word_count(cls, background_text):
        if background_text:
            word_count = len(background_text.split())
            if word_count > 80:
                raise ValueError('Background must be 80 words or less')
        return background_text

    @field_validator('communication_style')
    @classmethod
    def validate_communication_style_word_count(cls, communication_style_text):
        if communication_style_text:
            word_count = len(communication_style_text.split())
            if word_count > 30:
                raise ValueError('Communication style must be 30 words or less')
        return communication_style_text

    @field_validator('race')
    @classmethod
    def validate_race(cls, race_value):
        if race_value is not None:
            valid_races = [
                'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
                'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
            ]
            if race_value not in valid_races:
                raise ValueError(f'Race must be one of: {", ".join(valid_races)}')
        return race_value

    @field_validator('size')
    @classmethod
    def validate_size(cls, size_value):
        if size_value is not None:
            valid_sizes = ['Small', 'Medium', 'Large']
            if size_value not in valid_sizes:
                raise ValueError(f'Size must be one of: {", ".join(valid_sizes)}')
        return size_value

    @field_validator('alignment')
    @classmethod
    def validate_alignment(cls, alignment_value):
        if alignment_value is not None:
            valid_alignments = [
                'Lawful Good', 'Neutral Good', 'Chaotic Good',
                'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
                'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
            ]
            if alignment_value not in valid_alignments:
                raise ValueError(f'Alignment must be one of: {", ".join(valid_alignments)}')
        return alignment_value

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, tags_list):
        if tags_list:
            processed_tags = []
            for tag in tags_list:
                if tag and not tag.startswith('#'):
                    # Auto-add hash prefix and convert to kebab-case
                    kebab_case = tag.lower().replace(' ', '-').replace('_', '-')
                    processed_tags.append(f'#{kebab_case}')
                else:
                    processed_tags.append(tag)
            return processed_tags
        return tags_list

class Character(CharacterBase):
    id: int
    
    class Config:
        from_attributes = True
