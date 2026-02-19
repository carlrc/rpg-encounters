export function useEncounterGraphOps({ elements, characters, players }) {
  const getAvailableCharactersForEncounter = (encounterData) => {
    if (!encounterData || !Array.isArray(encounterData.characters)) return characters.value

    const encounterCharacterIds = new Set(encounterData.characters.map((char) => char.id))
    return characters.value.filter((char) => !encounterCharacterIds.has(char.id))
  }

  const getAvailablePlayersForEncounter = (encounterData) => {
    if (!encounterData || !encounterData.players) return players.value

    const encounterPlayerIds = new Set(encounterData.players.map((player) => player.id))
    return players.value.filter((player) => !encounterPlayerIds.has(player.id))
  }

  const getCharactersForEncounter = (characterIds) => {
    if (!Array.isArray(characterIds) || !Array.isArray(characters.value)) {
      return []
    }
    return characters.value.filter((character) => characterIds.includes(character.id))
  }

  const getPlayersForEncounter = (playerIds) => {
    if (!playerIds) {
      return []
    }

    return players.value.filter((player) => playerIds.includes(player.id))
  }

  const addCharacterToEncounter = (encounterId, characterId) => {
    const character = characters.value.find((c) => c.id === characterId)
    const encounter = elements.value.find((el) => el.id === encounterId)

    encounter.data.characters = encounter.data.characters || []

    const isAlreadyInEncounter = encounter.data.characters.some((char) => char.id === characterId)

    if (!isAlreadyInEncounter) {
      encounter.data.characters.push(character)
    }
  }

  const removeCharacterFromEncounter = (encounterId, characterId) => {
    const encounter = elements.value.find((el) => el.id === encounterId)
    encounter.data.characters = (encounter.data.characters || []).filter(
      (char) => char.id !== characterId
    )
  }

  const addPlayerToEncounter = (encounterId, playerId) => {
    const player = players.value.find((p) => p.id === playerId)
    if (!player) return

    elements.value = elements.value.map((el) => {
      if (el.type !== 'encounter') return el

      const isTarget = String(el.id) === String(encounterId)
      const current = el.data?.players ?? []
      const filtered = current.filter((p) => p.id !== playerId)
      const nextPlayers = isTarget ? [...filtered, player] : filtered

      return { ...el, data: { ...el.data, players: nextPlayers } }
    })
  }

  const removePlayerFromEncounter = (encounterId, playerId) => {
    const encounter = elements.value.find((el) => el.id === encounterId)
    encounter.data.players = (encounter.data.players || []).filter(
      (assigned) => assigned.id !== playerId
    )
  }

  return {
    getAvailableCharactersForEncounter,
    getAvailablePlayersForEncounter,
    getCharactersForEncounter,
    getPlayersForEncounter,
    addCharacterToEncounter,
    removeCharacterFromEncounter,
    addPlayerToEncounter,
    removePlayerFromEncounter,
  }
}
