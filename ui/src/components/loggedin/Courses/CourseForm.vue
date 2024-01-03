<template>
  <form @submit.prevent="$emit('on-submit', course)">
    <div class="row">
      <div class="col-xl-9">
        <div class="form-group">
          <label for="name">Name</label>
          <input
            type="text"
            class="form-control"
            id="name"
            v-model="v$.course.name.$model"
            placeholder="Wie soll der Kurs heißen?"
          />
          <div
            class="input-errors"
            v-for="(error, index) of v$.course.name.$errors"
            :key="index"
          >
            <div class="error-msg">{{ error.$message }}</div>
          </div>
        </div>
        <div class="form-group">
          <label for="description">Beschreibung</label>
          <input
            type="text"
            class="form-control"
            id="description"
            v-model="v$.course.description.$model"
            placeholder="Das ist der Platz für die Beschreibung."
          />
          <div
            class="input-errors"
            v-for="(error, index) of v$.course.description.$errors"
            :key="index"
          >
            <div class="error-msg">{{ error.$message }}</div>
          </div>
        </div>

        <div class="form-group">
          <label for="image">Bild-Url</label>
          <input
            type="text"
            class="form-control"
            id="image"
            v-model="v$.course.imgLink.$model"
            placeholder="Hier können Sie die Bild-Url einfügen"
          />
          <div
            class="input-errors"
            v-for="(error, index) of v$.course.imgLink.$errors"
            :key="index"
          >
            <div class="error-msg">{{ error.$message }}</div>
          </div>
        </div>
      </div>
      <div class="col-xl-3">
        <div v-if="!v$.course.imgLink.$invalid">
          <p>Vorschau:</p>
          <img :src="course.imgLink" class="img-fluid mini-preview" />
        </div>
      </div>
    </div>

    <div class="p-3 mt-4">
      <!-- <div class="d-inline-block"> -->
      <h2 class="d-inline">Kursinhalt hinzufügen</h2>
      <!-- </div>
      <div class="d-inline-block"> -->
      <button
        type="button"
        class="btn btn-primary d-inline mx-4"
        @click="addContent"
      >
        <i class="fa fa-plus" aria-hidden="true"></i>
      </button>

      <!-- </div> -->
      <div class="row">
        <ContentForm
          v-for="(content, index) in course.contents"
          v-bind:key="index"
          v-bind:excontent="content"
          @delete="deleteContent(index)"
          v-model="course.contents[index]"
        ></ContentForm>
      </div>
    </div>
    <!-- save button -->
    <div class="d-flex justify-content-end">
      <button type="submit" class="btn btn-primary">Speichern</button>
    </div>
  </form>
</template>
<script>
import useVuelidate from "@vuelidate/core";
import { required, url } from "@vuelidate/validators";
import ContentForm from "./Content/ContentForm.vue";

export function validName(name) {
  let validNamePattern = new RegExp("^[a-zA-Z]+(?:[-'\\s][a-zA-Z]+)*$");
  if (validNamePattern.test(name)) {
    return true;
  }
  return false;
}

export default {
  setup() {
    return { v$: useVuelidate() };
  },
  props: {
    existingcourse: {
      type: Object,
    },
  },
  data() {
    return {
      course: this.existingcourse || {
        name: "",
        description: "",
        imgLink: "",
        contents: [],
      },
    };
  },
  validations() {
    return {
      course: {
        name: {
          required,
          validName,
        },
        description: {
          required,
        },
        imgLink: {
          required,
          url,
        },
      },
    };
  },
  methods: {
    addContent() {
      this.course.contents.push({
        name: "",
        type: "",
        content: "",
      });
    },
    deleteContent(index) {
      this.course.contents.splice(index, 1);
    },
  },
  components: { ContentForm },
};
</script>

<style>
.mini-preview {
  max-height: 150px;
  max-width: 150px;
}
</style>
