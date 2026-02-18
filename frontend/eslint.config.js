import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  ...tseslint.configs.recommended,
  {
    ignores: ["dist", "node_modules"],
  }
);
