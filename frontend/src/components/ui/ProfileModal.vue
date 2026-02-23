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
        :items="billingItems"
        :selected-item-id="selectedItemId"
        list-title="Profile"
        :show-search="false"
        :contained="true"
        create-button-text=""
        empty-message="No billing items"
        @select-item="selectItem"
      >
        <template #detail-content>
          <ProfileBillingCard
            :loading="loading"
            :error="error"
            :title="selectedItemTitle"
            :token-traits="tokenTraits"
            :format-token-value="formatTokenValue"
          />
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
  import { useProfileBilling } from '@/composables/ui/useProfileBilling'

  const props = defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close', 'logout'])

  const {
    billingItems,
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
