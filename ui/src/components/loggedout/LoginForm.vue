<template>
  <div class="m-4">
    <h1>Anmelden</h1>
    <form @submit.prevent="login" class="mt-4">
      <!-- Email input -->

      <div
        class="form-group mb-4"
        :class="{ error: v$.username.$errors.length }"
      >
        <label for="usernameLogin">Email oder Username</label>
        <input
          id="usernameLogin"
          class="form-control mt-2"
          placeholder="Username oder E-Mail"
          type="text"
          v-model="v$.username.$model"
        />
        <div class="pre-icon os-icon os-icon-user-male-circle"></div>
        <!-- error message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.username.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>

      <!-- <div class="form-outline mb-4">
        <input
          v-model="username"
          type="email"
          id="loginName"
          class="form-control"
        />
        <label class="form-label" for="loginName">Email or username</label>
      </div> -->

      <!-- Password input -->
      <div
        class="form-group mb-4"
        :class="{ error: v$.password.$errors.length }"
      >
        <label for="passwordLogin">Password</label>
        <input
          id="passwordLogin"
          class="form-control mt-2"
          placeholder="Passwort"
          type="password"
          v-model="v$.password.$model"
        />
        <div class="pre-icon os-icon os-icon-fingerprint"></div>
        <!-- error message -->
        <div
          class="input-errors"
          v-for="(error, index) of v$.password.$errors"
          :key="index"
        >
          <div class="error-msg">{{ error.$message }}</div>
        </div>
      </div>
      <!-- <div class="form-outline mb-4">
        <input
          v-model="password"
          type="password"
          id="loginPassword"
          class="form-control"
        />
        <label class="form-label" for="loginPassword">Password</label>
      </div> -->

      <!-- 2 column grid layout -->
      <div class="row mb-4">
        <div class="col-md-6 d-flex justify-content-center">
          <!-- Checkbox -->
          <div class="form-check mb-3 mb-md-0">
            <input
              class="form-check-input"
              type="checkbox"
              value=""
              id="loginCheck"
              checked
            />
            <label class="form-check-label" for="loginCheck">
              Remember me
            </label>
          </div>
        </div>

        <div class="col-md-6 d-flex justify-content-center">
          <!-- Simple link -->
          <a class="link-secondary" @click="showModal = true"
            >Forgot password?</a
          >
        </div>
      </div>

      <!-- Submit button -->

      <div class="row justify-content-center mb-4">
        <div class="col-md-6">
          <button class="btn btn-primary mb-2">Anmelden</button>
        </div>
        <div class="col-md-6">
          <a
            @click="LoginChange"
            class="btn btn btn-outline-secondary mb-2"
            role="button"
            >Registrieren</a
          >
        </div>
      </div>
      <div class="row justify-content-center">
        <div class="alert alert-danger" v-if="loginFailed">
          {{ error }}
        </div>
      </div>
    </form>

    <!-- bootstrap modal with reset password form that opens buttonclick -->

    <div v-if="showModal">
      <transition name="modal">
        <div class="modal-mask">
          <div class="modal-wrapper">
            <div class="modal-dialog" role="document">
              <div class="modal-content rounded-box-highlight">
                <div class="modal-header">
                  <h2 class="modal-title">Passwort zurücksetzen</h2>
                  <button
                    type="button"
                    class="close"
                    data-dismiss="modal"
                    aria-label="Close"
                  >
                    <span aria-hidden="true" @click="showModal = false"
                      >&times;</span
                    >
                  </button>
                </div>
                <div class="modal-body">
                  <form>
                    <div class="form-outline mb-4">
                      <input
                        v-model="username"
                        type="text"
                        id="loginName"
                        class="form-control"
                      />
                      <label class="form-label" for="loginName"
                        >Email or username</label
                      >
                    </div>
                    <button @click="login" class="btn btn-primary mb-4">
                      Reset Password
                    </button>
                  </form>
                </div>
                <div class="modal-footer">
                  <button
                    type="button"
                    class="btn btn-secondary"
                    @click="showModal = false"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import useVuelidate from "@vuelidate/core";
import { required, minLength } from "@vuelidate/validators";

//const BASE_URL = process.env.VUE_APP_BASEURL;
//Get BASE_URL from store
//const BASE_URL = this.$store.state.BASE_URL;
//const BASE_URL = process.env.VUE_APP_BASE_URL;
const BASE_URL = "http://cslearning:5050";

export default {
  name: "LoginForm",
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      username: "",
      password: "",
      showModal: false,
      loginFailed: false,
      error: "",
    };
  },
  validations() {
    return {
      username: {
        required,
      },
      password: {
        required,
        minLength: minLength(8),
      },
    };
  },
  methods: {
    login() {
      this.loginFailed = false;
      // check if form is valid
      this.v$.$touch();
      if (this.v$.$invalid) {
        this.loginFailed = true;
        this.error = "Bitte alle Felder ausfüllen";
      }
      //create auth header
      const authHeader = {
        headers: {
          Authorization: "Basic " + btoa(this.username + ":" + this.password),
        },
      };
      //send user object to backend
      this.$http
        .get(BASE_URL + "/login", authHeader)
        .then((response) => {
          console.log("Should be: " + response.data.authToken);
          localStorage.setItem("token", response.data.authToken);
          // save authtoken to store
          this.$store.commit("setAuthToken", response.data.authToken);
          //log token
          //print authtoken from store
          console.log("Actual state in store: " + this.$store.state.authToken);
          // var date = new Date();
          // var time = date.getTime();
          // //add 30 minutes to current time
          // time += 30 * 60 * 1000;
          // //set new time to localstorage
          // localStorage.setItem("tokenTimeout", time);

          //log token from local storage
          // console.log(localStorage.getItem("token"));
          this.loginFailed = false;
          //redirect to login page
          //this.$router.push("/");
          this.$emit("login");
          this.$router.push("/");
        })
        .catch((error) => {
          this.loginFailed = true;
          this.error = error.response.data.message;
          console.log(error);
        });
    },
    LoginChange() {
      this.$emit("loginchange");
    },
  },
};
</script>

<style></style>
