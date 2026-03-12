<template>
  <div class="landing-page">
    <header>
      <h1>Bienvenue sur notre Application de Gestion d'Inventaire</h1>
    </header>
    <main>
      <section class="hero">
        <h2>Votre solution complète pour la gestion d'actifs</h2>
        <p>Découvrez comment notre application peut optimiser votre gestion d'inventaire.</p>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  data() {
    return {};
  },
};
</script>

<style scoped>
.landing-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: url('/path/to/your/image.jpg') no-repeat center center;
  background-size: cover;
}

header {
  text-align: center;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}

.hero {
  text-align: center;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
}
</style>