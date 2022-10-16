<template>
  <div class="columns mx-6 my-6">
    <div class="column field is-four-fifths mb-0">
      <div class="control has-icons-left">
        <input
          id="search"
          ref="inputSearch"
          v-model="acronyms.search"
          class="input"
          type="text"
          placeholder="Search"
          @keyup.ctrl.enter="beginAdd()"
          @keyup.tab="addButton?.focus()"
        />
        <span class="icon is-left is-small">
          <i class="fas fa-search"></i>
        </span>
      </div>
    </div>
    <div class="container column">
      <a id="add" class="button is-primary" @click="beginAdd()">
        <strong>Add</strong>
      </a>
    </div>
  </div>

  <div class="table-container">
    <table
      class="container table is-fullwidth is-hoverable fixed-columns has-text-left"
    >
      <thead>
        <tr>
          <th
            v-for="column in columns"
            :key="column.name"
            style="width: {{ column.width }}"
          >
            {{ column.name }}
            <span
              :class="{ 'has-text-primary': recentSort == column.name }"
              class="icon is-clickable is-small"
              @click="switchSort(column.name)"
            >
              <i :class="column.icon" class="fas"></i>
            </span>
          </th>
          <th style="width: 25%">Action</th>
        </tr>
      </thead>
      <tbody data-testid="table-body">
        <tr v-show="acronyms.insert.active">
          <td>
            <input
              ref="inputAddAbbreviation"
              v-model="acronyms.insert.abbreviation"
              class="input"
              placeholder="Abbreviation"
              @keyup.enter="valid(acronyms.insert) && submitAdd()"
            />
          </td>
          <td>
            <input
              ref="inputAddPhrase"
              v-model="acronyms.insert.phrase"
              class="input"
              placeholder="Phrase"
              @keyup.enter="valid(acronyms.insert) && submitAdd()"
            />
          </td>
          <td>
            <button
              :disabled="!valid(acronyms.insert)"
              class="button is-info is-light mx-1"
              @click="submitAdd()"
            >
              <strong>Submit</strong>
            </button>
            <button
              class="button is-light mx-1"
              @click="acronyms.insert.active = false"
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
                type="text"
                placeholder="Abbreviation"
              />
            </td>
            <td>
              <input
                v-model="acronym.phrase"
                class="input"
                placeholder="Phrase"
              />
            </td>
            <td>
              <button
                :disabled="!valid(acronym)"
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
              <span class="icon is-clickable" @click="acronym.delete = true">
                <i class="fas fa-trash-can"></i>
              </span>
            </td>
          </template>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { Acronym, useAcronymStore, valid } from "../stores/acronym";
import { nextTick, onMounted, reactive, ref } from "vue";

function beginAdd(): void {
  acronyms.insert.active = true;

  // nextTick is required since a v-show element is not available until the next
  // Vue update.
  if (!acronyms.search || acronyms.search.includes(" ")) {
    acronyms.insert.phrase = acronyms.search;
    nextTick(() => inputAddAbbreviation.value?.focus());
  } else {
    acronyms.insert.abbreviation = acronyms.search;
    nextTick(() => inputAddPhrase.value?.focus());
  }
}

function beginEdit(id: number): void {
  acronyms.getById(id).edit = true;
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
      abbreviation: acronyms.insert.abbreviation,
      phrase: acronyms.insert.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });
  if (!response.ok) {
    try {
      acronyms.error.message = (await response.json()).detail;
    } catch (_) {
      acronyms.error.message = await response.text();
    }

    acronyms.error.active = true;
    return;
  }

  acronyms.insert.abbreviation = "";
  acronyms.insert.phrase = "";
  acronyms.insert.active = false;

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
  const acronym = acronyms.getById(id);

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
  { name: "Abbreviation", ascending: true, icon: "fa-arrow-up", width: "25%" },
  { name: "Phrase", ascending: true, icon: "fa-arrow-up", width: "50%" },
]);
const inputAddAbbreviation = ref<HTMLElement | null>(null);
const inputAddPhrase = ref<HTMLElement | null>(null);
const inputEditAbbreviation = ref<Array<HTMLElement>>([]);
const inputSearch = ref<HTMLElement | null>(null);
const recentSort = ref("");

onMounted(acronyms.fetchData);
</script>

<style>
.fixed-columns {
  table-layout: fixed;
}
</style>
