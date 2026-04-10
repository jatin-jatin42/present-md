"""LLM-based storylining engine — turns parsed documents into slide outlines."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from present_md.parser.md_parser import Document

logger = logging.getLogger(__name__)


# ─── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class SlideContent:
    """Content plan for a single slide."""
    slide_number: int = 0
    slide_type: str = ""  # "title", "agenda", "executive_summary", "content", "chart", "conclusion"
    title: str = ""
    key_message: str = ""
    bullet_points: list[str] = field(default_factory=list)
    notes: str = ""  # Additional context for the visual engine
    source_sections: list[str] = field(default_factory=list)  # Which sections this draws from
    has_table_data: bool = False
    has_numeric_data: bool = False
    table_data: Optional[dict] = None  # Raw table data if applicable


@dataclass
class SlideOutline:
    """The full slide outline for a presentation."""
    document_title: str = ""
    document_subtitle: str = ""
    slides: list[SlideContent] = field(default_factory=list)
    total_slides: int = 0


# ─── Engine ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert presentation designer and content strategist. 
Your job is to transform a long-form markdown report into a concise, compelling 
slide presentation outline.

RULES:
1. Create exactly {min_slides} to {max_slides} slides.
2. Each slide must have exactly ONE key message.
3. Follow this mandatory flow:
   - Slide 1: Title slide (title + subtitle)
   - Slide 2: Agenda / Table of Contents (list the main topics)
   - Slide 3: Executive Summary (key findings in 3-5 bullet points)
   - Slides 4 to N-1: Section content (one key insight per slide)
   - Slide N: Conclusion / Key Takeaways
4. Keep bullet points to maximum 4-5 per slide, each under 15 words.
5. Identify any tables/numerical data that should become charts.
6. Do NOT include every detail — synthesize and prioritize.
7. Never lose a MAJOR insight or finding from the report.

OUTPUT FORMAT — respond with ONLY valid JSON:
{{
  "document_title": "...",
  "document_subtitle": "...",
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "title",
      "title": "...",
      "key_message": "...",
      "bullet_points": [],
      "notes": "Any visual/layout notes",
      "source_sections": ["Section name(s) this draws from"],
      "has_table_data": false,
      "has_numeric_data": false,
      "table_data": null
    }}
  ]
}}
"""

USER_PROMPT_TEMPLATE = """Here is the markdown report to convert into a presentation outline:

DOCUMENT TITLE: {title}
DOCUMENT SUBTITLE: {subtitle}

SECTIONS:
{sections_summary}

TABLES FOUND:
{tables_summary}

NUMBER OF IMAGES: {image_count}

Please create a presentation outline with {min_slides}-{max_slides} slides."""


