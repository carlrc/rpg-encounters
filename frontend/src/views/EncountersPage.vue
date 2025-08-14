<template>
  <div class="encounters-page">
    <EncounterBuilder />
  </div>
</template>

<script>
  import EncounterBuilder from '../components/EncounterBuilder.vue'

  export default {
    name: 'EncountersPage',
    components: {
      EncounterBuilder,
    },
  }
</script>

<style scoped>
  .encounters-page {
    height: 100%;
    width: 100%;
  }
</style>
