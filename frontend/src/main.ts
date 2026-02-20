import "./index.css";
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

const theme = localStorage.getItem("theme") as "light" | "dark" | "system" | null;
const dark =
  theme === "dark" ||
  (theme !== "light" &&
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-color-scheme: dark)").matches);
if (dark) document.documentElement.classList.add("dark");
else document.documentElement.classList.remove("dark");

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
