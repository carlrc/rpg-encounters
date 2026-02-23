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
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: var(--z-modal);
  }

  .encounter-popup {
    background: white;
    border-radius: 12px;
    box-shadow: var(--shadow-card-hover);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid var(--gray-100);
    flex-shrink: 0;
  }

  .popup-header h3 {
    margin: 0;
    color: var(--gray-800);
    font-size: 1.5em;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--gray-500);
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background: var(--gray-50);
    color: var(--danger-color);
  }
</style>
