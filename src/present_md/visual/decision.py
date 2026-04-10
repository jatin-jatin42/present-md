"""Visual Decision Engine — implements the 'Infographic-First' approach."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from present_md.parser.md_parser import Document, TableData
from present_md.storyliner.engine import SlideOutline, SlideContent

logger = logging.getLogger(__name__)


# ─── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class VisualElement:
    """A single visual element on a slide."""
    element_type: str  # "text", "chart", "table", "process_flow", "timeline",
                       # "comparison", "icon_grid", "stat_callout", "key_message_box"
    content: dict = field(default_factory=dict)  # Element-specific data
    position: Optional[dict] = None  # Will be filled by layout engine


@dataclass
class SlidePlan:
    """Complete visual plan for a single slide."""
    slide_number: int = 0
    slide_type: str = ""  # from SlideContent
    title: str = ""
    key_message: str = ""
    visual_type: str = ""  # Overall visual approach for this slide
    elements: list[VisualElement] = field(default_factory=list)
    notes: str = ""


@dataclass
class PresentationPlan:
    """Complete visual plan for the entire presentation."""
    document_title: str = ""
    document_subtitle: str = ""
    slides: list[SlidePlan] = field(default_factory=list)


# ─── Engine ─────────────────────────────────────────────────────────────────────

VISUAL_SYSTEM_PROMPT = """You are a presentation visual design expert. 
For each slide, you must decide the BEST visual representation.

INFOGRAPHIC-FIRST RULE: Before using text, always ask "Can this be visualized?"

Available visual types:
- "stat_callout": For 1-3 key statistics with big numbers and labels
- "icon_grid": For 3-6 concepts with icons and short labels  
- "process_flow": For sequential steps or processes (3-6 steps)
- "timeline": For chronological events or phases
- "comparison": For comparing 2-4 items side by side
- "chart_bar": For comparing values across categories
- "chart_pie": For showing proportions
- "chart_line": For showing trends over time
- "table": For structured data with multiple columns
- "bullet_list": LAST RESORT — maximum 4-5 bullets, under 15 words each
- "key_message_box": For a single powerful statement with supporting context

For each slide, return ONLY valid JSON:
{{
  "slides": [
    {{
      "slide_number": 1,
      "visual_type": "...",
      "elements": [
        {{
          "element_type": "...",
          "content": {{}}
        }}
      ]
    }}
  ]
}}
"""


class VisualDecisionEngine:
    """Decides how each slide's content should be visually represented."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def decide(self, outline: SlideOutline, document: Document) -> PresentationPlan:
        """Make visual decisions for all slides."""
        plan = PresentationPlan(
            document_title=outline.document_title,
            document_subtitle=outline.document_subtitle,
        )

        # Process slides in batches for efficiency
        # Batch all slides into one LLM call
        slides_description = self._describe_slides(outline, document)

        try:
            visual_decisions = self._call_llm(slides_description)
        except Exception as e:
            logger.warning(f"LLM visual decision failed: {e}, using fallback")
            visual_decisions = None

        for slide_content in outline.slides:
            slide_plan = self._create_slide_plan(
                slide_content, document, visual_decisions
            )
            plan.slides.append(slide_plan)

        return plan

    def _describe_slides(self, outline: SlideOutline, document: Document) -> str:
        """Create a description of all slides for the LLM."""
        parts = []
        for slide in outline.slides:
            table_info = ""
            if slide.has_table_data:
                # Find matching table from document
                for table in document.tables:
                    if table.title and any(
                        table.title.lower() in s.lower()
                        for s in slide.source_sections
                    ):
                        table_info = f" | Table: {table.title} ({len(table.rows)} rows)"
                        break

            parts.append(
                f"Slide {slide.slide_number} ({slide.slide_type}): "
                f"{slide.title}\n"
                f"  Key message: {slide.key_message}\n"
                f"  Bullets: {slide.bullet_points}\n"
                f"  Has numeric data: {slide.has_numeric_data}{table_info}"
            )
        return "\n\n".join(parts)

    def _call_llm(self, slides_description: str) -> Optional[dict]:
        """Call LLM for visual decisions."""
        logger.info("Calling LLM for visual decisions...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": VISUAL_SYSTEM_PROMPT},
                {"role": "user", "content": f"Decide visual types for these slides:\n\n{slides_description}"},
            ],
            temperature=0.2,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)

    def _create_slide_plan(
        self,
        slide_content: SlideContent,
        document: Document,
        visual_decisions: Optional[dict],
    ) -> SlidePlan:
        """Create a SlidePlan for a single slide."""
        plan = SlidePlan(
            slide_number=slide_content.slide_number,
            slide_type=slide_content.slide_type,
            title=slide_content.title,
            key_message=slide_content.key_message,
            notes=slide_content.notes,
        )

        # Try to get LLM decision
        llm_visual_type = None
        llm_elements = []
        if visual_decisions:
            for slide_dec in visual_decisions.get("slides", []):
                if slide_dec.get("slide_number") == slide_content.slide_number:
                    llm_visual_type = slide_dec.get("visual_type", "")
                    llm_elements = slide_dec.get("elements", [])
                    break

        # Use LLM decision or fallback
        if llm_visual_type:
            plan.visual_type = llm_visual_type
            for elem in llm_elements:
                plan.elements.append(VisualElement(
                    element_type=elem.get("element_type", "text"),
                    content=elem.get("content", {}),
                ))
        else:
            # Fallback visual decision
            plan.visual_type, plan.elements = self._fallback_decision(
                slide_content, document
            )

        return plan

    def _fallback_decision(
        self, slide: SlideContent, document: Document
    ) -> tuple[str, list[VisualElement]]:
        """Fallback visual decision when LLM is unavailable."""
        elements = []

        if slide.slide_type == "title":
            return "key_message_box", [VisualElement(
                element_type="key_message_box",
                content={"title": slide.title, "subtitle": slide.key_message},
            )]

        elif slide.slide_type == "agenda":
            return "bullet_list", [VisualElement(
                element_type="bullet_list",
                content={"items": slide.bullet_points},
            )]

        elif slide.slide_type == "executive_summary":
            return "bullet_list", [VisualElement(
                element_type="bullet_list",
                content={"items": slide.bullet_points[:5]},
            )]

        elif slide.has_numeric_data or slide.has_table_data:
            # Find matching table
            for table in document.tables:
                if table.has_numeric_data:
                    return "chart_bar", [VisualElement(
                        element_type="chart_bar",
                        content={
                            "headers": table.headers,
                            "rows": table.rows,
                            "title": table.title or slide.title,
                        },
                    )]
            return "table", [VisualElement(
                element_type="table",
                content={"title": slide.title},
            )]

        elif slide.slide_type == "conclusion":
            return "icon_grid", [VisualElement(
                element_type="icon_grid",
                content={"items": slide.bullet_points},
            )]

        else:
            # Default: try icon_grid for short items, bullet_list otherwise
            if slide.bullet_points and all(
                len(bp) < 50 for bp in slide.bullet_points
            ):
                return "icon_grid", [VisualElement(
                    element_type="icon_grid",
                    content={"items": slide.bullet_points},
                )]
            return "bullet_list", [VisualElement(
                element_type="bullet_list",
                content={"items": slide.bullet_points[:6]},
            )]
