import { defineStore } from "pinia";
import { ref, watch } from "vue";

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

  function deleteById(id: number): void {
    data.value = data.value.filter((acronym) => acronym.id !== id);
  }

  function getById(id: number): Acronym {
    return data.value.filter((acronym) => acronym.id === id)[0];
  }

  async function fetchData(offset: number): Promise<void> {
    let parameters: string;
    if (search.value) {
      parameters = `&abbreviation=${search.value}&phrase=${search.value}`;
    } else {
      parameters = "";
    }

    const response = await fetch(`/api/acronym?offset=${offset}${parameters}`);
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

  watch(search, async () => await fetchData(0));

  return {
    count,
    data,
    deleteById,
    error,
    fetchData,
    getById,
    search,
  };
});
