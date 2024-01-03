<template>
  <div class="row">
    <div class="col-12">
      <h1>Kurs bearbeiten</h1>
      <CourseForm
        :existingcourse="course"
        @on-submit="updateCourse"
      ></CourseForm>
    </div>
  </div>
</template>
<script>
import CourseForm from "./CourseForm.vue";
import { mapGetters } from "vuex";
export default {
  name: "CourseNew",
  data() {
    return {
      course: {},
      controlCourse: {},
    };
  },

  components: { CourseForm },
  methods: {
    updateCourse(course) {
      //Check if course has changed
      if (
        JSON.stringify(course).localeCompare(JSON.stringify(this.controlCourse))
      ) {
        console.log("No changes");
        this.$router.push("/Courses");
        return;
      }
      console.log("Course has changed");

      //filter new content from old content
      let newContent = course.contents.filter((content) => {
        return content.contentID == null;
      });
      console.log("After New Content Filter");
      //filter if content is deleted
      let deletedContent = this.controlCourse.contents.filter((content) => {
        return !course.contents.some((c) => c.contentID == content.contentID);
      });
      console.log("After Deleted Content Filter");

      //check if new content is empty
      if (newContent.length != 0) {
        console.log("newContent: ", newContent);
      }
      //check if deleted content is empty
      if (deletedContent.length != 0) {
        console.log("deletedContent: ", deletedContent);
      }

      console.log("Course Content: ", course.contents);

      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      //send course object to backend
      this.$http
        .put(process.env.VUE_APP_BASEURL + "/page", course, config)
        .then((response) => {
          console.log(response);
          //emit get course method from store
          if (response.status == 200) {
            this.$store.dispatch("fetchCourses");
            this.$router.push("/courses/" + course.pageID);
          }
        });
    },
  },

  computed: {
    ...mapGetters({ getCourse: "getCourseById" }),
  },
  created() {
    this.$store.dispatch("fetchCourses");
    this.course = this.getCourse(this.$route.params.id);
    this.controlCourse = this.getCourse(this.$route.params.id);
    console.log(this.course);
    console.log(this.controlCourse);
  },
};
</script>
