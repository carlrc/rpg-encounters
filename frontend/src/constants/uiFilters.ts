export const CHARACTER_FILTER_TABS = [
  { id: 'race', label: 'Race' },
  { id: 'alignment', label: 'Alignment' },
  { id: 'size', label: 'Size' },
  { id: 'gender', label: 'Gender' },
  { id: 'class', label: 'Class' },
]

export const MEMORY_FILTER_TABS = [
  { id: 'characters', label: 'Characters' },
  { id: 'race', label: 'Race' },
  { id: 'alignment', label: 'Alignment' },
]

export const REVEAL_FILTER_TABS = [
  { id: 'characters', label: 'Characters' },
  { id: 'race', label: 'Race' },
  { id: 'alignment', label: 'Alignment' },
]

export const createCharacterFilterState = () => ({
  race: [],
  alignment: [],
  size: [],
  gender: [],
  class: [],
  characterIds: [],
  showUnassigned: false,
})

export const createMemoryFilterState = () => ({
  characterIds: [],
  showUnassigned: false,
  race: [],
  alignment: [],
})

export const createRevealFilterState = () => ({
  characters: [],
  characterIds: [],
  showUnassigned: false,
  race: [],
  alignment: [],
})
