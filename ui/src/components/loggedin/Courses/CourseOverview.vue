<template>
  <div class="container">
    <div class="row">
      <div class="col-12"><h1>Kursübersicht</h1></div>
    </div>

    <div class="row h-100">
      <div class="col-xl-6">
        <div class="card card-static card-fixed-height card-different-color">
          <div class="row">
            <div class="col-6">
              <div class="card-image">
                <img
                  src="../../../assets/img/characters/character_illustration_2.svg"
                  alt="Card image cap"
                />
              </div>
            </div>
            <div class="col-6">
              <h2 class="extreme-highlight">hi!</h2>
            </div>
          </div>
          <h3 class="card-title">
            Freut mich, dass du die Kurse gefunden hast,
          </h3>
          <!-- Course Card -->
          <p class="card-description">Viel Spaß, beim Erledigen und Lernen!</p>
        </div>
      </div>
      <!-- Teacher Card-->
      <div class="col-xl-6" v-if="user.isTeacher">
        <div class="card card-static card-fixed-height card-different-color2">
          <div class="row"></div>
          <h3 class="card-title">Willkommen {{ user.name }}!</h3>
          <!-- Course Card -->
          <p class="card-description">
            In diesem Abschnitt findest du alle Kurse auf die du zugreifen
            darfst.
          </p>
          <p class="card-description">
            Als Besitzer eines Kurses kannst du diesen jederzeit bearbeiten und
            löschen. Als Bearbeiter einens Kurses kannst du den Kurs jederzeit
            bearbeiten. Als Teilnehmer kannst du dir den Kurs nur ansehen.
          </p>
          <!-- <p class="card-description">
            Um einen neuen Kurs zu erstellen, klicke auf den Button "Neuer Kurs"
          </p> -->
          <!-- success button to linked to new course route -->
          <router-link to="/Courses/New" class="btn btn-success">
            Neuer Kurs</router-link
          >
        </div>
      </div>
      <!-- Dynamic Content -->
      <div v-if="!courses.length" class="col-xl-6">
        <div class="card item1">
          <div class="card-image">
            <img
              src="../../../assets/img/other/webdesign_icons4.svg"
              alt="Card image cap"
            />
          </div>
          <h3 class="card-title">Sorry!</h3>
          <!-- Course Card -->
          <p class="card-description">
            Leider hast du zur Zeit keine Kurse, die du machen kannst.
          </p>
        </div>
      </div>

      <CourseCard
        v-for="course in courses"
        :key="course.PageID"
        :course="course"
      ></CourseCard>
    </div>
  </div>
</template>

<script>
import CourseCard from "./CourseCard.vue";
import { mapGetters } from "vuex";

// const BASE_URL = process.env.VUE_APP_BASEURL;
export default {
  name: "CourseOverview",

  computed: {
    ...mapGetters({ user: "getCurrentUser" }),
    ...mapGetters({ courses: "getAllCourses" }),
  },
  components: { CourseCard },
};
</script>

<style>
.card-different-color {
  background-color: var(--menu4);
}
.card-different-color2 {
  background-color: var(--menu4);
}
</style>