class Storyliner:
    """Uses an LLM to build a structured slide outline from a parsed document."""

    def __init__(self, api_key: str, model: str = "gpt-4o",
                 min_slides: int = 10, max_slides: int = 15):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.min_slides = min_slides
        self.max_slides = max_slides

    def build_outline(self, document: Document) -> SlideOutline:
        """Build a slide outline from the parsed document."""
        # Prepare summaries for the LLM
        sections_summary = self._summarize_sections(document)
        tables_summary = self._summarize_tables(document)

        system_prompt = SYSTEM_PROMPT.format(
            min_slides=self.min_slides,
            max_slides=self.max_slides,
        )
        user_prompt = USER_PROMPT_TEMPLATE.format(
            title=document.title or "Untitled",
            subtitle=document.subtitle or "",
            sections_summary=sections_summary,
            tables_summary=tables_summary,
            image_count=len(document.images),
            min_slides=self.min_slides,
            max_slides=self.max_slides,
        )

        try:
            logger.info(f"Calling LLM ({self.model}) for storylining...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            raw_output = response.choices[0].message.content
            logger.debug(f"LLM response length: {len(raw_output)} chars")
            return self._parse_response(raw_output, document)
        except Exception as e:
            logger.error(f"LLM storylining failed: {e}")
            return self._fallback_outline(document)

    def _summarize_sections(self, document: Document) -> str:
        """Create a summary of all sections for the LLM prompt."""
        parts = []
        for i, section in enumerate(document.sections):
            # Truncate long sections to keep prompt manageable and fit into AP rate limits
            text = section.full_text
            if len(text) > 500:
                text = text[:500] + "... [truncated]"

            content_types = []
            for block in section.content:
                if block.type == "table":
                    content_types.append("TABLE")
                elif block.type == "image":
                    content_types.append("IMAGE")
                elif block.type == "list":
                    content_types.append("LIST")
                else:
                    content_types.append("TEXT")

            parts.append(
                f"--- Section {i+1} (Level {section.level}): {section.title} ---\n"
                f"Content types: {', '.join(content_types) or 'TEXT'}\n"
                f"{text}\n"
            )
        return "\n".join(parts)

    def _summarize_tables(self, document: Document) -> str:
        """Create a summary of tables for the LLM prompt."""
        if not document.tables:
            return "No tables found."

        parts = []
        for i, table in enumerate(document.tables):
            title = table.title or f"Table {i+1}"
            headers = ", ".join(table.headers) if table.headers else "No headers"
            row_count = len(table.rows)
            has_numeric = "Yes" if table.has_numeric_data else "No"
            parts.append(
                f"Table {i+1}: '{title}' | Headers: [{headers}] | "
                f"Rows: {row_count} | Numeric data: {has_numeric}"
            )
        return "\n".join(parts)

    def _parse_response(self, raw: str, document: Document) -> SlideOutline:
        """Parse the LLM JSON response into a SlideOutline."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback: generate a basic outline
            return self._fallback_outline(document)

        outline = SlideOutline(
            document_title=data.get("document_title", document.title),
            document_subtitle=data.get("document_subtitle", document.subtitle),
        )

        for slide_data in data.get("slides", []):
            slide = SlideContent(
                slide_number=slide_data.get("slide_number", 0),
                slide_type=slide_data.get("slide_type", "content"),
                title=slide_data.get("title", ""),
                key_message=slide_data.get("key_message", ""),
                bullet_points=slide_data.get("bullet_points", []),
                notes=slide_data.get("notes", ""),
                source_sections=slide_data.get("source_sections", []),
                has_table_data=slide_data.get("has_table_data", False),
                has_numeric_data=slide_data.get("has_numeric_data", False),
                table_data=slide_data.get("table_data"),
            )
            outline.slides.append(slide)

        outline.total_slides = len(outline.slides)

        # Validate slide count
        if outline.total_slides < self.min_slides:
            logger.warning(
                f"LLM returned {outline.total_slides} slides, "
                f"minimum is {self.min_slides}"
            )
        elif outline.total_slides > self.max_slides:
            logger.warning(
                f"LLM returned {outline.total_slides} slides, "
                f"trimming to {self.max_slides}"
            )
            outline.slides = outline.slides[:self.max_slides]
            outline.total_slides = self.max_slides

        return outline

    def _fallback_outline(self, document: Document) -> SlideOutline:
        """Generate a basic fallback outline if LLM fails."""
        logger.warning("Using fallback outline generation")
        outline = SlideOutline(
            document_title=document.title,
            document_subtitle=document.subtitle,
        )

        # Slide 1: Title
        outline.slides.append(SlideContent(
            slide_number=1, slide_type="title",
            title=document.title, key_message=document.subtitle,
        ))

        # Slide 2: Agenda
        outline.slides.append(SlideContent(
            slide_number=2, slide_type="agenda",
            title="Agenda", bullet_points=document.toc_sections[:8],
        ))

        # Slide 3: Executive Summary
        exec_summary = document.executive_summary or ""
        outline.slides.append(SlideContent(
            slide_number=3, slide_type="executive_summary",
            title="Executive Summary",
            key_message=exec_summary[:200] if exec_summary else "Key findings overview",
        ))

        # Content slides from sections
        slide_num = 4
        for section in document.sections:
            if slide_num > self.max_slides - 1:
                break
            if section.level <= 2 and "executive summary" not in section.title.lower():
                points = []
                for block in section.content:
                    if block.type == "list":
                        points.extend(block.items[:3])
                    elif block.type == "paragraph" and len(block.text) < 100:
                        points.append(block.text)
                    if len(points) >= 4:
                        break

                outline.slides.append(SlideContent(
                    slide_number=slide_num, slide_type="content",
                    title=section.title, bullet_points=points[:5],
                    key_message=section.title,
                    source_sections=[section.title],
                ))
                slide_num += 1

        # Conclusion slide
        outline.slides.append(SlideContent(
            slide_number=slide_num, slide_type="conclusion",
            title="Key Takeaways", key_message="Summary of key findings",
        ))

        outline.total_slides = len(outline.slides)
        return outline
