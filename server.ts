import 'dotenv/config';
import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { clerkRagEngine, checkOllamaHealth } from './src/server/ragEngine.ts';
import { INITIAL_QUERY_HISTORY } from './src/server/seedCorpus.ts';
import { LegalDocumentInput, RetrievalMode } from './src/types/clerk.ts';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: '50mb' }));

  // GET /api/status — Returns current ChromaDB index status, local Ollama health, dossier cases, and seed history
  app.get('/api/status', async (_req, res) => {
    try {
      const status = clerkRagEngine.getStatus();
      const ollama = await checkOllamaHealth();
      res.json({
        ...status,
        ollama,
        initial_history: INITIAL_QUERY_HISTORY,
      });
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to load index status',
      });
    }
  });

  // GET /api/ollama/health — Live health check for local Ollama daemon
  app.get('/api/ollama/health', async (_req, res) => {
    try {
      const ollama = await checkOllamaHealth();
      res.json(ollama);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to check Ollama health',
      });
    }
  });

  // GET /api/cases/:caseName/chunks — Returns all 1-indexed page chunks for Visual Citation Inspector
  app.get('/api/cases/:caseName/chunks', (req, res) => {
    try {
      const chunks = clerkRagEngine.getCaseChunks(req.params.caseName);
      res.json({ case_name: req.params.caseName, chunks });
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to load case chunks',
      });
    }
  });

  // POST /api/ingest — Indexes or atomically replaces (replace_case) legal PDFs into legal_cases & legal_chunks
  app.post('/api/ingest', async (req, res) => {
    try {
      const documents = (req.body?.documents || []) as LegalDocumentInput[];
      if (!Array.isArray(documents) || documents.length === 0) {
        res.status(400).json({ error: 'No valid documents provided for indexing.' });
        return;
      }
      const result = await clerkRagEngine.ingestDocuments(documents);
      const status = clerkRagEngine.getStatus();
      res.json({
        ...result,
        cases: status.cases,
      });
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to index uploaded documents',
      });
    }
  });

  // DELETE /api/cases/:caseName — Removes a case from ChromaDB collections
  app.delete('/api/cases/:caseName', (req, res) => {
    try {
      const status = clerkRagEngine.deleteCase(req.params.caseName);
      res.json(status);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to remove case',
      });
    }
  });

  // POST /api/cases/clear — Clears all indexed cases
  app.post('/api/cases/clear', (_req, res) => {
    try {
      const status = clerkRagEngine.clearAllCases();
      res.json(status);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to clear cases',
      });
    }
  });

  // POST /api/cases/restore — Restores default landmark legal dossier
  app.post('/api/cases/restore', async (_req, res) => {
    try {
      const status = await clerkRagEngine.restoreDefaultDossier();
      res.json(status);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to restore landmark dossier',
      });
    }
  });

  // POST /api/reranker — Toggles BAAI/bge-reranker-v2-m3 cross-encoder reranking
  app.post('/api/reranker', (req, res) => {
    try {
      const enabled = Boolean(req.body?.enabled);
      const status = clerkRagEngine.setReranker(enabled);
      res.json(status);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to toggle reranker',
      });
    }
  });

  // POST /api/query — Executes 2-stage hybrid retrieval, Self-RAG grading, and 3-layer verification
  app.post('/api/query', async (req, res) => {
    try {
      const query = String(req.body?.query || '').trim();
      const mode = (req.body?.mode || 'FAST') as RetrievalMode;
      const forceFast = Boolean(req.body?.forceFast);

      if (!query) {
        res.status(400).json({ error: 'Please enter a legal question or fact pattern.' });
        return;
      }

      const result = await clerkRagEngine.executeQuery({ query, mode, forceFast });
      res.json(result);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Failed to execute legal query',
      });
    }
  });

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Clerk Legal Retrieval Assistant server listening on http://localhost:${PORT}`);
  });
}

startServer();
