<template>
  <div class="col-lg-12 shadow rounded my-4">
    <div class="m-2 py-4">
      <div class="row">
        <div class="col">
          <div class="form-outline">
            <label class="form-label" for="title"
              >Titel des Inhaltsblocks</label
            >
            <input
              @input="$emit('update:modelValue', content)"
              v-model="v$.content.name.$model"
              type="text"
              id="title"
              class="form-control"
              placeholder="Wie soll der neuine Inhalt heißen?"
            />
          </div>
        </div>
        <div class="col">
          <div class="form-outline">
            <label class="form-label" for="form3Example1"
              >Art des Inhalts
              <a href="Screendesign.pdf" target="_blank"
                ><i style="padding-left: 10px" class="fa fa-question-circle"></i
              ></a>
            </label>
            <select
              v-model="v$.content.type.$model"
              @change="$emit('update:modelValue', content)"
              class="form-select"
              aria-label="Default select example"
            >
              <option value="-1">Inhaltsblock auswählen</option>
              <option value="1">Text (HTML)</option>
              <option value="2">Foto Link</option>
              <option value="3">Video</option>
              <option value="4">Spiel</option>
              <option value="0">Ausblenden</option>
            </select>
          </div>
        </div>
      </div>
      <div class="row my-4">
        <div v-if="v$.content.type.$model == 0" class="col-xl-12">
          <!-- Inhalt ist ausgeblendet -->
          <p>Ausgeblendet</p>
          <p class="fst-italic">{{ content.content }}</p>
        </div>
        <div v-else-if="v$.content.type.$model == 1" class="col-xl-12">
          <!-- Texteditor -->
          <ckeditor
            :editor="editor"
            v-model="v$.content.content.$model"
            :config="editorConfig"
          ></ckeditor>
        </div>
        <div v-else-if="v$.content.type.$model == 2" class="col-xl-12">
          <!-- Foto inkl. Vorschau -->
          <div class="form-group">
            <div class="form-outline">
              <label class="form-label" for="title">Link zum Foto</label>
              <input
                v-model="v$.content.content.$model"
                type="text"
                id="title"
                class="form-control"
                placeholder="Das ist der Platz für die Bild-URL."
              />
            </div>
            <div
              class="input-errors"
              v-for="(error, index) of v$.content.content.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
            <div v-if="!v$.content.content.$invalid">
              <p>Vorschau:</p>
              <img
                :src="v$.content.content.$model"
                class="img-thumbnail"
                @error="getErrorImg"
              />
            </div>
          </div>
        </div>
        <div v-else-if="v$.content.type.$model == 3" class="col-xl-12">
          <!-- Video inkl. Vorschau -->
          <div class="form-group">
            <div class="form-outline">
              <label class="form-label" for="title">Link zum Video</label>
              <input
                v-model="v$.content.content.$model"
                type="text"
                id="title"
                class="form-control"
                placeholder="Hier kommt der Link zum Youtube Video rein."
              />
            </div>
            <div
              class="input-errors"
              v-for="(error, index) of v$.content.content.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>
        </div>
        <div v-else-if="v$.content.type.$model == 4" class="col-xl-12">
          <!-- Spiel inkl.Vorschau?? -->
          <div class="form-group">
            <div class="form-outline">
              <label class="form-label" for="title">Link zum Spiel</label>
              <input
                v-model="v$.content.content.$model"
                type="text"
                id="title"
                class="form-control"
                placeholder="Hier kommt der Link zum Spiel rein."
              />
            </div>
            <div
              class="input-errors"
              v-for="(error, index) of v$.content.content.$errors"
              :key="index"
            >
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>
        </div>
        <div v-else class="col-xl-12">
          <!-- Spiel inkl.Vorschau?? -->
          <p>{{ content.content }}Inhalt ist nicht bekannt.</p>
        </div>
      </div>
      <div class="d-flex justify-content-end">
        <button type="button" @click="$emit('delete')" class="btn btn-danger">
          Löschen
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import useVuelidate from "@vuelidate/core";
import { required, integer, url } from "@vuelidate/validators";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";

export function validContent() {}

export default {
  setup() {
    return { v$: useVuelidate() };
  },
  props: {
    excontent: { type: Object },
  },
  data() {
    return {
      content: this.excontent || {
        name: "",
        type: -1,
        content: "",
      },
      editor: ClassicEditor,
      editorConfig: {
        toolbar: [
          "heading",
          "|",
          "bold",
          "italic",
          "link",
          "bulletedList",
          "numberedList",
          "blockQuote",
          "insertTable",
          "undo",
          "redo",
        ],
      },
    };
  },
  beforeUpdate() {
    this.content = this.excontent || {
      name: "",
      type: -1,
      content: "",
    };
  },

  methods: {
    getErrorImg(event) {
      event.target.src =
        "https://via.placeholder.com/468x100/fa9131/ffffff?text=Bild+kann+leider+nicht+gefunden+werden";
    },
    getVideoEmbeding() {
      if (this.content.content.includes("youtube")) {
        return this.content.content.replace("watch?v=", "embed/");
      } else if (this.content.content.includes("vimeo")) {
        return this.content.content.replace(
          "vimeo.com/",
          "player.vimeo.com/video/"
        );
      }
    },
  },
  validations() {
    return {
      content: {
        name: {
          required,
        },
        type: {
          required,
          integer,
        },
        content: {
          required,
          condUrlVald:
            this.content.type == 2 ||
            this.content.type == 3 ||
            this.content.type == 4
              ? url
              : required,
          //TODO: Check if URL is a valid video link

          //   url: () => {
          //     if (
          //       this.v$.content.type.$model == 2 ||
          //       this.v$.content.type.$model == 3 ||
          //       this.v$.content.type.$model == 4
          //     ) {
          //       console.log("True");
          //       return true;
          //     }
          //     console.log("False");
          //     return false;
          //   },
        },
      },
    };
  },
};
</script>
