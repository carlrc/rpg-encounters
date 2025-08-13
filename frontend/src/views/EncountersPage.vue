<template>
  <div class="encounters-page">
    <WorldBuilder />
  </div>
</template>

<script>
  import WorldBuilder from '../components/WorldBuilder.vue'

  export default {
    name: 'EncountersPage',
    components: {
      WorldBuilder,
    },
  }
</script>

<style scoped>
  .encounters-page {
    height: 100%;
    width: 100%;
  }
</style>

<style scoped>
  .encounter-interface {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .character-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .character-avatar {
    flex-shrink: 0;
  }

  .avatar-image {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #007bff;
  }

  .avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #0056b3);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid #004085;
  }

  .avatar-initials {
    color: white;
    font-size: 24px;
    font-weight: bold;
  }

  .character-info h2 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.8em;
    font-weight: 700;
  }

  .character-info p {
    margin: 0;
    color: #6c757d;
    font-size: 1.1em;
    font-style: italic;
  }

  .encounter-controls {
    text-align: center;
  }

  .player-selection {
    margin-bottom: 30px;
  }

  .player-selection label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .control-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
  }

  .speak-button {
    padding: 16px 32px;
    font-size: 1.2em;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 140px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .challenge-button {
    padding: 12px 24px;
    font-size: 1em;
    font-weight: 600;
    border: 2px solid #6c757d;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
    background: white;
    color: #6c757d;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .challenge-button:hover:not(:disabled) {
    border-color: #007bff;
    color: #007bff;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
  }

  .challenge-button.active {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-color: #007bff;
  }

  .challenge-button.active:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
    border-color: #004085;
  }

  .challenge-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .speak-button:not(:disabled) {
    background: linear-gradient(135deg, #28a745, #218838);
    color: white;
  }

  .speak-button:not(:disabled):hover {
    background: linear-gradient(135deg, #218838, #1e7e34);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(40, 167, 69, 0.3);
  }

  .speak-button.recording {
    background: linear-gradient(135deg, #dc3545, #c82333) !important;
  }

  .speak-button.recording:hover {
    background: linear-gradient(135deg, #c82333, #bd2130) !important;
  }

  .speak-button.processing {
    background: linear-gradient(135deg, #ffc107, #e0a800) !important;
    cursor: not-allowed;
  }

  .speak-button:disabled {
    background: #6c757d;
    color: #fff;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }

  .skill-selection {
    margin-bottom: 20px;
  }

  .skill-selection label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .dice-result {
    margin-bottom: 20px;
    text-align: center;
  }

  .dice-number {
    font-size: 3em;
    font-weight: bold;
    color: #007bff;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 5px;
  }

  .dice-label {
    font-size: 1em;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .status {
    font-size: 1.1em;
    font-weight: 500;
    color: #6c757d;
    min-height: 24px;
    transition: color 0.3s ease;
  }

  .status.recording {
    color: #dc3545;
    font-weight: 600;
  }

  .status.processing {
    color: #ffc107;
    font-weight: 600;
  }
</style>
