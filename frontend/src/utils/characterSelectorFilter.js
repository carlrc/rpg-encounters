const NO_CHAR_SENTINEL = 'no-characters'

export function normalizeCharacterIds(modelValue) {
  const values = Array.isArray(modelValue) ? modelValue : []
  return values
    .filter((id) => id !== NO_CHAR_SENTINEL)
    .map((id) => Number(id))
    .filter((id) => !Number.isNaN(id))
}

export function filterCharactersByAttributes(characters, filters) {
  if (!Array.isArray(characters)) {
    return []
  }

  const filterState = filters || {}
  const races = Array.isArray(filterState.race) ? filterState.race : []
  const alignments = Array.isArray(filterState.alignment) ? filterState.alignment : []

  const hasRaceFilter = races.length > 0
  const hasAlignmentFilter = alignments.length > 0

  if (!hasRaceFilter && !hasAlignmentFilter) {
    return characters
  }

  return characters.filter((character) => {
    if (hasRaceFilter && !races.includes(character.race)) {
      return false
    }

    if (hasAlignmentFilter && !alignments.includes(character.alignment)) {
      return false
    }

    return true
  })
}

export function buildVisibleCharacterOptions({
  characters,
  filters,
  showNoCharactersOption = false,
}) {
  const filteredCharacters = filterCharactersByAttributes(characters, filters)
  const options = []

  if (showNoCharactersOption) {
    options.push({
      label: 'NONE - Select items with no assignments',
      value: NO_CHAR_SENTINEL,
      excludeFromSelectAll: true,
    })
  }

  filteredCharacters.forEach((character) => {
    if (!character) return
    const id = Number(character.id)
    if (Number.isNaN(id)) return

    options.push({
      label: character.name || `Character ${id}`,
      value: id,
    })
  })

  return options
}
