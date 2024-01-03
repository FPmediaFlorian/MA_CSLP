<template>
  <div class="row">
    <h3>Passwort Rechner</h3>
    <p>
      Hier kannst du die Einstellungen für dein Passwort machen und dann sehen
      wie sicher es ist.
    </p>
    <div class="col-3">
      <input type="range" min="2" max="32" class="slider" v-model="length" />
      <p>
        Value: <span id="lengthField">{{ length }}</span>
      </p>
      <div class="form-group">
        <input type="checkbox" id="uppercase" v-model="uppercase" />
        <label for="uppercase">Großbuchstaben</label>
      </div>
      <div class="form-group">
        <input type="checkbox" id="lowercase" v-model="lowercase" />
        <label for="lowercase">Kleinbuchstaben</label>
      </div>
      <div class="form-group">
        <input type="checkbox" id="numbers" v-model="numbers" />
        <label for="numbers">Zahlen</label>
      </div>
      <div class="form-group">
        <input type="checkbox" id="symbols" v-model="symbols" />
        <label for="symbols">Sonderzeichen</label>
      </div>
    </div>
    <div class="col-9">
      <div class="form-group">
        <label for="password">Beispiel Passwort</label>

        <p>{{ password }}</p>
      </div>
      <div class="form-group">
        <label for="possibleDifferentPasswords"
          >Mögliche verschiedene Passwörter</label
        >
        <p>
          {{
            toPlainString(possibleDifferentPasswords)
              .toString()
              .replace(/\B(?=(\d{3})+(?!\d))/g, ".")
          }}
        </p>
      </div>
      <div class="form-group">
        <label for="possibleDifferentPasswords"
          >So lange braucht ein Computer um alle Passwörter
          durchzuprobieren.</label
        >
        <p>
          {{ convertMStoYearsDaysHoursMinutesSeconds() }}
        </p>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: "PwChecker",
  data() {
    return {
      length: 8,
      uppercase: true,
      lowercase: true,
      numbers: true,
      symbols: true,
      password: "",
      possibleDifferentPasswords: 0,
      timeMS: 0,
    };
  },

  methods: {
    generatePassword() {
      const length = this.length;
      const uppercase = this.uppercase;
      const lowercase = this.lowercase;
      const numbers = this.numbers;
      const symbols = this.symbols;

      let charset = "";
      if (uppercase) charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      if (lowercase) charset += "abcdefghijklmnopqrstuvwxyz";
      if (numbers) charset += "0123456789";
      if (symbols) charset += "!@#$%^&*()_+~`|}{[]:;?><,./-=";

      let retVal = "";
      for (let i = 0, n = charset.length; i < length; ++i) {
        retVal += charset.charAt(Math.floor(Math.random() * n));
      }
      return retVal;
    },
    convertMStoYearsDaysHoursMinutesSeconds() {
      let ms = this.timeMS;
      let years = Math.floor(ms / 31536000000);
      let days = Math.floor((ms % 31536000000) / 86400000);
      let hours = Math.floor(((ms % 31536000000) % 86400000) / 3600000);
      let minutes = Math.floor(
        (((ms % 31536000000) % 86400000) % 3600000) / 60000
      );
      let seconds = Math.floor(
        ((((ms % 31536000000) % 86400000) % 3600000) % 60000) / 1000
      );
      return (
        this.toPlainString(years) +
        " Jahre, " +
        days +
        " Tage, " +
        hours +
        " Stunden, " +
        minutes +
        " Minuten, " +
        seconds +
        " Sekunden"
      );
    },
    toPlainString(num) {
      return ("" + +num).replace(
        /(-?)(\d*)\.?(\d*)e([+-]\d+)/,
        function (a, b, c, d, e) {
          return e < 0
            ? b + "0." + Array(1 - e - c.length).join(0) + c + d
            : b + c + d + Array(e - d.length + 1).join(0);
        }
      );
    },

    recalcPW() {
      console.log("recalcPW");
      let pw = this.generatePassword();
      this.password = pw;
      let charset = "";
      if (this.uppercase) charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      if (this.lowercase) charset += "abcdefghijklmnopqrstuvwxyz";
      if (this.numbers) charset += "0123456789";
      if (this.symbols) charset += "!@#$%^&*()_+~`|}{[]:;?><,./-=";

      this.possibleDifferentPasswords = Math.pow(charset.length, this.length);
      this.timeMS = this.possibleDifferentPasswords / 1000000000;
    },
  },
  watch: {
    $data: {
      handler: function () {
        console.log("data changed");
        this.recalcPW();
      },
      deep: true,
    },
  },
  mounted() {
    this.recalcPW();
  },
};
</script>
<style>
.show-hide {
  display: none;
}
</style>
