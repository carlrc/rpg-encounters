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
          <p class="landing-eyebrow">Run Better Sessions</p>
          <h1 class="landing-title">RPG Encounters, Ready Before Initiative</h1>
          <p class="landing-subtitle">
            Organize players, worlds, reveals, and encounters from one interface designed for fast
            prep and smooth table flow.
          </p>

          <div class="landing-hero-actions">
            <a href="#features" class="shared-btn shared-btn-primary landing-btn">Features</a>
            <a href="#gallery" class="shared-btn shared-btn-secondary landing-btn">Gallery</a>
          </div>

          <div class="landing-hero-image-wrap">
            <img
              src="/landing/assets/images/home/phone.png"
              alt="Landing showcase"
              class="landing-hero-image"
            />
          </div>
        </div>
      </section>

      <section class="landing-section" id="features">
        <h2 class="landing-section-title">Built for encounter-heavy campaigns</h2>
        <div class="landing-feature-grid">
          <article class="landing-feature-card">
            <h3>Player Management</h3>
            <p>Share player login links and keep participation scoped to each encounter flow.</p>
          </article>
          <article class="landing-feature-card">
            <h3>Character Context</h3>
            <p>
              Track personality, memories, and reveals to drive more consistent in-session
              responses.
            </p>
          </article>
          <article class="landing-feature-card">
            <h3>Encounter Canvas</h3>
            <p>
              Model encounter flow visually and adjust pacing without losing campaign continuity.
            </p>
          </article>
          <article class="landing-feature-card">
            <h3>World Switching</h3>
            <p>Move between worlds without breaking your workflow or reconfiguring core data.</p>
          </article>
        </div>
      </section>

      <section class="landing-section" id="gallery">
        <h2 class="landing-section-title">Campaign atmosphere, captured</h2>
        <div class="landing-gallery-grid">
          <img src="/landing/assets/images/home/mountain.jpg" alt="Mountain scene" />
          <img src="/landing/assets/images/home/forest.jpg" alt="Forest scene" />
          <img src="/landing/assets/images/home/photography.jpg" alt="Adventure scene" />
          <img src="/landing/assets/images/home/sample.jpg" alt="Campaign sample" />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
  import AppBanner from '@/components/ui/AppBanner.vue'
</script>
