<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    title="Audio Not Supported"
    close-aria-label="Close unsupported audio popup"
    popup-width="90%"
    popup-max-width="460px"
    popup-max-height="80vh"
    @close="emitClose"
  >
    <div class="shared-popup-body">
      <p class="shared-popup-message">Device not supported. Try updating or switching browsers.</p>
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
  })

  const emit = defineEmits(['close'])

  const emitClose = () => emit('close')
</script>

<style scoped></style>
