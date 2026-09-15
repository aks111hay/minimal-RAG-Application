export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface RetrievedChunk {
  id: string;
  text: string;
  source: string | null;
  score: number | null;
}

export interface QueryResponse {
  answer: string;
  retrieved_docs: RetrievedChunk[];
  rewritten_query: string | null;
  session_id: string;
}

export interface IngestResponse {
  status: string;
  message: string;
  chunks_created: number;
}

export interface HistoryResponse {
  session_id: string;
  messages: ChatMessage[];
}

/** A chat message as rendered in the UI, with local-only bookkeeping. */
export interface DisplayMessage extends ChatMessage {
  id: string;
  pending?: boolean;
  error?: boolean;
  retrieval?: {
    rewrittenQuery: string | null;
    chunks: RetrievedChunk[];
  };
}
