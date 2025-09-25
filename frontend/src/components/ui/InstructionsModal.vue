<template>
  <div v-if="isOpen" class="encounter-popup-overlay" @click="closeModal">
    <div class="encounter-popup" @click.stop>
      <div class="popup-header">
        <h3>Instructions</h3>
        <button class="close-button" @click="closeModal" aria-label="Close instructions">×</button>
      </div>
      <div class="modal-body" v-html="renderedMarkdown"></div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { serializeError } from 'serialize-error'
  import { marked } from 'marked'

  defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close'])

  const instructionsContent = ref('')

  const renderedMarkdown = computed(() => {
    if (!instructionsContent.value) return ''
    return marked(instructionsContent.value)
  })

  const closeModal = () => {
    emit('close')
  }

  const handleEscape = (event) => {
    if (event.key === 'Escape') {
      closeModal()
    }
  }

  onMounted(async () => {
    // Load the markdown content
    try {
      const response = await fetch('/instructions.md')
      instructionsContent.value = await response.text()
    } catch (error) {
      console.error('Failed to load instructions:', JSON.stringify(serializeError(error)))
      instructionsContent.value = '# Error\n\nFailed to load instructions content.'
    }

    // Add escape key listener
    document.addEventListener('keydown', handleEscape)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
  })
</script>

<style scoped>
  /* Use same popup styling as encounter popup */
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
    padding: var(--spacing-lg);
  }

  .encounter-popup {
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card-hover);
    max-width: 800px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg) var(--spacing-xl);
    border-bottom: 1px solid var(--gray-100);
    flex-shrink: 0;
  }

  .popup-header h3 {
    margin: 0;
    color: var(--gray-800);
    font-size: var(--font-size-xxl);
    font-weight: var(--font-weight-semibold);
  }

  .close-button {
    background: none;
    border: none;
    font-size: var(--font-size-xl);
    cursor: pointer;
    color: var(--gray-500);
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-round);
    transition: var(--transition-fast);
  }

  .close-button:hover {
    background: var(--gray-50);
    color: var(--danger-color);
  }

  .modal-body {
    padding: var(--spacing-xl);
    overflow-y: auto;
    flex: 1;
    line-height: 1.6;
  }

  /* Markdown content styles using same variables as encounter popup */
  .modal-body :deep(h1) {
    color: var(--gray-800);
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 24px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--gray-200);
  }

  .modal-body :deep(h2) {
    color: var(--gray-800);
    font-size: 1.5rem;
    font-weight: 600;
    margin: 32px 0 16px 0;
  }

  .modal-body :deep(h3) {
    color: var(--gray-800);
    font-size: 1.25rem;
    font-weight: 600;
    margin: 24px 0 12px 0;
  }

  .modal-body :deep(p) {
    color: var(--gray-800);
    margin: 0 0 var(--spacing-lg) 0;
  }

  .modal-body :deep(ul),
  .modal-body :deep(ol) {
    color: var(--gray-800);
    margin: 0 0 var(--spacing-lg) 0;
    padding-left: var(--spacing-xxl);
  }

  .modal-body :deep(li) {
    margin-bottom: var(--spacing-sm);
  }

  .modal-body :deep(strong) {
    font-weight: 600;
    color: var(--gray-800);
  }

  .modal-body :deep(code) {
    background-color: var(--gray-100);
    padding: 2px var(--spacing-xs);
    border-radius: var(--radius-sm);
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
  }

  .modal-body :deep(hr) {
    border: none;
    border-top: 1px solid var(--gray-200);
    margin: var(--spacing-xxl) 0;
  }

  .modal-body :deep(em) {
    color: var(--gray-600);
    font-style: italic;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .encounter-popup-overlay {
      padding: var(--spacing-lg);
    }

    .encounter-popup {
      width: 95%;
      max-height: 95vh;
    }

    .popup-header,
    .modal-body {
      padding: var(--spacing-lg);
    }

    .modal-body :deep(h1) {
      font-size: 1.75rem;
    }

    .modal-body :deep(h2) {
      font-size: 1.35rem;
    }
  }
</style>
