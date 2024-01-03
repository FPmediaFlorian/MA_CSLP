<template>
  <!-- Main entrypoint of the Application
      Shows the Registration/Login Form and a short description of the plattform -->

  <div class="main-container">
    <div class="viewport-loggedout">
      <!-- Create a 2 column bootstrap div -->
      <div class="row">
        <!-- Left column -->
        <div class="col-lg-8">
          <div class="left-column">
            <!-- add description component -->
            <StartDescription></StartDescription>
          </div>
        </div>
        <!-- Right column -->
        <div
          class="col-lg-4 rounded-box-highlight d-flex align-items-center justify-content-center"
        >
          <transition name="smooth">
            <!-- <TransitionGroup name="smooth"> -->
            <div v-if="login" class="right-column login-container w-100">
              <LoginForm @loginchange="LoginChange" @login="Login"></LoginForm>
            </div>
            <div v-else class="right-column login-container w-100">
              <RegisterForm @loginchange="LoginChange"></RegisterForm>
            </div>
            <!-- </TransitionGroup> -->
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
//import HelloWorld from "./components/HelloWorld.vue";
import LoginForm from "./LoginForm.vue";
import StartDescription from "./StartDescription.vue";
import RegisterForm from "./RegisterForm.vue";

//const BASE_URL = process.env.VUE_APP_BASEURL;

export default {
  data() {
    return {
      beMessage: "hi from frontend..",
      login: true,
    };
  },

  methods: {
    LoginChange() {
      this.login = !this.login;
    },
    Login() {
      this.$emit("login");
    },
  },

  mounted() {},

  name: "LoggedOutHome",
  components: {
    StartDescription,
    LoginForm,
    RegisterForm,
  },
};
</script>

<style>
h1 {
  font-size: 3rem;
}

.main-container {
  font-family: "Nunito", sans-serif;
  /*font-family: Avenir, Helvetica, Arial, sans-serif;*/
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100vh;
}
.viewport-loggedout {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 90vh;
  background-color: var(--offWhite);
  padding: 2em;
  margin-top: 5vh;
  margin-bottom: 5vh;
  margin-left: 5vw;
  margin-right: 5vw;
  border-radius: 50px;
}

.login-container {
  max-width: 360px;
}

.smooth-enter-active,
.smooth-leave-active {
  transition: opacity 0.1s ease;
}

.smooth-enter-from,
.smooth-leave-to {
  opacity: 0;
}
</style>
