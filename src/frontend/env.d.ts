// TypeScript environment file to add third party toolingtypes to compiler.
//
// For more information, visit
// https://www.typescriptlang.org/docs/handbook/declaration-files/templates/module-d-ts.html.

/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
