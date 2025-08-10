<template>
  <div class="import-button-container">
    <input
      ref="fileInput"
      type="file"
      accept=".md,.markdown,.json"
      @change="handleFileChange"
      style="display: none"
    />
    <button @click="$refs.fileInput.click()" class="shared-import-btn" :disabled="importing">
      <span v-if="importing">Importing...</span>
      <span v-else>Import {{ entityType }}s</span>
    </button>
  </div>
</template>

<script>
  export default {
    name: 'ImportButton',
    props: {
      entityType: {
        type: String,
        required: true,
      },
      importing: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['import'],
    setup(props, { emit }) {
      const handleFileChange = (event) => {
        emit('import', event)
      }

      return {
        handleFileChange,
      }
    },
  }
</script>
