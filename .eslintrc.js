// ESLint configuration file for linting JavaScript and TypeScript code.
//
// For more information, visit https://eslint.org/docs/user-guide/configuring.

// TODO: Research correct extends and plugins orders.
module.exports = {
  // The order of the extends plugins affects linter errors.
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/vue3-recommended",
    "@vue/typescript/recommended",
    "@vue/prettier",
    "plugin:vuejs-accessibility/recommended",
    "prettier",
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },
  plugins: ["@typescript-eslint", "vuejs-accessibility", "prettier"],
  root: true,
  rules: {
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        args: "all",
        argsIgnorePattern: "^_",
        ignoreRestSiblings: false,
        vars: "all",
      },
    ],
  },
};
