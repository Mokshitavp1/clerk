import React from 'react';
import { Scale, SlidersHorizontal } from 'lucide-react';

interface TopNavBarProps {
  totalCases: number;
  totalChunks: number;
  rerankerEnabled: boolean;
  onToggleReranker: () => void;
  onOpenContractModal: () => void;
}

export const TopNavBar: React.FC<TopNavBarProps> = ({
  totalCases,
  totalChunks,
  rerankerEnabled,
  onToggleReranker,
  onOpenContractModal,
}) => {
  return (
    <header className="h-[62px] bg-[#FDFBF8] border-b border-[#493628]/18 px-6 flex items-center justify-between shrink-0 z-20 select-none">
      {/* Brand Title Zone */}
      <div className="flex items-center gap-2.5 whitespace-nowrap shrink-0">
        <Scale className="w-5 h-5 text-[#AB886D] stroke-[2]" />
        <span className="font-serif-editorial font-bold text-[19px] tracking-[-0.02em] text-[#342219]">
          Legal Retrieval Assistant
        </span>
        <span className="hidden sm:inline-block text-[#AB886D] font-serif-editorial font-semibold text-sm ml-1">
          § CLERK
        </span>
      </div>

      {/* Right Status & Diagnostics Zone */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Active Cases Counter */}
        <button
          type="button"
          onClick={onOpenContractModal}
          title="Inspect ChromaDB Collections & Verification Contract"
          className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded border border-[#493628]/15 bg-[#F1EEE9]/70 hover:bg-[#E4E0E1] transition-colors text-[#493628] font-mono-tech text-[10px] font-medium uppercase tracking-[0.08em] cursor-pointer whitespace-nowrap"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#AB886D]" />
          <span>
            {totalCases} {totalCases === 1 ? 'CASE' : 'CASES'} ACTIVE ({totalChunks} CHUNKS)
          </span>
          <SlidersHorizontal className="w-3 h-3 text-[#806C5D] ml-0.5" />
        </button>

        {/* Optional Cross-Encoder Reranker Toggle (CLERK_ENABLE_RERANK) */}
        <button
          type="button"
          onClick={onToggleReranker}
          title="Toggle BAAI/bge-reranker-v2-m3 cross-encoder reranking"
          className={`hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded border font-mono-tech text-[10px] font-medium uppercase tracking-[0.07em] transition-colors cursor-pointer whitespace-nowrap ${
            rerankerEnabled
              ? 'bg-[#493628] text-[#FDFBF8] border-[#342219]'
              : 'bg-[#FDFBF8] text-[#806C5D] border-[#493628]/18 hover:border-[#493628]/40'
          }`}
        >
          <span>RERANKER: {rerankerEnabled ? 'ON' : 'OFF'}</span>
        </button>

        {/* System Health / Local Private Pill matching screenshot & PRD */}
        <div
          className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#EBF0E8] border border-[#4A6741]/30 text-[#4A6741] font-mono-tech text-[10px] font-semibold uppercase tracking-[0.08em] whitespace-nowrap"
          title="On-Premise Sovereign Execution — System Ready"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#4A6741]" />
          <span>LOCAL / PRIVATE</span>
        </div>
      </div>
    </header>
  );
};
