<template>
  <AppLayout>
    <router-view />
  </AppLayout>
  <NotificationContainer />
</template>

<script>
  import AppLayout from './components/layout/AppLayout.vue'
  import NotificationContainer from './components/ui/NotificationContainer.vue'

  export default {
    name: 'App',
    components: {
      AppLayout,
      NotificationContainer,
    },
  }
</script>
