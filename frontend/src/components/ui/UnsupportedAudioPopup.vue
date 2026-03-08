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
    <div class="unsupported-audio-body">
      <p class="unsupported-audio-message">
        Device not supported. Try updating or switching browsers.
      </p>
      <button
        type="button"
        class="shared-btn shared-btn-primary unsupported-audio-close"
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
  .unsupported-audio-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .unsupported-audio-message {
    margin: 0;
    color: var(--gray-700);
    line-height: 1.5;
  }

  .unsupported-audio-close {
    width: 100%;
  }
</style>
