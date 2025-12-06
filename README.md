# Process Semantic Layer

**The problem:** Most enterprise AI treats your documents like random text. It doesn't understand that "new hire," "onboarding," and "orientation" all mean the same thing in your business.

**The idea:** What if you could teach your AI the language of your business—explicitly?

This is a working experiment to test whether a simple concept graph improves document retrieval.

## Architecture

```
Query Text
    ↓
┌─────────────────────┐
│  Concept Matching   │ ← concepts.yaml (business knowledge)
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Document Filtering  │ ← Tagged documents (concept-labeled)
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Embedding Ranking   │ ← Sentence-transformers embeddings
└─────────────────────┘
    ↓
Top K Results (doc_id, title, concepts, score, snippet)
```

### Components

- **Concept Graph** (`data/concepts.yaml`): 12 business process concepts with names, synonyms, and relationships
- **Documents** (`data/documents/`): 5 markdown process documents with frontmatter metadata
- **Concept Matching** (`src/concept_graph.py`): Case-insensitive substring matching against concept names/synonyms
- **Document Tagging** (`src/document_loader.py`): Automatic concept assignment during document loading
- **Embedding Engine** (`src/embedding_engine.py`): Sentence-transformers for vectorization and cosine similarity
- **Retrieval Pipeline** (`src/retrieval_pipeline.py`): Orchestrates concept filtering → embedding ranking
- **FastAPI Endpoint** (`src/api.py`): Single POST /query endpoint exposing the pipeline

## Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `fastapi` + `uvicorn` - API framework
- `pydantic` - Data models
- `pyyaml` - Concept graph parsing
- `sentence-transformers` - Embedding generation
- `numpy` + `scikit-learn` - Vector operations

### 2. Run the Server

```powershell
python main.py
```

The server starts on `http://localhost:8000` with hot reload enabled.

On startup, the pipeline:
1. Loads 12 concepts from YAML
2. Loads 5 markdown documents
3. Tags each document with matched concepts
4. Generates embeddings using `all-MiniLM-L6-v2` model
5. Prepares for queries

### 3. Query the API

**Using PowerShell:**

```powershell
$body = @{
    query = "how do new hires get benefits?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $body -ContentType "application/json"
```

**Using curl:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "how do new hires get benefits?", "top_k": 3}'
```

**Response format:**

```json
[
  {
    "doc_id": "doc1",
    "title": "Employee Onboarding Procedure",
    "matched_concepts": ["employee_onboarding", "benefits_enrollment", "timekeeping"],
    "score": 0.847,
    "snippet": "This document outlines the complete employee onboarding process for new hires..."
  },
  ...
]
```

## Example Queries

| Query | Matched Concepts | Top Result |
|-------|-----------------|------------|
| "how do new hires get benefits?" | employee_onboarding, benefits_enrollment | Employee Onboarding Procedure |
| "processing payroll and tax" | payroll_processing, tax_filing | Payroll Processing Guidelines |
| "vendor contracts and approval" | vendor_management, contract_review, expense_approval | Vendor Management Process |
| "annual audit requirements" | compliance_audit, financial_reporting | Annual Compliance Audit Protocol |
| "expense tracking and budget" | expense_approval, financial_reporting, budget_planning | Financial Reporting and Budget Management |

## Project Structure

```
process-semantic-layer/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── main.py                        # Server entry point
├── data/
│   ├── concepts.yaml             # Business concept graph
│   └── documents/                # Process markdown documents
│       ├── doc1_onboarding.md
│       ├── doc2_payroll.md
│       ├── doc3_procurement.md
│       ├── doc4_compliance.md
│       └── doc5_reporting.md
└── src/
    ├── __init__.py
    ├── models.py                 # Pydantic data models
    ├── concept_graph.py          # Concept loading and matching
    ├── document_loader.py        # Document parsing and tagging
    ├── embedding_engine.py       # Embedding generation and ranking
    ├── retrieval_pipeline.py     # Orchestration logic
    └── api.py                    # FastAPI application

