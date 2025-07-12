from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class PlayerBase(BaseModel):
    name: str
    appearance: str = Field(..., description="Player appearance (max 40 words)")
    race: str = Field(..., description="Player race")
    class_name: str = Field(..., description="Player class")
    groups: List[str] = Field(default_factory=list, description="Player groups")

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

    @field_validator('groups')
    @classmethod
    def validate_groups(cls, groups_list):
        if groups_list:
            processed_groups = []
            for group in groups_list:
                if group and not group.startswith('#'):
                    # Auto-add hash prefix and convert to kebab-case
                    kebab_case = group.lower().replace(' ', '-').replace('_', '-')
                    processed_groups.append(f'#{kebab_case}')
                else:
                    processed_groups.append(group)
            return processed_groups
        return groups_list

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    appearance: Optional[str] = None
    race: Optional[str] = None
    class_name: Optional[str] = None
    groups: Optional[List[str]] = None

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

    @field_validator('groups')
    @classmethod
    def validate_groups(cls, groups_list):
        if groups_list:
            processed_groups = []
            for group in groups_list:
                if group and not group.startswith('#'):
                    # Auto-add hash prefix and convert to kebab-case
                    kebab_case = group.lower().replace(' ', '-').replace('_', '-')
                    processed_groups.append(f'#{kebab_case}')
                else:
                    processed_groups.append(group)
            return processed_groups
        return groups_list

class Player(PlayerBase):
    id: int
    
    class Config:
        from_attributes = True
