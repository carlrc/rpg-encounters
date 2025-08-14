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
      </div>

      <VueFlow
        v-model="elements"
        class="encounter-canvas"
        :default-viewport="{ zoom: 1 }"
        :min-zoom="0.1"
        :max-zoom="4"
        @connect="onConnect"
        @edge-click="onEdgeClick"
        :connection-line-style="{ stroke: '#007bff', strokeWidth: 2 }"
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
            @open-encounter="openCharacterEncounter"
            @add-character="addCharacterToEncounter"
            @remove-character="removeCharacterFromEncounter"
            @update-encounter-name="updateEncounterName"
            @update-encounter-description="updateEncounterDescription"
          />
        </template>
      </VueFlow>

      <!-- Character encounter popup -->
      <CharacterEncounterPopup
        :character="selectedCharacter"
        :is-open="showEncounterPopup"
        @close="closeEncounterPopup"
      />
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from 'vue'
  import { VueFlow } from '@vue-flow/core'
  import '@vue-flow/core/dist/style.css'
  import EncounterNode from './EncounterNode.vue'
  import CharacterEncounterPopup from './CharacterEncounterPopup.vue'
  import apiService from '../services/api.js'
  import { useGameData } from '../composables/useGameData.js'

  export default {
    name: 'EncounterBuilder',
    components: {
      VueFlow,
      EncounterNode,
      CharacterEncounterPopup,
    },
    setup() {
      const { gameData, loadGameData } = useGameData()

      // State
      const characters = ref([])
      const loading = ref(true)
      const error = ref(null)
      const selectedCharacter = ref(null)
      const showEncounterPopup = ref(false)
      const vueFlowRef = ref(null)

      // Vue Flow elements (just 2 rooms, no connections)
      const elements = ref([])

      // Get available characters for a specific encounter (exclude characters already in that encounter)
      const getAvailableCharactersForEncounter = (encounterData) => {
        if (!encounterData || !Array.isArray(encounterData.characters)) return characters.value

        const encounterCharacterIds = new Set(encounterData.characters.map((char) => char.id))
        return characters.value.filter((char) => !encounterCharacterIds.has(char.id))
      }

      // Create simple 2-encounter world with some initial characters
      const createSimpleWorld = () => {
        if (!Array.isArray(characters.value) || characters.value.length === 0) {
          // Create empty encounters if no characters available
          const encounters = [
            {
              id: 'encounter-1',
              type: 'encounter',
              position: { x: 200, y: 150 },
              data: {
                name: 'Tavern',
                description:
                  'A cozy tavern filled with the warm glow of candlelight and the cheerful chatter of patrons. The air is thick with the aroma of roasted meat and ale.',
                characters: [],
              },
            },
            {
              id: 'encounter-2',
              type: 'encounter',
              position: { x: 500, y: 150 },
              data: {
                name: 'Forest',
                description:
                  'A dense woodland with towering ancient trees whose branches form a natural canopy. Dappled sunlight filters through the leaves, creating dancing shadows on the forest floor.',
                characters: [],
              },
            },
          ]
          elements.value = encounters
          return
        }

        // Just 2 encounters with some initial characters
        const encounters = [
          {
            id: 'encounter-1',
            type: 'encounter',
            position: { x: 200, y: 150 },
            data: {
              name: 'Tavern',
              description:
                'A cozy tavern filled with the warm glow of candlelight and the cheerful chatter of patrons. The air is thick with the aroma of roasted meat and ale.',
              characters: characters.value.slice(0, 2), // First 2 characters
            },
          },
          {
            id: 'encounter-2',
            type: 'encounter',
            position: { x: 500, y: 150 },
            data: {
              name: 'Forest',
              description:
                'A dense woodland with towering ancient trees whose branches form a natural canopy. Dappled sunlight filters through the leaves, creating dancing shadows on the forest floor.',
              characters: characters.value.slice(2, 4), // Next 2 characters
            },
          },
        ]

        // Start with no connections - let user create them manually
        elements.value = encounters
      }

      // Load characters from API
      const loadCharacters = async () => {
        try {
          const loadedCharacters = await apiService.getCharacters()
          if (!Array.isArray(loadedCharacters)) {
            throw new Error('Invalid characters data received from API')
          }
          characters.value = loadedCharacters
          createSimpleWorld()
        } catch (err) {
          const errorMessage = err.message || 'Failed to load characters'
          error.value = errorMessage
          console.error('Character loading failed:', err)
          throw err // Re-throw to be caught by loadData
        }
      }

      const loadData = async () => {
        loading.value = true
        error.value = null

        try {
          await Promise.all([loadGameData(), loadCharacters()])
        } catch (err) {
          const errorMessage = err.message || 'Failed to load world data'
          error.value = `Encounter Builder Error: ${errorMessage}`
          console.error('Data loading failed:', err)
        } finally {
          loading.value = false
        }
      }

      // Character management
      const addCharacterToEncounter = (encounterId, characterId) => {
        // Validate inputs
        if (!encounterId || !characterId) {
          console.warn('Invalid encounterId or characterId provided to addCharacterToEncounter')
          return
        }

        const character = characters.value.find((c) => c.id === characterId)
        if (!character) {
          console.warn(`Character with id ${characterId} not found`)
          return
        }

        // Find the encounter and add the character
        const encounterIndex = elements.value.findIndex((el) => el.id === encounterId)
        if (encounterIndex === -1) {
          console.warn(`Encounter with id ${encounterId} not found`)
          return
        }

        const encounter = elements.value[encounterIndex]

        // Ensure encounter.data.characters exists
        if (!Array.isArray(encounter.data.characters)) {
          encounter.data.characters = []
        }

        // Check if character is already in this encounter
        const isAlreadyInEncounter = encounter.data.characters.some(
          (char) => char.id === characterId
        )

        if (!isAlreadyInEncounter) {
          // Simply add character to the encounter (can be in multiple encounters)
          encounter.data.characters.push(character)
        }
      }

      const removeCharacterFromEncounter = (encounterId, characterId) => {
        // Validate inputs
        if (!encounterId || !characterId) {
          console.warn(
            'Invalid encounterId or characterId provided to removeCharacterFromEncounter'
          )
          return
        }

        // Find the encounter and remove the character
        const encounterIndex = elements.value.findIndex((el) => el.id === encounterId)
        if (encounterIndex === -1) {
          console.warn(`Encounter with id ${encounterId} not found`)
          return
        }

        const encounter = elements.value[encounterIndex]

        // Ensure encounter.data.characters exists
        if (!Array.isArray(encounter.data.characters)) {
          encounter.data.characters = []
          return
        }

        encounter.data.characters = encounter.data.characters.filter(
          (char) => char.id !== characterId
        )
      }

      // Character encounter handlers
      const openCharacterEncounter = (character) => {
        // Validate character object
        if (!character || !character.id) {
          console.warn('Invalid character provided to openCharacterEncounter')
          return
        }

        selectedCharacter.value = character
        showEncounterPopup.value = true
      }

      const closeEncounterPopup = () => {
        showEncounterPopup.value = false
        selectedCharacter.value = null
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
            stroke: '#007bff',
            strokeWidth: 3,
          },
          data: {
            selectable: true,
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
      const addNewEncounter = () => {
        if (!vueFlowRef.value) return

        // Get current viewport to position encounter at center
        const viewport = vueFlowRef.value.getViewport()
        const canvasRect = vueFlowRef.value.$el.getBoundingClientRect()

        // Calculate center position accounting for viewport transform
        const centerX = (canvasRect.width / 2 - viewport.x) / viewport.zoom
        const centerY = (canvasRect.height / 2 - viewport.y) / viewport.zoom

        // Generate unique encounter ID
        const encounterId = `encounter-${Date.now()}`

        // Create new encounter object
        const newEncounter = {
          id: encounterId,
          type: 'encounter',
          position: {
            x: centerX - 150, // Offset by half encounter width for centering
            y: centerY - 75, // Offset by half encounter height for centering
          },
          data: {
            name: 'New Encounter',
            description: 'A mysterious new location waiting to be explored and described.',
            characters: [],
          },
        }

        // Add encounter to elements
        elements.value.push(newEncounter)
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

      // Handle edge clicks for selection and deletion
      const onEdgeClick = (event) => {
        const edge = event.edge
        if (edge && confirm(`Delete connection between encounters?`)) {
          const edgeIndex = elements.value.findIndex((el) => el.id === edge.id)
          if (edgeIndex !== -1) {
            elements.value.splice(edgeIndex, 1)
          }
        }
      }

      onMounted(() => {
        loadData()
      })

      return {
        loading,
        error,
        elements,
        characters,
        selectedCharacter,
        showEncounterPopup,
        vueFlowRef,
        getAvailableCharactersForEncounter,
        addCharacterToEncounter,
        removeCharacterFromEncounter,
        openCharacterEncounter,
        closeEncounterPopup,
        onConnect,
        isValidConnection,
        addNewEncounter,
        updateEncounterName,
        updateEncounterDescription,
        onEdgeClick,
      }
    },
  }
</script>

<style scoped>
  .encounter-builder {
    height: calc(100vh - 140px);
    width: 100%;
    position: relative;
  }

  .encounter-builder-container {
    height: 100%;
    width: 100%;
    position: relative;
  }

  .encounter-canvas {
    height: 100%;
    width: 100%;
    background: #f8f9fa;
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
    background: #28a745;
    color: white;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    margin-bottom: 4px;
  }

  .add-encounter-btn:hover {
    background: #218838;
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
  }

  .add-encounter-btn:active {
    transform: scale(1.05);
  }

  .add-encounter-label {
    font-size: 10px;
    color: #6c757d;
    text-align: center;
    line-height: 1.2;
    font-weight: 500;
    white-space: nowrap;
  }

  /* Edge styling for better interaction */
  :deep(.vue-flow__edge) {
    cursor: pointer;
  }

  :deep(.vue-flow__edge:hover) {
    stroke: #0056b3 !important;
    stroke-width: 4px !important;
  }

  :deep(.vue-flow__edge.selected) {
    stroke: #dc3545 !important;
    stroke-width: 4px !important;
  }

  /* Loading and error states */
  .shared-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 1.2em;
    color: #6c757d;
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
