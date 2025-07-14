// Validation rules and limits
export const WORD_LIMITS = {
    PLAYER_APPEARANCE: 40,
    CHARACTER_BACKGROUND: 80,
    CHARACTER_COMMUNICATION: 30
}

export const CHARACTER_LIMITS = {
    MEMORY_TEXT: 500,
    PLAYER_APPEARANCE: 240,
    CHARACTER_BACKGROUND: 480,
    CHARACTER_COMMUNICATION: 180
}

export const VALIDATION_MESSAGES = {
    REQUIRED_FIELD: 'This field is required',
    WORD_LIMIT_EXCEEDED: 'Word limit exceeded',
    INVALID_FORMAT: 'Invalid format'
}

export const FORM_FIELDS = {
    PLAYER: {
        REQUIRED: ['name', 'appearance', 'race', 'class_name', 'size', 'alignment'],
        OPTIONAL: ['avatar', 'tags']
    },
    CHARACTER: {
        REQUIRED: ['name', 'race', 'size', 'alignment', 'profession', 'background', 'communication_style'],
        OPTIONAL: ['avatar', 'tags']
    },
    MEMORY: {
        REQUIRED: ['title', 'memory_text'],
        OPTIONAL: ['linked_character_ids', 'visibility_type', 'keywords', 'player_races', 'player_alignments', 'player_tags', 'character_limit']
    }
}
