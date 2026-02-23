<template>
  <div class="landing-page">
    <header class="landing-header page-header">
      <div class="landing-header-inner header-content">
        <AppBanner />

        <router-link to="/login" class="shared-btn shared-btn-primary landing-login-btn">
          Login
        </router-link>
      </div>
    </header>

    <main>
      <section class="landing-hero" id="hero">
        <div class="landing-hero-inner">
          <h1 class="landing-title">Agents that fit into your sessions</h1>
          <p class="landing-subtitle">Create characters that players can speak with freely.</p>

          <div class="landing-hero-actions">
            <a href="#features" class="shared-btn shared-btn-primary landing-btn">Features</a>
            <a
              href="https://github.com/carlrc/rpg-encounters"
              class="shared-btn shared-btn-secondary landing-btn"
              target="_blank"
              rel="noopener noreferrer"
            >
              Code
            </a>
          </div>

          <div class="landing-hero-image-wrap">
            <img
              src="/landing/assets/images/home/session.jpeg"
              alt="Landing showcase"
              class="landing-hero-image"
            />
          </div>
        </div>
      </section>

      <section class="landing-section" id="highlights">
        <h2 class="landing-section-title">Built for in-person campaigns</h2>
        <div class="landing-feature-grid">
          <article class="landing-feature-card">
            <h3>DM Controlled</h3>
            <p>Everything is designed from the DMs perspective.</p>
          </article>
          <article class="landing-feature-card">
            <h3>Characters with Personality</h3>
            <p>
              Create characters with biases, motivations and trust based secrets, which dictate how
              they respond.
            </p>
          </article>
          <article class="landing-feature-card">
            <h3>Flexible Microphone System</h3>
            <p>
              Use a shared conference microphone or generate player links for mobile device support.
            </p>
          </article>
          <article class="landing-feature-card">
            <h3>Ability Checks</h3>
            <p>
              Players can choose ability checks using their charisma skills to influence characters.
            </p>
          </article>
        </div>
      </section>

      <section class="landing-section" id="features">
        <h2 class="landing-section-title">Features</h2>
        <div class="landing-gallery-list">
          <article v-for="item in galleryItems" :key="item.title" class="landing-gallery-item">
            <div class="landing-gallery-media">
              <img :src="item.src" :alt="item.alt" class="landing-gallery-image" />
            </div>
            <div class="landing-gallery-copy">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
  import AppBanner from '@/components/ui/AppBanner.vue'

  const galleryItems = [
    {
      src: '/landing/assets/images/home/encounters-screen.png',
      alt: 'Encounters screen',
      title: 'Visually manage encounters',
      description:
        'Assign characters and players to encounters that match the board in front of you.',
    },
    {
      src: '/landing/assets/images/home/encounter-popup.png',
      alt: 'Encounter popup',
      title: 'Dynamic conversations',
      description:
        'See how characters are being influenced in real time and what secrets are available to the players.',
    },
    {
      src: '/landing/assets/images/home/player-screen.png',
      alt: 'Player popup',
      title: 'Players can speak through their phone',
      description: 'Generate login links for players and let them control the conversation.',
    },
  ]
</script>
