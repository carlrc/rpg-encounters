<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="memory-content">
      <!-- Title -->
      <h3 class="shared-title">{{ memory.title }}</h3>

      <!-- Content -->
      <div class="shared-field shared-field-full-width">
        <div class="shared-field-label">Content</div>
        <div class="shared-field-value">
          <div class="shared-text-display">{{ memory.content }}</div>
          <div class="character-limit-info">
            {{ (memory.content || '').split(' ').length }}/{{ CONTENT_WORD_LIMIT }} words
          </div>
        </div>
      </div>

      <!-- Assigned Characters -->
      <div class="shared-field shared-field-full-width">
        <div class="shared-field-label">Assigned Characters</div>
        <div class="shared-field-value">
          <div class="shared-tags-display">
            <span
              v-for="characterId in memory.character_ids"
              :key="characterId"
              class="shared-tag-bubble"
            >
              {{ getCharacterName(characterId) }}
            </span>
          </div>
        </div>
      </div>

      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deleteMemory" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else class="shared-form">
      <!-- Title -->
      <input
        v-model="editForm.title"
        placeholder="Memory title"
        class="shared-input shared-input-name"
      />

      <!-- Content -->
      <div class="content-field">
        <label class="shared-field-label">Content</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.content"
          :placeholder="`Memory content (max ${CONTENT_WORD_LIMIT} words)`"
          :max-words="CONTENT_WORD_LIMIT"
        />
      </div>

      <!-- Character Selection -->
      <CharacterSelector
        v-model="editForm.character_ids"
        :characters="characters"
        label="Characters"
      />

      <div class="shared-actions">
        <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">
          Save
        </button>
        <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, computed } from 'vue'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from './entity/CharacterSelector.vue'

  const CONTENT_WORD_LIMIT = 200

  export default {
    name: 'MemoryCard',
    components: {
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
    },
    props: {
      memory: {
        type: Object,
        required: true,
      },
      characters: {
        type: Array,
        default: () => [],
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const isEditing = ref(false)

      const editForm = reactive({
        title: '',
        content: '',
        character_ids: [],
      })

      const isFormValid = computed(() => {
        return (
          editForm.title.trim().length > 0 &&
          editForm.content.trim().length > 0 &&
          editForm.character_ids.length > 0 &&
          editForm.content.trim().split(' ').length <= CONTENT_WORD_LIMIT
        )
      })

      const getCharacterName = (characterId) => {
        const character = props.characters.find((c) => c.id === characterId)
        return character ? character.name : `Character ${characterId}`
      }

      const startEdit = () => {
        editForm.title = props.memory.title || ''
        editForm.content = props.memory.content || ''
        editForm.character_ids = [...props.memory.character_ids]
        isEditing.value = true
      }

      const cancelEdit = () => {
        isEditing.value = false
      }

      const saveEdit = () => {
        if (isFormValid.value) {
          emit('update', props.memory.id, {
            title: editForm.title.trim(),
            content: editForm.content.trim(),
            character_ids: editForm.character_ids.map((id) => parseInt(id)),
          })
          isEditing.value = false
        }
      }

      const deleteMemory = () => {
        if (confirm(`Are you sure you want to delete "${props.memory.title}"?`)) {
          emit('delete', props.memory.id)
        }
      }

      return {
        isEditing,
        editForm,
        isFormValid,
        CONTENT_WORD_LIMIT,
        getCharacterName,
        startEdit,
        cancelEdit,
        saveEdit,
        deleteMemory,
      }
    },
  }
</script>

<style scoped>
  .memory-content {
    flex: 1;
  }

  .character-limit-info {
    font-size: 0.8em;
    color: #6c757d;
    text-align: right;
    margin-top: 4px;
  }

  .content-field {
    margin-bottom: 16px;
  }
</style>
