"""
Interactive demo of the Process Semantic Layer PoC.
Shows the system in action with example queries.
"""
from pathlib import Path
from src.concept_graph import ConceptGraph
from src.document_loader import DocumentLoader
from src.embedding_engine import EmbeddingEngine
from src.retrieval_pipeline import RetrievalPipeline

def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def print_result(rank, result):
    """Print a formatted search result."""
    print(f"\n{rank}. {result.title}")
    print(f"   Document ID: {result.doc_id}")
    print(f"   Relevance Score: {result.score:.3f}")
    if result.matched_concepts:
        print(f"   Matched Concepts: {', '.join(result.matched_concepts)}")
    else:
        print(f"   Matched Concepts: (none - ranked by embedding similarity)")
    print(f"   Snippet: {result.snippet[:120]}...")

def main():
    """Run the interactive demo."""
    print_banner("Process Semantic Layer - Interactive Demo")
    
    # Initialize system
    print("\n🚀 Initializing system...")
    project_root = Path(__file__).parent
    concepts_path = project_root / "data" / "concepts.yaml"
    docs_dir = project_root / "data" / "documents"
    
    concept_graph = ConceptGraph(str(concepts_path))
    document_loader = DocumentLoader(str(docs_dir), concept_graph)
    embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")
    
    pipeline = RetrievalPipeline(concept_graph, document_loader, embedding_engine)
    pipeline.initialize()
    
    print(f"✓ Loaded {len(concept_graph.concepts)} concepts")
    print(f"✓ Indexed {len(pipeline.documents)} documents")
    
    # Demo queries
    demo_queries = [
        {
            "query": "How do new employees sign up for health benefits?",
            "description": "Question about employee onboarding and benefits"
        },
        {
            "query": "What are the requirements for processing monthly payroll?",
            "description": "Question about payroll and salary processing"
        },
        {
            "query": "How do we approve vendor invoices and payments?",
            "description": "Question about procurement and expense management"
        },
        {
            "query": "What documentation is needed for the annual audit?",
            "description": "Question about compliance and regulatory requirements"
        },
        {
            "query": "budget allocation and spending limits",
            "description": "Question about financial planning (no verb, keyword style)"
        }
    ]
    
    print_banner("Running Demo Queries")
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n\n📋 Demo Query {i}/5")
        print(f"   Context: {demo['description']}")
        print(f"   Query: \"{demo['query']}\"")
        print("-" * 70)
        
        results = pipeline.query(demo['query'], top_k=2)
        
        if results:
            for rank, result in enumerate(results, 1):
                print_result(rank, result)
        else:
            print("\n   No results found.")
        
        if i < len(demo_queries):
            input("\n   Press Enter to continue...")
    
    # Interactive mode
    print_banner("Interactive Mode")
    print("\n💡 Now you can try your own queries!")
    print("   Type 'quit' or 'exit' to end the demo.\n")
    
    while True:
        try:
            user_query = input("\n🔍 Your query: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_query:
                continue
            
            print("-" * 70)
            results = pipeline.query(user_query, top_k=3)
            
            if results:
                for rank, result in enumerate(results, 1):
                    print_result(rank, result)
            else:
                print("\n   No results found.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n   Error: {e}")
    
    print_banner("Demo Complete - Thank You!")
    print("\n✨ The semantic layer successfully:")
    print("   • Matched queries to business concepts")
    print("   • Filtered documents using concept tags")
    print("   • Ranked results using embedding similarity")
    print("   • Provided explainable, structured responses")
    print("\n📖 See README.md for architecture details and design decisions.\n")

if __name__ == "__main__":
    main()
