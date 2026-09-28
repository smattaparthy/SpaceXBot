"use client";

import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import NavBar from "./NavBar";

// Same-origin path, forwarded to the backend by the rewrite in next.config.ts.
const API_URL = "/api";

const UNREACHABLE_MESSAGE =
  "Can't reach the Mission Control API. Check that the backend is running.";

// Retrieval always returns the top matches, even for off-topic questions.
// Only list sources that are both similar enough on their own and close to
// the best match, so loosely related documents aren't shown as the basis.
const MIN_SOURCE_SCORE = 0.4;
const MAX_GAP_FROM_BEST = 0.15;

const MAX_QUESTION_LENGTH = 1000;

const SUGGESTIONS = [
  "What is Dragon used for?",
  "How does Falcon 9 reuse its first stage?",
  "What is Starship designed to do?",
  "What can delay a launch?",
];

interface Source {
  file_name: string;
  chunk_id: number;
  score: number;
}

interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
}

interface Exchange {
  id: number;
  question: string;
  status: "loading" | "done" | "error";
  answer?: string;
  sources?: Source[];
  error?: string;
}

// "falcon9_overview.txt" -> "Falcon 9 overview"
function sourceLabel(fileName: string): string {
  const label = fileName
    .replace(/\.[^.]+$/, "")
    .replace(/[_-]+/g, " ")
    .replace(/([a-z])(\d)/gi, "$1 $2");
  return label.charAt(0).toUpperCase() + label.slice(1);
}

function errorMessage(status: number, body: unknown): string {
  if (status === 422) {
    return `Questions need to be between 1 and ${MAX_QUESTION_LENGTH.toLocaleString()} characters.`;
  }
  if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string") {
    return body.detail;
  }
  // A 5xx without the API's own error body means the forwarding proxy
  // couldn't reach the backend at all.
  if (status >= 500) {
    return UNREACHABLE_MESSAGE;
  }
  return `The Mission Control API returned an error (${status}). Try again.`;
}

export default function ChatWidget() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [draft, setDraft] = useState("");
  const nextId = useRef(0);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const pending = exchanges.some((exchange) => exchange.status === "loading");

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [exchanges]);

  function update(id: number, changes: Partial<Exchange>) {
    setExchanges((prev) =>
      prev.map((exchange) => (exchange.id === id ? { ...exchange, ...changes } : exchange)),
    );
  }

  async function ask(question: string) {
    const trimmed = question.trim();
    if (!trimmed || pending) return;

    const id = nextId.current++;
    setExchanges((prev) => [...prev, { id, question: trimmed, status: "loading" }]);
    setDraft("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });
      const body: unknown = await response.json().catch(() => null);

      if (!response.ok) {
        update(id, { status: "error", error: errorMessage(response.status, body) });
        return;
      }

      const data = body as ChatResponse;
      update(id, { status: "done", answer: data.answer, sources: data.sources });
    } catch {
      update(id, { status: "error", error: UNREACHABLE_MESSAGE });
    }
  }

  function retry(exchange: Exchange) {
    setExchanges((prev) => prev.filter((item) => item.id !== exchange.id));
    ask(exchange.question);
  }

  function startNewChat() {
    setExchanges([]);
    setDraft("");
    inputRef.current?.focus();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    ask(draft);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      ask(draft);
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <NavBar onNewChat={exchanges.length > 0 ? startNewChat : undefined} />

      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-5 sm:px-6">
        {exchanges.length === 0 ? (
          <section className="flex flex-1 flex-col justify-center py-16">
            <h1 className="font-display text-5xl leading-[0.95] font-semibold tracking-tight sm:text-7xl">
              Ask about SpaceX vehicles and launches.
            </h1>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-silver">
              Answers come only from the Mission Control knowledge base, and show which
              documents they&apos;re based on.
            </p>

            <p className="mt-12 text-silver">Or start with one of these:</p>
            <ul className="mt-3 border-t border-steel/60">
              {SUGGESTIONS.map((suggestion) => (
                <li key={suggestion} className="border-b border-steel/60">
                  <button
                    type="button"
                    onClick={() => ask(suggestion)}
                    className="w-full py-4 text-left text-lg text-ink/85 hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-silver"
                  >
                    {suggestion}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        ) : (
          <section aria-label="Conversation" aria-live="polite" aria-busy={pending} className="pb-8">
            {exchanges.map((exchange) => (
              <article key={exchange.id} className="border-b border-steel/40 py-10">
                <h2 className="font-display text-3xl leading-tight font-semibold tracking-tight sm:text-4xl">
                  {exchange.question}
                </h2>

                {exchange.status === "loading" && (
                  <div role="status" className="mt-6">
                    <div className="relative h-px w-full overflow-hidden bg-steel/40">
                      <div className="absolute inset-y-0 w-1/4 bg-silver motion-safe:animate-sweep" />
                    </div>
                    <p className="mt-3 text-silver">Searching the knowledge base…</p>
                  </div>
                )}

                {exchange.status === "done" && (
                  <div className="mt-5 motion-safe:animate-reveal">
                    <p className="max-w-prose text-lg leading-relaxed whitespace-pre-line text-ink/90">
                      {exchange.answer}
                    </p>
                    <SourceList sources={exchange.sources ?? []} />
                  </div>
                )}

                {exchange.status === "error" && (
                  <div role="alert" className="mt-5 border-l-2 border-alert pl-4">
                    <p className="text-alert">{exchange.error}</p>
                    <button
                      type="button"
                      onClick={() => retry(exchange)}
                      disabled={pending}
                      className="mt-2 text-ink underline underline-offset-4 hover:text-silver disabled:text-steel focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-silver"
                    >
                      Try again
                    </button>
                  </div>
                )}
              </article>
            ))}
            <div ref={endRef} />
          </section>
        )}
      </main>

      <form onSubmit={handleSubmit} className="sticky bottom-0 border-t border-steel/50 bg-space">
        <div className="mx-auto flex w-full max-w-2xl items-end gap-3 px-5 py-4 sm:px-6">
          <label htmlFor="question" className="sr-only">
            Your question
          </label>
          <textarea
            id="question"
            ref={inputRef}
            rows={1}
            value={draft}
            maxLength={MAX_QUESTION_LENGTH}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about SpaceX"
            className="field-sizing-content max-h-40 min-h-12 flex-1 resize-none bg-graphite px-4 py-2.5 text-lg text-ink outline-none placeholder:text-silver/70 focus-visible:ring-2 focus-visible:ring-silver"
          />
          <button
            type="submit"
            disabled={!draft.trim() || pending}
            className="h-12 shrink-0 bg-ink px-6 font-display text-lg font-semibold text-space hover:bg-silver disabled:bg-graphite disabled:text-steel focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-silver"
          >
            Ask
          </button>
        </div>
      </form>
    </div>
  );
}

function SourceList({ sources }: { sources: Source[] }) {
  const best = Math.max(0, ...sources.map((source) => source.score));
  const relevant = sources.filter(
    (source) => source.score >= MIN_SOURCE_SCORE && source.score >= best - MAX_GAP_FROM_BEST,
  );
  if (relevant.length === 0) return null;

  return (
    <p className="mt-5 text-sm text-silver">
      Based on {relevant.map((source) => sourceLabel(source.file_name)).join(", ")}
    </p>
  );
}
