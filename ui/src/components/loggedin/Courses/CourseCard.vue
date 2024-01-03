<template>
  <!-- Dynamic Content -->
  <div class="col-xl-6">
    <router-link :to="'/courses/' + course.pageID">
      <div class="card card-fixed-height">
        <div class="t-align-r">
          <div
            v-if="user.isTeacher || user.isAdmin"
            v-html="getAccessLevelBadge(course.pageID)"
          ></div>
        </div>
        <div class="card-image">
          <img :src="course.imgLink" alt="Card image cap" />
        </div>
        <h3 class="card-title">{{ course.name }}</h3>
        <!-- Course Card -->
        <p class="card-description">
          {{ course.description }}
        </p>
      </div>
    </router-link>
  </div>
</template>
<script>
import { mapGetters } from "vuex";

export default {
  props: ["course"],
  computed: {
    ...mapGetters({ accessLevel: "getAccessLvlForCourse" }),
    ...mapGetters({ user: "getCurrentUser" }),
  },
  methods: {
    getAccessLevelBadge(id) {
      switch (this.accessLevel(id)) {
        case 0:
          return "Teilnehmer</span>";
        case 1:
          return '<span class="badge bg-light text-dark">Teilnehmer</span>';
        case 2:
          return '<span class="badge bg-secondary">Bearbeiter</span>';
        case 3:
          return '<span class="badge bg-dark">Besitzer</span>';
        default:
          return "Unbekannt";
      }
    },
  },
};
</script>
<style>
.t-align-r {
  text-align: right;
}
</style>
