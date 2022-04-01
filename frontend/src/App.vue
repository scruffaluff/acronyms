<template>
  <div class="mt-6 container is-max-desktop">
    <div class="field">
      <div class="control has-icons-left has-icons-right">
        <input
          class="input"
          placeholder="Search"
          type="text"
          v-model="search"
        />
      </div>
    </div>
  </div>
  <table class="container table mt-6 has-text-left">
    <thead>
      <tr>
        <th>Abbreviation</th>
        <th>Expansion</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="acronym in acronymsFiltered">
        <td>{{ acronym.abbreviation }}</td>
        <td>{{ acronym.expansion }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { computed, ref } from "vue";

const acronyms = [
  { id: 1, abbreviation: "ROI", expansion: "Return On Investment" },
  { id: 2, abbreviation: "DM", expansion: "Data Mining" },
  { id: 3, abbreviation: "DM", expansion: "Direct Message" },
];
const search = ref("");

const acronymsFiltered = computed(() => {
  const text = search.value.toLowerCase();

  if (text === "") {
    return acronyms;
  } else if (text.includes(" ")) {
    return acronyms.filter((acronym) =>
      acronym.expansion.toLowerCase().includes(text)
    );
  } else {
    return acronyms.filter((acronym) =>
      acronym.abbreviation.toLowerCase().includes(text)
    );
  }
});

export default {
  data() {
    return { acronymsFiltered, search };
  },
};
</script>
