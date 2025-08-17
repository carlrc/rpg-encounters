// UI-specific validation constants (kept in frontend)
export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: 'This field is required',
  CHARACTER_LIMIT_EXCEEDED: 'Character limit exceeded',
  INVALID_FORMAT: 'Invalid format',
}

export const FORM_FIELDS = {
  PLAYER: {
    REQUIRED: [
      'name',
      'appearance',
      'race',
      'class_name',
      'size',
      'alignment',
      'abilities',
      'skills',
    ],
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
    REQUIRED: ['title', 'content', 'character_ids'],
    OPTIONAL: [
      'linked_character_ids',
      'visibility_type',
      'keywords',
      'player_races',
      'player_alignments',
      'character_limit',
    ],
  },
  REVEAL: {
    REQUIRED: ['title', 'character_ids', 'level_1_content'],
    OPTIONAL: ['level_2_content', 'level_3_content'],
  },
}
