<template>
  <div class="shared-card">
    <h3 class="shared-title">Settings</h3>
    <div class="shared-field danger-zone-field">
      <div class="shared-field-label">Danger Zone</div>
      <p class="shared-field-value">
        Deleting your account permanently removes all data. This action cannot be undone.
      </p>
      <button class="shared-btn shared-btn-danger danger-zone-delete" @click="emit('delete')">
        Delete Account
      </button>
    </div>
  </div>
</template>

<script setup>
  const emit = defineEmits(['delete'])
</script>

<style scoped>
  .danger-zone-field {
    padding-top: 0;
    margin-top: 0;
    border-top: none;
  }

  .danger-zone-delete {
    width: 100%;
    margin-top: var(--spacing-lg);
  }
</style>
