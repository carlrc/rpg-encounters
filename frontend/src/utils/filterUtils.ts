/**
 * Apply filters to a list of items
 * @param {Array} items - Array of items to filter
 * @param {Object} filters - Filter configuration object
 * @returns {Array} Filtered array of items
 */
export function applyFilters(items, filters) {
  if (!items || !Array.isArray(items)) {
    return []
  }

  if (!filters) {
    return items
  }

  return items.filter((item) => {
    // Race filter (multi-select)
    if (filters.race && filters.race.length > 0) {
      if (!filters.race.includes(item.race)) {
        return false
      }
    }

    // Alignment filter (multi-select)
    if (filters.alignment && filters.alignment.length > 0) {
      if (!filters.alignment.includes(item.alignment)) {
        return false
      }
    }

    // Size filter (multi-select)
    if (filters.size && filters.size.length > 0) {
      if (!filters.size.includes(item.size)) {
        return false
      }
    }

    // Gender filter (multi-select)
    if (filters.gender && filters.gender.length > 0) {
      if (!filters.gender.includes(item.gender)) {
        return false
      }
    }

    // Profession filter (text contains)
    if (filters.profession && filters.profession.trim()) {
      const professionSearch = filters.profession.toLowerCase().trim()
      const itemProfession = (item.profession || '').toLowerCase()
      if (!itemProfession.includes(professionSearch)) {
        return false
      }
    }

    // Class filter (multi-select)
    if (filters.class && filters.class.length > 0) {
      if (!filters.class.includes(item.class)) {
        return false
      }
    }

    // Encounter association filter
    if (filters.hasEncounter !== undefined) {
      // Check if item has encounters or encounter_ids
      const hasEncounters =
        (item.encounters && item.encounters.length > 0) ||
        (item.encounter_ids && item.encounter_ids.length > 0)
      if (filters.hasEncounter !== hasEncounters) {
        return false
      }
    }

    return true
  })
}

/**
 * Create an empty filter state object
 * @returns {Object} Empty filter state
 */
export function createEmptyFilters() {
  return {
    race: [],
    alignment: [],
    size: [],
    gender: [],
    profession: '',
    class: [],
    hasEncounter: undefined,
  }
}

/**
 * Check if any filters are active
 * @param {Object} filters - Filter state object
 * @returns {boolean} True if any filters are active
 */
export function hasActiveFilters(filters) {
  if (!filters) return false

  return !!(
    (filters.race && filters.race.length > 0) ||
    (filters.alignment && filters.alignment.length > 0) ||
    (filters.size && filters.size.length > 0) ||
    (filters.gender && filters.gender.length > 0) ||
    filters.profession ||
    (filters.class && filters.class.length > 0) ||
    filters.hasEncounter !== undefined
  )
}

/**
 * Count active filters
 * @param {Object} filters - Filter state object
 * @returns {number} Number of active filters
 */
export function countActiveFilters(filters) {
  if (!filters) return 0

  let count = 0
  if (filters.race && filters.race.length > 0) count++
  if (filters.alignment && filters.alignment.length > 0) count++
  if (filters.size && filters.size.length > 0) count++
  if (filters.gender && filters.gender.length > 0) count++
  if (filters.profession) count++
  if (filters.class && filters.class.length > 0) count++
  if (filters.hasEncounter !== undefined) count++

  return count
}

/**
 * Clear all filters
 * @param {Object} filters - Filter state object to clear
 */
export function clearAllFilters(filters) {
  if (!filters) return

  filters.race = []
  filters.alignment = []
  filters.size = []
  filters.gender = []
  filters.profession = ''
  filters.class = []
  filters.hasEncounter = undefined
}

/**
 * Remove a specific filter value
 * @param {Object} filters - Filter state object
 * @param {string} filterType - Type of filter ('race', 'alignment', etc.)
 * @param {*} value - Value to remove
 */
export function removeFilterValue(filters, filterType, value) {
  if (!filters || !filters[filterType]) return

  if (Array.isArray(filters[filterType])) {
    const index = filters[filterType].indexOf(value)
    if (index > -1) {
      filters[filterType].splice(index, 1)
    }
  } else {
    // For non-array filters like profession
    filters[filterType] = filterType === 'hasEncounter' ? undefined : ''
  }
}

/**
 * Apply character filters to a list of items (for memories/reveals)
 * @param {Array} items - Array of items to filter
 * @param {Object} filters - Character filter configuration object
 * @returns {Array} Filtered array of items
 */
export function applyCharacterFilters(items, filters) {
  if (!items || !Array.isArray(items)) {
    return []
  }

  if (!filters) {
    return items
  }

  if (filters.characterIds.length === 0 && !filters.showUnassigned) {
    return items
  }

  return items.filter((item) => {
    const hasNoCharacters = !item.character_ids || item.character_ids.length === 0

    // Check unassigned filter
    if (filters.showUnassigned && hasNoCharacters) {
      return true
    }

    // Check character filters
    if (filters.characterIds.length > 0 && item.character_ids) {
      return item.character_ids.some((id) => filters.characterIds.includes(id))
    }

    return false
  })
}

/**
 * Apply character attribute filters to a list of items (for memories/reveals)
 * Filters items based on the race/alignment/etc of their associated characters
 * @param {Array} items - Array of items to filter (memories/reveals with character_ids)
 * @param {Object} filters - Filter configuration object with race/alignment arrays
 * @param {Array} characters - Array of character objects to lookup attributes from
 * @returns {Array} Filtered array of items
 */
export function applyCharacterAttributeFilters(items, filters, characters) {
  if (!items || !Array.isArray(items)) {
    return []
  }

  if (!filters || !characters || !Array.isArray(characters)) {
    return items
  }

  // If no attribute filters are active, return all items
  const hasRaceFilter = filters.race && filters.race.length > 0
  const hasAlignmentFilter = filters.alignment && filters.alignment.length > 0

  if (!hasRaceFilter && !hasAlignmentFilter) {
    return items
  }

  // Create a lookup map for faster character attribute access
  const characterMap = new Map()
  characters.forEach((char) => {
    characterMap.set(char.id, char)
  })

  return items.filter((item) => {
    // Skip items with no character associations
    if (!item.character_ids || item.character_ids.length === 0) {
      return false
    }

    // Get all associated characters for this item
    const associatedCharacters = item.character_ids
      .map((id) => characterMap.get(id))
      .filter(Boolean) // Remove any undefined characters

    if (associatedCharacters.length === 0) {
      return false
    }

    // Check if ANY associated character matches the race filter
    if (hasRaceFilter) {
      const hasMatchingRace = associatedCharacters.some((char) => filters.race.includes(char.race))
      if (!hasMatchingRace) {
        return false
      }
    }

    // Check if ANY associated character matches the alignment filter
    if (hasAlignmentFilter) {
      const hasMatchingAlignment = associatedCharacters.some((char) =>
        filters.alignment.includes(char.alignment)
      )
      if (!hasMatchingAlignment) {
        return false
      }
    }

    return true
  })
}
