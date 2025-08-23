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
        >
          ⓘ
        </button>
      </div>
    </div>

    <!-- Encounter Description Section -->
    <div v-if="showDescription" class="encounter-description-section">
      <div
        v-if="!isEditingDescription"
        @click="startEditingDescription"
        class="encounter-description"
        :title="'Click to edit encounter description'"
      >
        {{ encounter.description || 'No description available. Click to add one.' }}
      </div>
      <textarea
        v-else
        v-model="editingDescription"
        @blur="saveEncounterDescription"
        @keyup.ctrl.enter="saveEncounterDescription"
        @keyup.escape="cancelEditingDescription"
        class="encounter-description-input"
        ref="descriptionInput"
        placeholder="Enter encounter description..."
        rows="3"
      />
    </div>

    <!-- Add Character Dropdown -->
    <div v-if="showAddCharacter" class="add-character-dropdown">
      <div class="dropdown-header">Add Character:</div>
      <div class="character-options">
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
  import { ref, nextTick, watch, onMounted } from 'vue'
  import { Handle } from '@vue-flow/core'
  import { getInitials } from '../utils/avatarUtils.js'

  export default {
    name: 'EncounterNode',
    components: {
      Handle,
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

      const startEditingDescription = () => {
        isEditingDescription.value = true
        editingDescription.value = props.encounter.description || ''
        // Focus the textarea on next tick
        nextTick(() => {
          if (descriptionInput.value) {
            descriptionInput.value.focus()
            descriptionInput.value.select()
          }
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
        const descriptionHeight = this.showDescription ? 80 : 0 // Height for description section

        // Count characters + add character button if available
        const totalItems =
          (this.encounter.characters?.length || 0) + (this.availableCharacters.length > 0 ? 1 : 0)

        if (totalItems === 0) {
          return {
            width: `300px`,
            height: `${baseHeight + descriptionHeight}px`,
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
          height: `${baseHeight + extraHeight + descriptionHeight}px`,
          minHeight: `${baseHeight}px`,
        }
      },
    },
  }
</script>

<style scoped>
  .encounter-node {
    background: #ffffff;
    border: 2px solid #007bff;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    position: relative;
    min-width: 150px;
    min-height: 100px;
  }

  .encounter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 4px;
  }

  .encounter-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #2c3e50;
  }

  .encounter-name {
    cursor: pointer;
    padding: 2px 4px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .encounter-name:hover {
    background-color: #f8f9fa;
  }

  .encounter-name-input {
    margin: 0;
    padding: 2px 4px;
    font-size: 14px;
    font-weight: 600;
    color: #2c3e50;
    border: 1px solid #007bff;
    border-radius: 4px;
    background: white;
    outline: none;
    min-width: 80px;
    max-width: 200px;
  }

  .encounter-name-input:focus {
    border-color: #0056b3;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  .encounter-actions {
    display: flex;
    gap: 4px;
  }

  .info-btn {
    width: 20px;
    height: 20px;
    border: none;
    border-radius: 50%;
    background: #007bff;
    color: white;
    font-size: 12px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .info-btn:hover {
    background: #0056b3;
    transform: scale(1.1);
  }

  .info-btn.active {
    background: #28a745;
  }

  /* Encounter Description Section */
  .encounter-description-section {
    margin-top: 8px;
    margin-bottom: 8px;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 6px;
    border: 1px solid #e9ecef;
  }

  .encounter-description {
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    font-size: 12px;
    color: #495057;
    line-height: 1.4;
    min-height: 20px;
  }

  .encounter-description:hover {
    background-color: #e9ecef;
  }

  .encounter-description-input {
    width: 100%;
    padding: 4px;
    font-size: 12px;
    color: #495057;
    border: 1px solid #007bff;
    border-radius: 4px;
    background: white;
    outline: none;
    resize: vertical;
    min-height: 60px;
    font-family: inherit;
  }

  .encounter-description-input:focus {
    border-color: #0056b3;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  .add-character-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 2px solid #007bff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    max-height: 200px;
    overflow-y: auto;
  }

  .dropdown-header {
    padding: 8px 12px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
    font-size: 12px;
    font-weight: 600;
    color: #495057;
  }

  .character-options {
    max-height: 150px;
    overflow-y: auto;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    border-bottom: 1px solid #f8f9fa;
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
    border-radius: 50%;
    object-fit: cover;
    border: 1px solid #007bff;
  }

  .option-avatar-placeholder {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #0056b3);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #004085;
  }

  .option-avatar-initials {
    color: white;
    font-size: 10px;
    font-weight: bold;
  }

  .option-info {
    flex: 1;
    min-width: 0;
  }

  .option-name {
    font-size: 12px;
    font-weight: 600;
    color: #2c3e50;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .option-profession {
    font-size: 10px;
    color: #6c757d;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .character-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: flex-start;
    align-items: flex-start;
    min-height: 60px;
    margin-top: 8px;
  }

  .character-avatar {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    transition: all 0.2s ease;
    position: relative;
    width: 120px;
    flex-shrink: 0;
  }

  .character-avatar:hover {
    background: #f8f9fa;
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
    border-radius: 50%;
    background: #dc3545;
    color: white;
    font-size: 12px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: all 0.2s ease;
    z-index: 10;
  }

  .remove-character-btn:hover {
    background: #c82333;
    transform: scale(1.1);
  }

  .avatar-image {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #007bff;
    margin-bottom: 2px;
  }

  .avatar-placeholder {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #0056b3);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #004085;
    margin-bottom: 2px;
  }

  .avatar-initials {
    color: white;
    font-size: 12px;
    font-weight: bold;
  }

  .character-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    min-height: 32px;
  }

  .character-profession {
    font-size: 11px;
    color: #2c3e50;
    font-weight: 600;
    text-align: center;
    line-height: 1.2;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
  }

  .character-name {
    font-size: 9px;
    color: #6c757d;
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
    border-radius: 50%;
    background: #28a745;
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
  }

  .add-encounter-btn:hover {
    background: #218838;
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
  }

  .add-character-btn.active {
    background: #dc3545;
    transform: rotate(45deg);
  }

  .add-character-btn.active:hover {
    background: #c82333;
  }

  /* Scrollbar styling for dropdown */
  .character-options::-webkit-scrollbar {
    width: 4px;
  }

  .character-options::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  .character-options::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
  }

  .character-options::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }

  /* Connection handle styles */
  .connection-handle {
    width: 12px;
    height: 12px;
    border: 2px solid #007bff;
    border-radius: 50%;
    background: white;
    position: absolute;
    transition: all 0.2s ease;
    cursor: crosshair;
    z-index: 10;
  }

  .connection-handle:hover {
    width: 16px;
    height: 16px;
    border-width: 3px;
    background: #007bff;
    box-shadow: 0 0 8px rgba(0, 123, 255, 0.4);
  }

  /* Ensure encounter node has relative positioning for absolute handles */
  .encounter-node {
    position: relative;
  }
</style>
