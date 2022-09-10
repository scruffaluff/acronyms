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
    <div class="columns mx-6 my-6">
      <div class="column field is-four-fifths mb-0">
        <div class="control has-icons-left">
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
      <div class="container column">
        <a class="button is-primary" v-on:click="beginAdd()">
          <strong>Add</strong>
        </a>
      </div>
    </div>

    <table class="container table is-fullwidth is-hoverable has-text-left">
      <thead>
        <tr>
          <th v-for="column in columns" v-bind:key="column.name">
            {{ column.name }}
            <span class="icon is-small" @click="switchSort(column.name)">
              <i class="fas" :class="column.icon"></i>
            </span>
          </th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-show="insert.enable">
          <td>
            <input
              class="input"
              placeholder="Abbreviation"
              type="text"
              v-model="insert.abbreviation"
            />
          </td>
          <td>
            <input
              class="input"
              placeholder="Phrase"
              type="text"
              v-model="insert.phrase"
            />
          </td>
          <td>
            <a class="button is-primary" v-on:click="submitAdd()">
              <strong>Submit</strong>
            </a>
          </td>
        </tr>
        <tr v-for="acronym in acronymsFiltered" v-bind:key="acronym.id">
          <template v-if="acronym.edit">
            <td>
              <input
                class="input"
                placeholder="Abbreviation"
                type="text"
                v-model="acronym.abbreviation"
              />
            </td>
            <td>
              <input
                class="input"
                placeholder="Phrase"
                type="text"
                v-model="acronym.phrase"
              />
            </td>
            <td>
              <a class="button is-primary" v-on:click="submitEdit(acronym.id)">
                <strong>Submit</strong>
              </a>
            </td>
          </template>
          <template v-else>
            <td>{{ acronym.abbreviation }}</td>
            <td>{{ acronym.phrase }}</td>
            <td>
              <span class="icon mx-1 is-right" @click="beginEdit(acronym.id)">
                <i class="fas fa-pencil"></i>
              </span>
              <span class="icon mx-1 is-right" @click="remove(acronym.id)">
                <i class="fas fa-trash-can"></i>
              </span>
            </td>
          </template>
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
  edit: boolean;
  phrase: string;
}

function beginAdd(): void {
  insert.enable = true;

  if (search.value.includes(" ")) {
    insert.phrase = search.value;
  } else {
    insert.abbreviation = search.value;
  }
}

function beginEdit(id: number): void {
  const acronym = acronyms.data.filter((acronym) => acronym.id == id)[0];
  acronym.edit = true;
}

async function fetchData(): Promise<void> {
  const response = await fetch("/api");
  acronyms.data = (await response.json()).map((acronym: any) => ({
    ...acronym,
    edit: false,
  }));
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

async function submitAdd(): Promise<void> {
  await fetch(`/api`, {
    body: JSON.stringify({
      abbreviation: insert.abbreviation,
      phrase: insert.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  insert.abbreviation = "";
  insert.phrase = "";
  insert.enable = false;
  search.value = "";
  await fetchData();
}

async function submitEdit(id: number): Promise<void> {
  const acronym = acronyms.data.filter((acronym) => acronym.id == id)[0];

  await fetch(`/api/${id}`, {
    body: JSON.stringify({
      abbreviation: acronym.abbreviation,
      phrase: acronym.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "PUT",
  });

  acronym.edit = false;
  await fetchData();
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
  { name: "phrase", ascending: true, icon: "fa-arrow-up" },
]);
let insert = reactive({
  abbreviation: "",
  enable: false,
  phrase: "",
});
const navBarBurger = ref(false);
const search = ref("");
let updates: { data: Array<Acronym> } = reactive({ data: [] });

const acronymsFiltered = computed(() => {
  const text = search.value.toLowerCase();

  return acronyms.data.filter((acronym) => {
    const abbreviation = acronym.abbreviation.toLowerCase();
    const phrase = acronym.phrase.toLowerCase();

    return abbreviation.includes(text) || phrase.includes(text);
  });
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
