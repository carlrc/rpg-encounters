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
    line-height: var(--line-height-body);
    color: var(--dev-text-secondary);
  }

  /* Markdown content styles using same variables as encounter popup */
  .modal-body :deep(h1) {
    color: var(--dev-text-primary);
    font-size: var(--font-size-section);
    font-weight: var(--font-weight-semibold);
    margin: 0 0 24px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--dev-border);
  }

  .modal-body :deep(h2) {
    color: var(--dev-text-primary);
    font-size: 1.5rem;
    font-weight: 600;
    margin: 32px 0 16px 0;
  }

  .modal-body :deep(h3) {
    color: var(--dev-text-primary);
    font-size: 1.25rem;
    font-weight: 600;
    margin: 24px 0 12px 0;
  }

  .modal-body :deep(p) {
    color: var(--dev-text-secondary);
    margin: 0 0 var(--spacing-lg) 0;
  }

  .modal-body :deep(ul),
  .modal-body :deep(ol) {
    color: var(--dev-text-secondary);
    margin: 0 0 var(--spacing-lg) 0;
    padding-left: var(--spacing-xxl);
  }

  .modal-body :deep(li) {
    margin-bottom: var(--spacing-sm);
  }

  .modal-body :deep(strong) {
    font-weight: 600;
    color: var(--dev-text-primary);
  }

  .modal-body :deep(code) {
    background-color: var(--dev-background);
    color: var(--dev-text-primary);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--dev-border);
    font-family: var(--font-mono);
    font-size: var(--font-size-code);
  }

  .modal-body :deep(hr) {
    border: none;
    border-top: 1px solid var(--dev-border);
    margin: var(--spacing-xxl) 0;
  }

  .modal-body :deep(em) {
    color: var(--dev-text-secondary);
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
