<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    title="Device Warning"
    close-aria-label="Close device warning popup"
    popup-width="90%"
    popup-max-width="460px"
    popup-max-height="80vh"
    @close="emitClose"
  >
    <div class="shared-popup-body">
      <p class="shared-popup-message">The application was designed for tablets and desktops.</p>
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
