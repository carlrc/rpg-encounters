<template>
  <div class="encounter-builder" role="main" aria-label="Encounter Builder Interface">
    <div v-if="loading" class="shared-loading" role="status" aria-live="polite">
      <span class="sr-only">Loading encounter data...</span>
      Loading encounter data...
    </div>
    <div v-else-if="error" class="shared-error" role="alert" aria-live="assertive">
      {{ error }}
    </div>

    <div v-else class="encounter-builder-container">
      <!-- Add Encounter Button -->
      <div class="add-encounter-container">
        <button
          @click="addNewEncounter"
          class="add-encounter-btn"
          title="Add Encounter"
          aria-label="Add new encounter to world"
        >
          +
        </button>
        <span class="add-encounter-label">Add Encounter</span>

        <!-- Save Canvas Button -->
        <button
          @click="saveCanvas"
          class="save-canvas-btn"
          :disabled="isSaving"
          :title="isSaving ? 'Saving...' : 'Save Canvas'"
          :aria-label="isSaving ? 'Saving canvas changes' : 'Save all canvas changes'"
        >
          {{ isSaving ? '...' : '💾' }}
        </button>
        <span class="save-canvas-label">{{ isSaving ? 'Saving...' : 'Save Canvas' }}</span>
      </div>

      <VueFlow
        v-model="elements"
        class="encounter-canvas"
        :default-viewport="{ zoom: 1 }"
        :min-zoom="0.1"
        :max-zoom="4"
        @connect="onConnect"
        @edge-click="onEdgeClick"
        @move-end="onViewportChange"
        @zoom-end="onViewportChange"
        @pane-ready="onPaneReady"
        :connection-line-style="{ stroke: '#A0A0A0', strokeWidth: 2 }"
        :is-valid-connection="isValidConnection"
        :connect-on-click="false"
        :edges-deletable="true"
        :nodes-deletable="false"
        :multi-selection-key-code="null"
        :connection-mode="'loose'"
        role="application"
        aria-label="Interactive encounter map with encounters and characters"
        ref="vueFlowRef"
      >
        <!-- Custom Encounter Node -->
        <template #node-encounter="{ data, id }">
          <EncounterNode
            :encounter="{ ...data, id }"
            :available-characters="getAvailableCharactersForEncounter(data)"
            :available-players="getAvailablePlayersForEncounter(data)"
            @open-encounter="openCharacterEncounter"
            @add-character="addCharacterToEncounter"
            @remove-character="removeCharacterFromEncounter"
            @add-player="addPlayerToEncounter"
            @remove-player="removePlayerFromEncounter"
            @update-encounter-name="updateEncounterName"
            @update-encounter-description="updateEncounterDescription"
            @clear-auto-open-description="clearAutoOpenDescription"
          />
        </template>
      </VueFlow>

      <!-- Character encounter popup -->
      <CharacterEncounterPopup
        :character="selectedCharacter"
        :encounter-id="parseInt(selectedEncounterId) || 0"
        :initial-player-id="route.query.playerId"
        :is-open="showEncounterPopup"
        :assigned-players="popupAssignedPlayers"
        @close="closeEncounterPopup"
      />
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { serializeError } from 'serialize-error'
  import { VueFlow } from '@vue-flow/core'
  import '@vue-flow/core/dist/style.css'
  import EncounterNode from './EncounterNode.vue'
  import CharacterEncounterPopup from './CharacterEncounterPopup.vue'
  import { getEncounters, createEncounter, saveCanvas as saveCanvasAPI } from '../services/api.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useWorldStore } from '@/stores/world'
  import { usePlayerStore } from '@/stores/players'
  import { useCharacterStore } from '../stores/characters.js'
  import { useNotification } from '../composables/useNotification.js'
  import { isTemporaryId } from '../utils/idUtils.js'
  import { saveViewport, getViewport } from '../utils/viewportState.js'

  const gameDataStore = useGameDataStore()
  const worldStore = useWorldStore()
  const playerStore = usePlayerStore()
  const characterStore = useCharacterStore()
  const { data: gameData } = storeToRefs(gameDataStore)
  const { entities: characters } = storeToRefs(characterStore)
  const { entities: playerEntities } = storeToRefs(playerStore)
  const { showSuccess, showError } = useNotification()
  const router = useRouter()
  const route = useRoute()

  // State
  const players = computed(() => playerEntities.value || [])
  const loading = ref(true)
  const error = ref(null)
  const selectedCharacter = ref(null)
  const selectedEncounterId = ref(null)
  const showEncounterPopup = ref(false)
  const vueFlowRef = ref(null)
  const isSaving = ref(false)

  const elements = ref([])

  const selectedEncounter = computed(() => {
    if (!selectedEncounterId.value) {
      return null
    }

    const encounterId = String(selectedEncounterId.value)
    return (
      elements.value.find((el) => el.type === 'encounter' && String(el.id) === encounterId) || null
    )
  })

  const popupAssignedPlayers = computed(() => selectedEncounter.value?.data.players || [])

  // Deletion tracking
  const deletedEncounterIds = ref([])
  const deletedConnectionIds = ref([])

  // Get available characters for a specific encounter (exclude characters already in that encounter)
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

  // Transform encounter data to Vue Flow format
  const transformEncounterDataToElements = (encounterData) => {
    // Transform database encounters to Vue Flow format
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
        isNew: false, // Existing encounters from database
      },
    }))

    // Transform database connections to Vue Flow edges
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
        isNew: false, // Existing connections from database
      },
    }))

    // Combine nodes and edges
    return [...vueFlowNodes, ...vueFlowEdges]
  }

  // Load encounters and connections from API
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

  // Helper function to get character objects from character IDs
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

  const loadData = async () => {
    // Triggered by state changes (even logout) where there is no world set
    if (!worldStore.currentWorldId) {
      return
    }

    loading.value = true
    error.value = null

    try {
      // Load characters first, then encounters (encounters need characters for associations)
      await gameDataStore.load()
      await characterStore.loadEntities()
      await playerStore.loadEntities()
      await loadEncounters()
    } catch (err) {
      const errorMessage = err.message || 'Failed to load world data'
      error.value = `Encounter Builder Error: ${errorMessage}`
      console.error('Data loading failed:', JSON.stringify(serializeError(err)))
    } finally {
      loading.value = false
    }
  }

  // Character management
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

    // Rebuild elements: remove player from all encounters, add to target
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

  // Character encounter handlers
  const openCharacterEncounter = (character, encounterId) => {
    // Validate character object
    if (!character || !character.id) {
      console.warn('Invalid character provided to openCharacterEncounter')
      return
    }

    // Validate encounter ID
    if (!encounterId) {
      console.warn('Invalid encounterId provided to openCharacterEncounter')
      return
    }

    selectedCharacter.value = character
    selectedEncounterId.value = encounterId
    showEncounterPopup.value = true

    // Add popup state to URL - preserve existing playerId if present
    router.replace({
      query: {
        ...route.query,
        popup: 'encounter',
        characterId: character.id,
        encounterId: encounterId,
        playerId: route.query.playerId || undefined,
      },
    })
  }

  const closeEncounterPopup = () => {
    showEncounterPopup.value = false
    selectedCharacter.value = null
    selectedEncounterId.value = null

    // Remove popup params from URL
    const { popup, characterId, encounterId, playerId, ...remainingQuery } = route.query
    router.replace({ query: remainingQuery })
  }

  // Handle new connections created by dragging
  const onConnect = (connection) => {
    // Validate connection object
    if (!connection || !connection.source || !connection.target) {
      console.warn('Invalid connection object provided to onConnect')
      return
    }

    // Check if connection already exists (in either direction)
    const existingEdge = elements.value.find(
      (el) =>
        el.source &&
        el.target &&
        ((el.source === connection.source && el.target === connection.target) ||
          (el.source === connection.target && el.target === connection.source))
    )

    if (existingEdge) {
      return
    }

    const newEdge = {
      id: `edge-${connection.source}-${connection.target}-${Date.now()}`,
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle,
      targetHandle: connection.targetHandle,
      type: 'straight',
      style: {
        stroke: '#A0A0A0',
        strokeWidth: 3,
      },
      data: {
        selectable: true,
        isNew: true, // New connection created by user
      },
    }

    elements.value.push(newEdge)
  }

  // Validate connections - allow all connections between different nodes
  const isValidConnection = (connection) => {
    if (!connection || !connection.source || !connection.target) {
      return false
    }
    return connection.source !== connection.target
  }

  // Add new encounter at current viewport center
  const addNewEncounter = async () => {
    if (!vueFlowRef.value) return

    try {
      // Get current viewport to position encounter at center
      const viewport = vueFlowRef.value.getViewport()
      const canvasRect = vueFlowRef.value.$el.getBoundingClientRect()

      // Calculate center position accounting for viewport transform
      const centerX = (canvasRect.width / 2 - viewport.x) / viewport.zoom
      const centerY = (canvasRect.height / 2 - viewport.y) / viewport.zoom

      // Create encounter in database immediately
      const encounterData = {
        name: 'New Encounter',
        description: '',
        position_x: centerX,
        position_y: centerY,
        character_ids: [],
        player_ids: [],
      }

      const createdEncounter = await createEncounter(encounterData)

      // Create new encounter object
      const newEncounter = {
        id: String(createdEncounter.id), // Vue Flow requires string IDs
        type: 'encounter',
        position: {
          x: createdEncounter.position_x,
          y: createdEncounter.position_y,
        },
        data: {
          name: createdEncounter.name,
          description: createdEncounter.description,
          characters: [],
          players: [],
          isNew: false, // Already saved to database
          autoOpenDescription: true,
        },
      }

      // Add encounter to elements
      elements.value.push(newEncounter)
      showSuccess('New encounter created!')
    } catch (error) {
      console.error('Failed to create encounter:', JSON.stringify(serializeError(error)))
      showError(`Failed to create encounter`)
    }
  }

  // Update encounter name
  const updateEncounterName = (encounterId, newName) => {
    const encounterIndex = elements.value.findIndex((el) => el.id === encounterId)
    if (encounterIndex !== -1) {
      elements.value[encounterIndex].data.name = newName
    }
  }

  // Update encounter description
  const updateEncounterDescription = (encounterId, newDescription) => {
    const encounterIndex = elements.value.findIndex((el) => el.id === encounterId)
    if (encounterIndex !== -1) {
      elements.value[encounterIndex].data.description = newDescription
    }
  }

  // Clear auto-open description flag
  const clearAutoOpenDescription = (encounterId) => {
    const encounterIndex = elements.value.findIndex((el) => el.id === encounterId)
    if (encounterIndex !== -1) {
      elements.value[encounterIndex].data.autoOpenDescription = false
    }
  }

  // Handle edge clicks for selection and deletion
  const onEdgeClick = (event) => {
    const edge = event.edge
    if (edge && confirm(`Delete connection between encounters?`)) {
      // Track deletion immediately before removal (not relying on watch)
      if (edge && !edge.data.isNew) {
        // Extract numeric ID from edge ID (edge-123 -> 123)
        const numericId = edge.id.replace('edge-', '')
        if (!isNaN(parseInt(numericId))) {
          deletedConnectionIds.value.push(parseInt(numericId))
        }
      }

      const edgeIndex = elements.value.findIndex((el) => el.id === edge.id)
      if (edgeIndex !== -1) {
        elements.value.splice(edgeIndex, 1)
      }
    }
  }

  // Helper function to identify orphaned connections
  const identifyOrphanedConnections = (deletedEncounterIds) => {
    const orphanedConnectionIds = []

    elements.value.forEach((el) => {
      if (el.source && el.target) {
        // Extract encounter IDs from Vue Flow node IDs
        const sourceId = el.source
        const targetId = el.target

        // Check if this connection references any deleted encounter
        if (deletedEncounterIds.includes(sourceId) || deletedEncounterIds.includes(targetId)) {
          // Extract connection ID from edge ID (edge-123 -> 123)
          const connectionId = el.id.replace('edge-', '')
          if (!isNaN(parseInt(connectionId))) {
            orphanedConnectionIds.push(parseInt(connectionId))
          }
        }
      }
    })

    return orphanedConnectionIds
  }

  // Watch elements array for deletions
  watch(
    elements,
    (newElements, oldElements) => {
      if (!oldElements || oldElements.length === 0) {
        // Initial load, skip deletion detection
        return
      }

      // Find deleted encounters
      const oldEncounters = oldElements.filter((el) => el.type === 'encounter')
      const newEncounters = newElements.filter((el) => el.type === 'encounter')

      const newEncounterIds = new Set(newEncounters.map((el) => el.id))

      // Identify deleted encounters
      const deletedEncounters = oldEncounters.filter((el) => !newEncounterIds.has(el.id))

      deletedEncounters.forEach((encounter) => {
        // Extract numeric ID - only for existing encounters (not UUIDs)
        if (!isTemporaryId(encounter.id) && !encounter.data.isNew) {
          // Only track deletion of existing encounters (not new ones that were never saved)
          deletedEncounterIds.value.push(parseInt(encounter.id))
        }
      })

      // Identify orphaned connections due to encounter deletions
      if (deletedEncounters.length > 0) {
        const encounterIds = deletedEncounters.map((el) => el.id)
        const orphanedIds = identifyOrphanedConnections(encounterIds)
        orphanedIds.forEach((id) => {
          if (!deletedConnectionIds.value.includes(id)) {
            deletedConnectionIds.value.push(id)
          }
        })
      }
    },
    { deep: true }
  )

  // Canvas serialization logic
  const serializeCanvasState = () => {
    const newEncounters = elements.value.filter((el) => el.type === 'encounter' && el.data.isNew)
    const existingEncounters = elements.value.filter(
      (el) => el.type === 'encounter' && !el.data.isNew
    )
    const newConnections = elements.value.filter((el) => el.source && el.target && el.data.isNew)
    const existingConnections = elements.value.filter(
      (el) => el.source && el.target && !el.data.isNew
    )

    // NEW: Track deleted encounters and their connections
    const deletedEncounters = deletedEncounterIds.value
    const deletedConnections = deletedConnectionIds.value

    return {
      newEncounters,
      existingEncounters,
      newConnections,
      existingConnections,
      deletedEncounters,
      deletedConnections,
    }
  }

  // Transform frontend format to backend format
  const transformToBackendFormat = (items, isConnection = false) => {
    return items.map((item) => {
      if (isConnection) {
        // No conversion needed - backend handles UUIDs and database IDs separately
        const sourceId = item.source // UUID or numeric string
        const targetId = item.target // UUID or numeric string

        return {
          id: isTemporaryId(item.id) ? undefined : parseInt(item.id.replace('edge-', '')),
          source_encounter_id: sourceId,
          target_encounter_id: targetId,
          source_handle: item.sourceHandle,
          target_handle: item.targetHandle,
          edge_type: item.type || 'straight',
          stroke_color: item.style?.stroke || '#A0A0A0',
          stroke_width: item.style?.strokeWidth || 3,
        }
      } else {
        // Transform encounter
        // For new encounters (UUIDs), pass the UUID string
        // For existing encounters, pass the integer ID
        const encounterId = isTemporaryId(item.id) ? item.id : parseInt(item.id)

        return {
          id: encounterId,
          name: item.data.name,
          description: item.data.description || '',
          position_x: item.position.x,
          position_y: item.position.y,
          character_ids: item.data.characters?.map((char) => char.id) || [],
          player_ids: item.data.players?.map((player) => player.id) || [],
        }
      }
    })
  }

  // Save canvas function
  const saveCanvas = async () => {
    try {
      isSaving.value = true
      const {
        newEncounters,
        existingEncounters,
        newConnections,
        existingConnections,
        deletedEncounters,
        deletedConnections,
      } = serializeCanvasState()

      const response = await saveCanvasAPI({
        new_encounters: transformToBackendFormat(newEncounters),
        existing_encounters: transformToBackendFormat(existingEncounters),
        new_connections: transformToBackendFormat(newConnections, true),
        existing_connections: transformToBackendFormat(existingConnections, true),
        deleted_encounter_ids: deletedEncounters,
        deleted_connection_ids: deletedConnections,
      })

      // Clear deletion tracking before updating elements
      deletedEncounterIds.value = []
      deletedConnectionIds.value = []

      // Use the extracted transformation logic to update elements with fresh data
      elements.value = transformEncounterDataToElements(response)

      // Show success notification
      showSuccess('Canvas saved successfully!')
    } catch (error) {
      console.error('Failed to save canvas:', JSON.stringify(serializeError(error)))
      showError(`Failed to save canvas`)
    } finally {
      isSaving.value = false
    }
  }

  // Handle world change events with reactive watcher
  watch(
    () => worldStore.currentWorldId,
    () => {
      // Clear current elements
      elements.value = []
      // Clear deletion tracking
      deletedEncounterIds.value = []
      deletedConnectionIds.value = []
      // Reload data for new world
      loadData()
    }
  )

  // Restore popup from URL params
  const restorePopupFromParams = () => {
    const { popup, characterId, encounterId } = route.query
    if (popup === 'encounter' && characterId && encounterId) {
      const character = characters.value.find((c) => c.id === parseInt(characterId))
      if (character) {
        selectedCharacter.value = character
        selectedEncounterId.value = encounterId
        showEncounterPopup.value = true
      }
    }
  }

  onMounted(() => {
    loadData()
  })

  // Restore popup when characters load
  watch(characters, () => {
    if (characters.value.length > 0) {
      restorePopupFromParams()
    }
  })

  // Handle viewport changes
  const onViewportChange = () => {
    if (vueFlowRef.value) {
      const viewport = vueFlowRef.value.getViewport()
      saveViewport(viewport)
    }
  }

  // Handle when pane is ready to restore viewport
  const onPaneReady = () => {
    const savedViewport = getViewport()
    if (savedViewport && vueFlowRef.value) {
      vueFlowRef.value.setViewport(savedViewport)
    }
  }
