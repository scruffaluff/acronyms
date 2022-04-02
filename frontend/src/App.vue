<template>
  <nav class="navbar" role="navigation" aria-label="main navigation">
    <div class="navbar-menu" style="margin-right: 0px">
      <div class="navbar-start">
        <a class="navbar-item title is-4 has-text-primary">Acronyms</a>
      </div>
      <div class="navbar-end">
        <div class="navbar-item">
          <div class="buttons">
            <a class="button is-primary">
              <strong>Sign up</strong>
            </a>
            <a class="button is-light">Log in</a>
          </div>
        </div>
      </div>
    </div>
  </nav>

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
          <span class="icon is-right" @click="remove(acronym.id)">
            <i class="fas fa-trash-can"></i>
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

interface Acronym {
  id: number;
  abbreviation: string;
  expansion: string;
}

async function remove(id: number): Promise<void> {
  await fetch(`/api/${id}`, { method: "DELETE" });
  acronyms = acronyms.filter((acronym) => acronym.id !== id);

  search.value = " ";
  search.value = "";
}

async function fetchData(): Promise<void> {
  const response = await fetch("/api");
  acronyms = await response.json();

  updateSearch();
}

function sort(column: { name: string; ascending: boolean }): void {
  const name = column.name as keyof Acronym;

  if (column.ascending) {
    acronyms.sort((left, right) => (left[name] > right[name] ? 1 : -1));
  } else {
    acronyms.sort((left, right) => (left[name] < right[name] ? 1 : -1));
  }

  updateSearch();
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

function updateSearch(): void {
  search.value = " ";
  search.value = "";
}

let acronyms: Array<Acronym> = [];
let columns = reactive([
  { name: "abbreviation", ascending: true, icon: "fa-arrow-up" },
  { name: "expansion", ascending: true, icon: "fa-arrow-up" },
]);
const search = ref("");

const acronymsFiltered = computed(() => {
  const text = search.value.toLowerCase();

  if (!text) {
    return acronyms;
  } else if (text.includes(" ")) {
    return acronyms.filter((acronym) =>
      acronym.expansion.toLowerCase().includes(text)
    );
  } else {
    return acronyms.filter((acronym) =>
      acronym.abbreviation.toLowerCase().includes(text)
    );
  }
});

onMounted(fetchData);
</script>

<style>
th {
  text-transform: capitalize;
}
</style>
