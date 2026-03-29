"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Send } from "lucide-react";
import { askQuestion } from "@/services/ask";
import type { AskAnswer } from "@/types/api";

export function ChatShell() {
  const [input, setInput] = useState("");
  const [lastQuery, setLastQuery] = useState("");
  const [lastAnswer, setLastAnswer] = useState<AskAnswer | null>(null);

  const askMutation = useMutation({
    mutationFn: askQuestion,
    onSuccess: (data) => {
      setLastAnswer(data.answer);
    },
  });

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const query = input.trim();
    if (!query) return;

    setLastQuery(query);
    await askMutation.mutateAsync(query);
    setInput("");
  };

  const human = lastAnswer?.answer_human ?? lastAnswer?.answer ?? "";
  const legal = lastAnswer?.answer_legal ?? "";

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col p-6">
      <h1 className="text-2xl font-semibold text-slate-900">VidhiSakhā</h1>
      <p className="mt-1 text-sm text-slate-500">Indian Constitutional Assistant</p>

      <div className="mt-6 flex-1 rounded-xl border border-slate-200 bg-white p-5">
        {lastQuery ? (
          <div className="space-y-4">
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Question</div>
              <div className="mt-1 rounded-md bg-slate-50 p-3 text-slate-800">{lastQuery}</div>
            </div>

            {askMutation.isPending && (
              <div className="rounded-md border border-slate-200 p-3 text-slate-600">
                Analyzing constitutional provisions...
              </div>
            )}

            {askMutation.isError && (
              <div className="rounded-md border border-red-200 bg-red-50 p-3 text-red-700">
                Request failed. Please retry.
              </div>
            )}

            {lastAnswer && (
              <div className="space-y-4">
                <div>
                  <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Human Answer</div>
                  <div className="mt-1 rounded-md border border-slate-200 p-3 text-slate-800">{human}</div>
                </div>

                <details className="rounded-md border border-slate-200 p-3">
                  <summary className="cursor-pointer text-sm font-medium text-slate-700">Legal Answer</summary>
                  <p className="mt-2 text-sm leading-relaxed text-slate-700">{legal || "No legal format answer available."}</p>
                </details>

                <div>
                  <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Citations</div>
                  {lastAnswer.citations?.length ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {lastAnswer.citations.map((c) => (
                        <span
                          key={`${c.article_id}-${c.title}`}
                          className="rounded-full border border-slate-300 bg-slate-50 px-3 py-1 text-xs text-slate-700"
                        >
                          Article {c.article_id} · {c.title}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-slate-500">I am not sufficiently confident. Please rephrase or mention a specific article/topic.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400">
            Ask your first constitutional question.
          </div>
        )}
      </div>

      <form onSubmit={onSubmit} className="mt-4 flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about constitutional rights, provisions, or articles..."
          className="h-11 flex-1 rounded-lg border border-transparent px-3 text-sm outline-none focus:border-slate-300"
        />
        <button
          type="submit"
          disabled={askMutation.isPending}
          className="inline-flex h-11 items-center gap-2 rounded-lg bg-slate-900 px-4 text-sm font-medium text-white disabled:opacity-60"
        >
          <Send className="h-4 w-4" />
          Ask
        </button>
      </form>
    </div>
  );
}
