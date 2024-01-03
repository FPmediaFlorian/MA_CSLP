import { store } from "@/store";
import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: () =>
      import(
        /* webpackChunkName: "Dashboard" */ "@/components/loggedin/MainDashboard.vue"
      ),
  },
  {
    path: "/Courses",
    name: "CourseOverview",
    component: () =>
      import(
        /* webpackChunkName: "CourseOverview" */ "@/components/loggedin/Courses/CourseOverview.vue"
      ),
  },
  {
    path: "/Courses/new",
    name: "CourseNew",
    component: () =>
      import(
        /* webpackChunkName: "CourseNew" */ "@/components/loggedin/Courses/CourseNew.vue"
      ),
  },
  {
    path: "/Courses/edit/:id",
    name: "CourseUpdate",
    component: () =>
      import(
        /* webpackChunkName: "CourseUpdate" */ "@/components/loggedin/Courses/CourseEdit.vue"
      ),
  },
  {
    path: "/Courses/access/:id",
    name: "AccessUpdate",
    component: () =>
      import(
        /* webpackChunkName: "AccessUpdate" */ "@/components/loggedin/Courses/Access/AccessEdit.vue"
      ),
  },

  {
    path: "/Courses/:id",
    name: "CourseDetail",
    component: () =>
      import(
        /* webpackChunkName: "CourseDetail" */ "@/components/loggedin/Courses/CourseDetail.vue"
      ),
  },
  {
    path: "/localgames/pwgame",
    name: "AccessPWGame",
    component: () =>
      import(
        /* webpackChunkName: "AccessUpdate" */ "@/components/loggedin/Courses/Games/PwChecker.vue"
      ),
  },
  {
    path: "/User",
    name: "UserProfile",
    component: () =>
      import(
        /* webpackChunkName: "UserProfile" */ "@/components/loggedin/User/UserProfile.vue"
      ),
  },
  {
    path: "/:catchAll(.*)",
    component: () =>
      import(/* webpackChunkName: "NotFound" */ "@/components/NotFound.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  console.log("RouteChange");
  // console.log(to);
  // console.log(from);
  //call vuex action to check if user is logged in
  store.dispatch("UpdateLoginState");
  //if not logged in, redirect to login page
  if (!store.getters.getLoginState) {
    console.log("Not logged in");
    //router.push("/").catch(() => {});
  }

  next();
  // //check if user is logged in
  // if (to.name !== "Login" && !localStorage.getItem("authToken")) {
  //   next({ name: "Login" });
  // } else {
  //   next();
  // }
});

export default router;
