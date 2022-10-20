<template>
  <template v-if="editor.edit && editor.id === acronym.id">
    <td>
      <input
        ref="abbreviationInput"
        v-model.trim="editor.abbreviation"
        aria-label="abbreviation-editor"
        class="input"
        type="text"
        placeholder="Abbreviation"
      />
    </td>
    <td>
      <input v-model.trim="editor.phrase" class="input" placeholder="Phrase" />
    </td>
    <td>
      <button
        :disabled="!editor.valid()"
        class="button is-light is-info mr-1"
        @click="submitEdit()"
      >
        <strong>Submit</strong>
      </button>
      <button class="button is-light" @click="editor.clear()">
        <strong>Cancel</strong>
      </button>
    </td>
  </template>
  <template v-else>
    <td>{{ acronym.abbreviation }}</td>
    <td>{{ acronym.phrase }}</td>
    <td v-if="editor.remove && editor.id === acronym.id">
      <button
        class="button is-light is-danger mr-1"
        @click="submitRemove(acronym.id)"
      >
        <strong>Delete</strong>
      </button>
      <button class="button is-light" @click="editor.clear()">
        <strong>Cancel</strong>
      </button>
    </td>
    <td v-else>
      <span
        class="icon mr-5 is-clickable"
        data-tooltip="Edit"
        @click="beginEdit()"
      >
        <i class="fas fa-pencil"></i>
      </span>
      <span
        class="icon is-clickable"
        data-tooltip="Delete"
        @click="beginRemove()"
      >
        <i class="fas fa-trash-can"></i>
      </span>
    </td>
  </template>
</template>

<script setup lang="ts">
import { useAcronymStore } from "@/stores/acronym";
import { useEditorStore } from "@/stores/editor";
import { nextTick, ref } from "vue";

function beginEdit(): void {
  editor.set(acronym);
  editor.begin("edit");
  nextTick(() => abbreviationInput.value?.focus());
}

function beginRemove(): void {
  editor.set(acronym);
  editor.begin("remove");
}

async function submitEdit(): Promise<void> {
  const response = await fetch(`/api/${editor.id}`, {
    body: JSON.stringify({
      abbreviation: editor.abbreviation,
      phrase: editor.phrase,
    }),
    headers: { "Content-Type": "application/json" },
    method: "PUT",
  });
  if (!response.ok) {
    console.error(response.text());
    return;
  }

  acronym.abbreviation = editor.abbreviation;
  acronym.phrase = editor.phrase;
  editor.clear();
}

async function submitRemove(id: number): Promise<void> {
  const response = await fetch(`/api/${id}`, { method: "DELETE" });
  if (!response.ok) {
    console.error(response.text());
    return;
  }

  await acronyms.deleteById(acronym.id);
  editor.clear();
}

const props = defineProps<{ identifier: number }>();
const abbreviationInput = ref<HTMLElement | null>(null);

const acronyms = useAcronymStore();
const acronym = acronyms.getById(props.identifier);
const editor = useEditorStore();
</script>

<style>
.fixed-columns {
  table-layout: fixed;
}
</style>
