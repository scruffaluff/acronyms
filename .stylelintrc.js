// Stylelint configuration file for linting CSS code.
//
// For more information, visit https://stylelint.io/user-guide/configure.

module.exports = {
  extends: [
    "stylelint-config-standard",
    "stylelint-config-prettier",
    "stylelint-config-standard-scss",
    "stylelint-config-prettier-scss",
  ],
  ignoreFiles: ["node_modules/"],
  rules: {
    "scss/at-import-partial-extension": "always",
  },
};
