"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem("theme");
    if (saved === "dark") setDark(true);
    else if (saved === "light") setDark(false);
    else setDark(window.matchMedia("(prefers-color-scheme: dark)").matches);
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
    window.localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark, ready]);

  if (!ready) {
    return (
      <button
        className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-300/30 bg-slate-900/30 text-slate-200 transition hover:bg-slate-800/60 dark:border-slate-600"
        aria-label="Toggle theme"
        type="button"
      >
        <Sun className="h-4 w-4" />
      </button>
    );
  }

  return (
    <button
      onClick={() => setDark((v) => !v)}
      className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-300/30 bg-slate-900/30 text-slate-200 transition hover:bg-slate-800/60 dark:border-slate-600"
      aria-label="Toggle theme"
      type="button"
    >
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}
