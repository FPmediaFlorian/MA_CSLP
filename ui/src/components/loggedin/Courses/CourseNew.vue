<template>
  <div class="row">
    <div class="col-12">
      <h1>Neuer Kurs</h1>
      <CourseForm @on-submit="createCourse"></CourseForm>
    </div>
  </div>
</template>
<script>
import CourseForm from "./CourseForm.vue";
export default {
  name: "CourseNew",
  components: { CourseForm },
  methods: {
    createCourse(course) {
      console.log(JSON.stringify(course));
      //call create course api
      //create Header
      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      //send course object to backend
      this.$http
        .post(process.env.VUE_APP_BASEURL + "/page", course, config)
        .then((response) => {
          console.log(response);
          //emit get course method from store
          if (response.status == 201) {
            this.$store.dispatch("fetchCourses");
            this.$router.push("/Courses");
          }
          //TODO: Error handling
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>
