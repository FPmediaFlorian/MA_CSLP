<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item">
        <router-link :to="'/Courses'"> Übersicht</router-link>
      </li>
      <li class="breadcrumb-item active" aria-current="page">Kurs Detail</li>
    </ol>
  </nav>
  <div class="row justify-content-center">
    <div class="alert alert-danger" v-if="error">
      {{ errorMessage }}
    </div>
  </div>
  <div class="row p-4">
    <div class="col-md-4">
      <!-- <img :src="course.imgLink" alt="Image for the course" /> -->
      <img
        :src="course.imgLink"
        class="img-fluid ${3|rounded-top,rounded-right,rounded-bottom,rounded-left,rounded-circle,|}"
        alt=""
      />
    </div>
    <div class="col-md-6 align-self-center">
      <h1>{{ course.name }}</h1>
      <p>{{ course.description }}</p>
    </div>
    <div v-if="isAdmin || isTeacher" class="col-md-2 align-self-center">
      <!-- deleteButton -->
      <button
        v-if="allowedToDelete()"
        type="button"
        class="btn btn-danger mb-1"
        @click="deleteCourse"
      >
        Kurs löschen
      </button>
      <!-- bearbeiten button -->
      <router-link
        :to="'/Courses/edit/' + course.pageID"
        v-if="allowedToEdit()"
      >
        <button type="button" class="btn btn-warning mb-1">
          Kurs bearbeiten
        </button>
      </router-link>
      <router-link
        :to="'/Courses/access/' + course.pageID"
        v-if="allowedToDelete()"
      >
        <button type="button" class="btn btn-warning mb-1">
          Kurs Zugriff verwalten
        </button>
      </router-link>
      <button
        type="button"
        class="btn btn-light mb-1"
        @click="duplicateCourse()"
      >
        Kurs duplizieren
      </button>
    </div>
  </div>
  <div class="row">
    <ContentDetail
      v-for="(content, index) in course.contents"
      :key="content.contentID"
      :content="content"
      :index="index"
    />
  </div>
</template>

<script>
import ContentDetail from "./Content/ContentDetail.vue";
import { mapGetters } from "vuex";
const BASE_URL = process.env.VUE_APP_BASEURL;
export default {
  name: "CourseDetail",
  data() {
    return {
      course: {},
      error: false,
      errorMessage: "",
    };
  },
  computed: {
    ...mapGetters({ accessLevel: "getAccessLvlForCourse" }),
    ...mapGetters({ isTeacher: "getCurrentUserIsTeacher" }),
    ...mapGetters({ isAdmin: "getCurrentUserIsAdmin" }),
    ...mapGetters({ getNewCourse: "getLastCoursefromCourseList" }),
  },
  methods: {
    getCourse() {
      this.error = false;
      //console.log(this.$route.params.id);
      try {
        //Auth Header
        const config = {
          headers: {
            authToken: localStorage.getItem("token"),
          },
        };
        this.$http
          .get(BASE_URL + "/page/" + this.$route.params.id, config)
          .then((response) => {
            // console.log("ALERTEALERTEALERTEALERTEALERTEALERTEALERTEALERTE");
            this.course = response.data;
            console.log(this.course);
            if (response.status !== 200) {
              this.error = true;
              this.errorMessage =
                "Leider ist beim Laden des Kurses ein Fehler aufgetreten. Bitte versuchen Sie es später noch einmal.";
            }
          });

        return this.course;
      } catch (error) {
        this.error = true;
        console.log(error);
      }
    },
    allowedToEdit() {
      // return false;
      if (this.accessLevel(this.course.pageID) > 1) {
        return true;
      } else {
        //check if user is admin
        if (this.$store.getters.getCurrentUser.isAdmin) {
          return true;
        }
        return false;
      }
    },
    allowedToDelete() {
      // return false;
      if (this.accessLevel(this.course.pageID) > 2) {
        return true;
      } else {
        //check if user is admin
        if (this.$store.getters.getCurrentUser.isAdmin) {
          return true;
        }
        return false;
      }
    },
    deleteCourse() {
      this.error = false;
      //Auth Header
      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      this.$http
        .delete(BASE_URL + "/page/" + this.$route.params.id, config)
        .then((response) => {
          console.log(response);
          if (response.status == 200) {
            //fetch courses
            this.$store.dispatch("fetchCourses");
            this.$router.push("/Courses");
          }
          //TODO Handle Delete Error
        })
        .catch((error) => {
          console.log(error);
          this.error = true;
          this.errorMessage =
            "Leider ist beim Löschen des Kurses ein Fehler aufgetreten. Bitte versuchen Sie es später noch einmal.";
        });
    },
    duplicateCourse() {
      this.error = false;
      //Auth Header
      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      const data = {
        pageID: this.course.pageID,
      };
      this.$http
        .post(BASE_URL + "/page/duplicate", data, config)
        .then((response) => {
          console.log(response);
          if (response.status == 201) {
            //fetch courses
            this.$store.dispatch("fetchCourses");

            this.$router.push("/Courses");
          }
          //TODO Handle Delete Error
        })
        .catch((error) => {
          console.log(error);
          this.error = true;
          this.errorMessage =
            "Leider ist beim Duplizieren des Kurses ein Fehler aufgetreten. Bitte versuchen Sie es später noch einmal.";
        });
    },
  },

  created() {
    this.getCourse();
    //update userloginstatus
  },
  components: { ContentDetail },
};
</script>

<style></style>
