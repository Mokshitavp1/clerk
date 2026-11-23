import React, { useRef, useState } from 'react';
import { Upload, FileText, Trash2, Database, Eye, RotateCcw, CheckCircle2, Loader2 } from 'lucide-react';
import { HistoryItem, LegalCaseRecord, VerificationStatus } from '../types/clerk.ts';
import { parseUploadedLegalFile } from '../utils/pdfParser.ts';

interface SidebarDossierProps {
  cases: LegalCaseRecord[];
  history: HistoryItem[];
  activeHistoryId: string | null;
  onSelectHistory: (item: HistoryItem) => void;
  onDocumentsIndexed: (cases: LegalCaseRecord[]) => void;
  onDeleteCase: (caseName: string) => void;
  onClearCases: () => void;
  onRestoreDefaultCases: () => void;
  onInspectCase: (caseName: string, pageNumber?: number) => void;
}

export const SidebarDossier: React.FC<SidebarDossierProps> = ({
  cases,
  history,
  activeHistoryId,
  onSelectHistory,
  onDocumentsIndexed,
  onDeleteCase,
  onClearCases,
  onRestoreDefaultCases,
  onInspectCase,
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [stagedFiles, setStagedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexProgress, setIndexProgress] = useState<{
    current: number;
    total: number;
    statusText: string;
  } | null>(null);

  const handleFileSelect = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const incoming = Array.from(fileList).filter(
      (f) =>
        f.name.toLowerCase().endsWith('.pdf') ||
        f.name.toLowerCase().endsWith('.txt') ||
        f.name.toLowerCase().endsWith('.md')
    );
    if (incoming.length > 0) {
      setStagedFiles((prev) => [...prev, ...incoming]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleBuildIndex = async () => {
    if (stagedFiles.length === 0 || isIndexing) return;
    setIsIndexing(true);
    try {
      const parsedDocs = [];
      for (let i = 0; i < stagedFiles.length; i++) {
        const f = stagedFiles[i];
        setIndexProgress({
          current: i + 1,
          total: stagedFiles.length,
          statusText: `Parsing ${f.name} (1-indexed pages)...`,
        });
        const doc = await parseUploadedLegalFile(f);
        parsedDocs.push(doc);
      }

      setIndexProgress({
        current: stagedFiles.length,
        total: stagedFiles.length,
        statusText: 'Chunking (200w / 25w overlap) & indexing in ChromaDB...',
      });

      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ documents: parsedDocs }),
      });

      if (!res.ok) {
        throw new Error('Failed to build index');
      }

      const data = await res.json();
      onDocumentsIndexed(data.cases || []);
      setStagedFiles([]);
      setIndexProgress({
        current: stagedFiles.length,
        total: stagedFiles.length,
        statusText: `Indexed ${parsedDocs.length} authority file(s) into ChromaDB.`,
      });
      setTimeout(() => setIndexProgress(null), 2500);
    } catch (err) {
      console.error(err);
      setIndexProgress({
        current: 0,
        total: stagedFiles.length,
        statusText: 'Error indexing documents. Please verify PDF format.',
      });
    } finally {
      setIsIndexing(false);
    }
  };

  const renderStatusBadge = (status: VerificationStatus) => {
    if (status === 'VERIFIED') {
      return (
        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono-tech font-semibold uppercase tracking-[0.08em] bg-[#EBF0E8]/15 text-[#A5D69B] border border-[#A5D69B]/35">
          <span className="w-1.5 h-1.5 rounded-full bg-[#A5D69B]" />
          § VERIFIED
        </span>
      );
    }
    if (status === 'UNVERIFIED') {
      return (
        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono-tech font-semibold uppercase tracking-[0.08em] bg-[#DFAD56]/15 text-[#F3C677] border border-[#DFAD56]/40">
          <span className="w-1.5 h-1.5 rounded-full bg-[#DFAD56]" />
          § UNVERIFIED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono-tech font-semibold uppercase tracking-[0.08em] bg-[#ECEAE6]/10 text-[#D6C0B3] border border-[#D6C0B3]/30">
        <span className="w-1.5 h-1.5 rounded-full bg-[#9C9995]" />
        § INSUFFICIENT
      </span>
    );
  };

  return (
    <aside className="w-full md:w-[290px] bg-[#493628] text-[#FDFBF8] flex flex-col shrink-0 border-r border-[#342219] select-none overflow-y-auto">
      {/* Knowledge Base Header & Dropzone */}
      <div className="p-6 pb-5">
        <h2 className="font-serif-editorial font-bold text-[22px] leading-[1.15] text-[#FDFBF8] mb-2">
          Knowledge Base
        </h2>
        <p className="text-[13.5px] leading-[1.5] text-[#E4E0E1]/90 mb-5 font-normal">
          1. Upload PDFs &rarr; 2. Build/Update &rarr; 3. Ask questions
        </p>

        {/* Custom Dashed Dropzone matching screenshot */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-[1.5px] border-dashed rounded-[10px] p-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${
            isDragging
              ? 'border-[#FDFBF8] bg-[#342219]/60'
              : 'border-[#D6C0B3]/40 bg-[#342219]/25 hover:border-[#D6C0B3]/70 hover:bg-[#342219]/40'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            multiple
            className="hidden"
            onChange={(e) => handleFileSelect(e.target.files)}
          />
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            className="bg-[#AB886D] hover:bg-[#B8967C] active:translate-y-[1px] text-[#342219] font-medium text-[13px] px-5 py-2.5 rounded-[7px] flex items-center gap-2 transition-all shadow-xs cursor-pointer"
          >
            <Upload className="w-4 h-4 stroke-[2.2]" />
            <span>Upload</span>
          </button>
        </div>

        {/* Staged Files & BUILD INDEX Button (FR-1.1 - FR-1.5) */}
        {stagedFiles.length > 0 && (
          <div className="mt-3.5 bg-[#342219]/60 border border-[#AB886D]/40 rounded-lg p-3">
            <div className="flex items-center justify-between text-[10px] font-mono-tech uppercase tracking-[0.08em] text-[#D6C0B3] mb-2">
              <span>STAGED FOR CHROMADB ({stagedFiles.length})</span>
              <button
                type="button"
                onClick={() => setStagedFiles([])}
                className="text-[#AB886D] hover:text-[#FDFBF8] underline cursor-pointer"
              >
                Clear
              </button>
            </div>
            <ul className="space-y-1 mb-3 max-h-24 overflow-y-auto text-xs text-[#E4E0E1]">
              {stagedFiles.map((f, i) => (
                <li key={`${f.name}-${i}`} className="truncate flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-[#AB886D] shrink-0" />
                  <span className="truncate">{f.name}</span>
                </li>
              ))}
            </ul>
            <button
              type="button"
              disabled={isIndexing}
              onClick={handleBuildIndex}
              className="w-full py-2 px-3 rounded bg-[#FDFBF8] hover:bg-[#F1EEE9] text-[#342219] font-mono-tech font-semibold text-[11px] uppercase tracking-[0.08em] flex items-center justify-center gap-2 transition-colors cursor-pointer disabled:opacity-60"
            >
              {isIndexing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-[#493628]" />
                  <span>INDEXING...</span>
                </>
              ) : (
                <>
                  <Database className="w-3.5 h-3.5 text-[#493628]" />
                  <span>BUILD INDEX ({stagedFiles.length})</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Synchronous Indexing Progress Bar */}
        {indexProgress && (
          <div className="mt-3 bg-[#342219]/75 border border-[#AB886D]/35 rounded-md p-2.5">
            <div className="flex items-center justify-between text-[10px] font-mono-tech text-[#D6C0B3] mb-1.5">
              <span className="flex items-center gap-1">
                {isIndexing ? (
                  <Loader2 className="w-3 h-3 animate-spin text-[#AB886D]" />
                ) : (
                  <CheckCircle2 className="w-3 h-3 text-[#A5D69B]" />
                )}
                STAGE {indexProgress.current}/{indexProgress.total}
              </span>
              <span>
                {Math.round(
                  (indexProgress.current / Math.max(1, indexProgress.total)) * 100
                )}
                %
              </span>
            </div>
            <div className="w-full h-1.5 bg-[#493628] rounded-full overflow-hidden mb-1.5">
              <div
                className="h-full bg-[#AB886D] transition-all duration-200"
                style={{
                  width: `${Math.min(
                    100,
                    Math.round(
                      (indexProgress.current / Math.max(1, indexProgress.total)) * 100
                    )
                  )}%`,
                }}
              />
            </div>
            <p className="text-[11px] text-[#E4E0E1] leading-snug">
              {indexProgress.statusText}
            </p>
          </div>
        )}

        {/* DOCUMENTS / CURRENT DOSSIER Section */}
        <div className="mt-5">
          <div className="flex items-center justify-between mb-2.5">
            <span className="font-mono-tech text-[10px] font-semibold uppercase tracking-[0.12em] text-[#AB886D]">
              DOCUMENTS
            </span>
            {cases.length > 0 ? (
              <button
                type="button"
                onClick={onClearCases}
                title="Clear dossier to test empty state"
                className="text-[10px] font-mono-tech text-[#D6C0B3]/70 hover:text-[#FDFBF8] transition-colors cursor-pointer"
              >
                CLEAR ALL
              </button>
            ) : (
              <button
                type="button"
                onClick={onRestoreDefaultCases}
                title="Load 5 Landmark Precedent PDFs"
                className="text-[10px] font-mono-tech text-[#AB886D] hover:text-[#FDFBF8] flex items-center gap-1 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-2.5 h-2.5" />
                <span>LOAD 5 SAMPLE PDFS</span>
              </button>
            )}
          </div>

          {cases.length === 0 ? (
            <div className="py-5 text-center">
              <p className="font-serif-editorial italic text-[14.5px] text-[#D6C0B3]/90 mb-3">
                No case PDFs uploaded yet.
              </p>
              <button
                type="button"
                onClick={onRestoreDefaultCases}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-[#AB886D]/45 bg-[#342219]/40 hover:bg-[#342219]/75 text-[#E4E0E1] font-mono-tech text-[10px] uppercase tracking-[0.07em] transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3 h-3 text-[#AB886D]" />
                <span>Load Landmark Dossier (5 Cases)</span>
              </button>
            </div>
          ) : (
            <ul className="space-y-1.5 max-h-[210px] overflow-y-auto pr-1">
              {cases.map((c) => (
                <li
                  key={c.case_name}
                  className="group flex items-center justify-between gap-2 px-2.5 py-2 rounded-md bg-[#342219]/35 hover:bg-[#342219]/65 border border-[#D6C0B3]/12 transition-colors"
                >
                  <button
                    type="button"
                    onClick={() => onInspectCase(c.case_name, 1)}
                    className="flex items-start gap-2 text-left min-w-0 flex-1 cursor-pointer"
                    title={`Inspect ${c.case_name} (${c.page_count} pages, ${c.chunk_count} chunks)`}
                  >
                    <FileText className="w-3.5 h-3.5 text-[#AB886D] shrink-0 mt-0.5" />
                    <div className="min-w-0 flex-1">
                      <p className="text-[12.5px] font-medium text-[#FDFBF8] truncate">
                        {c.case_name}
                      </p>
                      <p className="text-[10px] font-mono-tech text-[#D6C0B3]/80">
                        {c.page_count}p &middot; {c.chunk_count} chunks
                      </p>
                    </div>
                  </button>
                  <div className="flex items-center gap-1 opacity-75 group-hover:opacity-100">
                    <button
                      type="button"
                      onClick={() => onInspectCase(c.case_name, 1)}
                      title="Inspect indexed chunks"
                      className="p-1 text-[#D6C0B3] hover:text-[#FDFBF8] cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => onDeleteCase(c.case_name)}
                      title={`Remove ${c.case_name} from index`}
                      className="p-1 text-[#D6C0B3]/70 hover:text-[#F3C677] cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Structural Divider */}
      <div className="border-t border-[#D6C0B3]/15 mx-6" />

      {/* History Section matching screenshot & PRD */}
      <div className="p-6 pt-5 flex-1 flex flex-col min-h-0">
        <h2 className="font-serif-editorial font-bold text-[22px] leading-[1.15] text-[#FDFBF8] mb-2">
          History
        </h2>
        <span className="font-mono-tech text-[10px] font-semibold uppercase tracking-[0.12em] text-[#AB886D] mb-3 block">
          PAST QUERIES
        </span>

        {history.length === 0 ? (
          <p className="font-serif-editorial italic text-[13.5px] text-[#D6C0B3]/80">
            No queries executed in this session yet.
          </p>
        ) : (
          <ul className="space-y-2.5 overflow-y-auto pr-1">
            {history.map((item) => {
              const isSelected = activeHistoryId === item.id;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    onClick={() => onSelectHistory(item)}
                    className={`w-full text-left p-2.5 rounded-lg transition-all cursor-pointer border ${
                      isSelected
                        ? 'bg-[#342219]/75 border-[#AB886D]/60 shadow-xs'
                        : 'bg-transparent border-transparent hover:bg-[#342219]/40 hover:border-[#D6C0B3]/15'
                    }`}
                  >
                    <p className="text-[13.5px] font-medium text-[#FDFBF8] leading-[1.38] line-clamp-2 mb-1.5">
                      {item.query}
                    </p>
                    <div className="flex items-center justify-between gap-2">
                      {renderStatusBadge(item.status)}
                      <span className="font-mono-tech text-[9px] uppercase tracking-[0.06em] text-[#D6C0B3]/70">
                        {item.executed_mode === 'DEEP THINKING' ? 'DEEP' : 'FAST'}
                      </span>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
};
