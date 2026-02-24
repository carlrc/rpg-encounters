<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    title="Insufficient tokens"
    close-aria-label="Close insufficient tokens popup"
    popup-width="90%"
    popup-max-width="460px"
    popup-max-height="80vh"
    @close="emitClose"
  >
    <div class="billing-error-body">
      <p class="billing-error-message">Insufficient tokens.</p>
      <button
        type="button"
        class="shared-btn shared-btn-primary billing-error-close"
        @click="emitClose"
      >
        Close
      </button>
    </div>
  </SharedEncounterPopup>
</template>

<script setup>
  import SharedEncounterPopup from '../base/SharedEncounterPopup.vue'

  defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close'])

  const emitClose = () => emit('close')
</script>

<style scoped>
  .billing-error-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .billing-error-message {
    margin: 0;
    color: var(--gray-700);
    line-height: 1.5;
  }

  .billing-error-close {
    width: 100%;
  }
</style>
