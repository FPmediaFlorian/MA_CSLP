<template>
  <div class="mt-4">
    <h1>Registrieren</h1>
    <form @submit.prevent="onSubmit" class="mt-4">
      <!-- First and user Name Row -->

      <div class="form-group mb-4">
        <label for="">Name</label
        ><input
          class="form-control"
          placeholder="Name"
          type="text"
          v-model="v$.name.$model"
        />
        <div class="pre-icon os-icon os-icon-user-male-circle"></div>
        <!-- Error Message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.name.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <div class="form-group mb-4">
        <label for=""> Username:</label
        ><input
          class="form-control"
          placeholder="Username"
          type="text"
          v-model="v$.username.$model"
        />
        <div class="pre-icon os-icon os-icon-user-male-circle"></div>
        <!-- Error Message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.username.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <!-- Email Row -->
      <div class="form-group mb-4">
        <label for="">E-Mail Adresse</label>
        <input
          class="form-control"
          placeholder="E-Mail Adresse"
          type="email"
          v-model="v$.mail.$model"
        />
        <div class="pre-icon os-icon os-icon-email-2-at2"></div>
        <!-- Error Message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.mail.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <!-- Password and Confirm Password Row -->

      <div class="form-group mb-4">
        <label for=""> Passwort</label
        ><input
          class="form-control"
          placeholder="Passwort"
          type="password"
          v-model="v$.password.$model"
        />
        <div class="pre-icon os-icon os-icon-fingerprint"></div>
        <!-- Error Message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.password.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <div class="form-group mb-4">
        <label for="">Passwort bestätigen</label
        ><input
          @input="checkPassword()"
          class="form-control"
          placeholder="Passwort bestätigen"
          type="password"
          v-model="v$.confirmPassword.$model"
        />
        <!-- Error Message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.confirmPassword.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="row justify-content-center d-flex mb-4">
        <div class="col-md-6">
          <!-- bootstrap buttom -->
          <a @click="Register" class="btn btn-primary" :disabled="v$.$invalid">
            Registrieren
          </a>
        </div>
        <div class="col-md-6">
          <!-- bootstrap buttom -->
          <a
            @click="LoginChange"
            class="btn btn-outline-secondary"
            role="button"
            >Login</a
          >
        </div>
      </div>
      <!-- Error Messages -->
      <div class="row justify-content-center">
        <div class="alert alert-danger" v-if="registerFail">
          {{ registerMessage }}
        </div>
      </div>
      <div class="row justify-content-center">
        <div class="alert alert-success" v-if="registerSuccess">
          {{ registerMessage }}
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import useVuelidate from "@vuelidate/core";
import { required, email, minLength, sameAs } from "@vuelidate/validators";

const BASE_URL = process.env.VUE_APP_BASEURL;

export function validName(name) {
  let validNamePattern = new RegExp("^[a-zA-Z]+(?:[-'\\s][a-zA-Z]+)*$");
  if (validNamePattern.test(name)) {
    return true;
  }
  return false;
}

export function validUsername(username) {
  let validUsernamePattern = new RegExp("^[a-zA-Z0-9_-]{3,16}$");
  if (validUsernamePattern.test(username)) {
    return true;
  }
  return false;
}

export default {
  name: "LoginForm",
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      username: "",
      password: "",
      confirmPassword: "",
      mail: "",
      name: "",
      registerFail: false,
      registerSuccess: false,
      registerMessage: "",
    };
  },
  validations() {
    return {
      name: {
        required,
        name_validation: {
          $validator: validName,
          $message:
            "Ungültiger Name. Ein Name darf nur Bindestriche (-) und Abstände ( ) enthalten.",
        },
      },
      username: {
        required,
        username_validation: {
          $validator: validUsername,
          $message:
            "Ungültiger Username. Ein Username darf nur Kleinbuchstaben, Zahlen und Unterstriche (_) enthalten.",
        },
      },
      mail: { required, email },
      password: { required, min: minLength(6) },
      confirmPassword: { required, sameAsPassword: sameAs(this.password) },
    };
  },

  methods: {
    Register() {
      console.log("Register");
      //create request
      const request = {
        name: this.name,
        username: this.username,
        mail: this.mail,
        password: this.password,
      };
      //send request
      this.$http
        .post(BASE_URL + "/user", request)
        .then((response) => {
          console.log(response);
          //Show success message
          this.registerSuccess = true;
          this.registerFail = false;
          this.registerMessage = "Registrierung erfolgreich";
          //this.LoginChange();
        })
        .catch((error) => {
          console.log(error);
          //Show error message
          this.registerFail = true;
          this.registerSuccess = false;
          this.registerMessage = error.response.data.message;
        });
    },
    LoginChange() {
      this.$emit("loginchange");
      //this.$parent.LoginChange();
    },
  },
};
</script>

<style></style>
