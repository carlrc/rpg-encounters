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
      @change="handleAvatarUpload"
      style="display: none"
    />
    <button @click="$refs.avatarInput.click()" class="shared-avatar-btn shared-avatar-upload-btn">
      {{ modelValue ? 'Change Avatar' : 'Add Avatar' }}
    </button>
    <button
      v-if="modelValue"
      @click="removeAvatar"
      class="shared-avatar-btn shared-avatar-remove-btn"
    >
      Remove
    </button>
  </div>
</template>

<script>
  import { getInitials, handleAvatarUpload } from '../../utils/avatarUtils.js'

  export default {
    name: 'AvatarUpload',
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
      const onAvatarUpload = (event) => {
        handleAvatarUpload(event, (result) => {
          emit('update:modelValue', result)
        })
      }

      const removeAvatar = () => {
        emit('update:modelValue', null)
      }

      return {
        getInitials,
        handleAvatarUpload: onAvatarUpload,
        removeAvatar,
      }
    },
  }
</script>
