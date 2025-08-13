<template>
  <div class="world-builder">
    <div v-if="loading" class="shared-loading">Loading world data...</div>
    <div v-else-if="error" class="shared-error">{{ error }}</div>

    <div v-else class="world-builder-container">
      <VueFlow
        v-model="elements"
        class="world-canvas"
        :default-viewport="{ zoom: 1 }"
        @connect="onConnect"
        :connection-line-style="{ stroke: '#007bff', strokeWidth: 2 }"
        :is-valid-connection="isValidConnection"
        :connect-on-click="false"
      >
        <!-- Custom Room Node -->
        <template #node-room="{ data, id }">
          <RoomNode
            :room="{ ...data, id }"
            :available-characters="getAvailableCharactersForRoom(data)"
            @open-encounter="openCharacterEncounter"
            @add-character="addCharacterToRoom"
            @remove-character="removeCharacterFromRoom"
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

      // Vue Flow elements (just 2 rooms, no connections)
      const elements = ref([])

      // Get available characters for a specific room (exclude characters already in that room)
      const getAvailableCharactersForRoom = (roomData) => {
        if (!roomData || !roomData.characters) return characters.value

        const roomCharacterIds = new Set(roomData.characters.map((char) => char.id))
        return characters.value.filter((char) => !roomCharacterIds.has(char.id))
      }

      // Create simple 2-room world with some initial characters
      const createSimpleWorld = () => {
        if (characters.value.length === 0) return

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
          characters.value = await apiService.getCharacters()
          createSimpleWorld()
        } catch (err) {
          error.value = 'Failed to load characters'
          console.error('Character loading failed:', err)
        }
      }

      const loadData = async () => {
        loading.value = true
        error.value = null

        try {
          await Promise.all([loadGameData(), loadCharacters()])
        } catch (err) {
          error.value = 'Failed to load world data'
          console.error('Data loading failed:', err)
        } finally {
          loading.value = false
        }
      }

      // Character management
      const addCharacterToRoom = (roomId, characterId) => {
        const character = characters.value.find((c) => c.id === characterId)
        if (!character) return

        // Find the room and add the character
        const roomIndex = elements.value.findIndex((el) => el.id === roomId)
        if (roomIndex !== -1) {
          const room = elements.value[roomIndex]

          // Check if character is already in this room
          const isAlreadyInRoom = room.data.characters.some((char) => char.id === characterId)

          if (!isAlreadyInRoom) {
            // Simply add character to the room (can be in multiple rooms)
            room.data.characters.push(character)

            // Force reactivity update
            elements.value = [...elements.value]
          }
        }
      }

      const removeCharacterFromRoom = (roomId, characterId) => {
        // Find the room and remove the character
        const roomIndex = elements.value.findIndex((el) => el.id === roomId)
        if (roomIndex !== -1) {
          const room = elements.value[roomIndex]
          room.data.characters = room.data.characters.filter((char) => char.id !== characterId)

          // Force reactivity update
          elements.value = [...elements.value]
        }
      }

      // Character encounter handlers
      const openCharacterEncounter = (character) => {
        selectedCharacter.value = character
        showEncounterPopup.value = true
      }

      const closeEncounterPopup = () => {
        showEncounterPopup.value = false
        selectedCharacter.value = null
      }

      // Handle new connections created by dragging
      const onConnect = (connection) => {
        console.log('Connection attempt:', connection)

        // Check if connection already exists (in either direction)
        const existingEdge = elements.value.find(
          (el) =>
            (el.source === connection.source && el.target === connection.target) ||
            (el.source === connection.target && el.target === connection.source)
        )

        if (existingEdge) {
          console.log('Connection already exists')
          return
        }

        const newEdge = {
          id: `edge-${connection.source}-${connection.target}-${Date.now()}`,
          source: connection.source,
          target: connection.target,
          type: 'straight',
          style: {
            stroke: '#007bff',
            strokeWidth: 2,
          },
        }

        console.log('Adding new edge:', newEdge)
        elements.value = [...elements.value, newEdge]
      }

      // Validate connections - allow all connections between different nodes
      const isValidConnection = (connection) => {
        console.log('Validating connection:', connection)
        return connection.source !== connection.target
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
        getAvailableCharactersForRoom,
        addCharacterToRoom,
        removeCharacterFromRoom,
        openCharacterEncounter,
        closeEncounterPopup,
        onConnect,
        isValidConnection,
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
  }

  .world-canvas {
    height: 100%;
    width: 100%;
    background: #f8f9fa;
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
</style>
