// import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";

// Vue.use(Vuex);
//get base url from .env.delelopment.local file
//const BASE_URL = process.env.VUE_APP_BASE_URL;
const BASE_URL = "http://cslearning:5050";
//get url where application is running

export const store = new Vuex.Store({
  state: {
    BASE_URL: BASE_URL,
    authToken: "",
    user: {},
    courses: [],
    loginState: false,
    accesses: [],
  },
  mutations: {
    //this.commit
    setAuthToken(state, payload) {
      state.authToken = payload;
    },
    setLoginState(state, payload) {
      state.loginState = payload;
    },
    setUser(state, payload) {
      state.user = payload;
    },
    setCourses(state, payload) {
      state.courses = payload;
    },
    setAccesses(state, payload) {
      state.accesses = payload;
    },
  },
  actions: {
    //fetch data from Backend
    //this.dispatch
    // setAuthToken({ commit }, payload) {
    //   commit("setAuthToken", payload);
    // },

    async UpdateLoginState(state) {
      //log token
      //console.log(localStorage.getItem("token"));
      //print Base URL
      state.commit("setAuthToken", localStorage.getItem("token"));
      console.log("update login state called");

      //   console.log("From UpdateLoginState / Token: " + state.getters.getToken);
      if (state.getters.getToken === null) {
        //set login state to false
        state.commit("setLoginState", false);
      } else {
        //check if token timed out
        //add headers
        const config = {
          headers: {
            authToken: state.getters.getToken,
          },
        };
        axios
          .get(BASE_URL + "/checkToken", config)
          .then((response) => {
            // console.log(response);
            //Set login state to true
            if (response.status === 200) {
              state.commit("setLoginState", true);
              state.dispatch("fetchUserData");
              state.dispatch("fetchCourses");
              state.dispatch("fetchAccessLvls");
            }
            //TODO: vielleicht bessere lösung finden, wenn repsone nicht 200 ist
          })
          .catch((error) => {
            console.log(error);
            //set login state to false
            state.commit("setLoginState", false);
            //remove token from state
            state.commit("setAuthToken", null);
            //state.setAuthToken = null;
          });
      }
    },
    async Logout(state) {
      state.commit("setAuthToken", null);
      state.commit("setLoginState", false);
      localStorage.removeItem("token");
    },
    // get userdata from backend
    async fetchUserData(state) {
      //add headers
      const config = {
        headers: {
          authToken: state.getters.getToken,
        },
      };
      axios
        .get(BASE_URL + "/user", config)
        .then((response) => {
          //   console.log(response);
          state.commit("setUser", response.data);
        })
        .catch((error) => {
          console.log(error);
        });
    },
    // get courses from backend
    async fetchCourses(state) {
      try {
        //Auth Header
        const config = {
          headers: {
            authToken: state.getters.getToken,
          },
        };
        axios.get(BASE_URL + "/pages", config).then((response) => {
          //set courses
          state.commit("setCourses", response.data);
          //fetch Access Levels
          state.dispatch("fetchAccessLvls");
          //   console.log(response.data);
        });
      } catch (error) {
        // console.log(error);
      }
    },
    async fetchAccessLvls(state) {
      try {
        //Auth Header
        const config = {
          headers: {
            authToken: state.getters.getToken,
          },
        };
        axios.get(BASE_URL + "/access", config).then((response) => {
          //set accesses
          state.commit("setAccesses", response.data);
          //   console.log(response.data);
        });
      } catch (error) {
        // console.log(error);
      }
    },
  },
  getters: {
    getCurrentUser: (state) => {
      //   console.log("From Getter: " + state.user);
      return state.user;
    },
    getCurrentUserIsTeacher: (state) => {
      //   console.log("From Getter: " + state.user);
      return state.user.isTeacher;
    },
    getCurrentUserIsAdmin: (state) => {
      //   console.log("From Getter: " + state.user);
      return state.user.isAdmin;
    },
    getAllCourses: (state) => {
      return state.courses;
    },
    getCourseCount: (state) => {
      return state.courses.length;
    },
    getLoginState: (state) => {
      return state.loginState;
    },
    getToken: (state) => {
      return state.authToken;
    },
    getAccessLvlForCourse: (state) => (courseId) => {
      //get course by id
      //console.log("From AccessLVL Getter: CourseID: " + courseId);
      //   console.log(
      //     "From AccessLVL Getter: Accesses: " + state.accesses[0].pageID
      //   );

      //get access from state with corresponding course id
      try {
        const access = state.accesses.find(
          (access) => access.pageID == courseId
        );

        return access.accessLvl;
      } catch (error) {
        return -1;
      }

      //console.log("From AccessLVL Getter: AccessLvl: " + access);
      //return access level
    },
    //get course by id
    getCourseById: (state) => (courseId) => {
      //   console.log("From Getter: " + courseId);

      return state.courses.find((course) => course.pageID == courseId);
    },
    getLastCoursefromCourseList: (state) => {
      return state.courses[state.courses.length - 1];
    },
  },
});
