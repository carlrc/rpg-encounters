// Validation rules and limits
export const CHARACTER_LIMITS = {
  MEMORY_TEXT: 500,
  PLAYER_APPEARANCE: 180,
  CHARACTER_BACKGROUND: 240,
  CHARACTER_COMMUNICATION: 180,
  CHARACTER_MOTIVATION: 300,
}

export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: 'This field is required',
  WORD_LIMIT_EXCEEDED: 'Word limit exceeded',
  INVALID_FORMAT: 'Invalid format',
}

export const FORM_FIELDS = {
  PLAYER: {
    REQUIRED: ['name', 'appearance', 'race', 'class_name', 'size', 'alignment'],
    OPTIONAL: ['avatar'],
  },
  CHARACTER: {
    REQUIRED: [
      'name',
      'race',
      'size',
      'alignment',
      'profession',
      'background',
      'communication_style',
      'motivation',
    ],
    OPTIONAL: ['avatar'],
  },
  MEMORY: {
    REQUIRED: ['title', 'memory_text'],
    OPTIONAL: [
      'linked_character_ids',
      'visibility_type',
      'keywords',
      'player_races',
      'player_alignments',
      'character_limit',
    ],
  },
}
