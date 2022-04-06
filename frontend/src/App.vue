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
    <div class="navbar-menu" id="login" :class="{ 'is-active': navBarBurger }">
      <div class="navbar-end">
        <div class="navbar-item">
          <a class="button is-primary">
            <strong>Sign up</strong>
          </a>
        </div>
        <div class="navbar-item">
          <a class="button is-light">Log in</a>
        </div>
      </div>
    </div>
  </nav>

  <main class="main section">
    <div class="mx-6 my-6 container">
      <div class="field">
        <div class="control has-icons-left has-icons-right">
          <input
            class="input"
            placeholder="Search"
            type="text"
            v-model="search"
          />
          <span class="icon is-left is-small">
            <i class="fas fa-search"></i>
          </span>
        </div>
      </div>
    </div>

    <table class="container table is-fullwidth is-hoverable has-text-left">
      <thead>
        <tr>
          <th v-for="column in columns">
            {{ column.name }}
            <span class="icon is-small" @click="switchSort(column.name)">
              <i class="fas" :class="column.icon"></i>
            </span>
          </th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="acronym in acronymsFiltered">
          <td>{{ acronym.abbreviation }}</td>
          <td>{{ acronym.expansion }}</td>
          <td>
            <span class="icon mx-1 is-right" @click="put(acronym.id)">
              <i class="fas fa-pencil"></i>
            </span>
            <span class="icon mx-1 is-right" @click="remove(acronym.id)">
              <i class="fas fa-trash-can"></i>
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </main>

  <footer class="footer py-6">
    <div class="container">
      <h4>
        <strong>Acronyms</strong> by
        <a href="https://github.com/scruffaluff">Scruffaluff</a>.
      </h4>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

interface Acronym {
  id: number;
  abbreviation: string;
  expansion: string;
}

async function fetchData(): Promise<void> {
  const response = await fetch("/api");
  acronyms.data = await response.json();
}

async function put(id: number): Promise<void> {
  await fetch(`/api/${id}`, {
    body: JSON.stringify({ abbreviation: "BB", expansion: "Boop Bopping" }),
    headers: { "Content-Type": "application/json" },
    method: "PUT",
  });
  await fetchData();
}

async function remove(id: number): Promise<void> {
  await fetch(`/api/${id}`, { method: "DELETE" });
  await fetchData();
}

function sort(column: { name: string; ascending: boolean }): void {
  const name = column.name as keyof Acronym;

  if (column.ascending) {
    acronyms.data.sort((left, right) => (left[name] > right[name] ? 1 : -1));
  } else {
    acronyms.data.sort((left, right) => (left[name] < right[name] ? 1 : -1));
  }
}

function switchSort(name: string): void {
  const column = columns.filter((order) => order.name == name)[0];

  if (column.ascending) {
    column.icon = "fa-arrow-down";
    column.ascending = false;
  } else {
    column.icon = "fa-arrow-up";
    column.ascending = true;
  }

  sort(column);
}

let acronyms: { data: Array<Acronym> } = reactive({ data: [] });
let columns = reactive([
  { name: "abbreviation", ascending: true, icon: "fa-arrow-up" },
  { name: "expansion", ascending: true, icon: "fa-arrow-up" },
]);
const navBarBurger = ref(false);
const search = ref("");

const acronymsFiltered = computed(() => {
  const text = search.value.toLowerCase();

  if (!text) {
    return acronyms.data;
  } else if (text.includes(" ")) {
    return acronyms.data.filter((acronym) =>
      acronym.expansion.toLowerCase().includes(text)
    );
  } else {
    return acronyms.data.filter((acronym) =>
      acronym.abbreviation.toLowerCase().includes(text)
    );
  }
});

onMounted(fetchData);
</script>

<style>
.main {
  flex: 1;
}
.title {
  margin-bottom: 0;
}
th {
  text-transform: capitalize;
}
</style>
