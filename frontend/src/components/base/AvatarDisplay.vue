<template>
  <div class="shared-avatar-section">
    <div class="shared-avatar-container">
      <img v-if="avatar" :src="avatar" :alt="resolvedAlt" class="shared-avatar-image" />
      <div v-else class="shared-avatar-placeholder">
        <span class="shared-avatar-initials">{{ initials }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import { getInitials } from '../../utils/avatarUtils'

  const props = defineProps({
    name: {
      type: String,
      required: true,
    },
    avatar: {
      type: String,
      default: '',
    },
    alt: {
      type: String,
      default: '',
    },
  })

  const resolvedAlt = computed(() => props.alt || props.name)
  const initials = computed(() => getInitials(props.name))
</script>
