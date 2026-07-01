"""
Markdown Parser - Document Processing

Title: Markdown Parser

Purpose:
Parses Markdown files and extracts structured knowledge from them.
Converts raw Markdown content into KnowledgeDocument objects with
hierarchical sections and metadata.

Responsibilities:
- Read Markdown files
- Extract headings and sections
- Maintain document hierarchy
- Preserve content structure
- Extract keywords from titles

TODO:
- [ ] Add advanced parsing features (Phase 3)
- [ ] Support code block extraction (Phase 3)
- [ ] Add metadata extraction from frontmatter (Phase 3)
- [ ] Improve keyword extraction (Phase 3)
"""

import re
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from knowledge.knowledge_models import (
    KnowledgeDocument,
    KnowledgeSection,
    KnowledgeMetadata,
)


class MarkdownParser:
    """
    Parser for Markdown documents.
    
    Converts raw Markdown content into structured KnowledgeDocument objects.
    Extracts sections based on heading hierarchy and preserves content.
    """

    @staticmethod
    def parse_file(file_path: str) -> KnowledgeDocument:
        """
        Parse a Markdown file into a KnowledgeDocument.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            KnowledgeDocument with parsed content and metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
            ValueError: If file is not a valid Markdown file
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.suffix.lower() == ".md":
            raise ValueError(f"File must be Markdown (.md): {file_path}")
        
        content = path.read_text(encoding="utf-8")
        
        return MarkdownParser.parse_content(
            content=content,
            source=file_path,
        )

    @staticmethod
    def parse_content(content: str, source: str = "inline") -> KnowledgeDocument:
        """
        Parse Markdown content string into a KnowledgeDocument.
        
        Args:
            content: Raw Markdown content
            source: Source identifier for metadata
            
        Returns:
            KnowledgeDocument with parsed content and metadata
        """
        # Extract title (first H1 heading or filename)
        title = MarkdownParser._extract_title(content)
        
        # Parse sections
        sections = MarkdownParser._extract_sections(content)
        
        # Generate document ID from title
        doc_id = MarkdownParser._generate_id(title)
        
        # Extract keywords from all section titles
        keywords = MarkdownParser._extract_keywords(sections)
        
        # Create metadata
        now = datetime.now()
        metadata = KnowledgeMetadata(
            source=source,
            created_at=now,
            updated_at=now,
            version="1.0",
            tags=[],
            custom_fields={},
        )
        
        # Create document
        document = KnowledgeDocument(
            id=doc_id,
            title=title,
            sections=sections,
            metadata=metadata,
            raw_content=content,
        )
        
        return document

    @staticmethod
    def _extract_title(content: str) -> str:
        """
        Extract the title from Markdown content.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            Title string (first H1 or "Untitled")
        """
        lines = content.split("\n")
        
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        
        return "Untitled Document"

    @staticmethod
    def _extract_sections(content: str) -> List[KnowledgeSection]:
        """
        Extract sections from Markdown content.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            List of KnowledgeSection objects in order
        """
        sections = []
        lines = content.split("\n")
        
        current_section = None
        section_content = []
        order = 0
        
        for line in lines:
            # Check if this line is a heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            
            if heading_match:
                # Save previous section if exists
                if current_section:
                    content_text = "\n".join(section_content).strip()
                    if content_text:
                        section = KnowledgeSection(
                            title=current_section["title"],
                            content=content_text,
                            level=current_section["level"],
                            order=current_section["order"],
                        )
                        sections.append(section)
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                current_section = {
                    "title": title,
                    "level": level,
                    "order": order,
                }
                section_content = []
                order += 1
            else:
                # Accumulate content
                if current_section:
                    section_content.append(line)
        
        # Save final section
        if current_section:
            content_text = "\n".join(section_content).strip()
            if content_text:
                section = KnowledgeSection(
                    title=current_section["title"],
                    content=content_text,
                    level=current_section["level"],
                    order=current_section["order"],
                )
                sections.append(section)
        
        return sections

    @staticmethod
    def _extract_keywords(sections: List[KnowledgeSection]) -> List[str]:
        """
        Extract keywords from section titles.
        
        Args:
            sections: List of knowledge sections
            
        Returns:
            List of keyword strings
        """
        keywords = []
        
        for section in sections:
            # Split title on common word boundaries
            words = re.findall(r"\w+", section.title.lower())
            keywords.extend(words)
        
        # Remove duplicates and return
        return list(set(keywords))

    @staticmethod
    def _generate_id(title: str) -> str:
        """
        Generate a unique ID from a title.
        
        Args:
            title: Document title
            
        Returns:
            ID string (lowercase, hyphens, no spaces)
        """
        # Convert to lowercase
        id_str = title.lower()
        
        # Replace spaces and special chars with hyphens
        id_str = re.sub(r"[^\w\s-]", "", id_str)
        id_str = re.sub(r"[-\s]+", "-", id_str)
        
        # Remove leading/trailing hyphens
        id_str = id_str.strip("-")
        
        return id_str or "untitled"