```

## Design Decisions

### Why a Concept Graph?

Real enterprise systems deal with domain-specific terminology. A concept graph captures business vocabulary (e.g., "onboarding" = "new hire" = "orientation") that pure embedding models might miss. This PoC shows how explicit semantic structures complement ML-based retrieval.

### Why Tag Documents in Advance?

Pre-tagging documents with concepts enables **semantic filtering** - we can narrow the search space before computing similarity. This is faster and more explainable than embedding-only approaches.

### Why Sentence-Transformers?

The `all-MiniLM-L6-v2` model provides:
- Fast embedding generation (384-dim vectors)
- Good semantic understanding for short documents
- No external API dependencies
- Suitable for local development and PoCs

### Why In-Memory?

This PoC prioritizes clarity over scale. In-memory storage keeps the code simple and implementation time under 5 hours. A production system would use vector databases (Pinecone, Weaviate, Qdrant) and persistent storage.

### Why FastAPI?

FastAPI offers:
- Automatic OpenAPI documentation (`/docs`)
- Pydantic validation (type safety)
- Async support (if needed later)
- Minimal boilerplate

## API Reference

### POST /query

Execute a semantic query against the document collection.

**Request:**
```json
{
  "query": "string (required, min 1 char)",
  "top_k": "integer (optional, default 5, range 1-20)"
}
```

**Response:**
```json
[
  {
    "doc_id": "string",
    "title": "string",
    "matched_concepts": ["string"],
    "score": "float (0.0-1.0)",
    "snippet": "string"
  }
]
```

### GET /

Health check returning service status.

### GET /health

Detailed health check with component status and counts.

## Testing the System

1. **Test concept matching:** Query "new hire orientation" should match `employee_onboarding`
2. **Test semantic filtering:** Query "payroll taxes" should filter to payroll/compliance docs
3. **Test embedding ranking:** Query with no concept match should still return relevant docs by similarity
4. **Test edge cases:** Empty query, very long query, top_k=1

## Extending This PoC

**Add more concepts:** Expand `concepts.yaml` with additional business terms and relationships

**Add more documents:** Place markdown files in `data/documents/` with YAML frontmatter

**Improve matching:** Implement fuzzy matching or stemming in `concept_graph.py`

**Better snippets:** Extract sentences around matched keywords instead of first N characters

**Add concept relationships:** Use `related_to` field to expand queries with related concepts

**Persistent storage:** Integrate vector database (Qdrant, Weaviate) for larger document collections

**Logging and metrics:** Track query patterns, concept hit rates, and retrieval performance

## Limitations

- **No authentication:** API is completely open
- **No persistence:** Restarting server reloads and re-embeds everything
- **Simple matching:** Concept matching is basic substring match (no NLP)
- **No query expansion:** Related concepts are loaded but not used for query expansion
- **Single-language:** Only handles English text
- **No caching:** Every query regenerates embeddings and scores
- **Limited error handling:** Basic exception handling only

## Time Investment

This PoC was designed as a ~5 hour implementation:
- Foundation (structure, models, data): 60 min
- Core components (concept graph, loader): 90 min
- Embeddings and ranking: 60 min
- Pipeline integration: 60 min
- API and documentation: 30 min

Actual complexity may vary based on environment setup and debugging.

## Key Takeaways

✅ **Semantic layers work** - Combining concept graphs with embeddings improves retrieval quality

✅ **Architecture matters** - Clear separation of concerns (concept matching → filtering → ranking) makes the system understandable

✅ **Explainability** - Returned results include matched concepts, making the system's reasoning transparent

✅ **Practical AI patterns** - This approach reflects real enterprise AI architectures, not just academic exercises

---

**Built with:** Python 3.10+, FastAPI, Sentence-Transformers, scikit-learn

**License:** MIT (or your preferred license)
