"""
Document loader and tagger.
Loads markdown documents and tags them with matched concepts.
"""
import re
from pathlib import Path
from typing import Optional
from src.models import Document, TaggedDocument
from src.concept_graph import ConceptGraph


class DocumentLoader:
    """Loads documents from markdown files and tags them with concepts."""
    
    def __init__(self, docs_dir: str, concept_graph: ConceptGraph):
        """
        Initialize document loader.
        
        Args:
            docs_dir: Directory containing markdown documents
            concept_graph: ConceptGraph instance for tagging
        """
        self.docs_dir = Path(docs_dir)
        self.concept_graph = concept_graph
        
        if not self.docs_dir.exists():
            raise FileNotFoundError(f"Documents directory not found: {docs_dir}")
    
    def load_documents(self) -> list[TaggedDocument]:
        """
        Load all markdown documents from the directory and tag with concepts.
        
        Returns:
            List of TaggedDocument objects
        """
        documents = []
        
        # Find all markdown files
        md_files = sorted(self.docs_dir.glob("*.md"))
        
        if not md_files:
            raise ValueError(f"No markdown files found in {self.docs_dir}")
        
        for md_file in md_files:
            try:
                # Parse the markdown file
                doc = self._parse_markdown(str(md_file))
                
                # Tag with concepts
                tagged_doc = self._tag_document(doc)
                
                documents.append(tagged_doc)
            except Exception as e:
                print(f"Warning: Failed to load {md_file.name}: {e}")
                continue
        
        return documents
    
    def _parse_markdown(self, path: str) -> Document:
        """
        Parse a markdown file, extracting frontmatter and content.
        
        Args:
            path: Path to the markdown file
            
        Returns:
            Document object
        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter (YAML between --- delimiters)
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', 
                                     content, re.DOTALL)
        
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            body = frontmatter_match.group(2).strip()
            
            # Parse frontmatter for doc_id and title
            doc_id = self._extract_frontmatter_field(frontmatter_text, 'doc_id')
            title = self._extract_frontmatter_field(frontmatter_text, 'title')
        else:
            # No frontmatter - use filename as fallback
            body = content.strip()
            doc_id = Path(path).stem
            title = Path(path).stem.replace('_', ' ').title()
        
        # Use filename as fallback for missing fields
        if not doc_id:
            doc_id = Path(path).stem
        if not title:
            title = Path(path).stem.replace('_', ' ').title()
        
        return Document(doc_id=doc_id, title=title, content=body)
    
    def _extract_frontmatter_field(self, frontmatter: str, field: str) -> Optional[str]:
        """
        Extract a field value from frontmatter text.
        
        Args:
            frontmatter: Frontmatter text
            field: Field name to extract
            
        Returns:
            Field value or None
        """
        pattern = rf'^{field}:\s*(.+)$'
        match = re.search(pattern, frontmatter, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _tag_document(self, doc: Document) -> TaggedDocument:
        """
        Tag a document with matched concepts based on its content.
        
        Args:
            doc: Document to tag
            
        Returns:
            TaggedDocument with matched concepts
        """
        # Match concepts against title and content
        text_to_match = f"{doc.title} {doc.content}"
        matched_concept_ids = self.concept_graph.match_concepts(text_to_match)
        
        return TaggedDocument(
            doc_id=doc.doc_id,
            title=doc.title,
            content=doc.content,
            matched_concepts=matched_concept_ids,
            embedding=None  # Will be populated by embedding engine
        )
