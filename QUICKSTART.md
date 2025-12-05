# Quick Start Guide

## Installation

```powershell
# Clone or navigate to the project
cd process-semantic-layer

# Install dependencies
pip install -r requirements.txt
```

## Usage Options

### Option 1: Interactive Demo (Recommended)
```powershell
python demo.py
```
Shows 5 example queries, then lets you try your own.

### Option 2: Direct Pipeline Test
```powershell
python test_pipeline.py
```
Runs 4 pre-defined test queries and shows detailed results.

### Option 3: API Server
```powershell
python main.py
```
Starts FastAPI server on http://127.0.0.1:8001

Query via PowerShell:
```powershell
$body = @{
    query = "how do new hires get benefits?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8001/query" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

Query via curl:
```bash
curl -X POST "http://127.0.0.1:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "how do new hires get benefits?", "top_k": 3}'
```

## Example Queries to Try

- "How do new employees enroll in benefits?"
- "What is the payroll processing timeline?"
- "How do we onboard new vendors?"
- "What are compliance audit requirements?"
- "How do we track employee time and attendance?"
- "What is the expense approval process?"
- "How do we manage vendor contracts?"
- "What are the tax filing deadlines?"

## Project Files

| File | Purpose |
|------|---------|
| `demo.py` | Interactive demonstration |
| `test_pipeline.py` | Automated testing |
| `main.py` | API server entry point |
| `test_api.py` | API testing script |
| `README.md` | Full documentation |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details |

## Troubleshooting

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`

**"Port already in use"**
- Change port in `main.py` (line 13)

**"Slow first query"**
- Model downloads on first run (~90MB)
- Cached after first execution

## Key Concepts

1. **Concept Matching**: Queries are matched to business concepts using keywords
2. **Document Filtering**: Only documents with matched concepts are searched (when concepts match)
3. **Embedding Ranking**: Remaining documents ranked by semantic similarity
4. **Hybrid Approach**: Combines symbolic (concepts) + ML (embeddings) for best results

## What Makes This Different

Unlike pure keyword search or embeddings-only:
- ✅ Understands business terminology (concepts and synonyms)
- ✅ Filters before ranking (faster, more focused)
- ✅ Explainable results (shows which concepts matched)
- ✅ Falls back gracefully (if no concepts match, uses embeddings)

---

For detailed architecture and design decisions, see `README.md`
