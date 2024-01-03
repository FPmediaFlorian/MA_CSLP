<template>
  <div class="row">
    <div class="col">
      <!-- add img -->
      <img
        src="../../assets/img/characters/character_illustration_2.svg"
        alt="chat"
      />
    </div>
    <div class="col d-flex align-items-end">
      <div class="row">
        <div class="col-12">
          <p class="extreme-highlight">HI!</p>
        </div>
        <div class="col-12">
          <h1>Ich bin Dany,</h1>
        </div>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col m-4">
      <p>
        deine Beschützerin im Internet. Meld dich jetzt an und wir lernen
        gemeinsam wie du das Internet verwenden kannst. Bitte deine Eltern dir
        bei der Anmeldung zu helfen. Bist du erstmal angemeldet können wir
        direkt gemeinsam mit den ersten Abenteuern beginnen.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "StartDescription",
  data() {
    return { username: "", password: "" };
  },
  methods: {
    login() {
      console.log("login");
    },
  },
};
</script>

<style></style>
