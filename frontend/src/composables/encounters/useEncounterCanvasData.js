import { serializeError } from 'serialize-error'

export function useEncounterCanvasData({
  elements,
  error,
  getEncounters,
  getCharactersForEncounter,
  getPlayersForEncounter,
}) {
  const transformEncounterDataToElements = (encounterData) => {
    const vueFlowNodes = encounterData.encounters.map((encounter) => ({
      id: String(encounter.id),
      type: 'encounter',
      position: {
        x: encounter.position_x || 200,
        y: encounter.position_y || 150,
      },
      data: {
        name: encounter.name,
        description: encounter.description || '',
        characters: getCharactersForEncounter(encounter.character_ids || []),
        players: getPlayersForEncounter(encounter.player_ids || []),
        isNew: false,
      },
    }))

    const vueFlowEdges = (encounterData.connections || []).map((connection) => ({
      id: `edge-${connection.id}`,
      source: String(connection.source_encounter_id),
      target: String(connection.target_encounter_id),
      sourceHandle: connection.source_handle,
      targetHandle: connection.target_handle,
      type: connection.edge_type === 'bezier' ? 'default' : connection.edge_type || 'straight',
      style: {
        stroke: connection.stroke_color || '#A0A0A0',
        strokeWidth: connection.stroke_width || 3,
      },
      data: {
        selectable: true,
        isNew: false,
      },
    }))

    return [...vueFlowNodes, ...vueFlowEdges]
  }

  const loadEncounters = async () => {
    try {
      const encounterData = await getEncounters()
      if (!encounterData || !Array.isArray(encounterData.encounters)) {
        throw new Error('Invalid encounter data received from API')
      }

      elements.value = transformEncounterDataToElements(encounterData)
    } catch (err) {
      const errorMessage = err.message || 'Failed to load encounters'
      error.value = errorMessage
      console.error('Encounter loading failed:', JSON.stringify(serializeError(err)))
      throw err
    }
  }

  return {
    transformEncounterDataToElements,
    loadEncounters,
  }
}
