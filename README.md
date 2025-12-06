# Process Semantic Layer - Proof of Concept

A lightweight semantic layer demonstrating how a concept graph guides enterprise document retrieval. This PoC combines business process concepts, document tagging, embeddings, and vector similarity search through a simple FastAPI endpoint.

## Purpose

**The core question:** Can a simple concept graph—representing business processes—meaningfully improve how AI systems retrieve enterprise knowledge?

This project tests that hypothesis with a working system. It proves that structured business knowledge (concepts like "employee onboarding" or "payroll processing") can guide retrieval better than embeddings or keywords alone.

The system:
1. **Maps queries to business concepts** using name and synonym matching
2. **Filters documents** based on concept tags (semantic pre-filtering)
3. **Ranks filtered documents** using embedding similarity (semantic relevance)
4. **Returns structured results** with matched concepts and relevance scores

This architecture reflects real-world applied AI patterns where domain knowledge guides retrieval.

---

## Context: Why This Matters Now

As a business process management consultant, I've watched organizations struggle to connect their AI investments with their actual operational knowledge. We have decades of work in business semantics—standards like SBVR (Semantics of Business Vocabulary and Rules)—that defined how to capture business meaning formally.

Then AI came along, and we threw it all away for "let the LLM figure it out."

This experiment asks: **What if we didn't?**

What if we took the structured business vocabulary work seriously—but made it lightweight enough for the AI age? Not heavyweight ontologies. Not complex rule engines. Just: here are our business concepts, here are the synonyms, here's how they relate.

This PoC tests whether that middle ground—structured enough to guide, simple enough to maintain—actually works.

**Full disclosure:** I'm not an AI researcher. I'm not a knowledge graph expert. I'm a process consultant learning in public. If you spot issues or see better approaches, I want to hear them. This is about asking good questions, not claiming perfect answers.

---

## Architecture

```
Query Text
    ↓
┌─────────────────────┐
│  Concept Matching   │ ← data/concepts.yaml (business knowledge)
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

---

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

### 2. Run a Test

The easiest way to see the system work:

```powershell
python test_pipeline.py
```

This runs 4 test queries and shows results with concept matching, filtering, and ranking visualization.

### 3. Or Start the API Server

```powershell
python main.py
```

The server starts on `http://localhost:8001` with hot reload enabled.

On startup, the pipeline:
1. Loads 12 concepts from YAML
2. Loads 5 markdown documents
3. Tags each document with matched concepts
4. Generates embeddings using `all-MiniLM-L6-v2` model
5. Prepares for queries

### 4. Query the API

**Using PowerShell:**

```powershell
$body = @{
    query = "how do new hires get benefits?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/query" -Method Post -Body $body -ContentType "application/json"
```

**Using curl:**

```bash
curl -X POST "http://localhost:8001/query" \
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
    "score": 0.455,
    "snippet": "This document outlines the complete employee onboarding process for new hires..."
  }
]
```

---

## Test Results

| Query | Top Result | Confidence | Matched Concepts |
|-------|-----------|------------|------------------|
| "how do new hires get benefits?" | Employee Onboarding | 45.5% | employee_onboarding, benefits_enrollment |
| "processing payroll and tax" | Payroll Guidelines | 73.8% | payroll_processing, tax_filing |
| "vendor contracts and approval" | Vendor Management | 69.2% | vendor_management, contract_review |
| "annual audit requirements" | Compliance Audit | 57.0% | compliance_audit, financial_reporting |

**4 out of 4 queries returned the correct document as top result.**

The system understands the difference between:
- Documents that *mention* a keyword
- Documents that *relate to* a business concept

---

## Why This Matters

### For Strategy

Most RAG systems are black boxes. You ask a question, get documents back, but can't explain *why*.

This architecture combines:
- **Explicit business logic** (concept graph in plain YAML)
- **AI pattern matching** (embeddings for semantic similarity)
- **Transparent reasoning** (every result shows matched concepts)

Result: AI that aligns with how your organization actually thinks and can explain its decisions.

### For Compliance

Query: "show me payroll tax documents"

**Without semantic layer:**  
Result: *[mixed documents, no explanation]*

**With semantic layer:**  
Result: "Payroll Guidelines" (73.8% confidence)  
Matched: payroll_processing, tax_filing  

For regulated industries (finance, healthcare, legal), this explainability isn't optional—it's essential.

### For Knowledge Management

The concept graph is just YAML:
```yaml
- id: employee_onboarding
  name: Employee Onboarding
  synonyms:
    - new hire
    - joining process
    - orientation
  related_to:
    - benefits_enrollment
    - timekeeping
```

Business analysts can edit this. No ontology engineers required. Documents auto-tag themselves based on these concepts during ingestion.

---

## Project Structure

