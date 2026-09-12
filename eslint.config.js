import js from "@eslint/js";
import globals from "globals";

export default [
  {
    ignores: [
      ".venv/",
      "node_modules/",
      "frontend/build/",
      "src/cdpp/static/dist/",
    ],
  },
  js.configs.recommended,
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
    },
  },
];
