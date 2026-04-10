"""Main pipeline orchestrator for present-md."""

import logging

from present_md.parser.md_parser import MarkdownParser
from present_md.storyliner.engine import Storyliner
from present_md.visual.decision import VisualDecisionEngine
from present_md.layout.grid import GridSystem
from present_md.renderer.template import TemplateReader
from present_md.renderer.builder import PresentationBuilder

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class PresentationPipeline:
    """Orchestrates the full Markdown → PPTX conversion pipeline."""

    def __init__(self, api_key: str, model: str = "gpt-4o",
                 min_slides: int = 10, max_slides: int = 15):
        self.api_key = api_key
        self.model = model
        self.min_slides = min_slides
        self.max_slides = max_slides

    def run(self, input_path: str, template_path: str, output_path: str):
        """Execute the full pipeline."""
        # --- Step 1: Parse Markdown ---
        logger.info("Step 1/5: Parsing Markdown...")
        parser = MarkdownParser()
        document = parser.parse_file(input_path)
        logger.info(
            f"  Parsed {len(document.sections)} sections, "
            f"{len(document.tables)} tables, "
            f"{len(document.images)} images"
        )

        # --- Step 2: Storyline via LLM ---
        logger.info("Step 2/5: Building storyline via LLM...")
        storyliner = Storyliner(
            api_key=self.api_key,
            model=self.model,
            min_slides=self.min_slides,
            max_slides=self.max_slides,
        )
        slide_outline = storyliner.build_outline(document)
        logger.info(f"  Generated {len(slide_outline.slides)} slide outlines")

        # --- Step 3: Visual Decisions ---
        logger.info("Step 3/5: Making visual decisions (Infographic-First)...")
        visual_engine = VisualDecisionEngine(
            api_key=self.api_key,
            model=self.model,
        )
        slide_plan = visual_engine.decide(slide_outline, document)
        logger.info("  Visual types assigned to all slides")

        # --- Step 4: Read Template & Calculate Layout ---
        logger.info("Step 4/5: Reading template and calculating layouts...")
        template_reader = TemplateReader()
        theme = template_reader.read(template_path)
        logger.info(f"  Theme: {len(theme.colors)} colors, fonts: {theme.fonts}")

        grid = GridSystem(theme)

        # --- Step 5: Render PPTX ---
        logger.info("Step 5/5: Rendering PPTX...")
        builder = PresentationBuilder(theme, grid, template_path)
        builder.build(slide_plan)
        builder.save(output_path)
        logger.info(f"  Saved to {output_path}")
