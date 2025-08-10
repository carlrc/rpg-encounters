<template>
  <div class="entity-basic-fields">
    <!-- Name Field -->
    <BaseFormField
      v-model="localData.name"
      type="text"
      :placeholder="`${entityType} name`"
      variant="name"
      required
      @update:modelValue="updateField('name', $event)"
    />

    <!-- Two Column Layout -->
    <div class="shared-field-columns">
      <!-- Left Column -->
      <div class="shared-field-column">
        <BaseFormField
          v-model="localData.race"
          type="select"
          label="Race"
          placeholder="Select Race"
          :options="dropdownOptions.races"
          required
          @update:modelValue="updateField('race', $event)"
        />

        <BaseFormField
          v-if="showField('class_name')"
          v-model="localData.class_name"
          type="select"
          label="Class"
          placeholder="Select Class"
          :options="dropdownOptions.classes"
          required
          @update:modelValue="updateField('class_name', $event)"
        />

        <BaseFormField
          v-if="showField('alignment')"
          v-model="localData.alignment"
          type="select"
          label="Alignment"
          placeholder="Select Alignment"
          :options="dropdownOptions.alignments"
          :required="fieldConfig.alignment?.required"
          @update:modelValue="updateField('alignment', $event)"
        />
      </div>

      <!-- Right Column -->
      <div class="shared-field-column">
        <BaseFormField
          v-model="localData.size"
          type="select"
          label="Size"
          placeholder="Select Size"
          :options="getSizeOptions()"
          required
          @update:modelValue="updateField('size', $event)"
        />

        <BaseFormField
          v-if="showField('profession')"
          v-model="localData.profession"
          type="text"
          label="Profession"
          placeholder="Profession"
          @update:modelValue="updateField('profession', $event)"
        />

        <BaseFormField
          v-if="showField('gender')"
          v-model="localData.gender"
          type="select"
          label="Gender"
          placeholder="Select Gender"
          :options="dropdownOptions.genders"
          @update:modelValue="updateField('gender', $event)"
        />
      </div>
    </div>

    <!-- Gender Field (Full Width) - for entities that need it full width -->
    <BaseFormField
      v-if="showField('gender') && fieldConfig.gender?.fullWidth"
      v-model="localData.gender"
      type="select"
      label="Gender"
      placeholder="Select Gender"
      :options="dropdownOptions.genders"
      full-width
      @update:modelValue="updateField('gender', $event)"
    />
  </div>
</template>

<script>
  import { reactive, computed, watch } from 'vue'
  import BaseFormField from '../base/BaseFormField.vue'
  import { useDropdownOptions } from '../../composables/useDropdownOptions.js'

  export default {
    name: 'EntityBasicFields',
    components: {
      BaseFormField,
    },
    props: {
      modelValue: {
        type: Object,
        required: true,
      },
      entityType: {
        type: String,
        required: true,
        validator: (value) => ['character', 'player'].includes(value.toLowerCase()),
      },
      fieldConfig: {
        type: Object,
        default: () => ({}),
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const { getOptionsForEntity } = useDropdownOptions()

      const dropdownOptions = computed(() => getOptionsForEntity(props.entityType))

      // Local reactive copy of the data
      const localData = reactive({
        name: '',
        race: '',
        size: '',
        alignment: '',
        gender: '',
        class_name: '',
        profession: '',
        ...props.modelValue,
      })

      // Default field configurations for different entity types
      const defaultFieldConfigs = {
        character: {
          name: { required: true },
          race: { required: true },
          size: { required: true },
          alignment: { required: true },
          gender: { required: false, fullWidth: false },
          profession: { required: false },
          class_name: { show: false },
        },
        player: {
          name: { required: true },
          race: { required: true },
          size: { required: true },
          alignment: { required: true },
          gender: { required: false, fullWidth: true },
          class_name: { required: true, show: true },
          profession: { show: false },
        },
      }

      const fieldConfig = computed(() => ({
        ...defaultFieldConfigs[props.entityType.toLowerCase()],
        ...props.fieldConfig,
      }))

      const showField = (fieldName) => {
        const config = fieldConfig.value[fieldName]
        return config?.show !== false
      }

      const getSizeOptions = () => {
        return props.entityType.toLowerCase() === 'character'
          ? dropdownOptions.value.sizes
          : dropdownOptions.value.sizes
      }

      const updateField = (fieldName, value) => {
        localData[fieldName] = value
        emit('update:modelValue', { ...localData })
      }

      // Watch for external changes to modelValue
      watch(
        () => props.modelValue,
        (newValue) => {
          Object.assign(localData, newValue)
        },
        { deep: true }
      )

      return {
        localData,
        dropdownOptions,
        fieldConfig,
        showField,
        getSizeOptions,
        updateField,
      }
    },
  }
</script>

<style scoped>
  .entity-basic-fields {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .shared-field-columns {
      grid-template-columns: 1fr;
    }
  }
</style>
