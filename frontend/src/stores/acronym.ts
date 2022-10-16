import { defineStore } from "pinia";

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

export const useAcronymStore = defineStore("acronym", {
  actions: {
    markDelete(id: number): void {
      const acronym = this.data.filter((acronym) => acronym.id == id)[0];
      acronym.delete = true;
    },

    markEdit(id: number): void {
      const acronym = this.data.filter((acronym) => acronym.id == id)[0];
      acronym.edit = true;
    },

    async fetchData(): Promise<void> {
      const response = await fetch("/api");
      if (!response.ok) {
        console.error(response.text());
        return;
      }

      this.data = (await response.json()).map((acronym: AcronymResponse) => ({
        ...acronym,
        delete: false,
        edit: false,
      }));
    },
  },

  getters: {
    matches(state): Acronym[] {
      const text = state.search.toLowerCase();

      return state.data.filter((acronym) => {
        const abbreviation = acronym.abbreviation.toLowerCase();
        const phrase = acronym.phrase.toLowerCase();

        return abbreviation.includes(text) || phrase.includes(text);
      });
    },
  },

  state: () => {
    return {
      error: { active: false, message: "" },
      insert: { abbreviation: "", active: false, phrase: "" },
      data: [] as Acronym[],
      search: "",
    };
  },
});
