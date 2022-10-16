<template>
  <nav class="navbar p-4 px-6" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <div class="navbar-item title mb-0 is-4 has-text-primary">Acronyms</div>
      <a
        :class="{ 'is-active': navBarBurger }"
        class="navbar-burger"
        data-target="login"
        role="button"
        aria-label="menu"
        aria-expanded="false"
        @click="navBarBurger = !navBarBurger"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div id="login" :class="{ 'is-active': navBarBurger }" class="navbar-menu">
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
</template>

<script setup lang="ts">
import { ref } from "vue";

const navBarBurger = ref(false);
</script>
