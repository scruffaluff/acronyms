<template>
  <nav class="navbar p-2 px-6" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <div class="navbar-item title mb-0 is-4 has-text-primary">Acronyms</div>
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
        <div class="navbar-item">
          <span
            :aria-checked="isDark"
            :class="isDark ? 'is-dark' : 'is-light'"
            class="has-tooltip-bottom"
            data-tooltip="Toggle Color Scheme"
            role="switch"
            tabindex="-1"
            @click="toggleDark()"
          >
            <i :class="isDark ? 'fa-moon' : 'fa-sun'" class="fas mr-2"></i>
          </span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useDark, useToggle } from "@vueuse/core";
import { ref } from "vue";

const navBarBurger = ref(false);

const isDark = useDark();
const toggleDark = useToggle(isDark);
</script>

<style>
.title {
  margin-bottom: 0;
}
</style>
