from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class PlayerBase(BaseModel):
    name: str
    appearance: str = Field(..., description="Player appearance (max 40 words)")
    race: str = Field(..., description="Player race")
    class_name: str = Field(..., description="Player class")
    size: str = Field(..., description="Player size")
    alignment: str = Field(..., description="Player alignment")
    tags: List[str] = Field(default_factory=list, description="Player tags")

    @field_validator('appearance')
    @classmethod
    def validate_appearance_word_count(cls, appearance_text):
        if appearance_text:
            word_count = len(appearance_text.split())
            if word_count > 40:
                raise ValueError('Appearance must be 40 words or less')
        return appearance_text

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

    @field_validator('class_name')
    @classmethod
    def validate_class_name(cls, class_value):
        valid_classes = [
            'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 
            'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 
            'Warlock', 'Wizard'
        ]
        if class_value not in valid_classes:
            raise ValueError(f'Class must be one of: {", ".join(valid_classes)}')
        return class_value

    @field_validator('size')
    @classmethod
    def validate_size(cls, size_value):
        valid_sizes = ['Small', 'Medium']
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

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    appearance: Optional[str] = None
    race: Optional[str] = None
    class_name: Optional[str] = None
    size: Optional[str] = None
    alignment: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator('appearance')
    @classmethod
    def validate_appearance_word_count(cls, appearance_text):
        if appearance_text:
            word_count = len(appearance_text.split())
            if word_count > 40:
                raise ValueError('Appearance must be 40 words or less')
        return appearance_text

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

    @field_validator('class_name')
    @classmethod
    def validate_class_name(cls, class_value):
        if class_value is not None:
            valid_classes = [
                'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 
                'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 
                'Warlock', 'Wizard'
            ]
            if class_value not in valid_classes:
                raise ValueError(f'Class must be one of: {", ".join(valid_classes)}')
        return class_value

    @field_validator('size')
    @classmethod
    def validate_size(cls, size_value):
        if size_value is not None:
            valid_sizes = ['Small', 'Medium']
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

class Player(PlayerBase):
    id: int
    
    class Config:
        from_attributes = True
