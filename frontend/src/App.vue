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
    <div class="columns mx-6 my-6">
      <div class="column field is-four-fifths mb-0">
        <div class="control has-icons-left">
          <input
            ref="inputSearch"
            v-model="acronyms.search"
            class="input"
            placeholder="Search"
            type="text"
            @keydown.tab="addButton?.focus()"
          />
          <span class="icon is-left is-small">
            <i class="fas fa-search"></i>
          </span>
        </div>
      </div>
      <div class="container column">
        <a class="button is-primary" @click="beginAdd()">
          <strong>Add</strong>
        </a>
      </div>
    </div>

    <div class="table-container">
      <table class="container table is-fullwidth is-hoverable has-text-left">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.name"
              style="width: {{ column.width }}"
            >
              {{ column.name }}
              <span
                class="icon is-clickable is-small"
                :class="{ 'has-text-primary': recentSort == column.name }"
                @click="switchSort(column.name)"
              >
                <i class="fas" :class="column.icon"></i>
              </span>
            </th>
            <th style="width: 25%">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-show="insert.active">
            <td>
              <input
                ref="inputAddAbbreviation"
                v-model="insert.abbreviation"
                class="input"
                placeholder="Abbreviation"
                type="text"
                @keyup.enter="submitAdd()"
              />
            </td>
            <td>
              <input
                ref="inputAddPhrase"
                v-model="insert.phrase"
                class="input"
                placeholder="Phrase"
                type="text"
                @keyup.enter="submitAdd()"
              />
            </td>
            <td>
              <button class="button is-info is-light mx-1" @click="submitAdd()">
                <strong>Submit</strong>
              </button>
              <button
                class="button is-light mx-1"
                @click="insert.active = false"
              >
                <strong>Cancel</strong>
              </button>
            </td>
          </tr>
          <tr v-for="acronym in acronyms.matches" :key="acronym.id">
            <template v-if="acronym.edit">
              <td>
                <input
                  ref="inputEditAbbreviation"
                  v-model="acronym.abbreviation"
                  class="input"
                  placeholder="Abbreviation"
                  type="text"
                />
              </td>
              <td>
                <input
                  v-model="acronym.phrase"
                  class="input"
                  placeholder="Phrase"
                  type="text"
                />
              </td>
              <td>
                <button
                  class="button is-light is-info mr-1"
                  @click="submitEdit(acronym.id)"
                >
                  <strong>Submit</strong>
                </button>
                <button class="button is-light" @click="acronym.edit = false">
                  <strong>Cancel</strong>
                </button>
              </td>
            </template>
            <template v-else>
              <td>{{ acronym.abbreviation }}</td>
              <td>{{ acronym.phrase }}</td>
              <td v-if="acronym.delete">
                <button
                  class="button is-light is-danger mr-1"
                  @click="submitDelete(acronym.id)"
                >
                  <strong>Delete</strong>
                </button>
                <button class="button is-light" @click="acronym.delete = false">
                  <strong>Cancel</strong>
                </button>
              </td>
              <td v-else>
                <span
                  class="icon mr-5 is-clickable"
                  @click="beginEdit(acronym.id)"
                >
                  <i class="fas fa-pencil"></i>
                </span>
                <span
                  class="icon is-clickable"
                  @click="acronyms.markDelete(acronym.id)"
                >
                  <i class="fas fa-trash-can"></i>
                </span>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </main>

  <footer class="footer py-6">
    <div class="container">
      <h4>
        <strong>Acronyms</strong> by
        <a href="https://github.com/scruffaluff">Scruffaluff</a>.
      </h4>
    </div>
  </footer>

  <div id="error-modal" class="modal" :class="{ 'is-active': error.active }">
    <div class="modal-background"></div>
    <div class="modal-content">
      <article class="message is-danger">
        <div class="message-header">
          <p>Error</p>
          <button
            aria-label="delete"
            class="delete"
            @click="error.active = false"
          ></button>
        </div>
        <div class="message-body">
          {{ error.message }}
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from "vue";
import { Acronym, useAcronymStore } from "./stores/acronym";

function beginAdd(): void {
  insert.active = true;

  // nextTick is required since a v-show element is not available until the next
  // Vue update.
  if (!acronyms.search || acronyms.search.includes(" ")) {
    insert.phrase = acronyms.search;
    nextTick(() => inputAddAbbreviation.value?.focus());
  } else {
    insert.abbreviation = acronyms.search;
    nextTick(() => inputAddPhrase.value?.focus());
  }
}

function beginEdit(id: number): void {
  acronyms.markEdit(id);
  nextTick(() => inputEditAbbreviation.value[0].focus());
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
  const response = await fetch(`/api`, {
    body: JSON.stringify({
      abbreviation: insert.abbreviation,
      phrase: insert.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });
  if (!response.ok) {
    error.message = await response.text();
    error.active = true;
    return;
  }

  insert.abbreviation = "";
  insert.phrase = "";
  insert.active = false;

  acronyms.search = "";
  inputSearch.value?.focus();
  await acronyms.fetchData();
}

async function submitDelete(id: number): Promise<void> {
  const response = await fetch(`/api/${id}`, { method: "DELETE" });
  if (!response.ok) {
    console.error(response.text());
    return;
  }

  await acronyms.fetchData();
}

async function submitEdit(id: number): Promise<void> {
  const acronym = acronyms.data.filter((acronym) => acronym.id == id)[0];

  const response = await fetch(`/api/${id}`, {
    body: JSON.stringify({
      abbreviation: acronym.abbreviation,
      phrase: acronym.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "PUT",
  });
  if (!response.ok) {
    console.error(response.text());
    return;
  }

  acronym.edit = false;
  await acronyms.fetchData();
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
  recentSort.value = name;
}

const acronyms = useAcronymStore();
const addButton = ref<HTMLElement | null>(null);
const columns = reactive([
  { name: "abbreviation", ascending: true, icon: "fa-arrow-up", width: "25%" },
  { name: "phrase", ascending: true, icon: "fa-arrow-up", width: "50%" },
]);
const error = reactive({
  active: false,
  message: "",
});
const insert = reactive({
  abbreviation: "",
  active: false,
  phrase: "",
});
const inputAddAbbreviation = ref<HTMLElement | null>(null);
const inputAddPhrase = ref<HTMLElement | null>(null);
const inputEditAbbreviation = ref<Array<HTMLElement>>([]);
const inputSearch = ref<HTMLElement | null>(null);
const navBarBurger = ref(false);
const recentSort = ref("");

onMounted(acronyms.fetchData);
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
