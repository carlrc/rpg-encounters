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

    <!-- Add Character Dropdown -->
    <div v-if="showAddCharacter" class="add-character-dropdown" @click.stop>
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

      <!-- Add Character Button (reusing add encounter button styling) -->
      <div
        v-if="availableCharacters.length > 0"
        class="character-avatar"
        title="Add character to encounter"
      >
        <button
          @click="showAddCharacter = !showAddCharacter"
          class="add-encounter-btn add-character-btn"
          :class="{ active: showAddCharacter }"
        >
          +
        </button>
        <span class="character-name">Add Character</span>
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
    },
    emits: [
      'open-encounter',
      'add-character',
      'remove-character',
      'update-encounter-name',
      'update-encounter-description',
      'clear-auto-open-description',
    ],
    setup(props, { emit }) {
      const showAddCharacter = ref(false)
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
        showDescription,
        isEditingName,
        editingName,
        nameInput,
        isEditingDescription,
        editingDescription,
        descriptionInput,
        addCharacter,
        removeCharacter,
        startEditingName,
        saveEncounterName,
        cancelEditingName,
        toggleDescription,
        startEditingDescription,
        saveEncounterDescription,
        cancelEditingDescription,
        getInitials,
      }
    },
    computed: {
      encounterStyle() {
        const baseHeight = 150
        const charWidth = 120 // Fixed character width from CSS
        const encounterPadding = 24 // 12px padding on each side
        const gapBetweenChars = 12 // Gap between characters

        // Count characters + add character button if available
        const totalItems =
          (this.encounter.characters?.length || 0) + (this.availableCharacters.length > 0 ? 1 : 0)

        if (totalItems === 0) {
          return {
            width: `300px`,
            height: `${baseHeight}px`,
            minHeight: `${baseHeight}px`,
          }
        }

        // Calculate encounter width to fit at least 2 items per row
        const minWidthFor2Items = charWidth * 2 + gapBetweenChars + encounterPadding
        const calculatedWidth = Math.max(minWidthFor2Items, 300)

        // Calculate dynamic height based on number of items (characters + add button)
        const availableWidth = calculatedWidth - encounterPadding
        const itemsPerRow = Math.floor(availableWidth / (charWidth + gapBetweenChars))
        const rows = Math.ceil(totalItems / Math.max(1, itemsPerRow))

        // Add extra height for each row of items (80px per row)
        const extraHeight = Math.max(0, (rows - 1) * 80)

        return {
          width: `${calculatedWidth}px`,
          height: `${baseHeight + extraHeight}px`,
          minHeight: `${baseHeight}px`,
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
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
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
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
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

  .add-character-dropdown {
    position: absolute;
    top: 100%;
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
    background: #e3f2fd;
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

  .character-grid {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    justify-content: flex-start;
    align-items: flex-start;
    min-height: 60px;
    margin-top: var(--spacing-sm);
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

  /* Add Encounter Button (reused from EncounterBuilder) */
  .add-encounter-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: var(--radius-round);
    background: var(--success-color);
    color: white;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    box-shadow: var(--shadow-success);
  }

  .add-encounter-btn:hover {
    background: var(--success-dark);
    transform: scale(1.1);
    box-shadow: var(--shadow-success-hover);
  }

  .add-character-btn.active {
    background: var(--danger-color);
    transform: rotate(45deg);
  }

  .add-character-btn.active:hover {
    background: var(--danger-dark);
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
    border: 2px solid var(--primary-color);
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
    background: var(--primary-color);
    box-shadow: 0 0 8px rgba(0, 123, 255, 0.4);
  }

  /* Ensure encounter node has relative positioning for absolute handles */
  .encounter-node {
    position: relative;
  }
</style>
