<template>
  <div class="container">
    <div class="field">
      <label class="label">Search</label>
      <div class="control has-icons-left has-icons-right">
        <input
          class="input is-success"
          type="text"
          placeholder="Search"
          v-model="search"
        />
        <span class="icon is-small is-left">
          <i class="fas fa-user"></i>
        </span>
        <span class="icon is-small is-right">
          <i class="fas fa-check"></i>
        </span>
      </div>
    </div>
  </div>
  <table class="container table mt-4">
    <thead>
      <tr>
        <th>Abbreviation</th>
        <th>Expansion</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="acronym in acronyms">
        <td>{{ acronym.abbreviation }}</td>
        <td>{{ acronym.expansion }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
const acronyms = [
  { id: 1, abbreviation: "ROI", expansion: "Return On Investment" },
  { id: 2, abbreviation: "DM", expansion: "Data Mining" },
  { id: 3, abbreviation: "DM", expansion: "Direct Message" },
];

export default {
  data() {
    return { acronyms, search: "" };
  },
};
</script>

<style>
#app {
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  color: #2c3e50;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  margin-top: 60px;
  text-align: center;
}
table {
  text-align: left;
}
</style>
