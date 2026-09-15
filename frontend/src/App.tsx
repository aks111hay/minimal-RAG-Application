import { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import { RetrievalInspector } from "./components/RetrievalInspector";
import { sendQuery, checkHealth, clearHistory, ApiError } from "./api/client";
import type { DisplayMessage } from "./types";

function newSessionId(): string {
  return `session-${Math.random().toString(36).slice(2, 8)}`;
}

export default function App() {
  const [sessions, setSessions] = useState<string[]>([newSessionId()]);
  const [activeSession, setActiveSession] = useState<string>(sessions[0]);
  const [messagesBySession, setMessagesBySession] = useState<Record<string, DisplayMessage[]>>({});
  const [inspectedMessageId, setInspectedMessageId] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    checkHealth().then(setBackendOnline);
    const interval = setInterval(() => {
      checkHealth().then(setBackendOnline);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const activeMessages = messagesBySession[activeSession] ?? [];
  const inspectedMessage = activeMessages.find((m) => m.id === inspectedMessageId);

  function updateMessages(sessionId: string, updater: (prev: DisplayMessage[]) => DisplayMessage[]) {
    setMessagesBySession((prev) => ({
      ...prev,
      [sessionId]: updater(prev[sessionId] ?? []),
    }));
  }

  async function handleSend(question: string) {
    const sessionId = activeSession;
    const userMsg: DisplayMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: question,
    };
    const pendingId = `${Date.now()}-assistant`;
    const pendingMsg: DisplayMessage = {
      id: pendingId,
      role: "assistant",
      content: "",
      pending: true,
    };

    updateMessages(sessionId, (prev) => [...prev, userMsg, pendingMsg]);
    setIsBusy(true);

    try {
      const result = await sendQuery(question, sessionId);
      updateMessages(sessionId, (prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                ...m,
                content: result.answer,
                pending: false,
                retrieval: {
                  rewrittenQuery: result.rewritten_query,
                  chunks: result.retrieved_docs,
                },
              }
            : m,
        ),
      );
      setInspectedMessageId(pendingId);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "Couldn't reach the backend. Make sure it's running on the configured URL.";
      updateMessages(sessionId, (prev) =>
        prev.map((m) => (m.id === pendingId ? { ...m, content: msg, pending: false, error: true } : m)),
      );
    } finally {
      setIsBusy(false);
    }
  }

  function handleNewSession() {
    const id = newSessionId();
    setSessions((prev) => [id, ...prev]);
    setActiveSession(id);
    setInspectedMessageId(null);
  }

  async function handleDeleteSession(id: string) {
    try {
      await clearHistory(id);
    } catch {
      // Best-effort server-side cleanup; still remove locally either way.
    }
    setSessions((prev) => prev.filter((s) => s !== id));
    setMessagesBySession((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    if (activeSession === id) {
      setSessions((prev) => {
        const remaining = prev.filter((s) => s !== id);
        const fallback = remaining[0] ?? newSessionId();
        setActiveSession(fallback);
        return remaining.length > 0 ? remaining : [fallback];
      });
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={(id) => {
          setActiveSession(id);
          setInspectedMessageId(null);
        }}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        backendOnline={backendOnline}
      />

      <ChatWindow
        messages={activeMessages}
        onSend={handleSend}
        isBusy={isBusy}
        inspectedMessageId={inspectedMessageId}
        onInspect={(id) => setInspectedMessageId(id)}
      />

      <RetrievalInspector
        rewrittenQuery={inspectedMessage?.retrieval?.rewrittenQuery ?? null}
        chunks={inspectedMessage?.retrieval?.chunks ?? []}
      />
    </div>
  );
}
