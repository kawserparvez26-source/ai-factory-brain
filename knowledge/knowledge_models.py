"""
Knowledge Models - Data Structures

Title: Knowledge Data Models

Purpose:
Defines the core data structures and models for the Knowledge Foundation.
Uses dataclasses for clean, type-safe representation of knowledge entities.
No business logic - pure data representation.

TODO:
- [ ] Extend models for Phase 3+ as needed
- [ ] Add validation constraints (Phase 3)
- [ ] Support additional metadata (Phase 3)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class KnowledgeMetadata:
    """
    Metadata for a knowledge document.
    
    Attributes:
        source: Original file path or source identifier
        created_at: When the document was first processed
        updated_at: When the document was last updated
        version: Version identifier for the document
        tags: Optional categorization tags
        custom_fields: Additional metadata as key-value pairs
    """
    source: str
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSection:
    """
    A section within a knowledge document.
    
    Attributes:
        title: Section heading
        content: Section text content
        level: Heading level (1-6 for Markdown)
        order: Position in document
    """
    title: str
    content: str
    level: int
    order: int


@dataclass
class KnowledgeDocument:
    """
    A complete knowledge document with structured content.
    
    Attributes:
        id: Unique identifier for the document
        title: Document title
        sections: List of sections within the document
        metadata: Document metadata
        raw_content: Original document content
    """
    id: str
    title: str
    sections: List[KnowledgeSection]
    metadata: KnowledgeMetadata
    raw_content: str


@dataclass
class KnowledgeIndex:
    """
    Index entry for fast lookup of knowledge documents.
    
    Attributes:
        document_id: Reference to the knowledge document
        title: Document title for display
        keywords: Extracted keywords for searching
        source: Original source path
        metadata: Document metadata
    """
    document_id: str
    title: str
    keywords: List[str]
    source: str
    metadata: KnowledgeMetadata
