<template>
  <div class="row">
    <div v-if="!user.isAdmin" class="col-xl-6 justify-content-center mb-3">
      <h3>Hi {{ user.username }}</h3>
      <h5>
        Wir sind Ben und Malik, hier kannst du mit uns an deinem Profil
        arbeiten.
      </h5>
      <img
        src="./../../../assets/img/characters/workers_illustration.svg"
        class="img-fluid ${3|rounded-top,rounded-right,rounded-bottom,rounded-left,rounded-circle,|}"
        alt=""
      />
    </div>
    <div class="col-xl-6 justify-content-center">
      <div class="card">
        <h1>Profil bearbeiten</h1>
        <form @submit.prevent="onSubmit" class="mt-4">
          <!-- First and user Name Row -->

          <div class="form-group mb-4">
            <label for="">Name</label
            ><input
              class="form-control"
              placeholder="Name"
              type="text"
              v-model="v$.user.name.$model"
            />
            <div class="pre-icon os-icon os-icon-user-male-circle"></div>
            <!-- Error Message -->
            <div
              class="input-errors"
              v-for="(error, index) of v$.user.name.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>

          <div class="form-group mb-4">
            <label for=""> Username:</label
            ><input
              class="form-control"
              placeholder="Username"
              type="text"
              v-model="v$.user.username.$model"
            />
            <div class="pre-icon os-icon os-icon-user-male-circle"></div>
            <!-- Error Message -->
            <div
              class="input-errors"
              v-for="(error, index) of v$.user.username.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>

          <!-- Email Row -->
          <div class="form-group mb-4">
            <label for="">E-Mail Adresse</label>
            <input
              class="form-control"
              placeholder="E-Mail Adresse"
              type="email"
              v-model="v$.user.mail.$model"
            />
            <div class="pre-icon os-icon os-icon-email-2-at2"></div>
            <!-- Error Message -->
            <div
              class="input-errors"
              v-for="(error, index) of v$.user.mail.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="row justify-content-center d-flex mb-4">
            <div class="col-md-6">
              <!-- bootstrap buttom -->
              <a
                @click="updateUser"
                class="btn btn-primary"
                :disabled="checkUserInfoValid"
              >
                Änderungen speichern
              </a>
            </div>
            <div class="col-md-6">
              <!-- bootstrap buttom -->
              <a
                @click="$forceUpdate"
                class="btn btn-outline-light"
                role="button"
                >Verwerfen</a
              >
            </div>
          </div>
          <!-- Error Messages -->
          <div class="row justify-content-center">
            <div class="alert alert-danger" v-if="updateFail">
              {{ updateMessage }}
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="alert alert-success" v-if="updateSccess">
              {{ updateMessage }}
            </div>
          </div>
        </form>

        <h2>Passwort ändern</h2>
        <form @submit.prevent="onSubmit" class="mt-4">
          <!-- Password and Confirm Password Row -->

          <div class="form-group mb-4">
            <label for=""> Passwort</label
            ><input
              class="form-control"
              placeholder="Passwort"
              type="password"
              v-model="vPW$.user.password.$model"
            />
            <div class="pre-icon os-icon os-icon-fingerprint"></div>
            <!-- Error Message -->
            <div
              class="input-errors"
              v-for="(error, index) of vPW$.user.password.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>

          <div class="form-group mb-4">
            <label for="">Passwort bestätigen</label
            ><input
              class="form-control"
              placeholder="Passwort bestätigen"
              type="password"
              v-model="vPW$.user.confirmPassword.$model"
            />
            <!-- Error Message -->
            <div
              class="input-errors"
              v-for="(error, index) of vPW$.user.confirmPassword.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="row justify-content-center d-flex mb-4">
            <div class="col-md-6">
              <!-- bootstrap buttom -->
              <a
                @click="updatePassword"
                class="btn btn-primary"
                :disabled="
                  vPW$.user.password.$invalid ||
                  vPW$.user.confirmPassword.$invalid
                "
              >
                Änderungen speichern
              </a>
            </div>
            <div class="col-md-6">
              <!-- bootstrap buttom -->
              <a
                @click="$forceUpdate"
                class="btn btn-outline-light"
                role="button"
                >Verwerfen</a
              >
            </div>
          </div>
          <!-- Error Messages -->
          <div class="row justify-content-center">
            <div class="alert alert-danger" v-if="pwUpdateFail">
              {{ updateMessage }}
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="alert alert-success" v-if="pwUpdateSuccess">
              {{ updateMessage }}
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script>
import useVuelidate from "@vuelidate/core";
import { required, email, minLength, sameAs } from "@vuelidate/validators";
const BASE_URL = process.env.VUE_APP_BASEURL;

