import { useRef, useState } from "react";
import { FileText, Loader2, UploadCloud, CheckCircle2, XCircle } from "lucide-react";
import { embedText, uploadPdf } from "../api/client";
import { ApiError } from "../api/client";

type Status =
  | { kind: "idle" }
  | { kind: "loading"; label: string }
  | { kind: "success"; label: string }
  | { kind: "error"; label: string };

export function UploadPanel() {
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [pasteText, setPasteText] = useState("");
  const [pasteId, setPasteId] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setStatus({ kind: "loading", label: `Chunking & embedding "${file.name}"…` });
    try {
      const result = await uploadPdf(file);
      setStatus({ kind: "success", label: result.message });
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Upload failed. Is the backend running?";
      setStatus({ kind: "error", label: msg });
    }
  }

  async function handlePasteSubmit() {
    if (!pasteText.trim()) return;
    const id = pasteId.trim() || `note-${Date.now()}`;
    setStatus({ kind: "loading", label: "Embedding text…" });
    try {
      const result = await embedText(id, pasteText.trim());
      setStatus({ kind: "success", label: result.message });
      setPasteText("");
      setPasteId("");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Embedding failed. Is the backend running?";
      setStatus({ kind: "error", label: msg });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="font-display text-xs uppercase tracking-widest text-text-muted">
        Knowledge base
      </p>

      {/* PDF drop zone */}
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="group flex flex-col items-center justify-center gap-1.5 rounded-md border border-dashed border-border bg-panel-raised px-3 py-5 text-center transition-colors hover:border-accent-dim hover:bg-panel"
      >
        <UploadCloud className="h-5 w-5 text-text-muted transition-colors group-hover:text-accent" />
        <span className="text-xs text-text-muted">
          Drop a <span className="text-text-primary">.pdf</span> or click to upload
        </span>
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
          e.target.value = "";
        }}
      />

      {/* Paste-text quick ingest */}
      <details className="group rounded-md border border-border bg-panel-raised">
        <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2 text-xs text-text-muted">
          <FileText className="h-3.5 w-3.5" />
          Paste raw text instead
        </summary>
        <div className="flex flex-col gap-2 border-t border-border p-3">
          <input
            value={pasteId}
            onChange={(e) => setPasteId(e.target.value)}
            placeholder="doc id (optional)"
            className="rounded-sm border border-border bg-base px-2 py-1.5 font-mono text-xs text-text-primary placeholder:text-text-muted/60 focus:border-accent-dim"
          />
          <textarea
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
            rows={4}
            placeholder="Paste a paragraph or two…"
            className="resize-none rounded-sm border border-border bg-base px-2 py-1.5 text-xs text-text-primary placeholder:text-text-muted/60 focus:border-accent-dim"
          />
          <button
            onClick={handlePasteSubmit}
            disabled={!pasteText.trim()}
            className="self-end rounded-sm bg-accent-dim/30 px-3 py-1 text-xs font-medium text-accent transition-colors hover:bg-accent-dim/50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Embed
          </button>
        </div>
      </details>

      {/* Status */}
      {status.kind !== "idle" && (
        <div
          className={`flex items-start gap-2 rounded-md border px-3 py-2 text-xs animate-fade-in ${
            status.kind === "success"
              ? "border-accent-dim/50 bg-accent-dim/10 text-accent"
              : status.kind === "error"
                ? "border-danger/50 bg-danger/10 text-danger"
                : "border-border bg-panel-raised text-text-muted"
          }`}
        >
          {status.kind === "loading" && <Loader2 className="mt-0.5 h-3.5 w-3.5 shrink-0 animate-spin" />}
          {status.kind === "success" && <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />}
          {status.kind === "error" && <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />}
          <span className="leading-snug">{status.label}</span>
        </div>
      )}
    </div>
  );
}
