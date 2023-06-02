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
      <a
        id="add"
        class="button is-primary"
        role="button"
        tabindex="-1"
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
            v-for="column of columns"
            :key="column.name"
            :style="{ width: column.width }"
          >
            {{ column.name }}
            <span
              :id="`${column.name.toLowerCase()}-sort`"
              :class="{ 'has-text-primary': lastSort == column.name }"
              class="icon is-clickable is-small has-tooltip-right"
              data-tooltip="Sort"
              role="button"
              tabindex="-1"
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

        <tr v-for="acronym of acronyms.data" :key="acronym.id">
          <AcronymRow :identifier="acronym.id" />
        </tr>
        <tr
          v-for="index of 10 - acronyms.data.length"
          :key="index"
          class="hidden-row"
        >
          <td>HRVS</td>
          <td>Hidden Row for Vertical Spacing</td>
          <td></td>
        </tr>
      </tbody>
    </table>

    <nav
      class="pagination is-centered mt-4 mx-2"
      role="navigation"
      aria-label="pagination"
    >
      <button
        class="button is-primary pagination-previous"
        :disabled="paginator.isFirstPage"
        @click="paginator.prev"
      >
        Previous
      </button>
      <ul v-if="paginator.pageCount > 7" class="pagination-list">
        <li>
          <button
            class="button pagination-link"
            :class="{ hidden: paginator.currentPage <= 3 }"
            :disabled="paginator.currentPage === 1"
            @click="paginator.currentPage = 1"
          >
            1
          </button>
        </li>
        <li>
          <span
            class="pagination-ellipsis"
            :class="{ hidden: paginator.currentPage <= 3 }"
            >&hellip;</span
          >
        </li>
        <li v-for="index of 5" :key="index">
          <button
            v-show="
              paginator.currentPage + index - 3 > 0 &&
              paginator.currentPage + index - 3 <= paginator.pageCount
            "
            class="button pagination-link"
            :disabled="index === 3"
            @click="paginator.currentPage += index - 3"
          >
            {{ paginator.currentPage + index - 3 }}
          </button>
        </li>
        <li>
          <span
            class="pagination-ellipsis"
            :class="{ hidden: paginator.currentPage > paginator.pageCount - 3 }"
            >&hellip;</span
          >
        </li>
        <li>
          <button
            class="button pagination-link"
            :class="{ hidden: paginator.currentPage > paginator.pageCount - 3 }"
            :disabled="paginator.currentPage === paginator.pageCount"
            @click="paginator.currentPage = paginator.pageCount"
          >
            {{ paginator.pageCount }}
          </button>
        </li>
      </ul>
      <ul v-else class="pagination-list" data-testid="pages">
        <li v-for="page of paginator.pageCount" :key="page">
          <button
            class="button pagination-link"
            :disabled="paginator.currentPage === page"
            @click="paginator.currentPage = page"
          >
            {{ page }}
          </button>
        </li>
      </ul>
      <button
        class="button is-primary pagination-next"
        :disabled="paginator.isLastPage"
        @click="paginator.next"
      >
        Next
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import AcronymRow from "@/components/AcronymRow.vue";
import { Acronym, useAcronymStore } from "@/stores/acronym";
import { useEditorStore } from "@/stores/editor";
import { useOffsetPagination, UseOffsetPaginationReturn } from "@vueuse/core";
import { nextTick, onMounted, reactive, ref, watch } from "vue";

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
  const response = await fetch(`/api/acronym`, {
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

async function switchPage(payload: { currentPage: number }): Promise<void> {
  await acronyms.fetchData(10 * (payload.currentPage - 1));
}

function switchSort(name: string): void {
  const column = columns.filter((order) => order.name === name)[0];

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

function updatePaginator(count: number): void {
  const newPaginator = useOffsetPagination({
    total: count,
    page: 1,
    pageSize: 10,
    onPageChange: switchPage,
  });

  for (const key_ in newPaginator) {
    const key = key_ as keyof UseOffsetPaginationReturn;
    // @ts-expect-error: TypeScript is incorrect here about reassigning refs.
    paginator.value[key] = newPaginator[key];
  }
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

// Paginator does not expose its total attribute for later mutation. So
// initialize with defaults for one page, and update after data fetch.
const paginator = ref<UseOffsetPaginationReturn>(
  useOffsetPagination({
    total: 10,
    page: 1,
    pageSize: 10,
    onPageChange: switchPage,
  })
);

defineExpose({ beginAdd });
watch(() => acronyms.count, updatePaginator);
onMounted(async () => await acronyms.fetchData(0));
</script>

<style>
.fixed-columns {
  table-layout: fixed;
}

.hidden {
  visibility: hidden;
}

.hidden-row {
  max-height: 100%;
  visibility: hidden;
}
</style>
