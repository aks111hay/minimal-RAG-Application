import { Search, GitBranch, FileText, Inbox } from "lucide-react";
import type { RetrievedChunk } from "../types";

interface RetrievalInspectorProps {
  rewrittenQuery: string | null;
  chunks: RetrievedChunk[];
}

function scoreToPercent(score: number | null, max: number): number {
  if (score === null || max <= 0) return 0;
  // Cross-encoder logits aren't bounded [0,1]; normalize against the
  // strongest score in this result set purely for the bar visualization.
  return Math.max(4, Math.min(100, (score / max) * 100));
}

export function RetrievalInspector({ rewrittenQuery, chunks }: RetrievalInspectorProps) {
  const maxScore = Math.max(1e-6, ...chunks.map((c) => c.score ?? 0));

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border bg-panel">
      <div className="border-b border-border px-4 py-4">
        <p className="font-display text-xs uppercase tracking-widest text-text-muted">
          Retrieval Inspector
        </p>
        <p className="mt-1 text-[10px] leading-relaxed text-text-muted">
          What the model actually saw before answering.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {chunks.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-10 text-center text-text-muted">
            <Inbox className="h-6 w-6" />
            <p className="text-xs">
              Ask a question to see the retrieval pipeline for that turn.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {rewrittenQuery && (
              <div className="rounded-md border border-accent-dim/40 bg-accent-dim/10 px-3 py-2.5">
                <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wide text-accent">
                  <GitBranch className="h-3 w-3" />
                  Query rewritten for retrieval
                </div>
                <p className="mt-1.5 font-mono text-xs leading-snug text-text-primary">
                  {rewrittenQuery}
                </p>
              </div>
            )}

            <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wide text-text-muted">
              <Search className="h-3 w-3" />
              Top {chunks.length} chunk{chunks.length === 1 ? "" : "s"} after hybrid search + rerank
            </div>

            <ol className="flex flex-col gap-3">
              {chunks.map((chunk, idx) => (
                <li
                  key={chunk.id}
                  className="rounded-md border border-border bg-panel-raised p-3"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 overflow-hidden">
                      <span className="shrink-0 font-mono text-[10px] text-text-muted">
                        #{idx + 1}
                      </span>
                      <FileText className="h-3 w-3 shrink-0 text-text-muted" />
                      <span className="truncate font-mono text-[10px] text-text-muted">
                        {chunk.id}
                      </span>
                    </div>
                    {chunk.score !== null && (
                      <span className="shrink-0 font-mono text-[10px] text-highlight">
                        {chunk.score.toFixed(3)}
                      </span>
                    )}
                  </div>

                  {/* Rerank score bar */}
                  <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-base">
                    <div
                      className="h-full rounded-full bg-highlight/70"
                      style={{ width: `${scoreToPercent(chunk.score, maxScore)}%` }}
                    />
                  </div>

                  <p className="mt-2 line-clamp-4 text-xs leading-relaxed text-text-muted">
                    {chunk.text}
                  </p>

                  {chunk.source && (
                    <p className="mt-1.5 truncate font-mono text-[10px] text-text-muted/70">
                      source: {chunk.source}
                    </p>
                  )}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </aside>
  );
}
