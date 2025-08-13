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
