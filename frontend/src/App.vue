<template>
  <AppLayout>
    <router-view />
  </AppLayout>
  <NotificationContainer />
</template>

<script setup>
  import AppLayout from './components/layout/AppLayout.vue'
  import NotificationContainer from './components/ui/NotificationContainer.vue'
</script>
