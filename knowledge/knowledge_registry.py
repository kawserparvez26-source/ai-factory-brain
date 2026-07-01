"""
Knowledge Registry - In-Memory Storage

Title: Knowledge Registry

Purpose:
Maintains an in-memory registry of all loaded knowledge documents.
Provides interfaces for storing, retrieving, and searching documents.
Acts as the central knowledge store for the reasoning system.

Responsibilities:
- Store knowledge documents in memory
- Maintain search indexes
- Provide retrieval interfaces
- Support keyword-based lookup
- Track document metadata

Design:
Pure data storage with no business logic. Documents are stored with
their index entries for fast retrieval. Extensible for future search
improvements (Phase 3+).

TODO:
- [ ] Add advanced search capabilities (Phase 3)
- [ ] Implement persistence layer (Phase 3)
- [ ] Add document update/versioning (Phase 3)
- [ ] Support filtering and aggregation (Phase 3)
"""

from typing import Dict, List, Optional
from knowledge.knowledge_models import (
    KnowledgeDocument,
    KnowledgeIndex,
)


class KnowledgeRegistry:
    """
    In-memory registry for knowledge documents.
    
    Stores documents and maintains indexes for efficient retrieval.
    Provides clean interfaces for document storage and search.
    """

    def __init__(self) -> None:
        """
        Initialize an empty knowledge registry.
        """
        # Map of document_id -> KnowledgeDocument
        self._documents: Dict[str, KnowledgeDocument] = {}
        
        # Map of document_id -> KnowledgeIndex (for fast lookup)
        self._indexes: Dict[str, KnowledgeIndex] = {}
        
        # Map of keyword -> list of document_ids (for search)
        self._keyword_index: Dict[str, List[str]] = {}

    def add_document(self, document: KnowledgeDocument) -> None:
        """
        Add a knowledge document to the registry.
        
        Args:
            document: KnowledgeDocument to add
        """
        doc_id = document.id
        
        # Store document
        self._documents[doc_id] = document
        
        # Create and store index entry
        index_entry = KnowledgeIndex(
            document_id=doc_id,
            title=document.title,
            keywords=self._extract_keywords_from_document(document),
            source=document.metadata.source,
            metadata=document.metadata,
        )
        self._indexes[doc_id] = index_entry
        
        # Update keyword index
        for keyword in index_entry.keywords:
            if keyword not in self._keyword_index:
                self._keyword_index[keyword] = []
            
            if doc_id not in self._keyword_index[keyword]:
                self._keyword_index[keyword].append(doc_id)

    def get_document(self, document_id: str) -> Optional[KnowledgeDocument]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: ID of document to retrieve
            
        Returns:
            KnowledgeDocument if found, None otherwise
        """
        return self._documents.get(document_id)

    def get_index(self, document_id: str) -> Optional[KnowledgeIndex]:
        """
        Retrieve an index entry by document ID.
        
        Args:
            document_id: ID of document
            
        Returns:
            KnowledgeIndex if found, None otherwise
        """
        return self._indexes.get(document_id)

    def search_by_keyword(self, keyword: str) -> List[KnowledgeDocument]:
        """
        Search for documents containing a keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of KnowledgeDocuments containing the keyword
        """
        keyword_lower = keyword.lower()
        doc_ids = self._keyword_index.get(keyword_lower, [])
        
        documents = []
        for doc_id in doc_ids:
            doc = self._documents.get(doc_id)
            if doc:
                documents.append(doc)
        
        return documents

    def search_by_title(self, title_query: str) -> List[KnowledgeDocument]:
        """
        Search for documents by title.
        
        Args:
            title_query: Partial or full title to search for
            
        Returns:
            List of KnowledgeDocuments with matching titles
        """
        query_lower = title_query.lower()
        
        matching_documents = []
        for document in self._documents.values():
            if query_lower in document.title.lower():
                matching_documents.append(document)
        
        return matching_documents

    def get_all_documents(self) -> List[KnowledgeDocument]:
        """
        Get all documents in the registry.
        
        Returns:
            List of all KnowledgeDocuments
        """
        return list(self._documents.values())

    def get_all_indexes(self) -> List[KnowledgeIndex]:
        """
        Get all index entries in the registry.
        
        Returns:
            List of all KnowledgeIndex entries
        """
        return list(self._indexes.values())

    def document_count(self) -> int:
        """
        Get the total number of documents in the registry.
        
        Returns:
            Count of documents
        """
        return len(self._documents)

    def contains_document(self, document_id: str) -> bool:
        """
        Check if a document exists in the registry.
        
        Args:
            document_id: ID to check
            
        Returns:
            True if document exists, False otherwise
        """
        return document_id in self._documents

    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the registry.
        
        Args:
            document_id: ID of document to remove
            
        Returns:
            True if document was removed, False if not found
        """
        if document_id not in self._documents:
            return False
        
        # Remove document
        del self._documents[document_id]
        
        # Remove index
        if document_id in self._indexes:
            index_entry = self._indexes[document_id]
            del self._indexes[document_id]
            
            # Remove from keyword index
            for keyword in index_entry.keywords:
                if keyword in self._keyword_index:
                    if document_id in self._keyword_index[keyword]:
                        self._keyword_index[keyword].remove(document_id)
                    
                    # Clean up empty keyword entries
                    if not self._keyword_index[keyword]:
                        del self._keyword_index[keyword]
        
        return True

    def _extract_keywords_from_document(
        self,
        document: KnowledgeDocument,
    ) -> List[str]:
        """
        Extract searchable keywords from a document.
        
        Args:
            document: Document to extract keywords from
            
        Returns:
            List of unique keywords
        """
        keywords = set()
        
        # Add title words
        title_words = document.title.lower().split()
        keywords.update(title_words)
        
        # Add section title words
        for section in document.sections:
            section_words = section.title.lower().split()
            keywords.update(section_words)
        
        return list(keywords)
