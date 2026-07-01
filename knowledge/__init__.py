"""
Knowledge Module - Foundation Package

Phase 2 Implementation: Knowledge Foundation

Purpose:
Provides the foundational knowledge system for AI Factory Brain.
Enables loading, parsing, and storing Markdown-based knowledge documents.

Key Components:
- knowledge_models: Data structures for knowledge representation
- markdown_parser: Parses Markdown files into structured documents
- knowledge_registry: In-memory storage and retrieval
- knowledge_loader: File loading and population

Usage:
    from knowledge import KnowledgeRegistry, KnowledgeLoader
    
    # Create registry
    registry = KnowledgeRegistry()
    
    # Create loader
    loader = KnowledgeLoader(registry)
    
    # Load knowledge files
    loader.load_file("docs/my_knowledge.md")
    
    # Search knowledge
    results = registry.search_by_keyword("reasoning")

TODO:
- [ ] Add persistence layer (Phase 3)
- [ ] Add advanced search (Phase 3)
- [ ] Add batch operations (Phase 3)
"""

from knowledge.knowledge_models import (
    KnowledgeDocument,
    KnowledgeSection,
    KnowledgeMetadata,
    KnowledgeIndex,
)
from knowledge.knowledge_registry import KnowledgeRegistry
from knowledge.markdown_parser import MarkdownParser
from knowledge.knowledge_loader import KnowledgeLoader

__all__ = [
    "KnowledgeDocument",
    "KnowledgeSection",
    "KnowledgeMetadata",
    "KnowledgeIndex",
    "KnowledgeRegistry",
    "MarkdownParser",
    "KnowledgeLoader",
]
