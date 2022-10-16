<template>
  <NavBar />

  <main class="main section>">
    <AcronymSearch />
  </main>

  <footer class="footer py-6">
    <div class="container">
      <h4>
        <strong>Acronyms</strong> by
        <a href="https://github.com/scruffaluff">Scruffaluff</a>.
      </h4>
    </div>
  </footer>

  <div
    id="error-modal"
    :class="{ 'is-active': acronyms.error.active }"
    class="modal"
    @keyup.esc="acronyms.error.active = false"
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

const acronyms = useAcronymStore();
</script>

<style>
.main {
  flex: 1;
}
.title {
  margin-bottom: 0;
}
table {
  table-layout: fixed;
}
th {
  text-transform: capitalize;
}
</style>
