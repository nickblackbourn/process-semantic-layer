"""
FastAPI application exposing the semantic layer query endpoint.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from src.models import QueryRequest, QueryResponse
from src.concept_graph import ConceptGraph
from src.document_loader import DocumentLoader
from src.embedding_engine import EmbeddingEngine
from src.retrieval_pipeline import RetrievalPipeline

# Initialize FastAPI app
app = FastAPI(
    title="Process Semantic Layer API",
    description="Document retrieval API using concept-based semantic filtering",
    version="1.0.0"
)

# Global pipeline instance (initialized on startup)
pipeline: RetrievalPipeline = None


@app.on_event("startup")
def startup_event():
    """Initialize the retrieval pipeline on app startup."""
    global pipeline
    
    print("\n" + "="*60)
    print("Starting Process Semantic Layer API")
    print("="*60)
    
    try:
        # Determine paths relative to project root
        # Assuming api.py is in src/ and data/ is at project root
        project_root = Path(__file__).parent.parent
        concepts_path = project_root / "data" / "concepts.yaml"
        docs_dir = project_root / "data" / "documents"
        
        print(f"Project root: {project_root}")
        print(f"Concepts path: {concepts_path}")
        print(f"Documents dir: {docs_dir}\n")
        
        # Initialize components
        concept_graph = ConceptGraph(str(concepts_path))
        document_loader = DocumentLoader(str(docs_dir), concept_graph)
        embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")
        
        # Create and initialize pipeline
        pipeline = RetrievalPipeline(concept_graph, document_loader, embedding_engine)
        pipeline.initialize()
        
        print("="*60)
        print("API Ready - POST queries to /query")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nERROR during startup: {e}")
        raise


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Process Semantic Layer API",
        "version": "1.0.0",
        "endpoints": {
            "query": "POST /query",
            "docs": "GET /docs"
        }
    }


@app.post("/query", response_model=list[QueryResponse])
def query_documents(request: QueryRequest) -> list[QueryResponse]:
    """
    Query documents using semantic layer.
    
    Process:
    1. Matches query to business concepts
    2. Filters documents by concepts
    3. Ranks by embedding similarity
    4. Returns top K results
    
    Args:
        request: QueryRequest with query text and top_k parameter
        
    Returns:
        List of QueryResponse objects with ranked results
    """
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Pipeline not initialized."
        )
    
    try:
        results = pipeline.query(request.query, request.top_k)
        return results
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Detailed health check with component status."""
    if pipeline is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "pipeline": "not initialized"
            }
        )
    
    return {
        "status": "healthy",
        "pipeline": "initialized",
        "documents_loaded": len(pipeline.documents),
        "concepts_loaded": len(pipeline.concept_graph.concepts)
    }
