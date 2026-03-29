"use client";

import { useState, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { askQuestion, checkBackendHealth, isBackendConnectionError } from "@/services/ask";
import type { AskAnswer } from "@/types/api";
import {
  Menu,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  Home,
  History,
  Scale,
  BookOpen,
  Search,
  Mic,
  Send,
  Settings,
  BellOff,
  User,
  ChevronDown,
  AlertCircle,
  Sparkles,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

type ChatMessage = {
  role: "user" | "assistant";
  text: string;
  legalText?: string;
  citations?: { article_id: string; title: string }[];
};

async function streamByWords(text: string, onChunk: (value: string) => void): Promise<void> {
  const words = text.split(/(\s+)/).filter(Boolean);
  const total = words.length;

  if (total === 0) {
    onChunk("");
    return;
  }

  let index = 0;
  let rendered = "";

  while (index < total) {
    const dynamicChunk = Math.min(7, Math.max(1, Math.ceil(total / 90)));
    const nextSlice = words.slice(index, index + dynamicChunk).join("");
    rendered += nextSlice;
    index += dynamicChunk;
    onChunk(rendered);
    await new Promise((resolve) => setTimeout(resolve, 24));
  }
}

const sidebarItems: Array<{ icon: typeof Home; label: string; href: string }> = [
  { icon: Home, label: "Home", href: "/" },
  { icon: History, label: "History", href: "/chat" },
  { icon: Scale, label: "Cases", href: "/cases" },
  { icon: BookOpen, label: "Statutes", href: "/statutes" },
  { icon: Search, label: "Research", href: "/research" },
];

export function JurisprudenceChat() {
  const [query, setQuery] = useState("");
  const [phase, setPhase] = useState<"idle" | "loading" | "typing" | "done">("idle");
  const [streaming, setStreaming] = useState(false);
  const [streamedHuman, setStreamedHuman] = useState("");
  const [answer, setAnswer] = useState<AskAnswer | null>(null);
  const [connectionLost, setConnectionLost] = useState(false);
  const [retryingConnection, setRetryingConnection] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const mutation = useMutation({
    mutationFn: askQuestion,
    onSuccess: async (data) => {
      setConnectionLost(false);
      const received = data.answer;
      setAnswer(received);
      setStreaming(true);
      setPhase("typing");
      setStreamedHuman("");
      const human =
        received.answer_human?.trim() ||
        received.answer?.trim() ||
        received.answer_legal?.trim() ||
        "I could not generate a complete answer right now. Please try rephrasing your question.";
      await streamByWords(human, setStreamedHuman);
      setStreaming(false);
      setPhase("done");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: human,
          legalText: received.answer_legal || "",
          citations: received.citations || [],
        },
      ]);
    },
    onError: async (error) => {
      if (isBackendConnectionError(error)) {
        const healthy = await checkBackendHealth(2500);
        setConnectionLost(!healthy);
      } else {
        setConnectionLost(false);
      }
      setStreaming(false);
      setPhase("done");
      const errorMessage = "I hit a temporary response issue. Please try again in a few seconds.";
      setStreamedHuman(errorMessage);
      setMessages((prev) => [...prev, { role: "assistant", text: errorMessage }]);
    },
  });

  const onAsk = async (event?: React.FormEvent) => {
    if (event) event.preventDefault();
    const q = query.trim();
    if (!q || mutation.isPending) return;

    setHistory((prev) => [q, ...prev.filter((x) => x !== q)].slice(0, 8));
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setAnswer(null);
    setStreamedHuman("");
    setPhase("loading");
    setQuery("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    setSidebarOpen(false);

    try {
      await mutation.mutateAsync(q);
    } catch {
      // handled by mutation.onError
    }
  };

  const retryConnection = async () => {
    if (retryingConnection) return;
    setRetryingConnection(true);
    const healthy = await checkBackendHealth();
    setConnectionLost(!healthy);
    setRetryingConnection(false);
  };

  const displayMessages =
    phase === "typing"
      ? [
          ...messages,
          {
            role: "assistant" as const,
            text: streamedHuman,
            legalText: answer?.answer_legal || "",
            citations: answer?.citations || [],
          },
        ]
      : messages;

  return (
    <main className="h-screen h-[100dvh] overflow-hidden bg-[#f5f7fb] text-slate-900 dark:bg-[#031a45] dark:text-slate-100">
      <div className="flex h-full w-full">
        {sidebarOpen && (
          <button
            className="fixed inset-0 z-30 bg-black/45 md:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar overlay"
            type="button"
          />
        )}

        <aside
          className={`fixed inset-y-0 left-0 z-40 flex w-[250px] flex-col border-r border-slate-200 bg-[#eef2f8] p-5 transition-all duration-300 ease-out dark:border-[#1b315e] dark:bg-[#04153d] md:static md:z-0 md:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"} ${sidebarCollapsed ? "md:w-[84px]" : "md:w-[250px]"}`}
        >
          <div>
            <div className="flex items-center gap-3">
              <button
                className="hidden shrink-0 items-center justify-center rounded-full text-slate-500 hover:bg-slate-200 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-[#14264a] dark:hover:text-slate-200 md:inline-flex h-9 w-9"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                type="button"
                aria-label="Toggle sidebar"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className={`text-2xl font-semibold tracking-wide transition-all ${sidebarCollapsed ? "hidden md:hidden" : ""}`}>
                VidhiSakhā
              </div>
              <button
                className="ml-auto rounded p-1 text-slate-500 hover:bg-slate-200 dark:hover:bg-[#14264a] md:hidden"
                onClick={() => setSidebarOpen(false)}
                type="button"
                aria-label="Close sidebar"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className={`mt-1 text-[11px] tracking-[0.24em] text-slate-500 transition-all dark:text-slate-400 ${sidebarCollapsed ? "md:hidden" : ""}`}>
              INDIAN CONSTITUTIONAL ASSISTANT
            </p>
          </div>

          <button
            onClick={() => {
              setMessages([]);
              setHistory([]);
              setQuery("");
              setAnswer(null);
              setPhase("idle");
            }}
            className={`mt-6 h-12 rounded-lg bg-[#0c2f67] text-sm font-semibold text-white transition-colors hover:bg-[#143c80] ${sidebarCollapsed ? "md:px-0" : ""}`}
          >
            <span className={sidebarCollapsed ? "md:hidden" : ""}>New Consultation</span>
            <span className={`hidden ${sidebarCollapsed ? "md:inline" : ""}`}>＋</span>
          </button>

          <nav className="mt-6 space-y-1 text-sm">
            {sidebarItems.map(({ icon: Cmp, label, href }, idx) => {
              const active = idx === 1;
              return (
                <Link
                  key={label}
                  href={href}
                  className={`flex h-10 w-full items-center gap-3 rounded-md px-3 transition-colors ${active ? "bg-slate-200 font-medium text-[#0d2f67] dark:bg-[#16284f] dark:text-[#5ea0ff]" : "text-slate-600 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-[#14264a]"}`}
                >
                  <Cmp className="h-4 w-4" />
                  <span className={sidebarCollapsed ? "md:hidden" : ""}>{label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <Link href="/help" className="flex h-9 w-full items-center gap-3 rounded-md px-3 transition-colors hover:bg-slate-200 dark:hover:bg-[#14264a]">
              <span className={sidebarCollapsed ? "md:hidden" : ""}>Help Center</span>
              <span className={`hidden ${sidebarCollapsed ? "md:inline" : ""}`}>?</span>
            </Link>
            <Link href="/" className="flex h-9 w-full items-center gap-3 rounded-md px-3 transition-colors hover:bg-slate-200 dark:hover:bg-[#14264a]">
              <span className={sidebarCollapsed ? "md:hidden" : ""}>Log Out</span>
              <span className={`hidden ${sidebarCollapsed ? "md:inline" : ""}`}>⎋</span>
            </Link>
          </div>
        </aside>

        <section className="relative flex h-full flex-1 flex-col">
          <header className="flex shrink-0 items-center justify-between p-5 pb-0 md:p-7 md:pb-0">
            <div className="flex items-center gap-2">
              <button
                className="inline-flex h-8 w-8 items-center justify-center rounded border border-slate-300 text-slate-600 transition hover:bg-slate-100 dark:border-[#274777] dark:text-slate-200 dark:hover:bg-[#123261] md:hidden"
                onClick={() => setSidebarOpen(true)}
                type="button"
                aria-label="Open sidebar"
              >
                <Menu className="h-4 w-4" />
              </button>
            </div>

            <nav className="mx-auto hidden items-center gap-8 text-sm md:flex">
              <Link href="/chat" className="border-b-2 border-[#2d67ff] pb-1 font-semibold text-[#2d67ff]">Recent Queries</Link>
              <Link href="/library" className="text-slate-500 transition-colors hover:text-slate-800 dark:text-slate-300 dark:hover:text-white">Legal Library</Link>
              <Link href="/vault" className="text-slate-500 transition-colors hover:text-slate-800 dark:text-slate-300 dark:hover:text-white">My Vault</Link>
            </nav>
            <div className="ml-auto flex items-center gap-3">
              <BellOff className="h-4 w-4 text-slate-500" />
              <Settings className="h-4 w-4 text-slate-500" />
              <ThemeToggle />
              <div className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-400/40 bg-slate-100 dark:bg-slate-700">
                <User className="h-4 w-4" />
              </div>
            </div>
          </header>

          <div className="flex-1 overflow-y-auto px-5 pb-48 pt-4 md:px-7">
            <div className="mx-auto w-full max-w-4xl">
            <div className="mt-4 space-y-3">
              {displayMessages.length === 0 && (
                <div className="flex w-full flex-col items-center justify-center py-12 md:py-24">
                  <h2 className="mb-10 text-center text-3xl font-semibold text-slate-800 dark:text-slate-100 md:text-4xl">VidhiSakhā Jurisprudence</h2>
                  
                  <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2">
                    <button
                      type="button"
                      onClick={() => setQuery("Explain the scope of Article 21 and if it includes the right to a clean environment?")}
                      className="rounded-xl border border-slate-200 bg-white p-5 text-left transition-all hover:-translate-y-1 hover:shadow-md dark:border-[#2a4677] dark:bg-[#0a1f45] dark:hover:bg-[#123261]"
                    >
                      <div className="font-semibold text-slate-800 dark:text-slate-200">Scope of Article 21</div>
                      <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">Does it include the right to a clean environment?</div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setQuery("What are the reasonable restrictions on freedom of speech under Article 19(2)?")}
                      className="rounded-xl border border-slate-200 bg-white p-5 text-left transition-all hover:-translate-y-1 hover:shadow-md dark:border-[#2a4677] dark:bg-[#0a1f45] dark:hover:bg-[#123261]"
                    >
                      <div className="font-semibold text-slate-800 dark:text-slate-200">Freedom of Speech</div>
                      <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">What are its reasonable restrictions?</div>
                    </button>
                  </div>
                </div>
              )}
              {displayMessages.map((msg, idx) => (
                <div
                  key={`${msg.role}-${idx}-${msg.text.slice(0, 24)}`}
                  className="flex gap-4 py-3"
                >
                  <div className={`flex shrink-0 items-center justify-center rounded-full ${msg.role === "user" ? "h-8 w-8 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200" : "h-10 w-10 bg-transparent text-[#2d67ff]"}`}>
                    {msg.role === "user" ? <User className="h-5 w-5" /> : <Scale className="h-6 w-6" />}
                  </div>
                  <div className={`mt-1 flex-1 text-[15px] leading-8 ${msg.role === "user" ? "font-medium text-slate-800 dark:text-slate-200" : "text-slate-700 dark:text-slate-200"}`}>
                    <div className="whitespace-pre-wrap">
                      {msg.text || (phase === "typing" ? "..." : "")}
                      {phase === "typing" && idx === displayMessages.length - 1 && (
                        <span className="ml-0.5 animate-pulse text-[#2d67ff]">▌</span>
                      )}
                    </div>

                    {msg.role === "assistant" && (msg.legalText || (phase === "typing" && idx === displayMessages.length - 1)) && (
                      <details className="group mt-5 mb-2 rounded-xl border border-slate-200 bg-[#f8fbff] p-4 transition-all dark:border-[#1f3765] dark:bg-[#0b1f44]">
                        <summary className="flex cursor-pointer list-none items-center justify-between text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500 hover:text-[#2d67ff] dark:text-slate-400 dark:hover:text-[#528bff]">
                          Legal Analysis (Statutory Detail & Precedents)
                          <ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
                        </summary>
                        <div className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-600 dark:text-slate-300">
                          {msg.legalText || (phase === "typing" ? "Analyzing constitutional provisions..." : "")}
                        </div>
                      </details>
                    )}

                    {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                      <div className="mt-5 flex flex-col gap-2">
                        {msg.citations.slice(0, 5).map((c) => (
                          <div
                            key={`${c.article_id}-${c.title}`}
                            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-left text-[11px] font-medium leading-relaxed text-slate-600 shadow-sm dark:border-[#2a4677] dark:bg-[#163562] dark:text-slate-300"
                          >
                            {`Art ${c.article_id}: ${c.title}`}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {phase === "loading" && (
                <div className="flex gap-4 py-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-transparent text-[#2d67ff]">
                    <Scale className="h-6 w-6 animate-pulse" />
                  </div>
                  <div className="mt-2.5 flex flex-1 items-center gap-1.5">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-[#3d89ff]" style={{ animationDelay: "0ms" }} />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-[#3d89ff]" style={{ animationDelay: "150ms" }} />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-[#3d89ff]" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}
            </div>

            {history.length > 0 && (
              <div className="mt-12 rounded-xl border border-slate-200 bg-white p-4 text-sm shadow-sm dark:border-[#214071] dark:bg-[#0a1f45]">
                <div className="mb-3 font-semibold text-slate-700 dark:text-slate-200">Recent Queries</div>
                <div className="flex flex-col gap-2">
                  {history.map((h) => (
                    <button
                      key={h}
                      onClick={() => setQuery(h)}
                      className="rounded-xl border border-slate-300 px-4 py-2.5 text-left text-xs leading-relaxed transition-colors hover:bg-slate-50 dark:border-[#2a4677] dark:hover:bg-[#123261]"
                    >
                      {h}
                    </button>
                  ))}
                </div>
              </div>
            )}
            </div>
          </div>

          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[rgba(245,247,251,0.95)] via-[#f5f7fb] to-transparent pt-16 pb-5 px-5 md:px-7 dark:from-[rgba(3,26,69,0.98)] dark:via-[#031a45] pointer-events-none">
            <div className="mx-auto w-full max-w-4xl pointer-events-auto">
              {connectionLost && (
                <div className="mb-4 rounded-xl border border-red-200 bg-[#fff1f1] px-4 py-3 text-sm text-red-700 shadow-sm dark:border-[#5c2740] dark:bg-[#3a1f33] dark:text-[#ffd9d9]">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <AlertCircle className="h-4 w-4" />
                      <div>
                        <div className="font-semibold">Digital Archive Connection Lost</div>
                        <div className="text-[11px] opacity-90">Unable to reach the Supreme Court database API. Please try again.</div>
                      </div>
                    </div>
                    <button
                      onClick={retryConnection}
                      className="rounded-md bg-[#174fae] px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-[#2565d7] disabled:opacity-60"
                      disabled={retryingConnection}
                    >
                      {retryingConnection ? "Retrying..." : "Retry Connection"}
                    </button>
                  </div>
                </div>
              )}

              <form onSubmit={onAsk} className="rounded-3xl border border-slate-300 bg-white px-3 py-2 shadow-md focus-within:border-[#3d89ff] focus-within:ring-1 focus-within:ring-[#3d89ff]/50 dark:border-[#2a4677] dark:bg-[#081838]">
                <div className="flex items-center gap-2">
                  <button type="button" className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-[#123261]">
                    <span className="text-2xl font-light">+</span>
                  </button>
                  <textarea
                    ref={textareaRef}
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      e.target.style.height = "auto";
                      e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (query.trim() && !mutation.isPending && !retryingConnection) {
                           onAsk();
                        }
                      }
                    }}
                    placeholder="Ask about constitutional rights, case laws, or statutes..."
                    className="min-h-[24px] max-h-[200px] flex-1 resize-none bg-transparent px-2 py-3 text-[15px] outline-none placeholder:text-slate-400 dark:text-white"
                    rows={1}
                  />
                  <button type="button" className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 dark:hover:bg-[#123261]">
                    <Mic className="h-5 w-5" />
                  </button>
                  <button
                    type="submit"
                    className={`inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-colors ${query.trim() ? "bg-[#1e63ff] text-white hover:bg-[#2d6fff]" : "bg-slate-100 text-slate-400 dark:bg-[#123261] dark:text-slate-500"}`}
                    disabled={mutation.isPending || retryingConnection || !query.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
