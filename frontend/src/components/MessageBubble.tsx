import { AlertCircle, Loader2, Sparkles } from "lucide-react";
import type { DisplayMessage } from "../types";

interface MessageBubbleProps {
  message: DisplayMessage;
  isActiveInspectorTarget: boolean;
  onInspect: () => void;
}

export function MessageBubble({ message, isActiveInspectorTarget, onInspect }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex animate-fade-in ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[75%] flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}>
        <div className="flex items-center gap-1.5 px-1 text-[10px] uppercase tracking-wide text-text-muted">
          {!isUser && <Sparkles className="h-2.5 w-2.5" />}
          {isUser ? "You" : "Assistant"}
        </div>

        <div
          className={`rounded-lg px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-accent-dim/25 text-text-primary"
              : message.error
                ? "border border-danger/40 bg-danger/10 text-danger"
                : "border border-border bg-panel-raised text-text-primary"
          }`}
        >
          {message.pending ? (
            <span className="flex items-center gap-2 text-text-muted">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Retrieving & generating…
            </span>
          ) : message.error ? (
            <span className="flex items-center gap-2">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              {message.content}
            </span>
          ) : (
            <span className="whitespace-pre-wrap">{message.content}</span>
          )}
        </div>

        {!isUser && !message.pending && !message.error && message.retrieval && (
          <button
            onClick={onInspect}
            className={`px-1 text-[10px] font-mono transition-colors ${
              isActiveInspectorTarget
                ? "text-accent"
                : "text-text-muted hover:text-accent"
            }`}
          >
            {message.retrieval.chunks.length > 0
              ? `view ${message.retrieval.chunks.length} retrieved chunk${message.retrieval.chunks.length === 1 ? "" : "s"} →`
              : "no chunks retrieved →"}
          </button>
        )}
      </div>
    </div>
  );
}