```
process-semantic-layer/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── main.py                        # Server entry point
├── test_pipeline.py               # Direct pipeline test (recommended first run)
├── demo.py                        # Interactive demonstration
├── data/
│   ├── concepts.yaml             # Business concept graph (12 concepts)
│   └── documents/                # Process markdown documents (5 docs)
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

---

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

This PoC prioritizes clarity over scale. In-memory storage keeps the code simple. A production system would use vector databases (Pinecone, Weaviate, Qdrant) and persistent storage.

### Why FastAPI?

FastAPI offers:
- Automatic OpenAPI documentation (`/docs`)
- Pydantic validation (type safety)
- Async support (if needed later)
- Minimal boilerplate

---

## What This Proves (And What It Doesn't)

### ✅ Proven

1. **Lightweight concept graphs work** - 12 concepts + synonyms is enough to see value
2. **Hybrid retrieval beats pure embedding search** for domain-specific queries
3. **Explainability scales** - Each result traces back to matched concepts
4. **Implementation is practical** - Plain YAML, standard Python libraries, no specialized infrastructure

### ❌ Not Proven (Yet)

1. **Scale** - Tested on 5 documents, not 5,000
2. **Maintenance** - How do you keep concepts aligned as business evolves?
3. **Multi-domain** - Does this work across different business units?
4. **Production hardening** - No auth, caching, or monitoring built in

This is a **directional experiment**, not a production system.

---

## Questions This Raises

**For executives:**
- What are the 10 most critical process concepts in your business?
- Can your AI systems reason about them explicitly?
- Do you need to explain your AI's decisions for compliance?

**For AI strategists:**
- When does semantic layer complexity outweigh benefits?
- How do you measure concept graph ROI?
- Should concept definitions be centralized or federated?

**For knowledge managers:**
- Who owns concept definitions—IT or business SMEs?
- Can concepts emerge automatically from document patterns?
- What's the governance model for concept evolution?

---

## What Could Come Next

This PoC opens several directions for exploration:

### Immediate Extensions
- **Scale testing:** Test on 100+ documents across multiple domains
- **Multi-hop reasoning:** Traverse concept relationships to expand queries
- **Automatic concept discovery:** Use LLMs to suggest new concepts from document patterns
- **Integration:** Connect to existing enterprise search or knowledge management systems

### Bigger Research Questions
- Can LLMs help maintain concept graphs automatically as business processes change?
- How do you align concept graphs across merged organizations?
- What does "process interoperability" look like with semantic layers?
- Can semantic layers satisfy AI governance requirements (EU AI Act, etc.)?

### Production Considerations
- Vector database integration for scale
- Concept versioning and change management
- Multi-tenant concept graphs (different teams, different concepts)
- Active learning feedback loops (users correct matches → concepts improve)

---

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

---

## Extending This PoC

**Add more concepts:** Expand `data/concepts.yaml` with additional business terms and relationships

**Add more documents:** Place markdown files in `data/documents/` with YAML frontmatter

**Improve matching:** Implement fuzzy matching or stemming in `concept_graph.py`

**Better snippets:** Extract sentences around matched keywords instead of first N characters

**Add concept relationships:** Use `related_to` field to expand queries with related concepts

**Persistent storage:** Integrate vector database (Qdrant, Weaviate) for larger document collections

**Logging and metrics:** Track query patterns, concept hit rates, and retrieval performance

---

## Limitations

This is a proof of concept with intentional constraints:

- **No authentication** - API is completely open
- **No persistence** - Restarting server reloads and re-embeds everything
- **Simple matching** - Concept matching is basic substring match (no NLP)
- **No query expansion** - Related concepts are loaded but not used yet
- **Single-language** - Only handles English text
- **No caching** - Every query recomputes similarities
- **Limited error handling** - Basic exception handling only

These limitations keep the implementation simple for learning and experimentation.

---

## A Note on Approach

This experiment comes from a business process management perspective, not a pure AI/ML perspective. The concept graph structure draws inspiration from business semantics standards (particularly SBVR) adapted for modern retrieval systems.

**What this means:**
- The concepts represent business vocabulary, not arbitrary tags
- The relationships (`related_to`) mirror how business processes actually connect
- The emphasis on explainability reflects enterprise governance needs

**What this doesn't mean:**
- This isn't claiming to be the "right" way to do semantic layers
- There are likely better embedding models, matching algorithms, or architectures
- Experts in knowledge graphs or NLP may spot obvious improvements

**The point:** Can process consultants and business analysts—people who understand organizational semantics—contribute meaningfully to AI architecture? Or does this all need to be ML engineering?

I'm testing the former. Feedback welcome.

---

## The Bigger Picture

This experiment sits at the intersection of three trends:

1. **Knowledge Graphs → Semantic Layers**  
   Moving from heavyweight ontologies to lightweight, task-specific concept models

2. **RAG → Hybrid Retrieval**  
   Combining symbolic reasoning (concepts) with neural retrieval (embeddings)

3. **Black Box AI → Explainable AI**  
   Building systems that can articulate their reasoning process

The question isn't "Should we use embeddings or concept graphs?"

The question is: **"How do we combine structured business knowledge with statistical learning to build AI that organizations can trust?"**

This PoC is one answer. What's yours?

---

## Further Reading

- `QUICKSTART.md` - Quick reference for developers

---

**Status:** Proof of concept  
**Purpose:** Strategic experiment and architectural learning  
**Built by:** Nick Blackbourn  
**Use:** Fork it, break it, extend it with your concepts  

*Ask questions, not for answers.*
