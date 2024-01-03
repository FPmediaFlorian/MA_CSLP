<template>
  <div class="row">
    <div class="col-12">
      <h1>Kurszugriffe bearbeiten</h1>
      <div class="row">
        <CourseCard :course="course"></CourseCard>
        <div class="col-xl-6">
          <div class="card text-start">
            <h2 class="mb-4 text-center">Zugriffe für Gruppen erteilen:</h2>
            <h3 class="mb-4">Schreibzugriff:</h3>
            <div class="row mb-2">
              <div class="col-xl-8">
                <p>Allen <b>Lehrern</b> Schreibzugiff gewähren:</p>
              </div>
              <div class="col-xl-4">
                <button
                  type="button"
                  class="btn btn-warning"
                  @click="setAllTeachersToEditor()"
                >
                  Schreibzugriff
                </button>
              </div>
            </div>

            <h3 class="mb-4">Lesezugriff:</h3>
            <div class="row mb-2">
              <div class="col-xl-8">
                <p>Allen <b>Lehrern</b> Lesezugriff gewähren:</p>
              </div>
              <div class="col-xl-4 item">
                <button
                  type="button"
                  class="btn btn-warning"
                  @click="setAllTeachersToReader()"
                >
                  Lesezugriff
                </button>
              </div>
            </div>
            <div class="row mb-4">
              <div class="row">
                <div class="col-xl-8">
                  <p>Allen <b>Schülern/Usern</b> Lesezugriff gewähren:</p>
                </div>
                <div class="col-xl-4">
                  <button
                    type="button"
                    class="btn btn-warning"
                    @click="setAllStudentsToReader()"
                  >
                    Lesezugriff
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-xl-8">
      <div class="shadow rounded m-4 p-3">
        <h2>Schreibzugriff bearbeiten</h2>

        <div class="list-group">
          <label
            class="list-group-item"
            v-for="access in accesses"
            :key="access.userID"
          >
            <div class="row">
              <div class="col-md-4">
                <p>{{ access.name }}:</p>
              </div>
              <div class="col-md-2">
                <!-- role badge -->
                <span class="badge rounded-pill bg-secondary">{{
                  access.role
                }}</span>
              </div>
              <div class="col-md-6 text-center">
                <!-- checkbox -->
                <div
                  class="btn-group"
                  role="group"
                  aria-label="Basic radio toggle button group"
                >
                  <input
                    type="radio"
                    class="btn-check"
                    :name="access.userID"
                    :id="access.userID + '1'"
                    autocomplete="off"
                    value="2"
                    v-model="access.accessLvl"
                    checked
                  />
                  <label
                    class="btn btn-outline-primary"
                    :for="access.userID + '1'"
                    >Schreiben</label
                  >

                  <input
                    type="radio"
                    class="btn-check"
                    :name="access.userID"
                    :id="access.userID + '2'"
                    value="1"
                    v-model="access.accessLvl"
                    autocomplete="off"
                  />
                  <label
                    class="btn btn-outline-primary"
                    :for="access.userID + '2'"
                    >Lesen</label
                  >

                  <input
                    type="radio"
                    class="btn-check"
                    :name="access.userID"
                    :id="access.userID + '3'"
                    autocomplete="off"
                    value="0"
                    v-model="access.accessLvl"
                  />
                  <label
                    class="btn btn-outline-primary"
                    :for="access.userID + '3'"
                    >Keine</label
                  >
                </div>
              </div>
            </div>
          </label>
        </div>
        <!-- Save button -->
        <div class="row">
          <div class="col-12">
            <button
              type="button"
              class="btn btn-success my-3"
              @click="saveAccesses()"
            >
              Speichern
            </button>
          </div>
        </div>
        <div class="row justify-content-center">
          <div class="alert alert-danger" v-if="error">
            {{ errorMessage }}
          </div>
        </div>
        <div class="row justify-content-center">
          <div class="alert alert-success" v-if="success">
            {{ successMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapGetters } from "vuex";
import CourseCard from "../CourseCard.vue";

export default {
  name: "AccessEdit",
  data() {
    return {
      course: {},
      accesses: [],
      accessesControl: [],
      error: false,
      errorMessage:
        "Die Zugriffe konnten nicht gespeichert werden, bitte später erneut versuchen.",
      success: false,
      successMessage: "Die Zugriffe wurden erfolgreich gespeichert.",
    };
  },
  computed: {
    ...mapGetters({ getCourse: "getCourseById" }),
  },
  methods: {
    getAccesses() {
      //create header
      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      this.$http
        .get(
          process.env.VUE_APP_BASEURL +
            "/access/allusers/" +
            this.$route.params.id,
          config
        )
        .then((response) => {
          if (response.status === 200) {
            this.accesses = response.data;
            // this.accessesControl = response.data;
            this.accessesControl = JSON.parse(JSON.stringify(response.data));
            console.log(this.accesses);
            console.log(this.accessesControl);
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },
    saveAccesses() {
      this.error = false;
      this.success = false;
      //change all accessLvl to int
      this.accesses.forEach((access) => {
        access.accessLvl = parseInt(access.accessLvl);
      });

      //create header
      const config = {
        headers: {
          authToken: localStorage.getItem("token"),
        },
      };
      //filter out unchanged accesses
      const changedAccesses = this.accesses.filter((access) => {
        console.log(access);
        console.log(this.accessesControl);
        return (
          access.accessLvl !==
          this.accessesControl.find(
            (accessControl) => accessControl.userID === access.userID
          ).accessLvl
        );
      });

      console.log("changed accesses: " + changedAccesses);

      this.$http
        .put(
          process.env.VUE_APP_BASEURL + "/access/" + this.$route.params.id,
          changedAccesses,
          config
        )
        .then((response) => {
          if (response.status === 200) {
            console.log(response.data);
            this.success = true;
            //this.$router.push("/courses/" + this.$route.params.id);
          } else {
            this.error = true;
          }
        })
        .catch((error) => {
          console.log(error);
          this.error = true;
          this.errorMessage += " " + error;
        });
    },
    setAllTeachersToEditor() {
      this.accesses.forEach((access) => {
        if (access.role === "Lehrer") {
          access.accessLvl = 2;
        }
      });
    },
    setAllTeachersToReader() {
      this.accesses.forEach((access) => {
        if (access.role === "Lehrer") {
          access.accessLvl = 1;
        }
      });
    },
    setAllStudentsToReader() {
      this.accesses.forEach((access) => {
        if (
          access.role === "User" ||
          access.role === "Schüler" ||
          access.role === "Schülerin" ||
          access.role === "Student"
        ) {
          access.accessLvl = 1;
        }
      });
    },
  },
  created() {
    this.$store.dispatch("fetchCourses");
    this.course = this.getCourse(this.$route.params.id);
    this.getAccesses();
    console.log(this.course);
    console.log(this.accesses);
  },

  components: { CourseCard },
};
</script>
