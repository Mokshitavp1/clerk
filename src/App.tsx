import React, { useEffect, useState } from 'react';
import { X, Database } from 'lucide-react';
import { TopNavBar } from './components/TopNavBar.tsx';
import { SidebarDossier } from './components/SidebarDossier.tsx';
import { MemorandumView } from './components/MemorandumView.tsx';
import { CitationInspectorModal } from './components/CitationInspectorModal.tsx';
import {
  HistoryItem,
  LegalCaseRecord,
  OllamaHealthStatus,
  QueryExecutionResponse,
  RetrievalMode,
} from './types/clerk.ts';

const PRESET_QUERIES: Array<{ label: string; query: string; suggestedMode: RetrievalMode }> = [
  {
    label: 'Delaware Corporate Veil (Fast Dominance)',
    query:
      'What is the standard for piercing the corporate veil in Delaware regarding undercapitalization?',
    suggestedMode: 'FAST',
  },
  {
    label: 'Section 74 Liquidated Damages (Competing Precedents)',
    query: 'What is the test for liquidated damages under Section 74 of the Contract Act?',
    suggestedMode: 'FAST',
  },
  {
    label: 'NY Medical Malpractice CPLR § 214-a',
    query: 'Statute of limitations for medical malpractice in New York',
    suggestedMode: 'FAST',
  },
  {
    label: 'Chevron Deference (Fail-Closed Insufficient)',
    query: 'Chevron deference standard after Loper Bright Enterprises',
    suggestedMode: 'AUTO',
  },
];

