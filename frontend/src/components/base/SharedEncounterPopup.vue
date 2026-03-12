<template>
  <div v-if="isOpen" class="encounter-popup-overlay" @click="emitClose">
    <div class="encounter-popup" :style="popupStyle" @click.stop>
      <slot name="pre-header" />
      <div class="popup-header">
        <slot name="header-left">
          <h3 v-if="title">{{ title }}</h3>
        </slot>
        <button class="close-button" :aria-label="closeAriaLabel" @click="emitClose">
          &times;
        </button>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup>
  import { computed, onMounted, onUnmounted } from 'vue'

  const props = defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: '',
    },
    closeAriaLabel: {
      type: String,
      default: 'Close popup',
    },
    closeOnEscape: {
      type: Boolean,
      default: true,
    },
    popupWidth: {
      type: String,
      default: '90%',
    },
    popupMaxWidth: {
      type: String,
      default: '600px',
    },
    popupMaxHeight: {
      type: String,
      default: '90vh',
    },
  })

  const emit = defineEmits(['close'])

  const emitClose = () => {
    emit('close')
  }

  const handleEscape = (event) => {
    if (!props.closeOnEscape || !props.isOpen) return
    if (event.key === 'Escape') {
      emitClose()
    }
  }

  const popupStyle = computed(() => ({
    width: props.popupWidth,
    maxWidth: props.popupMaxWidth,
    maxHeight: props.popupMaxHeight,
  }))

  onMounted(() => {
    document.addEventListener('keydown', handleEscape)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
  })
</script>

<style scoped>
  .encounter-popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(4, 5, 7, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: var(--z-modal);
    padding: 16px;
  }

  .encounter-popup {
    background: var(--dev-surface);
    border: 1px solid var(--dev-border);
    border-radius: 12px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    color: var(--dev-text-primary);
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--dev-border);
    flex-shrink: 0;
  }

  .popup-header h3 {
    margin: 0;
    color: var(--dev-text-primary);
    font-size: 1.25rem;
    line-height: 1.2;
  }

  .close-button {
    background: transparent;
    border: 1px solid var(--dev-border);
    font-size: 20px;
    cursor: pointer;
    color: var(--dev-text-secondary);
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    transition:
      color 140ms ease,
      border-color 140ms ease,
      background-color 140ms ease;
  }

  .close-button:hover {
    background: var(--dev-surface-hover);
    border-color: #c9ccd3;
    color: var(--dev-text-primary);
  }
</style>
