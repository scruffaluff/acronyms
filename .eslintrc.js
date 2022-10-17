// ESLint configuration file for linting JavaScript and TypeScript code.
//
// For more information, visit https://eslint.org/docs/user-guide/configuring.

module.exports = {
  // The order of the extends plugins affects linter errors.
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
    "@vue/typescript/recommended",
    "@vue/prettier",
    "prettier",
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },
  plugins: ["prettier"],
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