export function validName(name) {
  let validNamePattern = new RegExp("^[a-zA-Z]+(?:[-'\\s][a-zA-Z]+)*$");
  if (validNamePattern.test(name)) {
    return true;
  }
  return false;
}

export function validUsername(username) {
  let validUsernamePattern = new RegExp("^[a-zA-Z0-9_-]{3,16}$");
  if (validUsernamePattern.test(username)) {
    return true;
  }
  return false;
}

export default {
  setup() {
    return { v$: useVuelidate(), vPW$: useVuelidate() };
  },
  data() {
    return {
      user: {},
      error: false,
      updateFail: false,
      updateSccess: false,
      updateMessage: "",
      pwUpdateFail: false,
      pwUpdateSuccess: false,
    };
  },
  validations() {
    return {
      user: {
        name: {
          required,
          name_validation: {
            $validator: validName,
            $message:
              "Ungültiger Name. Ein Name darf nur Bindestriche (-) und Abstände ( ) enthalten.",
          },
        },
        username: {
          required,
          username_validation: {
            $validator: validUsername,
            $message:
              "Ungültiger Username. Ein Username darf nur Kleinbuchstaben, Zahlen und Unterstriche (_) enthalten.",
          },
        },
        mail: { required, email },
        password: { required, min: minLength(6) },
        confirmPassword: {
          required,
          sameAsPassword: sameAs(this.user.password),
        },
      },
    };
  },
  methods: {
    getUser() {
      try {
        const config = {
          headers: {
            authToken: localStorage.getItem("token"),
          },
        };
        this.$http.get(BASE_URL + "/user", config).then((response) => {
          this.user = response.data;
          console.log(response.data);
        });
        console.log(this.user);
        this.error = false;
        return this.user;
      } catch (error) {
        this.error = true;
        console.log(error);
      }
    },
    updateUser() {
      this.pwUpdateSuccess = false;
      this.pwUpdateFail = false;
      this.updateSccess = false;
      this.updateFail = false;
      try {
        //Auth Header
        const config = {
          headers: {
            authToken: localStorage.getItem("token"),
          },
        };
        //create request body for user
        const body = {
          userID: this.user.userID,
          name: this.user.name,
          username: this.user.username,
          mail: this.user.mail,
        };
        this.$http.put(BASE_URL + "/user", body, config).then((response) => {
          this.user = response.data;
          console.log(response.data);

          if (response.status == 200) {
            this.updateSccess = true;
            this.updateFail = false;
            this.updateMessage = "Änderungen erfolgreich gespeichert";
          } else {
            this.updateSccess = false;
            this.updateFail = true;
            this.updateMessage =
              "Änderungen konnten nicht gespeichert werden Error: " +
              response.status;
          }
          this.getUser();
        });
        console.log(this.user);
        return this.user;
      } catch (error) {
        this.updateSccess = false;
        this.updateFail = true;
        this.updateMessage =
          "Änderungen konnten nicht gespeichert werden. Error:" + error;

        console.log(error);
      }
    },
    updatePassword() {
      this.pwUpdateSuccess = false;
      this.pwUpdateFail = false;
      this.updateSccess = false;
      this.updateFail = false;
      try {
        //Auth Header
        const config = {
          headers: {
            authToken: localStorage.getItem("token"),
          },
        };
        //create request body for user
        const body = {
          userID: this.user.userID,
          password: this.user.password,
        };
        this.$http.put(BASE_URL + "/user", body, config).then((response) => {
          this.user = response.data;
          console.log(response.data);

          if (response.status == 200) {
            this.pwUpdateSuccess = true;
            this.pwUpdateFail = false;
            this.updateMessage = "Passwort erfolgreich geändert";
          } else {
            this.pwUpdateSuccess = false;
            this.pwUpdateFail = true;
            this.updateMessage =
              "Passwort konnte nicht gespeichert werden. Error: " +
              response.status;
          }
          this.getUser();
        });
        console.log(this.user);
        return this.user;
      } catch (error) {
        this.pwUpdateSccess = false;
        this.pwUpdateFail = true;
        this.updateMessage =
          "Änderungen konnten nicht gespeichert werden. Error:" + error;

        console.log(error);
      }
    },
    //check userinfovalidation
    checkUserInfoValid() {
      if (
        this.v$.user.name.$invalid ||
        this.v$.user.username.$invalid ||
        this.v$.user.mail.$invalid
      ) {
        return true;
      }
      return false;
    },
  },

  created() {
    this.getUser();
  },
  name: "UserProfile",
};
</script>

<style>
.card:hover {
  transform: none;
  transition: 0.3s;
}
</style>
