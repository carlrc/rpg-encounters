<template>
  <div class="encounter-node" :style="encounterStyle">
    <!-- Connection handles - one per side, each can be both source and target -->
    <Handle
      id="right"
      type="source"
      position="right"
      class="connection-handle right-handle"
      :style="{ right: '-6px', top: '50%', transform: 'translateY(-50%)' }"
    />
    <Handle
      id="left"
      type="source"
      position="left"
      class="connection-handle left-handle"
      :style="{ left: '-6px', top: '50%', transform: 'translateY(-50%)' }"
    />
    <Handle
      id="bottom"
      type="source"
      position="bottom"
      class="connection-handle bottom-handle"
      :style="{ bottom: '-6px', left: '50%', transform: 'translateX(-50%)' }"
    />
    <Handle
      id="top"
      type="source"
      position="top"
      class="connection-handle top-handle"
      :style="{ top: '-6px', left: '50%', transform: 'translateX(-50%)' }"
    />

    <div class="encounter-header">
      <h4
        v-if="!isEditingName"
        @click="startEditingName"
        class="encounter-name"
        :title="'Click to edit encounter name'"
      >
        {{ encounter.name }}
      </h4>
      <input
        v-else
        v-model="editingName"
        @blur="saveEncounterName"
        @keyup.enter="saveEncounterName"
        @keyup.escape="cancelEditingName"
        class="encounter-name-input"
        ref="nameInput"
        :placeholder="encounter.name"
      />
      <div class="encounter-actions">
        <button
          @click="toggleDescription"
          class="info-btn"
          :class="{ active: showDescription }"
          :title="showDescription ? 'Hide description' : 'Show description'"
          :aria-expanded="showDescription"
          :aria-describedby="showDescription ? `description-${encounter.id}` : null"
          aria-label="Toggle encounter description"
        >
          ⓘ
        </button>
      </div>
    </div>

    <!-- Encounter Description Section - Floating Box -->
    <div
      v-if="showDescription"
      class="encounter-description-section"
      :id="`description-${encounter.id}`"
      role="tooltip"
      @click.stop
    >
      <div
        v-if="!isEditingDescription"
        @click="startEditingDescription"
        @mousedown.stop
        @mousemove.stop
        @mouseup.stop
        @dragstart.prevent
        class="encounter-description-display"
        :title="'Click to edit encounter description'"
      >
        {{ encounter.description || 'No description available. Click to add one.' }}
      </div>
      <BaseTextareaWithCharacterCounter
        v-else
        v-model="editingDescription"
        @blur="saveEncounterDescription"
        @keyup.ctrl.enter="saveEncounterDescription"
        @keyup.escape="cancelEditingDescription"
        @mousedown.stop
        @mousemove.stop
        @mouseup.stop
        @dragstart.prevent
        :max-characters="500"
        placeholder="Enter encounter description..."
        ref="descriptionInput"
        class="encounter-description-input"
      />
    </div>

    <div class="players-section">
      <div class="section-header">Players</div>
      <div class="players-scroll">
        <div
          v-for="player in encounter.players || []"
          :key="player.id"
          class="character-avatar player-chip"
          :title="player.rl_name || player.name"
        >
          <button
            class="remove-character-btn"
            @click.stop="removePlayer(player.id)"
            title="Remove player"
          >
            ×
          </button>
          <img
            v-if="player.avatar"
            :src="player.avatar"
            :alt="player.rl_name || player.name"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            <span class="avatar-initials">{{ getInitials(player.rl_name || player.name) }}</span>
          </div>
          <div class="character-info">
            <span class="character-profession">{{ player.rl_name || 'Unknown Player' }}</span>
            <span class="character-name">{{ player.name }}</span>
          </div>
        </div>

        <div
          v-if="availablePlayers.length > 0"
          class="character-avatar player-chip add-player-chip"
          title="Add player to encounter"
        >
          <button
            @click="toggleAddPlayerDropdown"
            class="add-encounter-btn add-player-btn add-assignee-btn"
            :class="{ active: showAddPlayer }"
          >
            +
          </button>
          <span class="player-add-label">Add Player</span>
        </div>
      </div>

      <div v-if="showAddPlayer" class="add-assignee-dropdown player-dropdown" @click.stop>
        <div class="dropdown-header">Add Player:</div>
        <div
          class="character-options"
          @wheel.stop
          @scroll.stop
          @mousedown.stop
          @mousemove.stop
          @mouseup.stop
        >
          <div
            v-for="player in availablePlayers"
            :key="player.id"
            class="character-option"
            @click="addPlayer(player.id)"
          >
            <div class="option-avatar">
              <img
                v-if="player.avatar"
                :src="player.avatar"
                :alt="player.rl_name || player.name"
                class="option-avatar-image"
              />
              <div v-else class="option-avatar-placeholder">
                <span class="option-avatar-initials">{{
                  getInitials(player.rl_name || player.name)
                }}</span>
              </div>
            </div>
            <div class="option-info">
              <div class="option-name">{{ player.rl_name || player.name }}</div>
              <div class="option-profession">{{ player.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="characters-section">
      <div class="section-header">Characters</div>
      <div class="character-grid">
        <div
          v-for="character in encounter.characters"
          :key="character.id"
          class="character-avatar"
          @click="$emit('open-encounter', character, encounter.id)"
          :title="character.name"
        >
          <button
            class="remove-character-btn"
            @click.stop="removeCharacter(character.id)"
            title="Remove character"
          >
            ×
          </button>
          <img
            v-if="character.avatar"
            :src="character.avatar"
            :alt="character.name"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            <span class="avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
          <div class="character-info">
            <span class="character-profession">{{ character.profession }}</span>
            <span class="character-name">{{ character.name }}</span>
          </div>
        </div>

        <div
          v-if="availableCharacters.length > 0"
          class="character-avatar add-character-tile"
          title="Add character to encounter"
        >
          <button
            @click="toggleAddCharacterDropdown"
            class="add-encounter-btn add-character-btn add-assignee-btn"
            :class="{ active: showAddCharacter }"
          >
            +
          </button>
          <span class="character-name">Add Character</span>
        </div>
      </div>

      <div v-if="showAddCharacter" class="add-assignee-dropdown character-dropdown" @click.stop>
        <div class="dropdown-header">Add Character:</div>
        <div
          class="character-options"
          @wheel.stop
          @scroll.stop
          @mousedown.stop
          @mousemove.stop
          @mouseup.stop
        >
          <div
            v-for="character in availableCharacters"
            :key="character.id"
            class="character-option"
            @click="addCharacter(character.id)"
          >
            <div class="option-avatar">
              <img
                v-if="character.avatar"
                :src="character.avatar"
                :alt="character.name"
                class="option-avatar-image"
              />
              <div v-else class="option-avatar-placeholder">
                <span class="option-avatar-initials">{{ getInitials(character.name) }}</span>
              </div>
            </div>
            <div class="option-info">
              <div class="option-name">{{ character.name }}</div>
              <div class="option-profession">{{ character.profession }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
  import { Handle } from '@vue-flow/core'
  import { getInitials } from '../utils/avatarUtils.js'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'

  export default {
    name: 'EncounterNode',
    components: {
      Handle,
      BaseTextareaWithCharacterCounter,
    },
    props: {
      encounter: {
        type: Object,
        required: true,
      },
      availableCharacters: {
        type: Array,
        default: () => [],
      },
      availablePlayers: {
        type: Array,
        default: () => [],
      },
    },
    emits: [
      'open-encounter',
      'add-character',
      'remove-character',
      'add-player',
      'remove-player',
      'update-encounter-name',
      'update-encounter-description',
      'clear-auto-open-description',
    ],
    setup(props, { emit }) {
      const showAddCharacter = ref(false)
      const showAddPlayer = ref(false)
      const showDescription = ref(false)
      const isEditingName = ref(false)
      const editingName = ref('')
      const nameInput = ref(null)
      const isEditingDescription = ref(false)
      const editingDescription = ref('')
      const descriptionInput = ref(null)

      const addCharacter = (characterId) => {
        emit('add-character', props.encounter.id, characterId)
        showAddCharacter.value = false
      }

      const removeCharacter = (characterId) => {
        emit('remove-character', props.encounter.id, characterId)
      }

      const addPlayer = (playerId) => {
        emit('add-player', props.encounter.id, playerId)
        showAddPlayer.value = false
      }

      const removePlayer = (playerId) => {
        emit('remove-player', props.encounter.id, playerId)
      }

      const toggleAddCharacterDropdown = () => {
        showAddCharacter.value = !showAddCharacter.value
        if (showAddCharacter.value) {
          showAddPlayer.value = false
        }
      }

      const toggleAddPlayerDropdown = () => {
        showAddPlayer.value = !showAddPlayer.value
        if (showAddPlayer.value) {
          showAddCharacter.value = false
        }
      }

      const startEditingName = () => {
        isEditingName.value = true
        editingName.value = props.encounter.name
        // Focus the input on next tick
        nextTick(() => {
          if (nameInput.value) {
            nameInput.value.focus()
            nameInput.value.select()
          }
        })
      }

      const saveEncounterName = () => {
        if (editingName.value.trim() && editingName.value.trim() !== props.encounter.name) {
          emit('update-encounter-name', props.encounter.id, editingName.value.trim())
        }
        isEditingName.value = false
        editingName.value = ''
      }

      const cancelEditingName = () => {
        isEditingName.value = false
        editingName.value = ''
      }

      const toggleDescription = () => {
        showDescription.value = !showDescription.value
      }

      // Handle click outside to close description
      const handleClickOutside = (event) => {
        const encounterNode = event.target.closest('.encounter-node')
        const isInfoButton = event.target.closest('.info-btn')
        const isDescriptionSection = event.target.closest('.encounter-description-section')
        const isDropdown = event.target.closest('.add-assignee-dropdown')
        const isAddButton = event.target.closest('.add-assignee-btn')

        if (!isDropdown && !isAddButton) {
          showAddCharacter.value = false
          showAddPlayer.value = false
        }

        if (!encounterNode && !isInfoButton && !isDescriptionSection && showDescription.value) {
          showDescription.value = false
        }
      }

      // Handle escape key to close description
      const handleEscapeKey = (event) => {
        if (event.key === 'Escape' && showDescription.value) {
          showDescription.value = false
        }
      }

      const startEditingDescription = () => {
        isEditingDescription.value = true
        editingDescription.value = props.encounter.description || ''
        // Focus will be handled by the BaseTextareaWithCharacterCounter component
        nextTick(() => {
          // Component will auto-focus when rendered
        })
      }

      const saveEncounterDescription = () => {
        // Always emit the update, even if it's empty (allows clearing descriptions)
        const newDescription = editingDescription.value.trim()
        emit('update-encounter-description', props.encounter.id, newDescription)

        // Clear auto-open flag after first save
        if (props.encounter.autoOpenDescription) {
          emit('clear-auto-open-description', props.encounter.id)
        }

        isEditingDescription.value = false
        editingDescription.value = ''
      }

      const cancelEditingDescription = () => {
        isEditingDescription.value = false
        editingDescription.value = ''
      }

      // Auto-open description for new encounters
      const handleAutoOpenDescription = () => {
        if (props.encounter.autoOpenDescription) {
          showDescription.value = true
          nextTick(() => {
            startEditingDescription()
          })
        }
      }

      // Watch for encounter changes to handle auto-open
      watch(
        () => props.encounter.autoOpenDescription,
        (newValue) => {
          if (newValue) {
            handleAutoOpenDescription()
          }
        },
        { immediate: true }
      )

      // Handle auto-open on mount for existing encounters with the flag
      onMounted(() => {
        if (props.encounter.autoOpenDescription) {
          handleAutoOpenDescription()
        }
        // Add event listeners for click outside and escape key
        document.addEventListener('click', handleClickOutside)
        document.addEventListener('keydown', handleEscapeKey)
      })

      onUnmounted(() => {
        // Clean up event listeners
        document.removeEventListener('click', handleClickOutside)
        document.removeEventListener('keydown', handleEscapeKey)
      })

      return {
        showAddCharacter,
        showAddPlayer,
        showDescription,
        isEditingName,
        editingName,
        nameInput,
        isEditingDescription,
        editingDescription,
        descriptionInput,
        addCharacter,
        removeCharacter,
        addPlayer,
        removePlayer,
        startEditingName,
        saveEncounterName,
        cancelEditingName,
        toggleDescription,
        toggleAddCharacterDropdown,
        toggleAddPlayerDropdown,
        startEditingDescription,
        saveEncounterDescription,
        cancelEditingDescription,
        getInitials,
      }
    },
    computed: {
      encounterStyle() {
        const cardWidth = 450
        const horizontalPadding = 24
        const charWidth = 120
        const gapBetweenItems = 12
        const playerBaseHeight = 110
        const playerExpandedHeight = 140
        const characterRowBaseHeight = 170
        const characterRowAdditionalHeight = 130

        const charactersCount = this.encounter.characters?.length || 0
        const hasAddCharacterTile = this.availableCharacters.length > 0
        const totalCharacterTiles = charactersCount + (hasAddCharacterTile ? 1 : 0)

        const hasPlayers = (this.encounter.players?.length || 0) > 0
        const hasAddPlayerTile = this.availablePlayers.length > 0
        const playersHeight =
          hasPlayers || hasAddPlayerTile ? playerExpandedHeight : playerBaseHeight

        const contentWidth = Math.max(0, cardWidth - horizontalPadding)
        const itemsPerRow = Math.max(1, Math.floor(contentWidth / (charWidth + gapBetweenItems)))
        const characterRows = Math.max(1, Math.ceil(totalCharacterTiles / itemsPerRow))
        const characterHeight =
          characterRowBaseHeight + (characterRows - 1) * characterRowAdditionalHeight

        const totalHeight = playersHeight + characterHeight

        return {
          width: `${cardWidth}px`,
          height: `${totalHeight}px`,
          minHeight: `${playerBaseHeight + characterRowBaseHeight}px`,
        }
      },
    },
  }
</script>

<style scoped>
  .encounter-node {
    background: var(--bg-white);
    border: 2px solid var(--primary-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md);
    box-shadow: var(--shadow-card);
    position: relative;
    min-width: 150px;
    min-height: 100px;
  }

  .encounter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
    border-bottom: 1px solid var(--border-default);
    padding-bottom: var(--spacing-xs);
  }

  .encounter-header h4 {
    margin: 0;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--text-label);
  }

  .encounter-name {
    cursor: pointer;
    padding: var(--spacing-xs) var(--spacing-xs);
    border-radius: var(--radius-sm);
    transition: background-color var(--transition-fast);
  }

  .encounter-name:hover {
    background-color: var(--bg-light);
  }

  .encounter-name-input {
    margin: 0;
    padding: var(--spacing-xs) var(--spacing-xs);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--text-label);
    border: 1px solid var(--primary-color);
    border-radius: var(--radius-sm);
    background: var(--bg-white);
    outline: none;
    min-width: 80px;
    max-width: 200px;
  }

  .encounter-name-input:focus {
    border-color: var(--primary-dark);
    box-shadow: var(--shadow-encounter-focus);
  }

  .encounter-actions {
    display: flex;
    gap: var(--spacing-xs);
  }

  .info-btn {
    width: 20px;
    height: 20px;
    border: none;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    color: white;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
  }

  .info-btn:hover {
    background: var(--primary-dark);
    transform: scale(1.1);
  }

  .info-btn.active {
    background: var(--success-color);
  }

  /* Encounter Description Section - Floating Box */
  .encounter-description-section {
    position: absolute;
    bottom: calc(100% + var(--spacing-sm));
    left: 0;
    right: 0;
    height: 200px;
    overflow-y: auto;
    z-index: 1000;
    background: var(--bg-white);
    border: 2px solid var(--primary-color);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card-hover);
    padding: var(--spacing-md);
    animation: fadeInSlide var(--transition-fast);
    display: flex;
    flex-direction: column;
  }

  @keyframes fadeInSlide {
    from {
      opacity: 0;
      transform: translateY(var(--spacing-sm));
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Add a small arrow pointing down to the info button */
  .encounter-description-section::before {
    content: '';
    position: absolute;
    bottom: -8px;
    right: var(--spacing-md);
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid var(--primary-color);
  }

  .encounter-description-section::after {
    content: '';
    position: absolute;
    bottom: -6px;
    right: calc(var(--spacing-md) + 1px);
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-top: 7px solid var(--bg-white);
  }

  .encounter-description-display {
    cursor: pointer;
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    transition: background-color var(--transition-fast);
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    line-height: 1.4;
    flex: 1;
    overflow-y: auto;
    background: var(--bg-light);
    border: 1px solid var(--border-default);
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .encounter-description-display:hover {
    background-color: var(--border-default);
    border-color: var(--primary-color);
  }

  /* Scrollbar styling for description display */
  .encounter-description-display::-webkit-scrollbar {
    width: 4px;
  }

  .encounter-description-display::-webkit-scrollbar-track {
    background: var(--bg-light);
    border-radius: 2px;
  }

  .encounter-description-display::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 2px;
  }

  .encounter-description-display::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
  }

  .encounter-description-input {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    font-family: inherit;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  /* Override the BaseTextareaWithCharacterCounter styles for better integration */
  .encounter-description-input :deep(.shared-word-counter-field) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .encounter-description-input :deep(.shared-textarea) {
    border: 1px solid var(--primary-color);
    border-radius: var(--radius-sm);
    background: var(--bg-white);
    outline: none;
    resize: none;
    flex: 1;
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    font-family: inherit;
    user-select: text;
    -webkit-user-select: text;
    -moz-user-select: text;
    -ms-user-select: text;
  }

  .encounter-description-input :deep(.shared-textarea:focus) {
    border-color: var(--primary-dark);
    box-shadow: var(--shadow-encounter-focus);
  }

  .encounter-description-input :deep(.shared-word-counter) {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    text-align: right;
    margin-top: var(--spacing-xs);
  }

  .encounter-description-input :deep(.shared-word-counter.over-limit) {
    color: var(--danger-color);
    font-weight: var(--font-weight-semibold);
  }

  .players-section {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    padding-top: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    position: relative;
  }

  .characters-section {
    position: relative;
  }

  .section-header {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .players-scroll {
    display: flex;
    gap: var(--spacing-md);
    align-items: flex-start;
    overflow-x: auto;
    overflow-y: visible;
    padding: var(--spacing-sm) 0 var(--spacing-xs);
  }

  .player-chip {
    flex: 0 0 auto;
    cursor: default;
  }

  .player-chip:hover {
    background: var(--bg-light);
  }

  .add-player-chip {
    align-items: center;
    justify-content: center;
    min-width: 100px;
  }

  .add-player-btn {
    margin-bottom: var(--spacing-xs);
  }

  /* Match spacing under "+ Add Player" for consistency */
  .add-character-btn {
    margin-bottom: var(--spacing-xs);
  }

  .player-add-label {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    text-align: center;
  }

  .character-grid {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    justify-content: flex-start;
    align-items: flex-start;
    min-height: 80px;
    margin-top: var(--spacing-sm);
  }

  .add-character-tile {
    align-items: center;
    justify-content: center;
  }

  .add-assignee-dropdown {
    position: absolute;
    top: calc(100% + var(--spacing-xs));
    left: 0;
    right: 0;
    background: var(--bg-white);
    border: 2px solid var(--primary-color);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card-hover);
    z-index: 1000;
    max-height: 200px;
    overflow-y: auto;
  }

  .player-dropdown {
    top: calc(100% + var(--spacing-xs));
  }

  .character-dropdown {
    top: calc(100% + var(--spacing-xs));
  }

  .dropdown-header {
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--bg-light);
    border-bottom: 1px solid var(--border-default);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--text-secondary);
  }

  .character-options {
    max-height: 150px;
    overflow-y: auto;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    transition: background-color var(--transition-fast);
    border-bottom: 1px solid var(--bg-light);
  }

  .character-option:hover {
    background: var(--color-encounter-hover);
  }

  .character-option:last-child {
    border-bottom: none;
  }

  .option-avatar {
    flex-shrink: 0;
  }

  .option-avatar-image {
    width: 24px;
    height: 24px;
    border-radius: var(--radius-round);
    object-fit: cover;
    border: 1px solid var(--primary-color);
  }

  .option-avatar-placeholder {
    width: 24px;
    height: 24px;
    border-radius: var(--radius-round);
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--primary-darker);
  }

  /* Player dropdown avatars use secondary accents */
  .player-dropdown .option-avatar-image {
    border-color: var(--secondary-color);
  }

  .player-dropdown .option-avatar-placeholder {
    background: linear-gradient(135deg, var(--secondary-color), var(--secondary-dark));
    border-color: var(--secondary-darker);
  }

  .option-avatar-initials {
    color: white;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
  }

  .option-info {
    flex: 1;
    min-width: 0;
  }

  .option-name {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--text-label);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .option-profession {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .character-avatar {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    position: relative;
    width: 120px;
    flex-shrink: 0;
  }

  .character-avatar:hover {
    background: var(--bg-light);
    transform: scale(1.05);
  }

  .character-avatar:hover .remove-character-btn {
    opacity: 1;
  }

  .remove-character-btn {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 16px;
    height: 16px;
    border: none;
    border-radius: var(--radius-round);
    background: var(--danger-color);
    color: white;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: all var(--transition-fast);
    z-index: 10;
  }

  .remove-character-btn:hover {
    background: var(--danger-dark);
    transform: scale(1.1);
  }

  .avatar-image {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-round);
    object-fit: cover;
    border: 2px solid var(--primary-color);
    margin-bottom: 2px;
  }

  .avatar-placeholder {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-round);
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid var(--primary-darker);
    margin-bottom: 2px;
  }

  /* Player chips use secondary accents */
  .player-chip .avatar-image {
    border-color: var(--secondary-color);
  }

  .player-chip .avatar-placeholder {
    background: linear-gradient(135deg, var(--secondary-color), var(--secondary-dark));
    border-color: var(--secondary-darker);
  }

  .avatar-initials {
    color: white;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
  }

  .character-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    min-height: 32px;
  }

  .character-profession {
    font-size: var(--font-size-sm);
    color: var(--text-label);
    font-weight: var(--font-weight-semibold);
    text-align: center;
    line-height: 1.2;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
  }

  .character-name {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    text-align: center;
    line-height: 1.2;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Add buttons for player/character assignments */
  .add-encounter-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: var(--radius-round);
    background: var(--addition-alpha-15);
    color: var(--addition-dark);
    border: 1px solid var(--addition-color);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    box-shadow: var(--shadow-secondary);
  }

  .add-encounter-btn:hover {
    background: var(--addition-alpha-20);
    border-color: var(--addition-dark);
    transform: scale(1.1);
    box-shadow: var(--shadow-secondary-hover);
  }

  .add-character-btn.active {
    background: var(--addition-alpha-20);
    border-color: var(--addition-dark);
    transform: rotate(45deg);
  }

  .add-player-btn.active {
    background: var(--addition-alpha-20);
    border-color: var(--addition-dark);
    transform: rotate(45deg);
  }

  .add-character-btn.active:hover {
    background: var(--addition-alpha-20);
  }

  .add-player-btn.active:hover {
    background: var(--addition-alpha-20);
  }

  /* Scrollbar styling for dropdown */
  .character-options::-webkit-scrollbar {
    width: 4px;
  }

  .character-options::-webkit-scrollbar-track {
    background: var(--bg-light);
  }

  .character-options::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 2px;
  }

  .character-options::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
  }

  /* Scrollbar styling for description section */
  .encounter-description-section::-webkit-scrollbar {
    width: 6px;
  }

  .encounter-description-section::-webkit-scrollbar-track {
    background: var(--bg-light);
    border-radius: 3px;
  }

  .encounter-description-section::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 3px;
  }

  .encounter-description-section::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
  }

  /* Connection handle styles */
  .connection-handle {
    width: 12px;
    height: 12px;
    border: 2px solid var(--border-default);
    border-radius: var(--radius-round);
    background: var(--bg-white);
    position: absolute;
    transition: all var(--transition-fast);
    cursor: crosshair;
    z-index: 10;
  }

  .connection-handle:hover {
    width: 16px;
    height: 16px;
    border-width: 3px;
    background: var(--text-primary);
    box-shadow: var(--shadow-voice-hover);
  }

  /* Ensure encounter node has relative positioning for absolute handles */
  .encounter-node {
    position: relative;
  }
</style>
