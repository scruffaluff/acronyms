import { defineStore } from "pinia";
import { computed, ref } from "vue";

export interface Acronym {
  id: number;
  abbreviation: string;
  phrase: string;
}

export const useAcronymStore = defineStore("acronym", () => {
  const data = ref<Acronym[]>([]);
  const error = ref({ active: false, message: "" });
  const search = ref("");

  const matches = computed(() => {
    const text = search.value.toLowerCase();

    return data.value.filter((acronym) => {
      const abbreviation = acronym.abbreviation.toLowerCase();
      const phrase = acronym.phrase.toLowerCase();

      return abbreviation.includes(text) || phrase.includes(text);
    });
  });

  function getById(id: number): Acronym {
    return data.value.filter((acronym) => acronym.id === id)[0];
  }

  async function fetchData(): Promise<void> {
    const response = await fetch("/api");
    if (!response.ok) {
      console.error(response.text());
      return;
    }

    data.value = await response.json();
  }

  return {
    data,
    error,
    fetchData,
    getById,
    matches,
    search,
  };
});
