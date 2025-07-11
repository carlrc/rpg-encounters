<template>
  <div class="player-card">
    <div v-if="!isEditing" class="player-content">
      <h3 class="player-name">{{ player.name }}</h3>
      <p class="player-description">{{ player.description }}</p>
      <div class="player-actions">
        <button @click="startEdit" class="edit-btn">Edit</button>
        <button @click="deletePlayer" class="delete-btn">Delete</button>
      </div>
    </div>
    
    <div v-else class="player-edit-form">
      <input 
        v-model="editForm.name" 
        placeholder="Player name"
        class="edit-input"
      />
      <textarea 
        v-model="editForm.description" 
        placeholder="Player description"
        class="edit-textarea"
      ></textarea>
      <div class="edit-actions">
        <button @click="saveEdit" class="save-btn">Save</button>
        <button @click="cancelEdit" class="cancel-btn">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
  name: 'PlayerCard',
  props: {
    player: {
      type: Object,
      required: true
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    const editForm = reactive({
      name: '',
      description: ''
    })

    const startEdit = () => {
      editForm.name = props.player.name
      editForm.description = props.player.description
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      editForm.name = ''
      editForm.description = ''
    }

    const saveEdit = () => {
      if (editForm.name.trim() && editForm.description.trim()) {
        emit('update', props.player.id, {
          name: editForm.name.trim(),
          description: editForm.description.trim()
        })
        isEditing.value = false
      }
    }

    const deletePlayer = () => {
      if (confirm(`Are you sure you want to delete ${props.player.name}?`)) {
        emit('delete', props.player.id)
      }
    }

    return {
      isEditing,
      editForm,
      startEdit,
      cancelEdit,
      saveEdit,
      deletePlayer
    }
  }
}
</script>

<style scoped>
.player-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  transition: transform 0.2s, box-shadow 0.2s;
}

.player-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.player-name {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.2em;
  font-weight: bold;
}

.player-description {
  margin: 0 0 15px 0;
  color: #666;
  line-height: 1.4;
  min-height: 40px;
}

.player-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn, .save-btn, .cancel-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.edit-btn:hover {
  background-color: #0056b3;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.save-btn:hover {
  background-color: #218838;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.player-edit-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-input, .edit-textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.edit-textarea {
  min-height: 60px;
  resize: vertical;
}

.edit-actions {
  display: flex;
  gap: 8px;
}
</style>
