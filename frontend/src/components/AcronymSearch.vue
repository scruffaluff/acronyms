<template>
  <div class="columns mx-6 my-6">
    <div class="column field is-four-fifths mb-0">
      <div class="control has-icons-left">
        <input
          id="search"
          ref="searchInput"
          v-model.trim="acronyms.search"
          aria-label="search"
          class="input"
          type="text"
          placeholder="Search"
          @keydown.ctrl.enter.exact="beginAdd()"
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
            :style="`width: ${column.width}`"
          >
            {{ column.name }}
            <span
              :id="`${column.name.toLowerCase()}-sort`"
              :class="{ 'has-text-primary': lastSort == column.name }"
              class="icon is-clickable is-small has-tooltip-right"
              data-tooltip="Sort"
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
          v-show="editor.edit && editor.id === null"
          v-motion-slide-visible-left
        >
          <td>
            <input
              ref="addAbbreviationInput"
              v-model.trim="editor.abbreviation"
              class="input"
              placeholder="Abbreviation"
              @keyup.enter="editor.valid() && submitAdd()"
            />
          </td>
          <td>
            <input
              ref="addPhraseInput"
              v-model.trim="editor.phrase"
              class="input"
              placeholder="Phrase"
              @keyup.enter="editor.valid() && submitAdd()"
            />
          </td>
          <td>
            <button
              :disabled="!editor.valid()"
              class="button is-info is-light mx-1"
              @click="submitAdd()"
            >
              <strong>Submit</strong>
            </button>
            <button class="button is-light mx-1" @click="editor.edit = false">
              <strong>Cancel</strong>
            </button>
          </td>
        </tr>

        <tr v-for="acronym in acronyms.matches" :key="acronym.id">
          <AcronymRow :identifier="acronym.id" />
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { Acronym, useAcronymStore } from "../stores/acronym";
import { useEditorStore } from "../stores/editor";
import AcronymRow from "@/components/AcronymRow.vue";
import { nextTick, onMounted, reactive, ref } from "vue";

function beginAdd(): void {
  editor.edit = true;

  // nextTick is required since a v-show element is not available until the next
  // Vue update.
  if (!acronyms.search || acronyms.search.includes(" ")) {
    editor.phrase = acronyms.search;
    nextTick(() => addAbbreviationInput.value?.focus());
  } else {
    editor.abbreviation = acronyms.search;
    nextTick(() => addPhraseInput.value?.focus());
  }
}

function sort(column: { name: string; ascending: boolean }): void {
  const name = column.name.toLowerCase() as keyof Acronym;

  if (column.ascending) {
    acronyms.data.sort((left, right) => (left[name] > right[name] ? 1 : -1));
  } else {
    acronyms.data.sort((left, right) => (left[name] < right[name] ? 1 : -1));
  }
}

async function submitAdd(): Promise<void> {
  const response = await fetch(`/api`, {
    body: JSON.stringify({
      abbreviation: editor.abbreviation,
      phrase: editor.phrase,
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

  acronyms.data.push({
    abbreviation: editor.abbreviation,
    id: (await response.json()).id,
    phrase: editor.phrase,
  });
  editor.clear();

  acronyms.search = "";
  searchInput.value?.focus();
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
  lastSort.value = name;
}

const addButton = ref<HTMLElement | null>(null);
const addAbbreviationInput = ref<HTMLElement | null>(null);
const addPhraseInput = ref<HTMLElement | null>(null);
const searchInput = ref<HTMLElement | null>(null);
const lastSort = ref("");

const acronyms = useAcronymStore();
const editor = useEditorStore();
const columns = reactive([
  { name: "Abbreviation", ascending: true, icon: "fa-arrow-up", width: "25%" },
  { name: "Phrase", ascending: true, icon: "fa-arrow-up", width: "50%" },
]);

defineExpose({ beginAdd });
onMounted(acronyms.fetchData);
</script>

<style>
.fixed-columns {
  table-layout: fixed;
}
</style>
