import React, { useState } from 'react';
import {
  AlertTriangle,
  Check,
  Copy,
  Download,
  FileSearch,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  ShieldAlert,
  BookOpen,
} from 'lucide-react';
import { QueryExecutionResponse, VerificationStatus } from '../types/clerk.ts';

interface MemorandumViewProps {
  isLoading: boolean;
  activeStep: 1 | 2 | 3;
  response: QueryExecutionResponse | null;
  onSwitchToDeepThinking: (query: string) => void;
  onContinueFastAnyway: (query: string) => void;
  onInspectCitation: (caseName: string, pageNumber: number) => void;
}

export const MemorandumView: React.FC<MemorandumViewProps> = ({
  isLoading,
  activeStep,
  response,
  onSwitchToDeepThinking,
  onContinueFastAnyway,
  onInspectCitation,
}) => {
  const [copied, setCopied] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [dismissedAmbiguityId, setDismissedAmbiguityId] = useState<string | null>(null);

  if (!isLoading && !response) {
    return null;
  }

  const handleCopy = () => {
    if (!response) return;
    navigator.clipboard.writeText(response.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const handleExportMarkdown = () => {
    if (!response) return;
    const content = `# CLERK LEGAL MEMORANDUM\n**Query:** ${response.query}\n**Verification Status:** § ${response.status}\n**Mode:** ${response.executed_mode}\n**Timestamp:** ${response.timestamp}\n\n---\n\n${response.answer}\n`;
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Clerk_Memorandum_${response.query_id}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderTrustBadge = (status: VerificationStatus) => {
    if (status === 'VERIFIED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#EBF0E8] border border-[#4A6741]/35 text-[#4A6741] font-mono-tech text-[10px] font-semibold uppercase tracking-[0.1em]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#4A6741]" />
          § VERIFIED
        </span>
      );
    }
    if (status === 'UNVERIFIED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#F7F1EB] border border-[#DFAD56]/60 text-[#9B6814] font-mono-tech text-[10px] font-semibold uppercase tracking-[0.1em]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#DFAD56]" />
          § UNVERIFIED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#ECEAE6] border border-[#9C9995]/50 text-[#5C5955] font-mono-tech text-[10px] font-semibold uppercase tracking-[0.1em]">
        <span className="w-1.5 h-1.5 rounded-full bg-[#9C9995]" />
        § INSUFFICIENT
      </span>
    );
  };

  // Format markdown paragraphs cleanly in editorial serif & sans
  const renderFormattedMarkdown = (markdownText: string) => {
    const blocks = markdownText.split(/\n\n+/);
    return blocks.map((block, idx) => {
      const trimmed = block.trim();
      if (!trimmed) return null;

      if (trimmed.startsWith('### ')) {
        const headingText = trimmed.replace(/^###\s+/, '');
        return (
          <h3
            key={idx}
            className="font-serif-editorial font-bold text-[20px] leading-[1.25] text-[#342219] mb-3 pb-2 border-b border-[#493628]/12"
          >
            {headingText}
          </h3>
        );
      }

      if (trimmed.startsWith('#### ')) {
        const subHeading = trimmed.replace(/^####\s+/, '');
        const lines = subHeading.split('\n');
        const firstLine = lines[0];
        const restLines = lines.slice(1).join('\n');
        return (
          <div key={idx} className="mb-4">
            <h4
              className="font-serif-editorial font-semibold text-[16.5px] leading-[1.3] text-[#493628] mb-1.5"
              dangerouslySetInnerHTML={{
                __html: firstLine
                  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                  .replace(/\*([^*]+)\*/g, '<em>$1</em>'),
              }}
            />
            {restLines && (
              <p
                className="text-[15px] leading-[1.68] text-[#342219]"
                dangerouslySetInnerHTML={{
                  __html: restLines
                    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*([^*]+)\*/g, '<em>$1</em>'),
                }}
              />
            )}
          </div>
        );
      }

      // Check for numbered or bulleted list
      const lines = trimmed.split('\n');
      if (lines.every((l) => /^(\d+\.|-|\*)\s+/.test(l.trim()))) {
        return (
          <ul key={idx} className="space-y-2 my-3 pl-4 border-l border-[#AB886D]/35">
            {lines.map((line, lIdx) => {
              const cleanLine = line.trim().replace(/^(\d+\.|-|\*)\s+/, '');
              return (
                <li
                  key={lIdx}
                  className="text-[15px] leading-[1.65] text-[#342219]"
                  dangerouslySetInnerHTML={{
                    __html: cleanLine
                      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*([^*]+)\*/g, '<em>$1</em>'),
                  }}
                />
              );
            })}
          </ul>
        );
      }

      return (
        <p
          key={idx}
          className="text-[15px] leading-[1.68] text-[#342219] mb-3.5"
          dangerouslySetInnerHTML={{
            __html: trimmed
              .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
              .replace(/\*([^*]+)\*/g, '<em>$1</em>')
              .replace(/\n/g, '<br />'),
          }}
        />
      );
    });
  };

  const showAmbiguityBanner =
    response?.ambiguity_alert?.detected &&
    response.executed_mode === 'FAST' &&
    dismissedAmbiguityId !== response.query_id;

  const currentCaption = isLoading
    ? activeStep === 1
      ? 'Stage 1 & 2: Querying ChromaDB legal_cases & legal_chunks (Dense BAAI/bge-m3 + BM25)...'
      : activeStep === 2
      ? 'Self-RAG Grading: Filtering passages against relevance_floor >= 0.40 and capping chunks...'
      : '3-Layer Verifier: Validating deterministic citations, body word length (>=15w), and LLM groundedness...'
    : response?.stepper_messages.verify;

  return (
    <div className="mt-6 space-y-5">
      {/* AMBIGUITY ALERT BANNER (Conditional — PRD Section 6.4.4 & FR-2.3) */}
      {showAmbiguityBanner && response.ambiguity_alert && (
        <div className="bg-[#F7F1EB] border border-[#DFAD56] rounded-[10px] p-4 shadow-xs">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-[#B87D1E] shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                <p className="font-serif-editorial font-bold text-[16px] text-[#342219]">
                  Multiple competing precedents detected (Score Δ ={' '}
                  {response.ambiguity_alert.score_delta.toFixed(2)} &le;{' '}
                  {response.ambiguity_alert.threshold.toFixed(2)})
                </p>
                <span className="font-mono-tech text-[9.5px] uppercase tracking-[0.08em] px-2 py-0.5 rounded bg-[#DFAD56]/25 text-[#7A510D]">
                  AMBIGUITY ROUTER ALERT
                </span>
              </div>
              <p className="text-[13.5px] text-[#493628] leading-[1.5] mb-2.5">
                Fast Mode targets only the single highest-scoring case (
                <span className="font-mono-tech font-medium">
                  {response.ambiguity_alert.top_cases[0]?.case_name}
                </span>
                ), which risks omitting competing holdings in{' '}
                <span className="font-mono-tech font-medium">
                  {response.ambiguity_alert.top_cases
                    .slice(1)
                    .map((c) => c.case_name)
                    .join(' & ')}
                </span>
                .
              </p>

              {/* Expandable <details><summary>Explain why</summary> per PRD 6.4.4 */}
              <details className="mb-3.5 text-[12.5px] text-[#493628] bg-[#FDFBF8]/80 rounded border border-[#493628]/15 px-3 py-2">
                <summary className="font-mono-tech text-[11px] font-semibold uppercase tracking-[0.06em] text-[#493628] cursor-pointer select-none">
                  Explain why (Stage 1 Cosine &amp; Hybrid Similarity Breakdown)
                </summary>
                <div className="mt-2 pt-2 border-t border-[#493628]/10 space-y-1.5">
                  <p className="text-xs text-[#806C5D] mb-2">
                    {response.ambiguity_alert.explanation}
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {response.ambiguity_alert.top_cases.map((tc, idx) => (
                      <div
                        key={tc.case_name}
                        className="p-2 rounded bg-[#F1EEE9] border border-[#493628]/12"
                      >
                        <p className="font-mono-tech text-[10px] font-semibold text-[#342219] truncate">
                          #{idx + 1} {tc.case_name}
                        </p>
                        <p className="font-mono-tech text-[10px] text-[#806C5D] mt-0.5">
                          Hybrid: <strong>{tc.hybrid_score.toFixed(2)}</strong> (Dense:{' '}
                          {tc.dense_score.toFixed(2)} | BM25: {tc.bm25_score.toFixed(2)})
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </details>

              {/* Dual Action Buttons per PRD 6.4.4 */}
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => onSwitchToDeepThinking(response.query)}
                  className="px-4 py-2 rounded-[6px] bg-[#493628] hover:bg-[#342219] text-[#FDFBF8] font-mono-tech text-[11px] font-semibold uppercase tracking-[0.07em] transition-colors cursor-pointer"
                >
                  Switch to Deep Thinking
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setDismissedAmbiguityId(response.query_id);
                    onContinueFastAnyway(response.query);
                  }}
                  className="px-3.5 py-2 rounded-[6px] bg-[#FDFBF8] hover:bg-[#E4E0E1] text-[#493628] border border-[#493628]/25 font-mono-tech text-[11px] font-medium uppercase tracking-[0.06em] transition-colors cursor-pointer"
                >
                  Continue with Fast anyway
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Auto Mode Routing Notice */}
      {!isLoading && response?.auto_routed_reason && (
        <div className="px-3.5 py-2 rounded-lg bg-[#FDFBF8] border border-[#493628]/15 flex items-center justify-between gap-2 text-xs text-[#493628]">
          <span className="font-mono-tech text-[10px] uppercase tracking-[0.07em] text-[#AB886D] font-semibold shrink-0">
            AUTO ROUTER &rarr; {response.executed_mode}
          </span>
          <span className="text-[12.5px] text-[#806C5D] truncate">
            {response.auto_routed_reason}
          </span>
        </div>
      )}

      {/* LIVE PIPELINE STEPPER (RETRIEVE -> GRADE -> VERIFY — PRD Section 6.4.5) */}
      <div className="bg-[#FDFBF8] border border-[#493628]/15 rounded-[10px] px-5 py-4">
        <div className="flex items-center justify-between gap-2">
          {/* Step 1: RETRIEVE */}
          <div className="flex items-center gap-2">
            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center font-mono-tech text-[10px] font-semibold ${
                !isLoading || activeStep > 1
                  ? 'bg-[#EBF0E8] text-[#4A6741] border border-[#4A6741]/35'
                  : 'bg-[#493628] text-[#FDFBF8]'
              }`}
            >
              {!isLoading || activeStep > 1 ? <Check className="w-3.5 h-3.5" /> : '●'}
            </span>
            <span className="font-mono-tech text-[11px] font-semibold uppercase tracking-[0.09em] text-[#342219]">
              1 RETRIEVE
            </span>
          </div>

          <div
            className={`flex-1 h-[2px] mx-2 ${
              !isLoading || activeStep >= 2 ? 'bg-[#4A6741]/45' : 'bg-[#D6C0B3]/50'
            }`}
          />

          {/* Step 2: GRADE */}
          <div className="flex items-center gap-2">
            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center font-mono-tech text-[10px] font-semibold ${
                !isLoading || activeStep > 2
                  ? 'bg-[#EBF0E8] text-[#4A6741] border border-[#4A6741]/35'
                  : activeStep === 2
                  ? 'bg-[#493628] text-[#FDFBF8]'
                  : 'bg-[#F1EEE9] text-[#806C5D] border border-[#493628]/15'
              }`}
            >
              {!isLoading || activeStep > 2 ? (
                <Check className="w-3.5 h-3.5" />
              ) : activeStep === 2 ? (
                '●'
              ) : (
                '2'
              )}
            </span>
            <span className="font-mono-tech text-[11px] font-semibold uppercase tracking-[0.09em] text-[#342219]">
              2 GRADE
            </span>
          </div>

          <div
            className={`flex-1 h-[2px] mx-2 ${
              !isLoading || activeStep >= 3 ? 'bg-[#4A6741]/45' : 'bg-[#D6C0B3]/50'
            }`}
          />

          {/* Step 3: VERIFY */}
          <div className="flex items-center gap-2">
            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center font-mono-tech text-[10px] font-semibold ${
                !isLoading
                  ? response?.verified
                    ? 'bg-[#EBF0E8] text-[#4A6741] border border-[#4A6741]/35'
                    : 'bg-[#ECEAE6] text-[#5C5955] border border-[#9C9995]/50'
                  : activeStep === 3
                  ? 'bg-[#493628] text-[#FDFBF8]'
                  : 'bg-[#F1EEE9] text-[#806C5D] border border-[#493628]/15'
              }`}
            >
              {!isLoading ? (
                response?.verified ? (
                  <Check className="w-3.5 h-3.5" />
                ) : (
                  '!'
                )
              ) : activeStep === 3 ? (
                '●'
              ) : (
                '3'
              )}
            </span>
            <span className="font-mono-tech text-[11px] font-semibold uppercase tracking-[0.09em] text-[#342219]">
              3 VERIFY
            </span>
          </div>
        </div>

        {/* Live Stepper Diagnostic Caption */}
        <div className="mt-3 pt-2.5 border-t border-[#493628]/10 flex flex-wrap items-center justify-between gap-2 text-xs text-[#806C5D]">
          <p className="font-serif-editorial italic text-[13.5px] text-[#493628]">
            &ldquo;{currentCaption}&rdquo;
          </p>
          {!isLoading && response && (
            <span className="font-mono-tech text-[10px] text-[#806C5D]">
              {response.latency_ms}ms &middot; {response.executed_mode}
            </span>
          )}
        </div>
      </div>

      {/* SYNTHESIZED MEMORANDUM CONTAINER (PRD Section 6.4.6) */}
      {!isLoading && response && (
        <article className="bg-[#FDFBF8] border border-[#493628]/18 rounded-[12px] p-6 sm:p-8 shadow-xs">
          {/* Top Bar: Trust Status Badge & Actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-5 border-b border-[#493628]/12">
            <div className="flex items-center gap-2.5">
              {renderTrustBadge(response.status)}
              <span className="font-mono-tech text-[10px] uppercase tracking-[0.07em] text-[#806C5D]">
                {response.executed_mode === 'DEEP THINKING'
                  ? 'PER-CASE ISOLATED SYNTHESIS (TOP-2/CASE)'
                  : 'SINGLE-AUTHORITY SYNTHESIS (TOP-4 CHUNKS)'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="px-2.5 py-1 rounded border border-[#493628]/18 hover:bg-[#F1EEE9] text-[#493628] font-mono-tech text-[10px] uppercase tracking-[0.06em] flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3 h-3 text-[#4A6741]" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'COPIED' : 'COPY'}</span>
              </button>
              <button
                type="button"
                onClick={handleExportMarkdown}
                className="px-2.5 py-1 rounded border border-[#493628]/18 hover:bg-[#F1EEE9] text-[#493628] font-mono-tech text-[10px] uppercase tracking-[0.06em] flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <Download className="w-3 h-3" />
                <span>EXPORT .MD</span>
              </button>
            </div>
          </div>

          {/* Memorandum Body Content */}
          <div className="prose-legal">
            {response.verified ? (
              renderFormattedMarkdown(response.body_markdown)
            ) : (
              <div className="py-4 px-4 rounded-lg bg-[#ECEAE6]/55 border border-[#9C9995]/40 text-[#342219]">
                <div className="flex items-start gap-3">
                  <ShieldAlert className="w-5 h-5 text-[#806C5D] shrink-0 mt-0.5" />
                  <div>
                    <p className="font-serif-editorial font-semibold text-[16px] text-[#342219] mb-1">
                      {response.answer}
                    </p>
                    <p className="text-[13px] text-[#806C5D]">
                      Clerk enforces a strict fail-closed verification contract (FR-3.4). Claims
                      lacking deterministic `(Case_Name, Page X)` metadata or falling below the{' '}
                      <code className="font-mono-tech">0.40</code> Self-RAG relevance floor are
                      withheld from synthesis.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Explicit Sources: Footer with Interactive Visual Citation Inspector Triggers */}
          {response.sources_line && (
            <div className="mt-6 pt-4 border-t border-[#493628]/15">
              <p className="font-mono-tech text-[12px] font-medium text-[#493628] mb-3">
                {response.sources_line}
              </p>

              {response.citations.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono-tech text-[9.5px] uppercase tracking-[0.09em] text-[#806C5D] mr-1 flex items-center gap-1">
                    <BookOpen className="w-3 h-3 text-[#AB886D]" />
                    INSPECT SOURCE PAGES:
                  </span>
                  {response.citations.map((cit, idx) => (
                    <button
                      key={`${cit.case_name}-${cit.page_number}-${idx}`}
                      type="button"
                      onClick={() => onInspectCitation(cit.case_name, cit.page_number)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#F1EEE9] hover:bg-[#E4E0E1] border border-[#493628]/20 text-[#342219] font-mono-tech text-[10.5px] transition-colors cursor-pointer"
                    >
                      <FileSearch className="w-3 h-3 text-[#AB886D]" />
                      <span>
                        {cit.case_name}, Page {cit.page_number}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 3-Layer Verification & Self-RAG Audit Drawer Toggle */}
          <div className="mt-5 pt-3 border-t border-[#493628]/10">
            <button
              type="button"
              onClick={() => setShowDiagnostics((prev) => !prev)}
              className="w-full flex items-center justify-between text-left font-mono-tech text-[10.5px] uppercase tracking-[0.08em] text-[#806C5D] hover:text-[#342219] py-1 transition-colors cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-[#AB886D]" />
                <span>
                  3-LAYER VERIFICATION &amp; SELF-RAG PIPELINE AUDIT (
                  {response.stage2_chunks.filter((c) => c.selected_for_context).length} CHUNKS USED
                  &middot; {response.dropped_below_floor_count} DROPPED &lt; 0.40)
                </span>
              </span>
              {showDiagnostics ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {showDiagnostics && (
              <div className="mt-3 pt-3 border-t border-[#493628]/10 space-y-4 text-xs">
                {/* 3-Layer Verifier Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Layer 1 */}
                  <div className="p-3 rounded-lg bg-[#F1EEE9]/80 border border-[#493628]/12">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono-tech text-[10px] font-semibold uppercase text-[#342219]">
                        LAYER 1: CITATION MATCH
                      </span>
                      <span
                        className={`font-mono-tech text-[9.5px] font-semibold px-1.5 py-0.5 rounded ${
                          response.verification_report.layer1_deterministic_citations.passed
                            ? 'bg-[#EBF0E8] text-[#4A6741]'
                            : 'bg-[#ECEAE6] text-[#6E6B66]'
                        }`}
                      >
                        {response.verification_report.layer1_deterministic_citations.passed
                          ? 'PASS'
                          : 'FAIL'}
                      </span>
                    </div>
                    <p className="text-[11.5px] text-[#806C5D] leading-snug">
                      {response.verification_report.layer1_deterministic_citations.passed
                        ? `Verified ${response.verification_report.layer1_deterministic_citations.extracted_citations.length} cited (Case_Name, Page X) pair(s) against prompt chunk metadata.`
                        : response.verification_report.layer1_deterministic_citations
                            .failure_reason}
                    </p>
                  </div>

                  {/* Layer 1b */}
                  <div className="p-3 rounded-lg bg-[#F1EEE9]/80 border border-[#493628]/12">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono-tech text-[10px] font-semibold uppercase text-[#342219]">
                        LAYER 1B: BODY LENGTH
                      </span>
                      <span
                        className={`font-mono-tech text-[9.5px] font-semibold px-1.5 py-0.5 rounded ${
                          response.verification_report.layer1b_body_length.passed
                            ? 'bg-[#EBF0E8] text-[#4A6741]'
                            : 'bg-[#ECEAE6] text-[#6E6B66]'
                        }`}
                      >
                        {response.verification_report.layer1b_body_length.word_count}w / &ge;
                        {response.verification_report.layer1b_body_length.min_required}w
                      </span>
                    </div>
                    <p className="text-[11.5px] text-[#806C5D] leading-snug">
                      Substantive body prior to <code className="font-mono-tech">Sources:</code>{' '}
                      contains {response.verification_report.layer1b_body_length.word_count} words
                      (minimum contract threshold: 15 words).
                    </p>
                  </div>

                  {/* Layer 2 */}
                  <div className="p-3 rounded-lg bg-[#F1EEE9]/80 border border-[#493628]/12">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono-tech text-[10px] font-semibold uppercase text-[#342219]">
                        LAYER 2: GROUNDEDNESS
                      </span>
                      <span
                        className={`font-mono-tech text-[9.5px] font-semibold px-1.5 py-0.5 rounded ${
                          response.verification_report.layer2_llm_groundedness.passed
                            ? 'bg-[#EBF0E8] text-[#4A6741]'
                            : 'bg-[#ECEAE6] text-[#6E6B66]'
                        }`}
                      >
                        {response.verification_report.layer2_llm_groundedness.passed
                          ? 'PASS'
                          : 'FAIL'}
                      </span>
                    </div>
                    <p className="text-[11.5px] text-[#806C5D] leading-snug">
                      {response.verification_report.layer2_llm_groundedness.reasoning}
                    </p>
                  </div>
                </div>

                {/* Stage 1 & Stage 2 Retrieval Scores */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-[#F1EEE9]/50 border border-[#493628]/12">
                    <p className="font-mono-tech text-[10px] font-semibold uppercase tracking-[0.07em] text-[#493628] mb-2">
                      STAGE 1: legal_cases SHORTLIST
                    </p>
                    <div className="space-y-1.5">
                      {response.stage1_shortlist.map((c, i) => (
                        <div
                          key={c.case_name}
                          className="flex items-center justify-between text-[11.5px] py-1 border-b border-[#493628]/8 last:border-0"
                        >
                          <span className="font-medium text-[#342219] truncate pr-2">
                            {i + 1}. {c.case_name}
                          </span>
                          <span className="font-mono-tech text-[10.5px] text-[#493628] shrink-0">
                            Score: <strong>{c.hybrid_score.toFixed(2)}</strong> (D:{c.dense_score.toFixed(2)}{' '}
                            B:{c.bm25_score.toFixed(2)})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-[#F1EEE9]/50 border border-[#493628]/12">
                    <p className="font-mono-tech text-[10px] font-semibold uppercase tracking-[0.07em] text-[#493628] mb-2">
                      STAGE 2: legal_chunks SELF-RAG GRADING (FLOOR &ge; 0.40)
                    </p>
                    <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                      {response.stage2_chunks.map((ch) => (
                        <div
                          key={ch.chunk_id}
                          className="flex items-center justify-between text-[11.5px] py-1 border-b border-[#493628]/8 last:border-0"
                        >
                          <button
                            type="button"
                            onClick={() => onInspectCitation(ch.case_name, ch.page_number)}
                            className="text-left font-mono-tech text-[10.5px] text-[#342219] hover:underline truncate pr-2 cursor-pointer"
                          >
                            {ch.case_name} (p.{ch.page_number})
                          </button>
                          <div className="flex items-center gap-2 shrink-0">
                            <span className="font-mono-tech text-[10.5px] text-[#493628]">
                              {ch.relevance_score.toFixed(2)}
                            </span>
                            <span
                              className={`font-mono-tech text-[9px] px-1.5 py-0.5 rounded uppercase ${
                                ch.selected_for_context
                                  ? 'bg-[#EBF0E8] text-[#4A6741]'
                                  : ch.passed_floor
                                  ? 'bg-[#F7F1EB] text-[#9B6814]'
                                  : 'bg-[#ECEAE6] text-[#6E6B66]'
                              }`}
                            >
                              {ch.selected_for_context
                                ? 'CAPPED IN CONTEXT'
                                : ch.passed_floor
                                ? 'PASSED FLOOR'
                                : 'DROPPED <0.4'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </article>
      )}
    </div>
  );
};
