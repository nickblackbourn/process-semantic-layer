"""
Direct test of the retrieval pipeline without the API layer.
"""
from pathlib import Path
from src.concept_graph import ConceptGraph
from src.document_loader import DocumentLoader
from src.embedding_engine import EmbeddingEngine
from src.retrieval_pipeline import RetrievalPipeline

print("\n" + "="*60)
print("Testing Process Semantic Layer - Direct Pipeline Test")
print("="*60 + "\n")

# Set up paths
project_root = Path(__file__).parent
concepts_path = project_root / "data" / "concepts.yaml"
docs_dir = project_root / "data" / "documents"

print(f"Project root: {project_root}")
print(f"Concepts: {concepts_path}")
print(f"Documents: {docs_dir}\n")

# Initialize components
print("Initializing components...")
concept_graph = ConceptGraph(str(concepts_path))
document_loader = DocumentLoader(str(docs_dir), concept_graph)
embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")

# Create and initialize pipeline
pipeline = RetrievalPipeline(concept_graph, document_loader, embedding_engine)
pipeline.initialize()

# Test queries
test_queries = [
    "how do new hires get benefits?",
    "processing payroll and tax",
    "vendor contracts and approval",
    "annual audit requirements"
]

print("\n" + "="*60)
print("Running Test Queries")
print("="*60)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 60)
    
    results = pipeline.query(query, top_k=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   Doc ID: {result.doc_id}")
        print(f"   Score: {result.score:.3f}")
        print(f"   Concepts: {', '.join(result.matched_concepts) if result.matched_concepts else 'none'}")
        print(f"   Snippet: {result.snippet[:100]}...")

print("\n" + "="*60)
print("Test Complete!")
print("="*60 + "\n")
