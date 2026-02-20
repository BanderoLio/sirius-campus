import { ref, watch, onMounted, onUnmounted } from "vue";

const THEME_KEY = "theme";

export type Theme = "light" | "dark" | "system";

function getSystemDark(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(dark: boolean) {
  const root = document.documentElement;
  if (dark) {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

function getStoredTheme(): Theme {
  if (typeof localStorage === "undefined") return "system";
  const t = localStorage.getItem(THEME_KEY);
  return t === "light" || t === "dark" || t === "system" ? t : "system";
}

export function useTheme() {
  const theme = ref<Theme>(getStoredTheme());
  const isDark = ref(false);

  function setTheme(value: Theme) {
    theme.value = value;
    localStorage.setItem(THEME_KEY, value);
    updateApplied();
  }

  function toggleTheme() {
    const next = isDark.value ? "light" : "dark";
    setTheme(next);
  }

  function updateApplied() {
    const dark =
      theme.value === "dark" || (theme.value === "system" && getSystemDark());
    isDark.value = dark;
    applyTheme(dark);
  }

  onMounted(() => {
    updateApplied();
    const mq =
      typeof window !== "undefined"
        ? window.matchMedia("(prefers-color-scheme: dark)")
        : null;
    const listener = () => {
      if (theme.value === "system") updateApplied();
    };
    mq?.addEventListener("change", listener);
    onUnmounted(() => {
      mq?.removeEventListener("change", listener);
    });
  });

  watch(theme, () => updateApplied(), { immediate: true });

  return { theme, setTheme, toggleTheme, isDark, updateApplied };
}
