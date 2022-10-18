<template>
  <div class="columns mx-6 my-6">
    <div class="column field is-four-fifths mb-0">
      <div class="control has-icons-left">
        <input
          id="search"
          ref="inputSearch"
          v-model="acronyms.search"
          aria-label="search"
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
      <a
        id="add"
        class="button is-primary"
        @keyup="keyUpHandler"
        @click="beginAdd()"
      >
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
              @keyup.ctrl.a="beginAdd()"
              @click="switchSort(column.name)"
            >
              <i :class="column.icon" class="fas"></i>
            </span>
          </th>
          <th style="width: 25%">Action</th>
        </tr>
      </thead>
      <tbody data-testid="table-body">
        <tr
          v-show="edit.active && edit.id === null"
          v-motion-slide-visible-left
        >
          <td>
            <input
              ref="inputAddAbbreviation"
              v-model="edit.abbreviation"
              class="input"
              placeholder="Abbreviation"
              @keyup.enter="edit.valid() && submitAdd()"
            />
          </td>
          <td>
            <input
              ref="inputAddPhrase"
              v-model="edit.phrase"
              class="input"
              placeholder="Phrase"
              @keyup.enter="edit.valid() && submitAdd()"
            />
          </td>
          <td>
            <button
              :disabled="!edit.valid()"
              class="button is-info is-light mx-1"
              @click="submitAdd()"
            >
              <strong>Submit</strong>
            </button>
            <button class="button is-light mx-1" @click="edit.active = false">
              <strong>Cancel</strong>
            </button>
          </td>
        </tr>
        <tr v-for="acronym in acronyms.matches" :key="acronym.id">
          <template v-if="edit.active && edit.id === acronym.id">
            <td>
              <input
                ref="inputEditAbbreviation"
                v-model="edit.abbreviation"
                aria-label="abbreviation-editor"
                class="input"
                type="text"
                placeholder="Abbreviation"
              />
            </td>
            <td>
              <input v-model="edit.phrase" class="input" placeholder="Phrase" />
            </td>
            <td>
              <button
                :disabled="!edit.valid()"
                class="button is-light is-info mr-1"
                @click="submitEdit()"
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
                @keyup="keyUpHandler"
              >
                <i class="fas fa-pencil"></i>
              </span>
              <span
                class="icon is-clickable"
                @click="acronym.delete = true"
                @keyup="keyUpHandler"
              >
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
import { Acronym, useAcronymStore } from "../stores/acronym";
import { useRefHistory } from "@vueuse/core";
import { nextTick, onMounted, reactive, ref } from "vue";

class Edit {
  abbreviation = "";
  active = false;
  id: number | null = null;
  phrase = "";

  clear(): void {
    this.abbreviation = "";
    this.active = false;
    this.id = null;
    this.phrase = "";
  }

  valid(): boolean {
    return this.abbreviation.length !== 0 && this.phrase.length !== 0;
  }
}

function beginAdd(): void {
  edit.value.active = true;

  // nextTick is required since a v-show element is not available until the next
  // Vue update.
  if (!acronyms.search || acronyms.search.includes(" ")) {
    edit.value.phrase = acronyms.search;
    nextTick(() => inputAddAbbreviation.value?.focus());
  } else {
    edit.value.abbreviation = acronyms.search;
    nextTick(() => inputAddPhrase.value?.focus());
  }
}

function beginEdit(id: number): void {
  const acronym = acronyms.getById(id);
  edit.value.id = id;
  edit.value.abbreviation = acronym.abbreviation;
  edit.value.phrase = acronym.phrase;

  edit.value.active = true;
  nextTick(() => inputEditAbbreviation.value[0].focus());
}

function keyUpHandler(event: KeyboardEvent): void {
  if (event.ctrlKey) {
    if (event.key === "a") {
      beginAdd();
    } else if (event.key === "Z") {
      redoEdit();
    } else if (event.key === "z") {
      undoEdit();
    }
  }
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
      abbreviation: edit.value.abbreviation,
      phrase: edit.value.phrase,
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

  edit.value.clear();

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

async function submitEdit(): Promise<void> {
  const response = await fetch(`/api/${edit.value.id}`, {
    body: JSON.stringify({
      abbreviation: edit.value.abbreviation,
      phrase: edit.value.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "PUT",
  });
  if (!response.ok) {
    console.error(response.text());
    return;
  }

  edit.value.clear();
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

const addButton = ref<HTMLElement | null>(null);
const inputAddAbbreviation = ref<HTMLElement | null>(null);
const inputAddPhrase = ref<HTMLElement | null>(null);
const inputEditAbbreviation = ref<Array<HTMLElement>>([]);
const inputSearch = ref<HTMLElement | null>(null);
const recentSort = ref("");

const acronyms = useAcronymStore();
const columns = reactive([
  { name: "Abbreviation", ascending: true, icon: "fa-arrow-up", width: "25%" },
  { name: "Phrase", ascending: true, icon: "fa-arrow-up", width: "50%" },
]);
const edit = ref(new Edit());
const { undo: undoEdit, redo: redoEdit } = useRefHistory(edit, {
  capacity: 25,
  deep: true,
});

document.addEventListener("keyup", keyUpHandler);
onMounted(acronyms.fetchData);
</script>

<style>
.fixed-columns {
  table-layout: fixed;
}
</style>
