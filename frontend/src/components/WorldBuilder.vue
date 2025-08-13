<template>
  <div class="world-builder" role="main" aria-label="World Builder Interface">
    <div v-if="loading" class="shared-loading" role="status" aria-live="polite">
      <span class="sr-only">Loading world data...</span>
      Loading world data...
    </div>
    <div v-else-if="error" class="shared-error" role="alert" aria-live="assertive">
      {{ error }}
    </div>

    <div v-else class="world-builder-container">
      <!-- Add Room Button -->
      <button
        @click="addNewRoom"
        class="add-room-btn"
        title="Add Room"
        aria-label="Add new room to world"
      >
        +
      </button>

      <VueFlow
        v-model="elements"
        class="world-canvas"
        :default-viewport="{ zoom: 1 }"
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
        aria-label="Interactive world map with rooms and characters"
        ref="vueFlowRef"
      >
        <!-- Custom Room Node -->
        <template #node-room="{ data, id }">
          <RoomNode
            :room="{ ...data, id }"
            :available-characters="getAvailableCharactersForRoom(data)"
            @open-encounter="openCharacterEncounter"
            @add-character="addCharacterToRoom"
            @remove-character="removeCharacterFromRoom"
            @update-room-name="updateRoomName"
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
  import RoomNode from './RoomNode.vue'
  import CharacterEncounterPopup from './CharacterEncounterPopup.vue'
  import apiService from '../services/api.js'
  import { useGameData } from '../composables/useGameData.js'

  export default {
    name: 'WorldBuilder',
    components: {
      VueFlow,
      RoomNode,
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

      // Get available characters for a specific room (exclude characters already in that room)
      const getAvailableCharactersForRoom = (roomData) => {
        if (!roomData || !Array.isArray(roomData.characters)) return characters.value

        const roomCharacterIds = new Set(roomData.characters.map((char) => char.id))
        return characters.value.filter((char) => !roomCharacterIds.has(char.id))
      }

      // Create simple 2-room world with some initial characters
      const createSimpleWorld = () => {
        if (!Array.isArray(characters.value) || characters.value.length === 0) {
          // Create empty rooms if no characters available
          const rooms = [
            {
              id: 'room-1',
              type: 'room',
              position: { x: 200, y: 150 },
              data: {
                name: 'Tavern',
                characters: [],
              },
            },
            {
              id: 'room-2',
              type: 'room',
              position: { x: 500, y: 150 },
              data: {
                name: 'Forest',
                characters: [],
              },
            },
          ]
          elements.value = rooms
          return
        }

        // Just 2 rooms with some initial characters
        const rooms = [
          {
            id: 'room-1',
            type: 'room',
            position: { x: 200, y: 150 },
            data: {
              name: 'Tavern',
              characters: characters.value.slice(0, 2), // First 2 characters
            },
          },
          {
            id: 'room-2',
            type: 'room',
            position: { x: 500, y: 150 },
            data: {
              name: 'Forest',
              characters: characters.value.slice(2, 4), // Next 2 characters
            },
          },
        ]

        // Start with no connections - let user create them manually
        elements.value = rooms
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
          error.value = `World Builder Error: ${errorMessage}`
          console.error('Data loading failed:', err)
        } finally {
          loading.value = false
        }
      }

      // Character management
      const addCharacterToRoom = (roomId, characterId) => {
        // Validate inputs
        if (!roomId || !characterId) {
          console.warn('Invalid roomId or characterId provided to addCharacterToRoom')
          return
        }

        const character = characters.value.find((c) => c.id === characterId)
        if (!character) {
          console.warn(`Character with id ${characterId} not found`)
          return
        }

        // Find the room and add the character
        const roomIndex = elements.value.findIndex((el) => el.id === roomId)
        if (roomIndex === -1) {
          console.warn(`Room with id ${roomId} not found`)
          return
        }

        const room = elements.value[roomIndex]

        // Ensure room.data.characters exists
        if (!Array.isArray(room.data.characters)) {
          room.data.characters = []
        }

        // Check if character is already in this room
        const isAlreadyInRoom = room.data.characters.some((char) => char.id === characterId)

        if (!isAlreadyInRoom) {
          // Simply add character to the room (can be in multiple rooms)
          room.data.characters.push(character)
        }
      }

      const removeCharacterFromRoom = (roomId, characterId) => {
        // Validate inputs
        if (!roomId || !characterId) {
          console.warn('Invalid roomId or characterId provided to removeCharacterFromRoom')
          return
        }

        // Find the room and remove the character
        const roomIndex = elements.value.findIndex((el) => el.id === roomId)
        if (roomIndex === -1) {
          console.warn(`Room with id ${roomId} not found`)
          return
        }

        const room = elements.value[roomIndex]

        // Ensure room.data.characters exists
        if (!Array.isArray(room.data.characters)) {
          room.data.characters = []
          return
        }

        room.data.characters = room.data.characters.filter((char) => char.id !== characterId)
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

      // Add new room at current viewport center
      const addNewRoom = () => {
        if (!vueFlowRef.value) return

        // Get current viewport to position room at center
        const viewport = vueFlowRef.value.getViewport()
        const canvasRect = vueFlowRef.value.$el.getBoundingClientRect()

        // Calculate center position accounting for viewport transform
        const centerX = (canvasRect.width / 2 - viewport.x) / viewport.zoom
        const centerY = (canvasRect.height / 2 - viewport.y) / viewport.zoom

        // Generate unique room ID
        const roomId = `room-${Date.now()}`

        // Create new room object
        const newRoom = {
          id: roomId,
          type: 'room',
          position: {
            x: centerX - 150, // Offset by half room width for centering
            y: centerY - 75, // Offset by half room height for centering
          },
          data: {
            name: 'New Room',
            characters: [],
          },
        }

        // Add room to elements
        elements.value.push(newRoom)
      }

      // Update room name
      const updateRoomName = (roomId, newName) => {
        const roomIndex = elements.value.findIndex((el) => el.id === roomId)
        if (roomIndex !== -1) {
          elements.value[roomIndex].data.name = newName
        }
      }

      // Handle edge clicks for selection and deletion
      const onEdgeClick = (event) => {
        const edge = event.edge
        if (edge && confirm(`Delete connection between rooms?`)) {
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
        getAvailableCharactersForRoom,
        addCharacterToRoom,
        removeCharacterFromRoom,
        openCharacterEncounter,
        closeEncounterPopup,
        onConnect,
        isValidConnection,
        addNewRoom,
        updateRoomName,
        onEdgeClick,
      }
    },
  }
</script>

<style scoped>
  .world-builder {
    height: calc(100vh - 140px);
    width: 100%;
    position: relative;
  }

  .world-builder-container {
    height: 100%;
    width: 100%;
    position: relative;
  }

  .world-canvas {
    height: 100%;
    width: 100%;
    background: #f8f9fa;
  }

  /* Add Room Button */
  .add-room-btn {
    position: absolute;
    top: 20px;
    right: 20px;
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
    z-index: 1000;
  }

  .add-room-btn:hover {
    background: #218838;
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
  }

  .add-room-btn:active {
    transform: scale(1.05);
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
