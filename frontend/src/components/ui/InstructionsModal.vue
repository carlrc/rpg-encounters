<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    title="Instructions"
    close-aria-label="Close instructions"
    popup-width="90%"
    popup-max-width="800px"
    popup-max-height="90vh"
    @close="closeModal"
  >
    <div class="modal-body" v-html="renderedMarkdown"></div>
  </SharedEncounterPopup>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { serializeError } from 'serialize-error'
  import { marked } from 'marked'
  import SharedEncounterPopup from '../base/SharedEncounterPopup.vue'

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

  onMounted(async () => {
    // Load the markdown content
    try {
      const response = await fetch('/instructions.md')
      instructionsContent.value = await response.text()
    } catch (error) {
      console.error('Failed to load instructions:', JSON.stringify(serializeError(error)))
      instructionsContent.value = '# Error\n\nFailed to load instructions content.'
    }
  })
</script>

<style scoped>
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
