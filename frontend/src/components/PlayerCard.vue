<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="player-content">
      <AvatarDisplay :name="player.name" :avatar="player.avatar" />

      <div class="player-title-section">
        <h3 class="real-name">{{ player.rl_name }}</h3>
        <h4 class="character-name">{{ getGenderEmoji(player.gender) }} {{ player.name }}</h4>
      </div>

      <div class="player-fields">
        <div class="shared-field-columns">
          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Race</label>
              <p class="shared-field-value">{{ player.race }}</p>
            </div>

            <div class="shared-field">
              <label class="shared-field-label">Class</label>
              <p class="shared-field-value">{{ player.class_name }}</p>
            </div>
          </div>

          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Size</label>
              <p class="shared-field-value">{{ player.size }}</p>
            </div>

            <div class="shared-field">
              <label class="shared-field-label">Alignment</label>
              <p class="shared-field-value">{{ player.alignment }}</p>
            </div>
          </div>
        </div>

        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Appearance</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ player.appearance }}</div>
            <div class="character-limit-info">
              {{ (player.appearance || '').length }}/{{
                gameData.validation_limits.player_appearance
              }}
              characters
            </div>
          </div>
        </div>

        <div
          v-if="displayAbilitiesSkills && Object.keys(displayAbilitiesSkills).length > 0"
          class="shared-field shared-field-full-width"
        >
          <div class="shared-field-label">Ability & Skill Modifiers</div>
          <div class="shared-field-value">
            <TraitsDisplay
              :traits="displayAbilitiesSkills"
              :category-names="abilitiesSkillsCategoryNames"
              :value-classifier="getValueClass"
            />
          </div>
        </div>
      </div>

      <div class="player-login-section">
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Player Login Link</div>
          <div class="login-link-controls">
            <input
              :value="loginLink"
              readonly
              placeholder="Click refresh to generate login link"
              class="shared-input login-link-input"
            />
            <div class="login-link-buttons">
              <button
                @click="generateLoginLink"
                :disabled="generatingLink"
                class="shared-btn shared-btn-secondary login-btn"
                title="Generate new login link"
              >
                {{ generatingLink ? '⏳' : '🔄' }}
              </button>
              <button
                @click="copyLoginLink"
                :disabled="!loginLink || copyingLink"
                class="shared-btn shared-btn-secondary login-btn"
                title="Copy login link"
              >
                {{ copyingLink ? '✓' : '📋' }}
              </button>
            </div>
          </div>
          <div v-if="loginLinkExpiry" class="login-link-expiry">
            Expires: {{ formatExpiry(loginLinkExpiry) }}
          </div>
        </div>
      </div>

      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deletePlayer" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else>
      <AvatarDisplay :name="player.name" :avatar="player.avatar" />
      <PlayerForm :initial-data="player" :is-editing="true" @save="saveEdit" @cancel="cancelEdit" />
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted, watch, watchEffect } from 'vue'
  import { storeToRefs } from 'pinia'
  import { serializeError } from 'serialize-error'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useNotification } from '../composables/useNotification.js'
  import { createPlayerLoginLink } from '../services/api.js'
  import AvatarDisplay from './base/AvatarDisplay.vue'
  import PlayerForm from './PlayerForm.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'

  export default {
    name: 'PlayerCard',
    components: {
      AvatarDisplay,
      PlayerForm,
      TraitsDisplay,
    },
    props: {
      player: {
        type: Object,
        required: true,
        validator: (value) => {
          return (
            value &&
            typeof value.id !== 'undefined' &&
            typeof value.name === 'string' &&
            value.name.length > 0
          )
        },
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const { showSuccess, showError } = useNotification()
      const isEditing = ref(false)

      const loginLink = ref('')
      const loginLinkExpiry = ref(null)
      const generatingLink = ref(false)
      const copyingLink = ref(false)

      const displayAbilitiesSkills = ref({})

      const { getGenderEmoji } = useDropdownOptions()

      const cleanupFunctions = []

      const startEdit = () => {
        isEditing.value = true
      }

      const cancelEdit = () => {
        isEditing.value = false
      }

      const saveEdit = (formData) => {
        emit('update', props.player.id, {
          name: formData.name.trim(),
          rl_name: formData.rl_name.trim(),
          appearance: formData.appearance.trim(),
          race: formData.race,
          class_name: formData.class_name,
          size: formData.size,
          alignment: formData.alignment,
          gender: formData.gender,
          abilities: formData.abilities,
          skills: formData.skills,
        })
        isEditing.value = false
      }

      const deletePlayer = () => {
        if (confirm(`Are you sure you want to delete ${props.player.name}?`)) {
          emit('delete', props.player.id)
        }
      }

      const generateLoginLink = async () => {
        generatingLink.value = true
        try {
          const response = await createPlayerLoginLink(props.player.id)
          loginLink.value = response.login_url
          loginLinkExpiry.value = response.expires_at
          showSuccess('Login link generated successfully')
        } catch (error) {
          showError('Failed to generate login link')
          console.error('Error generating login link:', JSON.stringify(serializeError(error)))
        } finally {
          generatingLink.value = false
        }
      }

      const copyLoginLink = async () => {
        if (!loginLink.value) return

        copyingLink.value = true
        try {
          await navigator.clipboard.writeText(loginLink.value)
          showSuccess('Login link copied to clipboard')
        } catch (error) {
          showError('Failed to copy login link')
          console.error('Error copying login link:', JSON.stringify(serializeError(error)))
        } finally {
          setTimeout(() => {
            copyingLink.value = false
          }, 1500)
        }
      }

      const formatExpiry = (expiryDate) => {
        if (!expiryDate) return ''
        const date = new Date(expiryDate)
        return date.toLocaleString()
      }

      const loadDisplayAbilitiesSkills = () => {
        const player = props.player
        const abilitiesSkills = {}

        if (player.abilities && Object.keys(player.abilities).length > 0) {
          abilitiesSkills.abilities = player.abilities
        }

        if (player.skills && Object.keys(player.skills).length > 0) {
          abilitiesSkills.skills = player.skills
        }

        displayAbilitiesSkills.value = abilitiesSkills
      }

      const abilitiesSkillsCategoryNames = {
        abilities: 'Ability Modifiers',
        skills: 'Skill Modifiers',
      }

      const getValueClass = (value) => {
        if (value > 0) return 'bias-positive'
        if (value < 0) return 'bias-negative'
        return 'bias-neutral'
      }

      onMounted(() => {
        loadDisplayAbilitiesSkills()
      })

      const playerIdWatcherCleanup = watchEffect(() => {
        if (props.player.id) {
          loadDisplayAbilitiesSkills()
        }
      })

      const abilitiesSkillsWatcherCleanup = watch(
        () => [props.player.abilities, props.player.skills],
        () => {
          loadDisplayAbilitiesSkills()
        },
        { deep: true }
      )

      const loginLinkWatcherCleanup = watch(
        () => props.player.id,
        (newPlayerId, oldPlayerId) => {
          if (newPlayerId !== oldPlayerId) {
            loginLink.value = ''
            loginLinkExpiry.value = null
          }
        }
      )

      cleanupFunctions.push(
        playerIdWatcherCleanup,
        abilitiesSkillsWatcherCleanup,
        loginLinkWatcherCleanup
      )

      onUnmounted(() => {
        cleanupFunctions.forEach((cleanup) => cleanup())
      })

      return {
        gameData,
        isEditing,
        getGenderEmoji,
        startEdit,
        cancelEdit,
        saveEdit,
        deletePlayer,
        loginLink,
        loginLinkExpiry,
        generatingLink,
        copyingLink,
        generateLoginLink,
        copyLoginLink,
        formatExpiry,
        displayAbilitiesSkills,
        abilitiesSkillsCategoryNames,
        getValueClass,
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .player-fields {
    flex: 1;
  }

  .appearance-field {
    margin-bottom: var(--spacing-lg);
  }

  .abilities-skills-section {
    margin-bottom: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .section-title {
    margin: 0 0 var(--spacing-lg) 0;
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    text-align: center;
  }

  /* Player title section - custom layout for dual names */
  .player-title-section {
    margin: 0 0 var(--spacing-xxl) 0;
    text-align: center;
    border-bottom: 3px solid var(--primary-color);
    padding-bottom: var(--spacing-sm);
  }

  .real-name {
    margin: 0 0 var(--spacing-xs) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xxl);
    font-weight: var(--font-weight-bold);
  }

  .character-name {
    margin: 0;
    color: var(--text-muted);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    font-style: italic;
  }

  /* Player login section styles */
  .player-login-section {
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .login-link-controls {
    display: flex;
    gap: var(--spacing-sm);
    align-items: stretch;
  }

  .login-link-input {
    flex: 1;
    min-width: 0;
    font-family: monospace;
    font-size: var(--font-size-sm);
  }

  .login-link-buttons {
    display: flex;
    gap: var(--spacing-xs);
  }

  .login-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    min-width: 44px;
    height: auto;
  }

  .login-link-expiry {
    margin-top: var(--spacing-xs);
    font-size: var(--font-size-sm);
    color: var(--text-muted);
    font-style: italic;
  }
</style>
