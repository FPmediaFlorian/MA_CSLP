import { createApp } from "vue";
import App from "./App.vue";
import VueAxios from "vue-axios";
import axios from "axios";
//import * as router from "vue-router";
import router from "./router";
import { store } from "./store";

import CKEditor from "@ckeditor/ckeditor5-vue";

//import Bootstrap
import "bootstrap/dist/css/bootstrap.css";
import "./assets/css/main.css";
import "bootstrap/dist/js/bootstrap.js";

import "./assets/fontawesome/css/fontawesome.css";
import "./assets/fontawesome/css/brands.css";
import "./assets/fontawesome/css/solid.css";

createApp(App)
  .use(VueAxios, axios)
  .use(router)
  .use(store)
  .use(CKEditor)
  .mount("#app");
