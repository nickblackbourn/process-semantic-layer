"""
Concept graph loader and query matcher.
Loads business concepts from YAML and matches them to text queries.
"""
import yaml
from pathlib import Path
from typing import Optional
from src.models import Concept


class ConceptGraph:
    """Manages the concept graph and provides concept matching functionality."""
    
    def __init__(self, yaml_path: str):
        """
        Load concepts from YAML file.
        
        Args:
            yaml_path: Path to the concepts YAML file
        """
        self.concepts: dict[str, Concept] = {}
        self._load_concepts(yaml_path)
    
    def _load_concepts(self, yaml_path: str) -> None:
        """Load and parse concepts from YAML file."""
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Concepts file not found: {yaml_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'concepts' not in data:
            raise ValueError("Invalid concepts file: missing 'concepts' key")
        
        for concept_data in data['concepts']:
            concept = Concept(**concept_data)
            self.concepts[concept.id] = concept
    
    def get_all_concepts(self) -> list[Concept]:
        """
        Return all concepts in the graph.
        
        Returns:
            List of all Concept objects
        """
        return list(self.concepts.values())
    
    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """
        Get a specific concept by ID.
        
        Args:
            concept_id: The concept ID to retrieve
            
        Returns:
            Concept object or None if not found
        """
        return self.concepts.get(concept_id)
    
    def match_concepts(self, text: str) -> list[str]:
        """
        Match concepts to text based on name and synonym matching.
        Uses case-insensitive substring matching.
        
        Args:
            text: Text to match concepts against
            
        Returns:
            List of concept IDs that match the text
        """
        if not text:
            return []
        
        normalized_text = self._normalize(text)
        matched_ids = []
        
        for concept_id, concept in self.concepts.items():
            # Check if concept name matches
            if self._normalize(concept.name) in normalized_text:
                matched_ids.append(concept_id)
                continue
            
            # Check if any synonym matches
            for synonym in concept.synonyms:
                if self._normalize(synonym) in normalized_text:
                    matched_ids.append(concept_id)
                    break
        
        return matched_ids
    
    def _normalize(self, text: str) -> str:
        """
        Normalize text for matching (lowercase).
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        return text.lower()
