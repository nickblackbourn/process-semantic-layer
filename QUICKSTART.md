# Quick Start Guide

## Installation

```powershell
# Clone or navigate to the project
cd process-semantic-layer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the Demo

```powershell
python run_demo.py
```

This runs 4 test queries with detailed visualization:
- Concept matching results
- Document filtering steps
- Ranking with confidence scores
- Performance summary dashboard

### Interactive Mode

```powershell
python run_demo.py --interactive
```

Enter your own queries and explore the system interactively.

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
| `run_demo.py` | Demo script (automated + interactive modes) |
| `README.md` | Full documentation |
| `data/concepts.yaml` | Business concept definitions |
| `data/documents/` | Sample process documents |

## Troubleshooting

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`

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