export default function App() {
  const [cases, setCases] = useState<LegalCaseRecord[]>([]);
  const [totalChunks, setTotalChunks] = useState<number>(0);
  const [rerankerEnabled, setRerankerEnabled] = useState<boolean>(false);
  const [ollamaHealth, setOllamaHealth] = useState<OllamaHealthStatus | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);

  const [queryText, setQueryText] = useState<string>('');
  const [mode, setMode] = useState<RetrievalMode>('FAST');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeStep, setActiveStep] = useState<1 | 2 | 3>(1);
  const [currentResponse, setCurrentResponse] = useState<QueryExecutionResponse | null>(null);

  const [inspectTarget, setInspectTarget] = useState<{
    caseName: string;
    pageNumber?: number;
  } | null>(null);
  const [showContractModal, setShowContractModal] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/status')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.cases)) {
          setCases(data.cases);
        }
        setTotalChunks(data.total_chunks || 0);
        setRerankerEnabled(Boolean(data.reranker_enabled));
        if (data.ollama) {
          setOllamaHealth(data.ollama);
        }
        if (Array.isArray(data.initial_history)) {
          setHistory(data.initial_history);
        }
      })
      .catch((err) => console.error('Failed to fetch initial status:', err));
  }, []);

  const executeLegalQuery = async (
    targetQuery: string,
    targetMode: RetrievalMode,
    forceFast: boolean = false
  ) => {
    const trimmed = targetQuery.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setActiveStep(1);

    const step2Timer = setTimeout(() => setActiveStep(2), 280);
    const step3Timer = setTimeout(() => setActiveStep(3), 580);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: trimmed,
          mode: targetMode,
          forceFast,
        }),
      });

      const data: QueryExecutionResponse = await res.json();
      setCurrentResponse(data);

      const newHistoryItem: HistoryItem = {
        id: data.query_id,
        query: data.query,
        status: data.status,
        requested_mode: data.requested_mode,
        executed_mode: data.executed_mode,
        timestamp: data.timestamp,
        response: data,
      };

      setHistory((prev) => {
        const filtered = prev.filter(
          (h) => h.query.toLowerCase() !== data.query.toLowerCase()
        );
        return [newHistoryItem, ...filtered];
      });
      setActiveHistoryId(data.query_id);
    } catch (err) {
      console.error('Query execution error:', err);
    } finally {
      clearTimeout(step2Timer);
      clearTimeout(step3Timer);
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeLegalQuery(queryText, mode, false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      executeLegalQuery(queryText, mode, false);
    }
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setActiveHistoryId(item.id);
    setQueryText(item.query);
    setMode(item.requested_mode);
    setCurrentResponse(item.response);
  };

  const handleDeleteCase = async (caseName: string) => {
    try {
      const res = await fetch(`/api/cases/${encodeURIComponent(caseName)}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      setCases(data.cases || []);
      setTotalChunks(data.total_chunks || 0);
    } catch (err) {
      console.error(err);
    }
  };

  const handleClearCases = async () => {
    try {
      const res = await fetch('/api/cases/clear', { method: 'POST' });
      const data = await res.json();
      setCases(data.cases || []);
      setTotalChunks(data.total_chunks || 0);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRestoreDefaultCases = async () => {
    try {
      const res = await fetch('/api/cases/restore', { method: 'POST' });
      const data = await res.json();
      setCases(data.cases || []);
      setTotalChunks(data.total_chunks || 0);
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleReranker = async () => {
    try {
      const res = await fetch('/api/reranker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !rerankerEnabled }),
      });
      const data = await res.json();
      setRerankerEnabled(Boolean(data.reranker_enabled));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F1EEE9] text-[#342219]">
      {/* 1. Global Fixed Top Navigation Bar */}
      <TopNavBar
        totalCases={cases.length}
        totalChunks={totalChunks}
        rerankerEnabled={rerankerEnabled}
        onToggleReranker={handleToggleReranker}
        onOpenContractModal={() => setShowContractModal(true)}
      />

      {/* Main Split Workspace: Fixed Sidebar (290px) + Primary Canvas */}
      <div className="flex-1 flex flex-col md:flex-row min-h-[calc(100vh-62px)]">
        {/* 2. Sidebar: Document Dossier & Knowledge Base */}
        <SidebarDossier
          cases={cases}
          history={history}
          activeHistoryId={activeHistoryId}
          onSelectHistory={handleSelectHistory}
          onDocumentsIndexed={(updatedCases) => {
            setCases(updatedCases);
            fetch('/api/status')
              .then((r) => r.json())
              .then((d) => setTotalChunks(d.total_chunks || 0));
          }}
          onDeleteCase={handleDeleteCase}
          onClearCases={handleClearCases}
          onRestoreDefaultCases={handleRestoreDefaultCases}
          onInspectCase={(caseName, pageNumber) =>
            setInspectTarget({ caseName, pageNumber })
          }
        />

        {/* 3. Primary Working Canvas (Centered 890px max-width) */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-10 md:py-12">
          <div className="max-w-[890px] mx-auto">
            {/* Hero Title & Subtitle matching screenshot & PRD */}
            <div className="text-center mb-6">
              <h1 className="font-serif-editorial font-bold text-[38px] sm:text-[45px] leading-[1.08] tracking-[-0.035em] text-[#493628] mb-3">
                Ask a Legal Question
              </h1>
              <p className="font-serif-editorial text-[16px] sm:text-[17px] leading-[1.55] text-[#806C5D] max-w-[650px] mx-auto">
                Enter your query, cite specific statutes, or describe a fact pattern. The system
                will retrieve relevant case law and synthesize a memorandum.
              </p>
            </div>

            {/* Mode Picker: Three-Pill Segmented Control matching screenshot */}
            <div className="flex items-center justify-center gap-2.5 mb-6">
              {(['FAST', 'DEEP THINKING', 'AUTO'] as RetrievalMode[]).map((m) => {
                const isActive = mode === m;
                return (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setMode(m)}
                    className={`px-4 py-2 rounded-[7px] font-serif-editorial text-[12.5px] font-semibold uppercase tracking-[0.04em] transition-all cursor-pointer border ${
                      isActive
                        ? 'bg-[#9E7B60] text-[#FDFBF8] border-[#8A684D] shadow-xs'
                        : 'bg-[#E6E2DD] text-[#342219] border-[#CFC7BF] hover:bg-[#DDD8D2]'
                    }`}
                  >
                    {m}
                  </button>
                );
              })}
            </div>

            {/* Query Composer Card matching screenshot */}
            <form
              onSubmit={handleFormSubmit}
              className="bg-[#FDFBF8] border border-[#493628]/14 rounded-[12px] p-5 sm:p-6 shadow-[0_2px_10px_rgba(73,54,40,0.04)]"
            >
              <div className="mb-4">
                <textarea
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  rows={5}
                  placeholder="E.g., What is the standard for piercing the corporate veil in Delaware regarding undercapitalization?"
                  className="w-full min-h-[148px] p-4 rounded-[4px] bg-[#FDFBF8] border border-[#493628]/15 focus:border-[#AB886D] focus:outline-none text-[15.5px] leading-[1.6] text-[#342219] placeholder:font-serif-editorial placeholder:italic placeholder:text-[#806C5D]/85 resize-y"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !queryText.trim()}
                className="w-full h-[44px] rounded-[6px] bg-[#493628] hover:bg-[#342219] active:translate-y-[1px] disabled:opacity-55 text-[#FDFBF8] font-serif-editorial font-semibold text-[13.5px] uppercase tracking-[0.08em] flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <span>{isLoading ? 'SYNTHESIZING & VERIFYING...' : 'RETRIEVE \u2192'}</span>
              </button>

              {/* Quick Sample Legal Inquiries for Instant Testing of PRD Scenarios */}
              <div className="mt-3.5 pt-3 border-t border-[#493628]/10 flex flex-wrap items-center gap-1.5">
                <span className="font-mono-tech text-[9.5px] uppercase tracking-[0.08em] text-[#806C5D] mr-1">
                  SAMPLE INQUIRIES:
                </span>
                {PRESET_QUERIES.map((preset) => (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => {
                      setQueryText(preset.query);
                      setMode(preset.suggestedMode);
                      executeLegalQuery(preset.query, preset.suggestedMode, false);
                    }}
                    className="px-2.5 py-1 rounded bg-[#F1EEE9] hover:bg-[#E4E0E1] border border-[#493628]/14 text-[#493628] font-mono-tech text-[10px] transition-colors cursor-pointer"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </form>

            {/* Live Pipeline Stepper, Ambiguity Alert & Synthesized Memorandum */}
            <MemorandumView
              isLoading={isLoading}
              activeStep={activeStep}
              response={currentResponse}
              onSwitchToDeepThinking={(q) => {
                setMode('DEEP THINKING');
                executeLegalQuery(q, 'DEEP THINKING', false);
              }}
              onContinueFastAnyway={(q) => {
                setMode('FAST');
                executeLegalQuery(q, 'FAST', true);
              }}
              onInspectCitation={(caseName, pageNumber) =>
                setInspectTarget({ caseName, pageNumber })
              }
            />
          </div>
        </main>
      </div>

      {/* Visual Citation & Page Chunk Inspector Modal (Phase 3 / FR-1.1) */}
      <CitationInspectorModal
        caseName={inspectTarget?.caseName || null}
        targetPage={inspectTarget?.pageNumber}
        onClose={() => setInspectTarget(null)}
      />

      {/* Interface Contract Reference Modal (PRD Section 9) */}
      {showContractModal && (
        <div
          className="fixed inset-0 z-50 bg-[#342219]/60 backdrop-blur-[1px] flex items-center justify-center p-4"
          onClick={() => setShowContractModal(false)}
        >
          <div
            className="bg-[#FDFBF8] border border-[#493628]/25 rounded-[12px] max-w-2xl w-full p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#493628]/15">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-[#AB886D]" />
                <h3 className="font-serif-editorial font-bold text-[20px] text-[#342219]">
                  Clerk Verification &amp; ChromaDB Contract Specification
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowContractModal(false)}
                className="p-1 text-[#806C5D] hover:text-[#342219] cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {ollamaHealth && (
              <div
                className={`mb-4 p-3 rounded-lg border text-xs ${
                  ollamaHealth.connected && ollamaHealth.model_available
                    ? 'bg-[#EBF0E8] border-[#4A6741]/35 text-[#342219]'
                    : 'bg-[#F7F1EB] border-[#DFAD56] text-[#342219]'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-mono-tech font-semibold uppercase tracking-[0.06em]">
                    LOCAL OLLAMA DAEMON ({ollamaHealth.base_url}):{' '}
                    {ollamaHealth.connected
                      ? ollamaHealth.model_available
                        ? 'CONNECTED & MODEL READY'
                        : 'CONNECTED (MODEL NOT PULLED)'
                      : 'OFFLINE (EXTRACTIVE FALLBACK ACTIVE)'}
                  </span>
                  <button
                    type="button"
                    onClick={() =>
                      fetch('/api/ollama/health')
                        .then((r) => r.json())
                        .then((d) => setOllamaHealth(d))
                    }
                    className="px-2 py-0.5 rounded bg-[#493628] text-[#FDFBF8] font-mono-tech text-[9.5px] uppercase cursor-pointer"
                  >
                    Re-Check Ollama
                  </button>
                </div>
                {ollamaHealth.guidance && (
                  <p className="text-[11.5px] text-[#493628]">{ollamaHealth.guidance}</p>
                )}
              </div>
            )}

            <pre className="p-4 rounded-lg bg-[#342219] text-[#F1EEE9] font-mono-tech text-[11.5px] overflow-x-auto leading-relaxed">
              {JSON.stringify(
                {
                  contract_spec: {
                    llm_model: ollamaHealth?.target_model || 'qwen2.5:7b-instruct',
                    ollama_base_url: ollamaHealth?.base_url || 'http://127.0.0.1:11434',
                    ollama_daemon_connected: Boolean(ollamaHealth?.connected),
                    embedding_model: 'BAAI/bge-m3',
                    chroma_collections: ['legal_cases', 'legal_chunks'],
                    active_persistence: {
                      cases_count: cases.length,
                      chunks_count: totalChunks,
                      reranker_enabled: rerankerEnabled,
                    },
                    chunk_parameters: { target_words: 200, overlap_words: 25 },
                    routing: { ambiguity_threshold: 0.1, relevance_floor: 0.4 },
                    verification_outputs: {
                      verified_schema: { answer: 'string', verified: 'boolean' },
                      body_min_words: 15,
                      fallback_string:
                        'No verified answer could be found in the uploaded documents for this question.',
                    },
                  },
                },
                null,
                2
              )}
            </pre>

            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={() => setShowContractModal(false)}
                className="px-4 py-2 rounded bg-[#493628] hover:bg-[#342219] text-[#FDFBF8] font-mono-tech text-[11px] uppercase tracking-[0.07em] cursor-pointer"
              >
                Close Specification
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
