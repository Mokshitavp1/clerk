export type QueryMode = 'FAST' | 'DEEP THINKING' | 'AUTO';
export type ExecutedMode = 'FAST' | 'DEEP THINKING';
export type VerificationStatus = 'VERIFIED' | 'UNVERIFIED' | 'INSUFFICIENT';

export interface PageContent {
  page_number: number; // Absolute 1-indexed page number (FR-1.1)
  text: string;
}

export interface LegalCaseRecord {
  case_name: string; // Sanitized basename (FR-1.3)
  display_title: string;
  citation: string;
  jurisdiction: string;
  year: number;
  summary: string;
  summary_mode: 'llm' | 'extractive_fallback'; // FR-1.4
  page_count: number;
  chunk_count: number;
  indexed_at: string;
  pages: PageContent[];
}

export interface LegalChunkRecord {
  chunk_id: string;
  case_name: string;
  page_number: number; // 1-indexed
  chunk_index: number;
  text: string;
  word_count: number;
}

export interface Stage1ShortlistItem {
  case_name: string;
  display_title: string;
  citation: string;
  dense_score: number;
  bm25_score: number;
  hybrid_score: number;
  summary: string;
}

export interface Stage2GradedChunk {
  chunk_id: string;
  case_name: string;
  page_number: number;
  chunk_index: number;
  text: string;
  word_count: number;
  dense_score: number;
  bm25_score: number;
  rerank_score?: number;
  final_score: number;
  passed_floor: boolean; // >= 0.40 relevance_floor (FR-2.4)
  selected_for_prompt: boolean; // Top-4 in Fast, Top-2 per case in Deep
}

export interface AmbiguityWarning {
  detected: boolean;
  top_case?: Stage1ShortlistItem;
  runner_up_case?: Stage1ShortlistItem;
  competing_cases: Stage1ShortlistItem[];
  score_delta: number;
  threshold: number; // 0.10
  explanation: string;
}

export interface CitedPairValidation {
  case_name: string;
  page_number: number;
  exists_in_prompt_chunks: boolean;
  matching_chunk_id?: string;
}

export interface VerificationAudit {
  layer1_citation_match: {
    passed: boolean;
    has_sources_line: boolean;
    cited_pairs: CitedPairValidation[];
    details: string;
  };
  layer1b_body_length: {
    passed: boolean;
    word_count: number;
    min_words: number; // 15 (FR-3.2)
  };
  layer2_llm_groundedness: {
    passed: boolean;
    supported_claims: string[];
    unsupported_claims: string[];
    reasoning: string;
  };
  retry_count: number;
  total_verification_ms: number;
}

export interface PerCaseIsolationResult {
  case_name: string;
  display_title: string;
  passed_verification: boolean;
  status: VerificationStatus;
  answer_section: string;
  citations: { case_name: string; page_number: number }[];
  chunks_used: number;
  drop_reason?: string;
}

export interface CitationItem {
  case_name: string;
  page_number: number;
  snippet: string;
  chunk_id?: string;
}

export interface QueryExecutionResponse {
  id: string;
  query: string;
  requested_mode: QueryMode;
  executed_mode: ExecutedMode;
  auto_routing_reason?: string;
  requires_ambiguity_intervention?: boolean;
  ambiguity: AmbiguityWarning;
  status: VerificationStatus;
  verified: boolean;
  answer: string;
  citations: CitationItem[];
  stage1_shortlist: Stage1ShortlistItem[];
  stage2_chunks: Stage2GradedChunk[];
  dropped_below_floor_count: number;
  verification_audit: VerificationAudit;
  per_case_results?: PerCaseIsolationResult[];
  reranker_enabled: boolean;
  latency_ms: number;
  timestamp: string;
}

export interface StagedPdfFile {
  id: string;
  file_name: string;
  case_name: string;
  size_bytes: number;
  pages: PageContent[];
  status: 'staged' | 'indexing' | 'indexed' | 'error';
  progress_pct?: number;
  status_detail?: string;
}
