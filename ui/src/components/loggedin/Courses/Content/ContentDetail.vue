<template>
  <div class="col-12">
    <div
      :class="'item' + getIndex()"
      class="card-content"
      v-if="content.type !== '0'"
    >
      <h3 class="card-title">{{ content.name }}</h3>
      <div class="content">
        <div v-if="content.type === '1'">
          <div v-html="getHTML()" class="text-start"></div>
        </div>
        <img
          v-else-if="content.type === '2'"
          :src="content.content"
          alt="Image for the course"
          class="img-fluid ${3|rounded-top,rounded-right,rounded-bottom,rounded-left,rounded-circle,|}"
        />

        <div v-else-if="content.type === '3'" class="video-container">
          <iframe
            width="560"
            height="315"
            :src="getVideoEmbeding()"
            frameborder="0"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
        <div v-else-if="content.type === '4'" class="game-container">
          <iframe
            width="800"
            height="450"
            :src="getGameEmbeding()"
            :style="style"
            frameborder="0"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      style: "",
    };
  },
  methods: {
    getIndex() {
      return (this.index + 1) % 5;
    },
    getHTML() {
      let parser = new DOMParser();
      let doc = parser.parseFromString(this.content.content, "application/xml");
      let errorNode = doc.querySelector("parsererror");

      //split content by space
      let content = this.content.content.split(" ");
      if (!errorNode) {
        //delete first occurrence of <p> and last occurrence of </p>

        //get first element of content
        let firstElement = content[0];
        //get last element of content
        let lastElement = content[content.length - 1];
        //delelte <p> from first element
        firstElement = firstElement.replace("<p>", "");
        //delete </p> from last element
        lastElement = lastElement.replace("</p>", "");
        //replace first element with new first element
        content[0] = firstElement;
        //replace last element with new last element
        content[content.length - 1] = lastElement;
      }
      //concatenate content wit <p></p> tag
      let newContent = content.map((item) => {
        return '<span class="underline">' + item + "</span>";
      });
      //join content
      let finalContent = newContent.join(" ");

      // if (!errorNode) {
      //   //delete first and last tag
      //   let content = doc.body.innerHTML;
      //   content = content.substring(3, content.length - 4);

      // }
      return "<p>" + finalContent + "</p>";
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
    getGameEmbeding() {
      //get path to game

      //ui / src / components / loggedin / Courses / Content / ContentDetail.vue;
      //return this.content.content;
      if (this.content.content.includes("itch")) {
        return this.content.content;
      } else if (
        this.content.content.includes("Lumi") ||
        this.content.content.includes("lumi")
      ) {
        if (this.content.content.includes("embed")) {
          return this.content.content;
        }
        //change lumi to lumi-embed
        let content = this.content.content.replace(
          "education/run/",
          "education/api/v1/run/"
        );
        //add /embed to the end of the path
        content = content + "/embed";
        return content;
      } else if (this.content.content.includes("/localgames/")) {
        this.style = " height: 440px;  width: 1000px; resize:none;";
        return this.content.content;
      }

      return "";
    },
  },
  props: ["content", "index"],
};
</script>
<style>
.card-content {
  background-color: var(--primary);
  padding: 2em;
  margin: 1em;
  transition: 0.3s;
  text-align: center;
  border-radius: 10px;
  border: none;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
  height: auto;
}
.card:hover {
  transform: none;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  padding-bottom: 1em;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
}
.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.underline:hover {
  text-decoration: underline;
  font-size: 1.3rem;
}
.game-container {
  background-color: white;
  padding: 20px 20px 0px 20px;
}
</style>
