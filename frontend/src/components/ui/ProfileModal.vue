<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    close-aria-label="Close profile popup"
    popup-width="90%"
    popup-max-width="720px"
    popup-max-height="90vh"
    @close="closeModal"
  >
    <template #header-left>
      <span class="popup-header-spacer" aria-hidden="true"></span>
    </template>

    <div class="profile-modal-body">
      <SplitViewLayout
        :items="profileItems"
        :selected-item-id="selectedItemId"
        list-title="Profile"
        :show-search="false"
        :contained="true"
        create-button-text=""
        empty-message="No profile items"
        @select-item="selectItem"
      >
        <template #detail-content>
          <ProfileBillingCard
            v-if="selectedItemId === 'billing'"
            :loading="loading"
            :error="error"
            :title="selectedItemTitle"
            :token-traits="tokenTraits"
            :format-token-value="formatTokenValue"
          />
          <ProfileSettingsCard v-else @delete="handleDeleteAccount" />
        </template>

        <template #footer-actions>
          <button class="shared-btn shared-btn-danger profile-logout-btn" @click="emit('logout')">
            Logout
          </button>
        </template>
      </SplitViewLayout>
    </div>
  </SharedEncounterPopup>
</template>

<script setup>
  import { watch } from 'vue'
  import SharedEncounterPopup from '../base/SharedEncounterPopup.vue'
  import SplitViewLayout from '../layout/SplitViewLayout.vue'
  import ProfileBillingCard from './ProfileBillingCard.vue'
  import ProfileSettingsCard from './ProfileSettingsCard.vue'
  import { deleteAccount } from '../../services/api'
  import { useProfileBilling } from '../../composables/ui/useProfileBilling'

  const props = defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close', 'logout'])

  const {
    profileItems,
    selectedItemId,
    loading,
    error,
    selectedItemTitle,
    tokenTraits,
    formatTokenValue,
    selectItem,
    fetchProfile,
  } = useProfileBilling()

  const closeModal = () => emit('close')
  const handleDeleteAccount = async () => {
    const confirmMessage = 'Are you sure you want to delete your account? This cannot be undone.'
    if (!confirm(confirmMessage)) {
      return
    }

    try {
      await deleteAccount()
      closeModal()
      emit('logout')
    } catch (err) {
      console.error('Failed to delete account:', err)
      alert('Failed to delete account. Please try again.')
    }
  }

  watch(
    () => props.isOpen,
    (isOpen) => {
      if (isOpen) {
        void fetchProfile()
      }
    }
  )
</script>

<style scoped>
  .popup-header-spacer {
    width: 30px;
    height: 30px;
  }

  .profile-modal-body {
    flex: 1;
    min-height: 0;
    width: 100%;
  }

  .profile-logout-btn {
    width: 100%;
  }
</style>
