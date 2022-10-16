import { defineStore } from "pinia";
import { computed, ref } from "vue";

export interface Acronym {
  id: number;
  abbreviation: string;
  delete: boolean;
  edit: boolean;
  phrase: string;
}

export interface AcronymResponse {
  id: number;
  abbreviation: string;
  phrase: string;
}

export const useAcronymStore = defineStore("acronym", () => {
  const data = ref<Acronym[]>([]);
  const error = ref({ active: false, message: "" });
  const insert = ref({ abbreviation: "", active: false, phrase: "" });
  const search = ref("");

  const matches = computed(() => {
    const text = search.value.toLowerCase();

    return data.value.filter((acronym) => {
      const abbreviation = acronym.abbreviation.toLowerCase();
      const phrase = acronym.phrase.toLowerCase();

      return abbreviation.includes(text) || phrase.includes(text);
    });
  });

  function markDelete(id: number): void {
    const acronym = data.value.filter((acronym) => acronym.id == id)[0];
    acronym.delete = true;
  }

  function markEdit(id: number): void {
    const acronym = data.value.filter((acronym) => acronym.id == id)[0];
    acronym.edit = true;
  }

  async function fetchData(): Promise<void> {
    const response = await fetch("/api");
    if (!response.ok) {
      console.error(response.text());
      return;
    }

    data.value = (await response.json()).map((acronym: AcronymResponse) => ({
      ...acronym,
      delete: false,
      edit: false,
    }));
  }

  return {
    data,
    error,
    fetchData,
    insert,
    markDelete,
    markEdit,
    matches,
    search,
  };
});
