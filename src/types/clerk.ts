export type RetrievalMode = 'FAST' | 'DEEP THINKING' | 'AUTO';

export type VerificationStatus = 'VERIFIED' | 'UNVERIFIED' | 'INSUFFICIENT';

export interface LegalPageInput {
  page_number: number; // 1-indexed per FR-1.1
  text: string;
}

export interface LegalDocumentInput {
  file_name: string;
  pages: LegalPageInput[];
}

export interface LegalCaseRecord {
  case_name: string; // Sanitized basename per FR-1.3
  file_name: string;
  page_count: number;
  chunk_count: number;
  summary: string;
  summary_mode: 'llm' | 'extractive_fallback';
  indexed_at: string;
}

export interface LegalChunkRecord {
  chunk_id: string;
  case_name: string;
  page_number: number; // 1-indexed
  chunk_index: number;
  text: string;
  word_count: number;
}

export interface ScoredCaseCandidate {
  case_name: string;
  summary: string;
  dense_score: number;
  bm25_score: number;
  hybrid_score: number;
}

export interface ScoredChunkCandidate {
  chunk_id: string;
  case_name: string;
  page_number: number;
  chunk_index: number;
  text: string;
  word_count: number;
  dense_score: number;
  bm25_score: number;
  rerank_score?: number;
  relevance_score: number;
  passed_floor: boolean; // >= 0.40 relevance_floor
  selected_for_context: boolean; // Top-4 in Fast, Top-2 per case in Deep
}

export interface CitedAuthority {
  case_name: string;
  page_number: number;
  valid_in_context: boolean;
  matched_chunk_id?: string;
}

export interface LayerVerificationReport {
  layer1_deterministic_citations: {
    passed: boolean;
    extracted_citations: CitedAuthority[];
    failure_reason?: string;
  };
  layer1b_body_length: {
    passed: boolean;
    word_count: number;
    min_required: number; // 15 words (BODY_MIN_WORDS)
  };
  layer2_llm_groundedness: {
    passed: boolean;
    supported_claims: string[];
    unsupported_claims: string[];
    reasoning: string;
  };
  retry_attempted: boolean;
}

export interface PerCaseIsolationResult {
  case_name: string;
  score: number;
  verified: boolean;
  status: VerificationStatus;
  section_markdown: string;
  citations: CitedAuthority[];
  chunks_used: ScoredChunkCandidate[];
}

export interface AmbiguityAlert {
  detected: boolean;
  score_delta: number;
  threshold: number; // 0.1
  top_cases: ScoredCaseCandidate[];
  explanation: string;
}

export interface QueryExecutionResponse {
  query_id: string;
  query: string;
  requested_mode: RetrievalMode;
  executed_mode: 'FAST' | 'DEEP THINKING';
  auto_routed_reason?: string;
  ambiguity_alert?: AmbiguityAlert;
  requires_ambiguity_confirmation?: boolean;
  status: VerificationStatus;
  verified: boolean;
  answer: string; // Full synthesized memorandum including Sources: footer or exact fallback string
  body_markdown: string;
  sources_line: string;
  citations: CitedAuthority[];
  stage1_shortlist: ScoredCaseCandidate[];
  stage2_chunks: ScoredChunkCandidate[];
  dropped_below_floor_count: number;
  verification_report: LayerVerificationReport;
  per_case_results?: PerCaseIsolationResult[];
  stepper_messages: {
    retrieve: string;
    grade: string;
    verify: string;
  };
  latency_ms: number;
  timestamp: string;
  contract_spec: {
    llm_model: string;
    embedding_model: string;
    chroma_collections: string[];
    chunk_parameters: { target_words: number; overlap_words: number };
    routing: { ambiguity_threshold: number; relevance_floor: number };
    reranker_enabled: boolean;
    ollama_base_url?: string;
    ollama_connected?: boolean;
  };
}

export interface OllamaHealthStatus {
  connected: boolean;
  base_url: string;
  target_model: string;
  model_available: boolean;
  installed_models: string[];
  guidance?: string;
}

export interface HistoryItem {
  id: string;
  query: string;
  status: VerificationStatus;
  requested_mode: RetrievalMode;
  executed_mode: 'FAST' | 'DEEP THINKING';
  timestamp: string;
  response: QueryExecutionResponse;
}
