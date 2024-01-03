<template>
  <!-- Menü -->
  <div class="row">
    <div class="col-md-6">
      <div class="m-3">
        <div class="col-12 d-flex justify-content-end text-right">
          <h1>Hallo {{ user.username }}</h1>
        </div>
        <div class="col-12 d-flex justify-content-end text-right">
          <p>Schön, dass du hier bist. ☺️</p>
          <!-- <p>Dein Token ist: {{ token }}</p> -->
        </div>

        <div class="col-12 d-flex justify-content-end text-right">
          <div class="card mb-3" style="max-width: 18rem">
            <div class="card-body">
              <h5 class="card-title">
                <span class="badge badge-secondary">{{ courses.length }}</span
                ><router-link v-if="courses.length > 1" to="/Courses"
                  >Kurse warten</router-link
                >

                <router-link v-else to="/Courses">Kurs wartet</router-link>
              </h5>
              <p class="card-text">
                Du kannst derzeit {{ courses.length }}
                <router-link v-if="courses.length > 1" to="/Courses"
                  >Kurse</router-link
                >
                <router-link v-else to="/Courses">Kurs</router-link>
                besuchen
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-md-6">
      <img
        class="img-fluid max-width-240px"
        src="./../../assets/img/characters/character_illustration_4.svg"
        alt="Card image cap"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
// const BASE_URL = process.env.VUE_APP_BASEURL;
//Create Menue here
//add router here
//Distinct betwen schüler, lehrer, admin
//
export default {
  name: "MainDashboard",
  computed: {
    ...mapGetters({ user: "getCurrentUser" }),
    ...mapGetters({ courses: "getAllCourses" }),
  },
};
</script>

<style>
.max-width-240px {
  max-width: 240px;
}
</style>
