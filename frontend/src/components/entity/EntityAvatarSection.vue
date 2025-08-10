<template>
  <div class="shared-avatar-edit-section">
    <div class="shared-avatar-container">
      <img v-if="modelValue" :src="modelValue" :alt="name" class="shared-avatar-image" />
      <div v-else class="shared-avatar-placeholder">
        <span class="shared-avatar-initials">{{ getInitials(name) }}</span>
      </div>
    </div>

    <input
      ref="avatarInput"
      type="file"
      accept="image/*"
      @change="handleUpload"
      style="display: none"
    />

    <button
      @click="$refs.avatarInput.click()"
      class="shared-avatar-btn shared-avatar-upload-btn"
      :disabled="isUploading"
    >
      <span v-if="isUploading">Uploading...</span>
      <span v-else>{{ modelValue ? 'Change Avatar' : 'Add Avatar' }}</span>
    </button>

    <button
      v-if="modelValue && !isUploading"
      @click="handleRemove"
      class="shared-avatar-btn shared-avatar-remove-btn"
    >
      Remove
    </button>

    <div v-if="uploadError" class="avatar-error">
      {{ uploadError }}
    </div>
  </div>
</template>

<script>
  import { useAvatarUpload } from '../../composables/useAvatarUpload.js'

  export default {
    name: 'EntityAvatarSection',
    props: {
      modelValue: {
        type: String,
        default: null,
      },
      name: {
        type: String,
        default: '',
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const { isUploading, uploadError, handleAvatarUpload, removeAvatar, getInitials } =
        useAvatarUpload(props.modelValue)

      const handleUpload = (event) => {
        handleAvatarUpload(event)
        // Watch for changes and emit to parent
        const checkForResult = () => {
          if (!isUploading.value && !uploadError.value) {
            // Avatar was successfully uploaded, get the result from the event
            const file = event.target.files[0]
            if (file) {
              const reader = new FileReader()
              reader.onload = (e) => {
                emit('update:modelValue', e.target.result)
              }
              reader.readAsDataURL(file)
            }
          }
        }
        setTimeout(checkForResult, 100)
      }

      const handleRemove = () => {
        removeAvatar()
        emit('update:modelValue', null)
      }

      return {
        isUploading,
        uploadError,
        handleUpload,
        handleRemove,
        getInitials,
      }
    },
  }
</script>

<style scoped>
  .avatar-error {
    color: var(--danger-color);
    font-size: var(--font-size-sm);
    margin-top: var(--spacing-sm);
    text-align: center;
  }
</style>
