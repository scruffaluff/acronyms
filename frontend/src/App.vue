<template>
  <NavBar />
  <hr class="divider m-0" />

  <main class="container main is-max-desktop">
    <AcronymSearch ref="acronymSearch" />
  </main>

  <footer class="footer bottom-fixed py-4">
    <div class="content has-text-centered">
      <h4 class="mb-0">
        <strong>Acronyms</strong> by
        <a class="has-text-primary" href="https://github.com/scruffaluff"
          >Scruffaluff</a
        >.
      </h4>
    </div>
  </footer>

  <div
    id="error-modal"
    v-motion-fade-visible
    :class="{ 'is-active': acronyms.error.active }"
    class="modal"
  >
    <div class="modal-background"></div>
    <div class="modal-content">
      <article class="message is-danger">
        <div class="message-header">
          <p>Error</p>
          <button
            class="delete"
            aria-label="delete"
            @click="acronyms.error.active = false"
          ></button>
        </div>
        <div class="message-body">
          {{ acronyms.error.message }}
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import AcronymSearch from "./components/AcronymSearch.vue";
import NavBar from "./components/NavBar.vue";
import { useAcronymStore } from "./stores/acronym";
import { ref } from "vue";

function keyDownHandler(event: KeyboardEvent): void {
  if (event.ctrlKey) {
    if (event.key === "a") {
      event.preventDefault();
      acronymSearch.value?.beginAdd();
    }
  } else if (event.key === "Escape") {
    if (acronyms.error.active) {
      acronyms.error.message = "";
      acronyms.error.active = false;
    }
  }
}

const acronymSearch = ref<InstanceType<typeof AcronymSearch> | null>(null);

const acronyms = useAcronymStore();
document.addEventListener("keydown", keyDownHandler);
</script>

<style>
/* Fixes footer to bottom of page with footer width relative to parent div. Do
not use 'position: fixed;' on footer instead. It will make the footer's width
relative to the body element. */
.main {
  flex: auto;
}
</style>
