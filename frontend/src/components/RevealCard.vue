<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="reveal-display">
      <!-- Title -->
      <h2 class="shared-title">{{ reveal.title }}</h2>

      <!-- Influence Level Display -->
      <div class="shared-field-columns">
        <div class="shared-field-column">
          <div class="shared-field">
            <div class="shared-field-label">
              Level 1: Standard (DC {{ getEffectiveThreshold('standard') }})
            </div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_1_content }}</div>
            </div>
          </div>

          <div v-if="reveal.level_2_content" class="shared-field">
            <div class="shared-field-label">
              Level 2: Privileged (DC {{ getEffectiveThreshold('privileged') }})
            </div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_2_content }}</div>
            </div>
          </div>
        </div>

        <div class="shared-field-column">
          <div v-if="reveal.level_3_content" class="shared-field">
            <div class="shared-field-label">
              Level 3: Exclusive (DC {{ getEffectiveThreshold('exclusive') }})
            </div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_3_content }}</div>
            </div>
          </div>

          <div class="shared-field">
            <div class="shared-field-label">Assigned Characters</div>
            <div class="shared-field-value">
              <div class="shared-tags-display">
                <span
                  v-for="characterId in reveal.character_ids"
                  :key="characterId"
                  class="shared-tag-bubble"
                >
                  {{ getCharacterName(characterId) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="confirmDelete" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else class="reveal-edit">
      <!-- Use Shared RevealForm -->
      <RevealForm
        :initial-data="editFormData"
        :characters="characters"
        :is-editing="true"
        @save="handleFormSave"
        @cancel="cancelEdit"
      />
    </div>
  </div>
</template>

<script>
  import { ref, computed } from 'vue'
  import RevealForm from './RevealForm.vue'
  import { useGameDataStore } from '../stores/gameData.js'
  import { storeToRefs } from 'pinia'
  import { getDCLabel } from '../utils/dcUtils.js'
  import { getCharacterName } from '../utils/characterUtils.js'

  export default {
    name: 'RevealCard',
    components: {
      RevealForm,
    },
    props: {
      reveal: {
        type: Object,
        required: true,
      },
      characters: {
        type: Array,
        default: () => [],
      },
      currentInfluenceLevel: {
        type: Number,
        default: 0,
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const isEditing = ref(false)

      // Prepare data for the shared RevealForm
      const editFormData = computed(() => {
        return {
          title: props.reveal.title,
          character_ids: [...props.reveal.character_ids],
          level_1_content: props.reveal.level_1_content || '',
          level_2_content: props.reveal.level_2_content || '',
          level_3_content: props.reveal.level_3_content || '',
          standard_threshold: props.reveal.standard_threshold,
          privileged_threshold: props.reveal.privileged_threshold,
          exclusive_threshold: props.reveal.exclusive_threshold,
        }
      })

      const startEdit = () => {
        isEditing.value = true
      }

      const cancelEdit = () => {
        isEditing.value = false
      }

      const handleFormSave = (formData) => {
        emit('update', props.reveal.id, formData)
        isEditing.value = false
      }

      const confirmDelete = () => {
        if (confirm(`Are you sure you want to delete this reveal?`)) {
          emit('delete', props.reveal.id)
        }
      }

      const getEffectiveThreshold = (level) => {
        switch (level) {
          case 'standard':
            return props.reveal.standard_threshold
          case 'privileged':
            return props.reveal.privileged_threshold
          case 'exclusive':
            return props.reveal.exclusive_threshold
          default:
            return 0
        }
      }

      return {
        gameData,
        isEditing,
        editFormData,
        getCharacterName: (id) => getCharacterName(id, props.characters),
        startEdit,
        cancelEdit,
        handleFormSave,
        confirmDelete,
        getEffectiveThreshold,
        getDCLabel: (value) => getDCLabel(value, gameData.value?.difficulty_classes),
      }
    },
  }
</script>

<style scoped>
  /* Styles for the reveal display view only - form styles are now in RevealForm.vue */
</style>
