<template>
  <!-- Main entrypoint of the Application
      Shows the Registration/Login Form and a short description of the plattform -->
  <div v-if="loginState">
    <div class="main">
      <div class="margin-side row mt-5 justify-content-center show-hide">
        <!-- <nav class="navbar">
          <button
            class="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
              <li class="nav-item">as</li>
            </ul> -->
        <div class="col-4">
          <router-link :to="'/'" class="menu-font">
            <div class="d-flex justify-content-center menu-item item1">
              Dashboard
            </div>
          </router-link>
        </div>
        <div class="col-3">
          <router-link :to="'/Courses'" class="menu-font">
            <div class="d-flex justify-content-center menu-item item2">
              Kurse
            </div>
          </router-link>
        </div>

        <div class="col-2">
          <router-link :to="'/User'" class="menu-font">
            <div class="d-flex justify-content-center menu-item item4">
              <i
                class="fa-solid fa-user"
                data-bs-toggle="tooltip"
                data-bs-placement="top"
                data-bs-custom-class="custom-tooltip"
                data-bs-title="Mein Profil"
              ></i>
            </div>
          </router-link>
        </div>
        <div class="col-2">
          <div
            class="d-flex justify-content-center menu-item item4"
            @click="logoutMeOut"
          >
            <i
              class="fa-solid fa-right-from-bracket"
              data-bs-toggle="tooltip"
              data-bs-placement="top"
              data-bs-custom-class="custom-tooltip"
              data-bs-title="Ausloggen"
            ></i>
          </div>
        </div>
        <!-- </div>
        </nav> -->
        <!-- <div class="col-1">
          <div class="d-flex justify-content-center menu-item item4">Konto</div>
        </div> -->
      </div>
      <div class="viewport">
        <router-view v-slot="{ Component, route }">
          <transition name="slide-fade" mode="out-in">
            <div :key="route.name" class="container-fluid h-100">
              <component :is="Component" :key="$route.path" />
            </div>
          </transition>
        </router-view>
      </div>
    </div>
  </div>
  <div v-else class="main">
    <LoggedOutHome @login="UpdateLoginState"></LoggedOutHome>
  </div>
</template>

<script>
//import HelloWorld from "./components/HelloWorld.vue";
import LoggedOutHome from "./components/loggedout/LoggedOutHome.vue";
//import MainDashboard from "./components/loggedin/MainDashboard.vue";
// import LoginForm from "./components/LoginForm.vue";
// import StartDescription from "./components/StartDescription.vue";
// import RegisterForm from "./RegisterForm.vue";

import { mapGetters, mapActions } from "vuex";

// const BASE_URL = process.env.VUE_APP_BASEURL;

export default {
  data() {
    return {
      //loginState: true,
    };
  },

  methods: {
    ...mapActions(["UpdateLoginState"]),
    ...mapActions({ logoutMeOut: "Logout" }),
  },
  computed: {
    ...mapGetters({ loginState: "getLoginState" }),
  },

  created() {
    this.UpdateLoginState();
  },
  // mounted() {
  //   this.UpdateLoginState();
  //   this.loginState = this.loggedIn;
  // },
  beforeUpdate() {
    this.UpdateLoginState();
  },
  // watch: {
  //   $route() {
  //     this.dispatch("UpdateLoginState");
  //   },
  // },
  name: "App",
  components: {
    LoggedOutHome,
  },
};
</script>

<style>
.main {
  width: 100%;
  flex-direction: column;
  margin-left: auto;

  margin-right: auto;
  max-width: 1920px;
  /* justify-content: center; */
  /* align-items: center; */
}
.viewport {
  background-color: var(--offWhite);
  margin-top: 0px;
  margin-bottom: 5vh;
  margin-left: 5vw;
  margin-right: 5vw;
  padding: 2em;
  border-radius: 50px;
  min-height: 80vh;
}
.margin-side {
  margin-left: 7vw !important;
  margin-right: 7vw !important;
}
.fill-height {
  min-height: 100%;
  height: 100%;
}

/* media query for small devices eg mobile phones*/
@media only screen and (max-width: 600px) {
  .margin-side {
    margin-left: 0px !important;
    margin-right: 0px !important;
  }
  .viewport {
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
