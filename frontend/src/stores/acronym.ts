import { defineStore } from "pinia";
import { ref, watch } from "vue";

// Type is suppose to represent function with any set of parameters.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Callback = (...args: any[]) => void;

export interface Acronym {
  id: number;
  abbreviation: string;
  phrase: string;
}

function debounce(callback: Callback, milliseconds = 100): Callback {
  let timeoutId: ReturnType<typeof setTimeout>;

  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => callback(...args), milliseconds);
  };
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

  watch(search, async () => await debounce(fetchData, 500)(0));

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
