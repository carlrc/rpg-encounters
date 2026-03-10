import { computed, ref } from 'vue'
import { serializeError } from 'serialize-error'
import { getProfile } from '@/services/api'

export function useProfileBilling() {
  const profileItems = [
    { id: 'billing', name: 'Billing' },
    { id: 'settings', name: 'Settings' },
  ]
  const selectedItemId = ref('billing')
  const loading = ref(false)
  const error = ref('')
  const profile = ref(null)

  const availableTokens = computed(() => profile.value?.available_tokens ?? 0)
  const selectedItemTitle = computed(() => {
    const selectedItem = profileItems.find((item) => item.id === selectedItemId.value)
    return selectedItem?.name || ''
  })

  const tokenTraits = computed(() => ({
    token_balance: {
      available: availableTokens.value,
    },
  }))

  const formatTokenValue = (value) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${Number(value).toLocaleString()}`
  }

  const selectItem = (itemId) => {
    selectedItemId.value = itemId
  }

  const fetchProfile = async () => {
    loading.value = true
    error.value = ''

    try {
      profile.value = await getProfile()
    } catch (err) {
      error.value = 'Failed to load billing details'
      console.error('Failed to fetch profile:', JSON.stringify(serializeError(err)))
    } finally {
      loading.value = false
    }
  }

  return {
    profileItems,
    selectedItemId,
    loading,
    error,
    availableTokens,
    selectedItemTitle,
    tokenTraits,
    formatTokenValue,
    selectItem,
    fetchProfile,
  }
}
