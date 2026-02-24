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

    <MemoryForm
      v-else
      :initial-data="memory"
      :characters="characters"
      :is-editing="true"
      @save="saveEdit"
      @cancel="cancelEdit"
    />
  </div>
</template>

<script>
  import { ref } from 'vue'
  import MemoryForm from './MemoryForm.vue'
  import { getCharacterName } from '../utils/characterUtils'

  const CONTENT_WORD_LIMIT = 200

  export default {
    name: 'MemoryCard',
    components: {
      MemoryForm,
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

      const startEdit = () => {
        isEditing.value = true
      }

      const cancelEdit = () => {
        isEditing.value = false
      }

      const saveEdit = (formData) => {
        emit('update', props.memory.id, {
          title: formData.title.trim(),
          content: formData.content.trim(),
          character_ids: formData.character_ids,
        })
        isEditing.value = false
      }

      const deleteMemory = () => {
        if (confirm(`Are you sure you want to delete "${props.memory.title}"?`)) {
          emit('delete', props.memory.id)
        }
      }

      return {
        isEditing,
        CONTENT_WORD_LIMIT,
        getCharacterName: (id) => getCharacterName(id, props.characters),
        startEdit,
        cancelEdit,
        saveEdit,
        deleteMemory,
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .memory-content {
    flex: 1;
  }

  .content-field {
    margin-bottom: var(--spacing-lg);
  }
</style>
