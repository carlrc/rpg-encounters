// Validation rules and limits
export const WORD_LIMITS = {
    PLAYER_APPEARANCE: 40,
    CHARACTER_BACKGROUND: 80,
    CHARACTER_COMMUNICATION: 30
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
    }
}