</script>

<style scoped>
  .encounter-builder {
    height: 100%;
    width: 100%;
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .encounter-builder-container {
    height: 100%;
    width: 100%;
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .encounter-canvas {
    height: 100%;
    width: 100%;
    background: var(--gray-50);
    flex: 1;
  }

  /* Add Encounter Button Container */
  .add-encounter-container {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 1000;
  }

  .add-encounter-btn {
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-button);
    margin-bottom: 4px;
  }

  .add-encounter-btn:hover {
    background: var(--primary-dark);
    transform: scale(1.1);
    box-shadow: var(--shadow-button-hover);
  }

  .add-encounter-btn:active {
    transform: scale(1.05);
  }

  .add-encounter-label {
    font-size: 10px;
    color: var(--gray-500);
    text-align: center;
    line-height: 1.2;
    font-weight: 500;
    white-space: nowrap;
  }

  /* Save Canvas Button */
  .save-canvas-btn {
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 50%;
    background: var(--secondary-color);
    color: white;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-secondary);
    margin-bottom: 4px;
    margin-top: 8px;
  }

  .save-canvas-btn:hover:not(:disabled) {
    background: var(--secondary-dark);
    transform: scale(1.1);
    box-shadow: var(--shadow-secondary-hover);
  }

  .save-canvas-btn:active:not(:disabled) {
    transform: scale(1.05);
  }

  .save-canvas-btn:disabled {
    background: var(--secondary-color);
    cursor: not-allowed;
    opacity: 0.6;
  }

  .save-canvas-label {
    font-size: 10px;
    color: var(--gray-500);
    text-align: center;
    line-height: 1.2;
    font-weight: 500;
    white-space: nowrap;
  }

  /* Edge styling for better interaction - Override Vue Flow defaults */
  :deep(.vue-flow__edge) {
    cursor: pointer;
    stroke: var(--border-default) !important;
    stroke-width: 3px !important;
  }

  :deep(.vue-flow__edge path) {
    stroke: var(--border-default) !important;
    stroke-width: 3px !important;
  }

  :deep(.vue-flow__edge:hover) {
    stroke: var(--text-primary) !important;
    stroke-width: 4px !important;
  }

  :deep(.vue-flow__edge:hover path) {
    stroke: var(--text-primary) !important;
    stroke-width: 4px !important;
  }

  :deep(.vue-flow__edge.selected) {
    stroke: var(--danger-color) !important;
    stroke-width: 4px !important;
  }

  :deep(.vue-flow__edge.selected path) {
    stroke: var(--danger-color) !important;
    stroke-width: 4px !important;
  }

  /* Override any Vue Flow default colors */
  :deep(.vue-flow__edge-default) {
    stroke: var(--border-default) !important;
  }

  :deep(.vue-flow__edge-straight) {
    stroke: var(--border-default) !important;
  }

  /* Loading and error states */
  .shared-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 1.2em;
    color: var(--gray-500);
  }

  .shared-error {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 1.2em;
    color: #dc3545;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    margin: 20px;
    padding: 20px;
  }

  /* Screen reader only content */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
</style>
