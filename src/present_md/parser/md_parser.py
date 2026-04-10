"""Markdown parser — converts .md files into a structured Document object."""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

import mistune

logger = logging.getLogger(__name__)


# ─── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class TableData:
    """Represents a parsed markdown table."""
    title: Optional[str] = None
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    alignment: list[str] = field(default_factory=list)

    @property
    def has_numeric_data(self) -> bool:
        """Check if table contains numeric values."""
        for row in self.rows:
            for cell in row:
                cleaned = re.sub(r'[,$%\s]', '', cell)
                try:
                    float(cleaned)
                    return True
                except ValueError:
                    continue
        return False


@dataclass
class ImageData:
    """Represents an embedded image (typically base64)."""
    alt_text: str = ""
    src: str = ""
    is_base64: bool = False


@dataclass
class ContentBlock:
    """A single block of content within a section."""
    type: str  # "paragraph", "list", "table", "image", "heading"
    text: str = ""
    level: int = 0  # heading level (1-6)
    items: list[str] = field(default_factory=list)  # for lists
    table: Optional[TableData] = None
    image: Optional[ImageData] = None


@dataclass
class Section:
    """A section defined by a heading and its content blocks."""
    title: str = ""
    level: int = 1  # heading level
    content: list[ContentBlock] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Get all text content in this section."""
        parts = [self.title]
        for block in self.content:
            if block.type == "paragraph":
                parts.append(block.text)
            elif block.type == "list":
                parts.extend(block.items)
            elif block.type == "table" and block.table:
                parts.append(f"[Table: {block.table.title or 'Untitled'}]")
        return "\n".join(parts)


@dataclass
class Document:
    """The full parsed markdown document."""
    title: str = ""
    subtitle: str = ""
    sections: list[Section] = field(default_factory=list)
    tables: list[TableData] = field(default_factory=list)
    images: list[ImageData] = field(default_factory=list)
    raw_text: str = ""

    @property
    def executive_summary(self) -> Optional[str]:
        """Find the executive summary section if it exists."""
        for section in self.sections:
            if "executive summary" in section.title.lower():
                return section.full_text
        return None

    @property
    def toc_sections(self) -> list[str]:
        """Get top-level section titles for agenda/TOC."""
        return [s.title for s in self.sections if s.level <= 2 and s.title]


# ─── Parser ─────────────────────────────────────────────────────────────────────

class MarkdownParser:
    """Parses a Markdown file into a structured Document."""

    def parse_file(self, filepath: str) -> Document:
        """Parse a markdown file from disk."""
        logger.info(f"Reading file: {filepath}")
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()
        return self.parse(raw_text)

    def parse(self, text: str) -> Document:
        """Parse raw markdown text into a Document."""
        doc = Document(raw_text=text)

        # Use mistune v3 to get AST tokens (with table plugin)
        md = mistune.Markdown()
        mistune.plugins.table.table(md)
        tokens, _state = md.parse(text)

        current_section: Optional[Section] = None
        pending_table_title: Optional[str] = None

        for node in tokens:
            node_type = node.get("type", "")

            if node_type == "heading":
                heading_text = self._extract_text(node.get("children", []))
                level = node.get("attrs", {}).get("level", 1)

                # Set document title/subtitle from top headings
                if level == 1 and not doc.title:
                    doc.title = heading_text
                    continue
                elif level == 3 and not doc.subtitle and not doc.sections:
                    doc.subtitle = heading_text
                    continue

                # Skip table of contents section
                if "table of contents" in heading_text.lower():
                    current_section = None
                    continue

                # Start a new section
                current_section = Section(title=heading_text, level=level)
                doc.sections.append(current_section)

            elif node_type == "paragraph":
                para_text = self._extract_text(node.get("children", []))

                # Check for "Title: ..." pattern (table title)
                title_match = re.match(r'^Title:\s*(.+)$', para_text)
                if title_match:
                    pending_table_title = title_match.group(1).strip()
                    continue

                # Check for embedded images
                images = self._extract_images(node.get("children", []))
                if images:
                    for img in images:
                        doc.images.append(img)
                        if current_section:
                            current_section.content.append(ContentBlock(
                                type="image", image=img
                            ))
                    continue

                # Skip ToC-like paragraphs (lines starting with [N.
                if re.match(r'^\[[\d.]+', para_text):
                    continue

                # Regular paragraph
                if para_text.strip() and current_section:
                    current_section.content.append(ContentBlock(
                        type="paragraph", text=para_text
                    ))

            elif node_type == "list":
                items = self._extract_list_items(node)
                if current_section and items:
                    current_section.content.append(ContentBlock(
                        type="list", items=items
                    ))

            elif node_type == "table":
                table = self._extract_table(node)
                if pending_table_title:
                    table.title = pending_table_title
                    pending_table_title = None
                doc.tables.append(table)
                if current_section:
                    current_section.content.append(ContentBlock(
                        type="table", table=table
                    ))

        logger.info(
            f"Parsed document: title='{doc.title}', "
            f"{len(doc.sections)} sections, "
            f"{len(doc.tables)} tables, "
            f"{len(doc.images)} images"
        )
        return doc

    def _extract_text(self, children: list) -> str:
        """Recursively extract plain text from AST children."""
        parts = []
        for child in children:
            if isinstance(child, str):
                parts.append(child)
            elif isinstance(child, dict):
                child_type = child.get("type", "")
                if child_type == "text":
                    parts.append(child.get("raw", child.get("text", "")))
                elif child_type == "codespan":
                    parts.append(child.get("raw", child.get("text", "")))
                elif child_type == "link":
                    link_text = self._extract_text(child.get("children", []))
                    parts.append(link_text)
                elif child_type == "strong":
                    parts.append(self._extract_text(child.get("children", [])))
                elif child_type == "emphasis":
                    parts.append(self._extract_text(child.get("children", [])))
                elif "children" in child:
                    parts.append(self._extract_text(child["children"]))
                elif "raw" in child:
                    parts.append(child["raw"])
        return "".join(parts)

    def _extract_images(self, children: list) -> list[ImageData]:
        """Extract image data from AST children."""
        images = []
        for child in children:
            if isinstance(child, dict) and child.get("type") == "image":
                src = child.get("src", child.get("attrs", {}).get("src", ""))
                alt = child.get("alt", child.get("attrs", {}).get("alt", ""))
                if isinstance(alt, list):
                    alt = self._extract_text(alt)
                images.append(ImageData(
                    alt_text=alt or "",
                    src=src,
                    is_base64=src.startswith("data:image/"),
                ))
        return images

    def _extract_list_items(self, node: dict) -> list[str]:
        """Extract items from a list node."""
        items = []
        for child in node.get("children", []):
            if child.get("type") == "list_item":
                text = self._extract_text(child.get("children", []))
                # Clean up nested paragraph wrappers
                text = text.strip()
                if text:
                    items.append(text)
        return items

    def _extract_table(self, node: dict) -> TableData:
        """Extract table data from a table node (mistune v3 format)."""
        table = TableData()
        children = node.get("children", [])

        for child in children:
            child_type = child.get("type", "")
            if child_type == "table_head":
                # In mistune v3, table_head contains cells directly
                table.headers = [
                    self._extract_text(cell.get("children", []))
                    for cell in child.get("children", [])
                    if cell.get("type") == "table_cell"
                ]
            elif child_type == "table_body":
                for row in child.get("children", []):
                    if row.get("type") == "table_row":
                        row_data = [
                            self._extract_text(cell.get("children", []))
                            for cell in row.get("children", [])
                            if cell.get("type") == "table_cell"
                        ]
                        table.rows.append(row_data)

        return table
