import { useState } from "react";
import { Plus, Trash2, MessageSquare, Radio } from "lucide-react";
import { UploadPanel } from "./UploadPanel";

interface SidebarProps {
  sessions: string[];
  activeSession: string;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  backendOnline: boolean | null;
}

export function Sidebar({
  sessions,
  activeSession,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  backendOnline,
}: SidebarProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border bg-panel">
      {/* Brand */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-sm bg-accent-dim/30">
          <span className="font-display text-sm font-semibold text-accent">R</span>
        </div>
        <div className="flex flex-col leading-tight">
          <span className="font-display text-sm font-semibold text-text-primary">
            Retrieval Console
          </span>
          <span className="flex items-center gap-1 text-[10px] text-text-muted">
            <Radio
              className={`h-2.5 w-2.5 ${
                backendOnline === null
                  ? "text-text-muted"
                  : backendOnline
                    ? "text-accent"
                    : "text-danger"
              }`}
            />
            {backendOnline === null
              ? "checking backend…"
              : backendOnline
                ? "backend online"
                : "backend unreachable"}
          </span>
        </div>
      </div>

      {/* Sessions */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <p className="font-display text-xs uppercase tracking-widest text-text-muted">
          Sessions
        </p>
        <button
          onClick={onNewSession}
          className="flex items-center gap-1 rounded-sm px-1.5 py-1 text-xs text-text-muted transition-colors hover:bg-panel-raised hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          New
        </button>
      </div>

      <nav className="flex max-h-56 flex-col gap-0.5 overflow-y-auto px-2 pb-2">
        {sessions.map((id) => (
          <div
            key={id}
            onMouseEnter={() => setHoveredId(id)}
            onMouseLeave={() => setHoveredId(null)}
            className={`group flex items-center gap-2 rounded-sm px-2.5 py-2 text-left text-sm transition-colors ${
              id === activeSession
                ? "bg-accent-dim/20 text-accent"
                : "text-text-muted hover:bg-panel-raised hover:text-text-primary"
            }`}
          >
            <button
              onClick={() => onSelectSession(id)}
              className="flex flex-1 items-center gap-2 overflow-hidden text-left"
            >
              <MessageSquare className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate font-mono text-xs">{id}</span>
            </button>
            {sessions.length > 1 && hoveredId === id && (
              <button
                onClick={() => onDeleteSession(id)}
                className="shrink-0 text-text-muted transition-colors hover:text-danger"
                aria-label={`Delete session ${id}`}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        ))}
      </nav>

      <div className="border-t border-border" />

      {/* Upload / ingestion */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <UploadPanel />
      </div>

      {/* Footer */}
      <div className="border-t border-border px-4 py-3">
        <p className="text-[10px] leading-relaxed text-text-muted">
          Hybrid search (BM25 + vector) → RRF fusion → cross-encoder rerank
        </p>
      </div>
    </aside>
  );
}
