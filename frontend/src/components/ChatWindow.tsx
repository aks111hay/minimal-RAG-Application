import { useEffect, useRef, useState } from "react";
import { ArrowUp, MessageSquareDashed } from "lucide-react";
import { MessageBubble } from "./MessageBubble";
import type { DisplayMessage } from "../types";

interface ChatWindowProps {
  messages: DisplayMessage[];
  onSend: (question: string) => void;
  isBusy: boolean;
  inspectedMessageId: string | null;
  onInspect: (id: string) => void;
}

export function ChatWindow({
  messages,
  onSend,
  isBusy,
  inspectedMessageId,
  onInspect,
}: ChatWindowProps) {
  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || isBusy) return;
    onSend(trimmed);
    setDraft("");
  }

  return (
    <main className="flex h-full flex-1 flex-col bg-base">
      {/* Message list */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-text-muted">
            <MessageSquareDashed className="h-8 w-8" />
            <div>
              <p className="font-display text-sm text-text-primary">Nothing indexed yet</p>
              <p className="mt-1 max-w-xs text-xs">
                Upload a PDF or paste some text on the left, then ask a question grounded in it.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-5">
            {messages.map((m) => (
              <MessageBubble
                key={m.id}
                message={m}
                isActiveInspectorTarget={inspectedMessageId === m.id}
                onInspect={() => onInspect(m.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Composer */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-border bg-panel px-6 py-4"
      >
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder="Ask a question about your documents…"
            className="max-h-40 flex-1 resize-none rounded-md border border-border bg-panel-raised px-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-muted/60 focus:border-accent-dim"
          />
          <button
            type="submit"
            disabled={!draft.trim() || isBusy}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-accent text-base transition-opacity disabled:cursor-not-allowed disabled:opacity-30"
            aria-label="Send question"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-3xl text-[10px] text-text-muted">
          Enter to send · Shift+Enter for a new line
        </p>
      </form>
    </main>
  );
}
