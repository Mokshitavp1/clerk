import React, { useEffect, useState } from 'react';
import { X, BookOpen, FileText, CheckCircle2 } from 'lucide-react';
import { LegalChunkRecord } from '../types/clerk.ts';

interface CitationInspectorModalProps {
  caseName: string | null;
  targetPage?: number;
  onClose: () => void;
}

export const CitationInspectorModal: React.FC<CitationInspectorModalProps> = ({
  caseName,
  targetPage,
  onClose,
}) => {
  const [chunks, setChunks] = useState<LegalChunkRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!caseName) return;
    setLoading(true);
    fetch(`/api/cases/${encodeURIComponent(caseName)}/chunks`)
      .then((r) => r.json())
      .then((data) => {
        setChunks(data.chunks || []);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [caseName]);

  if (!caseName) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-[#342219]/60 backdrop-blur-[1px] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-[#FDFBF8] border border-[#493628]/25 rounded-[12px] max-w-3xl w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 bg-[#493628] text-[#FDFBF8] flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <BookOpen className="w-5 h-5 text-[#AB886D] shrink-0" />
            <div className="min-w-0">
              <h3 className="font-serif-editorial font-bold text-[18px] truncate">
                {caseName.replace(/_/g, ' ')}
              </h3>
              <p className="font-mono-tech text-[10px] uppercase tracking-[0.08em] text-[#D6C0B3]">
                CHROMADB COLLECTION: legal_chunks &middot; SLIDING WINDOW (200 WORDS, 25 OVERLAP)
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded hover:bg-[#342219] text-[#D6C0B3] hover:text-[#FDFBF8] transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chunks Content */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1 bg-[#F1EEE9]">
          {loading ? (
            <p className="font-serif-editorial italic text-center py-8 text-[#806C5D]">
              Loading indexed chunks from ChromaDB...
            </p>
          ) : chunks.length === 0 ? (
            <p className="font-serif-editorial italic text-center py-8 text-[#806C5D]">
              No chunks found for this authority.
            </p>
          ) : (
            chunks.map((chunk) => {
              const isHighlighted = targetPage === chunk.page_number;
              return (
                <div
                  key={chunk.chunk_id}
                  className={`p-5 rounded-[10px] border transition-all ${
                    isHighlighted
                      ? 'bg-[#FDFBF8] border-[#4A6741] ring-2 ring-[#4A6741]/20'
                      : 'bg-[#FDFBF8] border-[#493628]/15'
                  }`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-3 border-b border-[#493628]/10">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-[#AB886D]" />
                      <span className="font-mono-tech text-[11px] font-semibold text-[#342219]">
                        {chunk.case_name}, Page {chunk.page_number}
                      </span>
                      <span className="font-mono-tech text-[10px] text-[#806C5D]">
                        (Chunk #{chunk.chunk_index} &middot; {chunk.word_count} words)
                      </span>
                    </div>
                    {isHighlighted && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#EBF0E8] text-[#4A6741] border border-[#4A6741]/30 font-mono-tech text-[9.5px] font-semibold uppercase tracking-[0.07em]">
                        <CheckCircle2 className="w-3 h-3" />
                        CITED AUTHORITY PAGE
                      </span>
                    )}
                  </div>
                  <p className="text-[14.5px] leading-[1.68] text-[#342219] whitespace-pre-line">
                    {chunk.text}
                  </p>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#FDFBF8] border-t border-[#493628]/15 flex items-center justify-between text-xs text-[#806C5D]">
          <span className="font-mono-tech text-[10px]">
            1-INDEXED ABSOLUTE PAGINATION (FR-1.1) &middot; ATOMIC CASE IDENTITY (FR-1.3)
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#493628] hover:bg-[#342219] text-[#FDFBF8] font-mono-tech text-[10.5px] uppercase tracking-[0.07em] cursor-pointer"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
