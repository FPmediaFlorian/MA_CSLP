<template>
  <div class="d-flex align-items-center justify-content-center vh-100">
    <div class="text-center">
      <h1 class="display-1 fw-bold">404</h1>
      <p class="fs-3">
        <span class="text-danger">Opps!</span> Seite nicht gefunden
      </p>
      <p class="lead">
        Sorry, die Seite die du gesucht hast gibt es leider nicht
      </p>
      <router-link to="/" class="btn btn-outline-dark mx-2"
        >Zurück zur Startseite</router-link
      >
      <router-link to="/courses" class="btn btn-primary mx-2"
        >Zu den Kursen</router-link
      >
    </div>
  </div>
</template>
