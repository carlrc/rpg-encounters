<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    :title="title"
    close-aria-label="Close insufficient tokens popup"
    popup-width="90%"
    popup-max-width="460px"
    popup-max-height="80vh"
    @close="emitClose"
  >
    <div class="shared-popup-body">
      <p class="shared-popup-message">{{ message }}</p>
      <button
        type="button"
        class="shared-btn shared-btn-primary shared-popup-action"
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
    title: {
      type: String,
      default: 'Insufficient Tokens',
    },
    message: {
      type: String,
      default: 'Purchase more tokens to continue.',
    },
  })

  const emit = defineEmits(['close'])

  const emitClose = () => emit('close')
</script>

<style scoped></style>
