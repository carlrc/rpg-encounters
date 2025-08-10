// D&D game data constants
export const RACES = [
  'Human',
  'Elf',
  'Dwarf',
  'Halfling',
  'Dragonborn',
  'Gnome',
  'Half-Elf',
  'Half-Orc',
  'Tiefling',
]

export const CLASSES = [
  'Barbarian',
  'Bard',
  'Cleric',
  'Druid',
  'Fighter',
  'Monk',
  'Paladin',
  'Ranger',
  'Rogue',
  'Sorcerer',
  'Warlock',
  'Wizard',
]

export const SIZES = {
  PLAYER: ['Small', 'Medium'],
  CHARACTER: ['Small', 'Medium', 'Large'],
}

export const ALIGNMENTS = [
  'Lawful Good',
  'Neutral Good',
  'Chaotic Good',
  'Lawful Neutral',
  'True Neutral',
  'Chaotic Neutral',
  'Lawful Evil',
  'Neutral Evil',
  'Chaotic Evil',
]

export const NAVIGATION_TABS = [
  { id: 'players', label: 'Players' },
  { id: 'characters', label: 'Characters' },
  { id: 'memories', label: 'Memories' },
  { id: 'encounters', label: 'Encounters' },
]

// D&D Difficulty Class constants
export const DIFFICULTY_CLASS = {
  ALWAYS: 0,
  VERY_EASY: 5,
  EASY: 10,
  MEDIUM: 15,
  HARD: 20,
  VERY_HARD: 25,
  NEARLY_IMPOSSIBLE: 30,
}

// DC threshold constants (matching backend defaults)
export const DEFAULT_THRESHOLDS = {
  public: DIFFICULTY_CLASS.ALWAYS,
  privileged: DIFFICULTY_CLASS.MEDIUM,
  exclusive: DIFFICULTY_CLASS.HARD,
}

// Threshold validation constants (DC scale)
export const THRESHOLD_LIMITS = {
  min: DIFFICULTY_CLASS.ALWAYS,
  max: DIFFICULTY_CLASS.NEARLY_IMPOSSIBLE,
  step: 5,
  minGap: 5, // Minimum gap between privileged and exclusive
}

// DC labels for UI display
export const DC_LABELS = {
  [DIFFICULTY_CLASS.ALWAYS]: 'Always (0)',
  [DIFFICULTY_CLASS.VERY_EASY]: 'Very Easy (5)',
  [DIFFICULTY_CLASS.EASY]: 'Easy (10)',
  [DIFFICULTY_CLASS.MEDIUM]: 'Medium (15)',
  [DIFFICULTY_CLASS.HARD]: 'Hard (20)',
  [DIFFICULTY_CLASS.VERY_HARD]: 'Very Hard (25)',
  [DIFFICULTY_CLASS.NEARLY_IMPOSSIBLE]: 'Nearly Impossible (30)',
}
