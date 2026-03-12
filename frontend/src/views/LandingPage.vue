<template>
  <div class="landing-page">
    <header class="landing-header page-header">
      <div class="landing-header-inner header-content">
        <div class="landing-header-left">
          <AppBanner />
        </div>

        <nav class="landing-nav" aria-label="Landing sections">
          <a href="#features" class="landing-nav-link">Features</a>
          <a href="#demo" class="landing-nav-link">Demos</a>
          <a
            href="https://github.com/carlrc/rpg-encounters"
            class="landing-nav-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </nav>

        <div class="landing-header-right">
          <router-link to="/login" class="shared-btn shared-btn-secondary landing-login-btn">
            Login
          </router-link>
        </div>
      </div>
    </header>

    <main>
      <section class="landing-hero" id="hero">
        <div class="landing-hero-inner">
          <h1 class="landing-title">Real-time voice NPCs for in-person tabletop games</h1>
          <p class="landing-subtitle">
            DM-controlled, so you don't have to perform every conversation.
          </p>

          <div class="landing-hero-actions">
            <a href="#features" class="shared-btn shared-btn-secondary landing-btn">Features</a>
            <a href="#demo" class="shared-btn shared-btn-secondary landing-btn">Demos</a>
            <a
              href="https://github.com/carlrc/rpg-encounters"
              class="shared-btn shared-btn-secondary landing-btn"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>

          <img
            src="/landing/assets/images/home/session.jpeg"
            alt="Landing showcase"
            width="1536"
            height="1024"
            class="landing-hero-image"
          />
        </div>
      </section>

      <section class="landing-section" id="highlights">
        <h2 class="landing-section-title">Built for voice at the table</h2>
        <div class="landing-feature-grid landing-feature-grid-centered">
          <article class="landing-feature-card">
            <h3>DM Centric</h3>
            <p>
              Everything is built from the DM perspective, to help you run an entertaining session.
            </p>
          </article>
          <article class="landing-feature-card">
            <h3>Interactive Roleplaying</h3>
            <p>
              The goal is to give players who value free-form roleplaying more interactivity in
              their sessions.
            </p>
          </article>
        </div>
      </section>

      <section class="landing-section" id="features">
        <h2 class="landing-section-title">Features</h2>
        <div class="landing-gallery-list">
          <article v-for="item in galleryItems" :key="item.title" class="landing-gallery-item">
            <div class="landing-gallery-media">
              <img
                :src="item.src"
                :alt="item.alt"
                :width="item.width"
                :height="item.height"
                class="landing-gallery-image"
              />
            </div>
            <div class="landing-gallery-copy">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="landing-section" id="demo">
        <h2 class="landing-section-title">Demos</h2>
        <div class="landing-feature-grid landing-feature-grid-centered">
          <a
            v-for="item in demoItems"
            :key="item.title"
            :href="item.href"
            class="landing-feature-card landing-demo-card"
            target="_blank"
            rel="noopener noreferrer"
          >
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </a>
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
      width: 1400,
      height: 1024,
    },
    {
      src: '/landing/assets/images/home/player-screen.png',
      alt: 'Player popup',
      title: 'Players can speak through their phone',
      description: 'Generate player links so they can talk to NPCs from their phones.',
      width: 1400,
      height: 1110,
    },
    {
      src: '/landing/assets/images/home/encounter-popup.png',
      alt: 'Encounter popup',
      title: 'Secrets that are unlocked with influence or ability checks',
      description:
        'Players can choose to free-form role play to gain influence or challenge characters with a charisma based ability check.',
      width: 1800,
      height: 1377,
    },
    {
      src: '/landing/assets/images/home/character-screen.png',
      alt: 'Character screen',
      title: 'Characters with attitude',
      description:
        'Configure characters with clear motivation and biases, dramatically changing how they respond to certain players.',
      width: 1400,
      height: 1184,
    },
  ]

  const demoItems = [
    {
      title: 'DM Perspective',
      description: 'Click to see how the DM controls a full NPC conversation.',
      href: 'https://rpg-encounters.com/videos/dm-centric-demo.mp4',
    },
    {
      title: 'Player Perspective',
      description: 'Click to watch how players talk to NPCs from their phones.',
      href: 'https://rpg-encounters.com/videos/player-centric-demo.mp4',
    },
  ]
</script>
