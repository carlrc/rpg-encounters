<template>
  <div class="shared-form">
    <!-- Real Name -->
    <input
      v-model="form.rl_name"
      placeholder="Real-life player name"
      class="shared-input shared-input-name"
    />

    <!-- Character Name -->
    <input
      v-model="form.name"
      placeholder="Character name"
      class="shared-input shared-input-name"
    />

    <!-- Two Column Layout -->
    <div class="shared-field-columns">
      <!-- Left Column -->
      <div class="shared-field-column">
        <select v-model="form.race" class="shared-select">
          <option value="">Select Race</option>
          <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
        </select>

        <select v-model="form.class_name" class="shared-select">
          <option value="">Select Class</option>
          <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">
            {{ playerClass }}
          </option>
        </select>
      </div>

      <!-- Right Column -->
      <div class="shared-field-column">
        <select v-model="form.size" class="shared-select">
          <option value="">Select Size</option>
          <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
        </select>

        <select v-model="form.alignment" class="shared-select">
          <option value="">Select Alignment</option>
          <option v-for="alignment in alignments" :key="alignment" :value="alignment">
            {{ alignment }}
          </option>
        </select>
      </div>
    </div>

    <!-- Gender Field (Full Width) -->
    <select v-model="form.gender" class="shared-select">
      <option value="">Select Gender</option>
      <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
    </select>

    <!-- Appearance Field (Full Width) -->
    <div class="appearance-field">
      <label class="shared-field-label">Appearance</label>
      <BaseTextareaWithCharacterCounter
        v-model="form.appearance"
        :placeholder="`Player appearance (max ${gameData?.validation_limits?.player_appearance || 500} characters)`"
        :max-characters="gameData?.validation_limits?.player_appearance || 500"
      />
    </div>

    <!-- Ability Modifiers Section -->
    <div class="abilities-skills-section">
      <h4 class="section-title">Ability Modifiers</h4>
      <RangeSliderControl
        v-model="form.abilities.Charisma"
        label="Charisma"
        :min="-5"
        :max="10"
        :step="1"
      />
    </div>

    <!-- Skill Modifiers Section -->
    <div class="abilities-skills-section">
      <h4 class="section-title">Skill Modifiers</h4>
      <RangeSliderControl
        v-for="skill in skillSliderFields"
        :key="skill"
        v-model="form.skills[skill]"
        :label="skill"
        :min="-5"
        :max="25"
        :step="1"
      />
    </div>

    <div class="shared-actions">
      <button @click="handleSave" class="shared-btn shared-btn-success" :disabled="!isFormValid">
        {{ isEditing ? 'Save' : 'Create' }}
      </button>
      <button @click="handleCancel" class="shared-btn shared-btn-secondary">Cancel</button>
    </div>
  </div>
</template>

<script>
  import { reactive, computed } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useFormValidation } from '../utils/useFormValidation'
  import { useDropdownOptions } from '../composables/useDropdownOptions'
  import { sanitizeDisplayName } from '../utils/nameUtils'
  import { useGameDataStore } from '../stores/gameData'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import RangeSliderControl from './base/RangeSliderControl.vue'

  export default {
    name: 'PlayerForm',
    components: {
      BaseTextareaWithCharacterCounter,
      RangeSliderControl,
    },
    props: {
      initialData: {
        type: Object,
        default: () => ({}),
      },
      isEditing: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['save', 'cancel'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const { genders } = useDropdownOptions()

      const form = reactive({
        name: props.initialData.name || '',
        rl_name: props.initialData.rl_name || '',
        appearance: props.initialData.appearance || '',
        race: props.initialData.race || '',
        class_name: props.initialData.class_name || '',
        size: props.initialData.size || '',
        alignment: props.initialData.alignment || '',
        gender: props.initialData.gender || '',
        abilities: {
          Charisma: props.initialData.abilities?.Charisma || 0,
        },
        skills: {
          Deception: props.initialData.skills?.Deception || 0,
          Intimidation: props.initialData.skills?.Intimidation || 0,
          Performance: props.initialData.skills?.Performance || 0,
          Persuasion: props.initialData.skills?.Persuasion || 0,
        },
      })

      const { isFormValid } = useFormValidation(form, 'PLAYER')

      const skillSliderFields = ['Deception', 'Intimidation', 'Performance', 'Persuasion']

      const handleSave = () => {
        if (isFormValid.value) {
          const formData = {
            name: sanitizeDisplayName(form.name),
            rl_name: sanitizeDisplayName(form.rl_name),
            appearance: form.appearance.trim(),
            race: form.race,
            class_name: form.class_name,
            size: form.size,
            alignment: form.alignment,
            gender: form.gender,
            abilities: form.abilities,
            skills: form.skills,
          }
          emit('save', formData)
        }
      }

      const handleCancel = () => {
        emit('cancel')
      }

      return {
        form,
        gameData,
        races: computed(() => gameData.value?.races || []),
        classes: computed(() => gameData.value?.classes || []),
        genders,
        sizes: computed(() => gameData.value?.sizes?.player || []),
        alignments: computed(() => gameData.value?.alignments || []),
        skillSliderFields,
        isFormValid,
        handleSave,
        handleCancel,
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .appearance-field {
    margin-bottom: var(--spacing-lg);
  }

  .abilities-skills-section {
    margin-bottom: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .section-title {
    margin: 0 0 var(--spacing-lg) 0;
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    text-align: center;
  }
</style>
