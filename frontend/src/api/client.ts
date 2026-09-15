import type { HistoryResponse, IngestResponse, QueryResponse } from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // body wasn't JSON; fall back to statusText
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function sendQuery(
  question: string,
  sessionId: string,
): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  return handle<QueryResponse>(res);
}

export async function getHistory(sessionId: string): Promise<HistoryResponse> {
  const res = await fetch(`${BASE_URL}/v1/history/${encodeURIComponent(sessionId)}`);
  return handle<HistoryResponse>(res);
}

export async function clearHistory(sessionId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/v1/history/${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
  });
  await handle(res);
}

export async function embedText(id: string, text: string): Promise<IngestResponse> {
  const res = await fetch(`${BASE_URL}/v1/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, text }),
  });
  return handle<IngestResponse>(res);
}

export async function uploadPdf(file: File): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/v1/embed-upload`, {
    method: "POST",
    body: formData,
  });
  return handle<IngestResponse>(res);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
