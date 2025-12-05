"""
Retrieval pipeline orchestrating concept-based filtering and embedding-based ranking.
"""
from src.concept_graph import ConceptGraph
from src.document_loader import DocumentLoader
from src.embedding_engine import EmbeddingEngine
from src.models import TaggedDocument, QueryResponse


class RetrievalPipeline:
    """Orchestrates the complete retrieval process: concept matching -> embedding ranking."""
    
    def __init__(
        self,
        concept_graph: ConceptGraph,
        document_loader: DocumentLoader,
        embedding_engine: EmbeddingEngine
    ):
        """
        Initialize the retrieval pipeline.
        
        Args:
            concept_graph: ConceptGraph instance
            document_loader: DocumentLoader instance
            embedding_engine: EmbeddingEngine instance
        """
        self.concept_graph = concept_graph
        self.document_loader = document_loader
        self.embedding_engine = embedding_engine
        self.documents: list[TaggedDocument] = []
        self._initialized = False
    
    def initialize(self) -> None:
        """
        Initialize the pipeline: load documents, tag with concepts, generate embeddings.
        Should be called once before querying.
        """
        if self._initialized:
            print("Pipeline already initialized")
            return
        
        print("Initializing retrieval pipeline...")
        
        # Load and tag documents
        print("Loading documents...")
        self.documents = self.document_loader.load_documents()
        print(f"Loaded {len(self.documents)} documents")
        
        # Log concept tagging results
        for doc in self.documents:
            print(f"  - {doc.doc_id}: {len(doc.matched_concepts)} concepts matched")
        
        # Generate embeddings
        self.documents = self.embedding_engine.embed_documents(self.documents)
        
        self._initialized = True
        print("Pipeline initialized successfully\n")
    
    def query(self, query_text: str, top_k: int = 5) -> list[QueryResponse]:
        """
        Execute a query against the document collection.
        
        Process:
        1. Match concepts from query text
        2. Filter documents by matched concepts (if any)
        3. Rank filtered documents by embedding similarity
        4. Return top K results with snippets
        
        Args:
            query_text: The search query
            top_k: Number of results to return
            
        Returns:
            List of QueryResponse objects, ranked by relevance
        """
        if not self._initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        if not query_text or not query_text.strip():
            return []
        
        print(f"\nProcessing query: '{query_text}'")
        
        # Step 1: Match concepts from query
        matched_concept_ids = self.concept_graph.match_concepts(query_text)
        print(f"Matched concepts: {matched_concept_ids if matched_concept_ids else 'none'}")
        
        # Step 2: Filter documents by concepts
        if matched_concept_ids:
            # Filter to documents that have at least one matching concept
            candidate_docs = [
                doc for doc in self.documents
                if any(concept_id in doc.matched_concepts for concept_id in matched_concept_ids)
            ]
            print(f"Filtered to {len(candidate_docs)} documents with matching concepts")
        else:
            # No concept match - search all documents
            candidate_docs = self.documents
            print(f"No concept match - searching all {len(candidate_docs)} documents")
        
        if not candidate_docs:
            print("No candidate documents found")
            return []
        
        # Step 3: Rank by embedding similarity
        query_embedding = self.embedding_engine.embed_query(query_text)
        ranked_docs = self.embedding_engine.rank_by_similarity(query_embedding, candidate_docs)
        
        # Step 4: Prepare results with snippets
        results = []
        for doc, score in ranked_docs[:top_k]:
            snippet = self._extract_snippet(doc, max_chars=200)
            
            response = QueryResponse(
                doc_id=doc.doc_id,
                title=doc.title,
                matched_concepts=doc.matched_concepts,
                score=float(score),
                snippet=snippet
            )
            results.append(response)
        
        print(f"Returning {len(results)} results\n")
        return results
    
    def _extract_snippet(self, doc: TaggedDocument, max_chars: int = 200) -> str:
        """
        Extract a snippet from the document content.
        Returns the first max_chars characters, attempting to end at sentence boundary.
        
        Args:
            doc: Document to extract snippet from
            max_chars: Maximum snippet length
            
        Returns:
            Snippet text
        """
        if not doc.content:
            return ""
        
        # If content is short enough, return it all
        if len(doc.content) <= max_chars:
            return doc.content
        
        # Get first max_chars
        snippet = doc.content[:max_chars]
        
        # Try to end at a sentence boundary (period, question mark, exclamation)
        for delimiter in ['. ', '? ', '! ']:
            last_sentence = snippet.rfind(delimiter)
            if last_sentence > max_chars // 2:  # Only if we keep at least half
                return snippet[:last_sentence + 1].strip()
        
        # No good sentence boundary - cut at space
        last_space = snippet.rfind(' ')
        if last_space > 0:
            snippet = snippet[:last_space]
        
        return snippet.strip() + "..."
