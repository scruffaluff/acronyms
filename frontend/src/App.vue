<template>
  <h1>Acronyms</h1>
  <table>
    <tr>
      <th>Abbreviation</th>
      <th>Expansion</th>
    </tr>
    <tr v-for="acronym in acronyms">
      <td>{{ acronym.abbreviation }}</td>
      <td>{{ acronym.expansion }}</td>
    </tr>
  </table>
</template>

<script lang="ts">
const acronyms = [
  { id: 1, abbreviation: "ROI", expansion: "Return On Investment" },
  { id: 2, abbreviation: "DM", expansion: "Data Mining"},
  { id: 3, abbreviation: "DM", expansion: "Direct Message"},
];

export default {
  data() {
    return { acronyms, count: 0 };
  }
}
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
