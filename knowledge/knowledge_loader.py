"""
Knowledge Loader - File Management

Title: Knowledge Loader

Purpose:
Loads Markdown files from the filesystem and populates the knowledge registry.
Handles batch loading, directory traversal, and error handling.

Responsibilities:
- Discover Markdown files
- Load files into documents
- Populate registry
- Report loading status
- Handle errors gracefully

Design:
Clean interface for loading knowledge from files. Separates file I/O
from document parsing and storage. Extensible for future sources
(databases, APIs, etc. in Phase 3+).

TODO:
- [ ] Add recursive directory loading (Phase 2)
- [ ] Add progress reporting (Phase 3)
- [ ] Add format validation (Phase 3)
- [ ] Support other file formats (Phase 3)
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

from knowledge.knowledge_registry import KnowledgeRegistry
from knowledge.markdown_parser import MarkdownParser
from knowledge.knowledge_models import KnowledgeDocument


class KnowledgeLoader:
    """
    Loader for knowledge files into the knowledge registry.
    
    Discovers and loads Markdown files from the filesystem.
    Provides interfaces for single file and batch loading.
    """

    def __init__(self, registry: KnowledgeRegistry) -> None:
        """
        Initialize the knowledge loader.
        
        Args:
            registry: KnowledgeRegistry instance to populate
        """
        self.registry = registry
        self.logger = logging.getLogger(__name__)

    def load_file(self, file_path: str) -> Optional[KnowledgeDocument]:
        """
        Load a single Markdown file into the registry.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            Loaded KnowledgeDocument if successful, None if error
        """
        try:
            # Parse the file
            document = MarkdownParser.parse_file(file_path)
            
            # Add to registry
            self.registry.add_document(document)
            
            self.logger.info(f"Loaded: {file_path} -> {document.id}")
            return document
            
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {file_path}")
            return None
        except ValueError as e:
            self.logger.error(f"Invalid file format: {file_path} - {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return None

    def load_directory(
        self,
        directory_path: str,
        recursive: bool = True,
    ) -> Dict[str, bool]:
        """
        Load all Markdown files from a directory.
        
        Args:
            directory_path: Path to directory
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary mapping file paths to success status
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            self.logger.error(f"Directory not found: {directory_path}")
            return {}
        
        if not dir_path.is_dir():
            self.logger.error(f"Not a directory: {directory_path}")
            return {}
        
        # Find all Markdown files
        if recursive:
            md_files = list(dir_path.rglob("*.md"))
        else:
            md_files = list(dir_path.glob("*.md"))
        
        # Load each file
        results = {}
        for md_file in md_files:
            file_path = str(md_file)
            document = self.load_file(file_path)
            results[file_path] = document is not None
        
        self.logger.info(
            f"Loaded {sum(results.values())}/{len(results)} files "
            f"from {directory_path}"
        )
        
        return results

    def load_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Load multiple Markdown files into the registry.
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        for file_path in file_paths:
            document = self.load_file(file_path)
            results[file_path] = document is not None
        
        successful = sum(results.values())
        self.logger.info(f"Loaded {successful}/{len(file_paths)} files")
        
        return results

    def get_status(self) -> Dict[str, int]:
        """
        Get current loading status.
        
        Returns:
            Dictionary with registry statistics
        """
        documents = self.registry.get_all_documents()
        
        total_sections = sum(len(doc.sections) for doc in documents)
        total_source_chars = sum(len(doc.raw_content) for doc in documents)
        
        return {
            "total_documents": self.registry.document_count(),
            "total_sections": total_sections,
            "total_characters": total_source_chars,
        }
