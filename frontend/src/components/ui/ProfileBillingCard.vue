<template>
  <div v-if="loading" class="shared-loading">Loading billing...</div>
  <div v-else-if="error" class="shared-error">{{ error }}</div>

  <div v-else class="shared-card">
    <h3 class="shared-title">{{ title }}</h3>
    <div class="shared-field billing-field">
      <div class="shared-field-label">Available Tokens</div>
      <div class="token-traits-wrapper">
        <TraitsDisplay
          :traits="tokenTraits"
          :show-category-title="false"
          :show-trait-names="false"
          :value-formatter="formatTokenValue"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
  import TraitsDisplay from '../base/TraitsDisplay.vue'

  defineProps({
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: String,
      default: '',
    },
    title: {
      type: String,
      default: 'Billing',
    },
    tokenTraits: {
      type: Object,
      required: true,
    },
    formatTokenValue: {
      type: Function,
      required: true,
    },
  })
</script>

<style scoped>
  .billing-field {
    padding-top: 0;
    margin-top: 0;
    border-top: none;
  }

  .token-traits-wrapper :deep(.traits-display-grid) {
    grid-template-columns: 1fr;
    margin-top: 0;
  }

  .token-traits-wrapper :deep(.trait-category-display) {
    min-height: 56px;
  }
</style>
