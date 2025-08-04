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

// Trust threshold constants (matching backend defaults)
export const DEFAULT_THRESHOLDS = {
  public: 0.0,
  privileged: 0.55,
  exclusive: 0.8,
}

// Threshold validation constants
export const THRESHOLD_LIMITS = {
  min: 0.0,
  max: 1.0,
  step: 0.25,
  minGap: 0.25, // Minimum gap between privileged and exclusive
}
