<template>
  <nav class="navbar p-4 px-6" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <div class="navbar-item title mb-0 is-4 has-text-primary">Acronyms</div>
      <a
        aria-label="menu"
        aria-expanded="false"
        class="navbar-burger"
        data-target="login"
        role="button"
        :class="{ 'is-active': navBarBurger }"
        @click="navBarBurger = !navBarBurger"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div id="login" class="navbar-menu" :class="{ 'is-active': navBarBurger }">
      <div class="navbar-end">
        <div class="navbar-item">
          <button class="button is-primary">
            <strong>Sign up</strong>
          </button>
        </div>
        <div class="navbar-item">
          <button class="button is-light">Log in</button>
        </div>
      </div>
    </div>
  </nav>

  <main class="main section">
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
    class="modal"
    :class="{ 'is-active': acronyms.error.active }"
  >
    <div class="modal-background"></div>
    <div class="modal-content">
      <article class="message is-danger">
        <div class="message-header">
          <p>Error</p>
          <button
            aria-label="delete"
            class="delete"
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
import { ref } from "vue";
import { useAcronymStore } from "./stores/acronym";
import AcronymSearch from "./components/AcronymSearch.vue";

const acronyms = useAcronymStore();
const navBarBurger = ref(false);
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
