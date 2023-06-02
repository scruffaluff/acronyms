import { Acronym } from "@/stores/acronym";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useEditorStore = defineStore("editor", () => {
  const abbreviation = ref("");
  const edit = ref(false);
  const id = ref<number | null>(null);
  const remove = ref(false);
  const phrase = ref("");

  function begin(option: "edit" | "remove"): void {
    if (option === "edit") {
      edit.value = true;
      remove.value = false;
    } else {
      edit.value = false;
      remove.value = true;
    }
  }

  function clear(): void {
    abbreviation.value = "";
    edit.value = false;
    id.value = null;
    remove.value = false;
    phrase.value = "";
  }

  function set(acronym: Acronym): void {
    id.value = acronym.id;
    abbreviation.value = acronym.abbreviation;
    phrase.value = acronym.phrase;
  }

  function valid(): boolean {
    return abbreviation.value.length !== 0 && phrase.value.length !== 0;
  }

  return {
    abbreviation,
    begin,
    edit,
    clear,
    id,
    phrase,
    remove,
    set,
    valid,
  };
});
