import { defineStore } from "pinia";
import { computed, ref } from "vue";

export interface Acronym {
  id: number;
  abbreviation: string;
  phrase: string;
}

export const useAcronymStore = defineStore("acronym", () => {
  const count = ref(0);
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

  function deleteById(id: number): void {
    data.value = data.value.filter((acronym) => acronym.id !== id);
  }

  function getById(id: number): Acronym {
    return data.value.filter((acronym) => acronym.id === id)[0];
  }

  async function fetchData(offset: number): Promise<void> {
    const response = await fetch(`/api/acronym?offset=${offset}`);
    if (!response.ok) {
      console.error(response.text());
      return;
    }

    const headerCount = response.headers.get("X-Total-Count");
    if (headerCount !== null) {
      count.value = parseInt(headerCount);
    }
    data.value = await response.json();
  }

  return {
    count,
    data,
    deleteById,
    error,
    fetchData,
    getById,
    matches,
    search,
  };
});
