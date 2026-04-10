"""Grid system for slide layout calculation.

Implements a fixed grid with margins, padding, and snap-to-grid positioning.
All measurements are in EMUs (English Metric Units) — pptx standard.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from pptx.util import Inches, Pt, Emu

logger = logging.getLogger(__name__)

# Standard slide dimensions (10" x 7.5" widescreen)
SLIDE_WIDTH = Inches(10)
SLIDE_HEIGHT = Inches(7.5)

# Margins
MARGIN_LEFT = Inches(0.6)
MARGIN_RIGHT = Inches(0.6)
MARGIN_TOP = Inches(0.5)
MARGIN_BOTTOM = Inches(0.4)

# Content area
CONTENT_LEFT = MARGIN_LEFT
CONTENT_TOP = Inches(1.5)  # Below title area
CONTENT_WIDTH = SLIDE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
CONTENT_HEIGHT = SLIDE_HEIGHT - CONTENT_TOP - MARGIN_BOTTOM

# Title area
TITLE_LEFT = MARGIN_LEFT
TITLE_TOP = MARGIN_TOP
TITLE_WIDTH = SLIDE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
TITLE_HEIGHT = Inches(0.8)

# Subtitle / key message area
SUBTITLE_TOP = TITLE_TOP + TITLE_HEIGHT
SUBTITLE_HEIGHT = Inches(0.4)

# Standard spacing
ELEMENT_GAP = Inches(0.2)  # Gap between elements
INNER_PADDING = Inches(0.15)  # Padding inside containers


@dataclass
class Rect:
    """A rectangle position/size in EMUs."""
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def shrink(self, padding: int) -> Rect:
        """Return a new Rect shrunk by padding on all sides."""
        return Rect(
            left=self.left + padding,
            top=self.top + padding,
            width=self.width - 2 * padding,
            height=self.height - 2 * padding,
        )


class GridSystem:
    """Fixed grid system for consistent slide layouts."""

    def __init__(self, theme=None):
        self.theme = theme
        self.slide_width = SLIDE_WIDTH
        self.slide_height = SLIDE_HEIGHT

    @property
    def title_rect(self) -> Rect:
        """Get the title area rectangle."""
        return Rect(TITLE_LEFT, TITLE_TOP, TITLE_WIDTH, TITLE_HEIGHT)

    @property
    def subtitle_rect(self) -> Rect:
        """Get the subtitle/key message area rectangle."""
        return Rect(TITLE_LEFT, SUBTITLE_TOP, TITLE_WIDTH, SUBTITLE_HEIGHT)

    @property
    def content_rect(self) -> Rect:
        """Get the main content area rectangle."""
        return Rect(CONTENT_LEFT, CONTENT_TOP, CONTENT_WIDTH, CONTENT_HEIGHT)

    def split_horizontal(self, rect: Rect, n: int, gap: int = None) -> list[Rect]:
        """Split a rectangle into n equal horizontal columns."""
        gap = gap if gap is not None else ELEMENT_GAP
        total_gap = gap * (n - 1)
        col_width = (rect.width - total_gap) // n

        rects = []
        current_left = rect.left
        for i in range(n):
            rects.append(Rect(current_left, rect.top, col_width, rect.height))
            current_left += col_width + gap
        return rects

    def split_vertical(self, rect: Rect, n: int, gap: int = None) -> list[Rect]:
        """Split a rectangle into n equal vertical rows."""
        gap = gap if gap is not None else ELEMENT_GAP
        total_gap = gap * (n - 1)
        row_height = (rect.height - total_gap) // n

        rects = []
        current_top = rect.top
        for i in range(n):
            rects.append(Rect(rect.left, current_top, rect.width, row_height))
            current_top += row_height + gap
        return rects

    def grid(self, rect: Rect, rows: int, cols: int,
             gap: int = None) -> list[list[Rect]]:
        """Create a rows × cols grid of rectangles."""
        row_rects = self.split_vertical(rect, rows, gap)
        result = []
        for row_rect in row_rects:
            col_rects = self.split_horizontal(row_rect, cols, gap)
            result.append(col_rects)
        return result

    def center_in(self, outer: Rect, width: int, height: int) -> Rect:
        """Center a rectangle of given size within an outer rectangle."""
        left = outer.left + (outer.width - width) // 2
        top = outer.top + (outer.height - height) // 2
        return Rect(left, top, width, height)

    def stat_callout_layout(self, n_stats: int) -> list[Rect]:
        """Layout for stat callout boxes (1-4 stats)."""
        n_stats = min(n_stats, 4)
        content = self.content_rect
        # Center stats vertically, split horizontally
        stat_height = Inches(2.5)
        centered = self.center_in(content, content.width, stat_height)
        return self.split_horizontal(centered, n_stats, Inches(0.3))

    def icon_grid_layout(self, n_items: int) -> list[Rect]:
        """Layout for icon + label grid (2-6 items)."""
        n_items = min(n_items, 6)
        content = self.content_rect

        if n_items <= 3:
            return self.split_horizontal(content, n_items, Inches(0.4))
        else:
            # 2 rows
            rows = 2
            cols = (n_items + 1) // 2
            grid = self.grid(content, rows, cols, Inches(0.3))
            rects = []
            for row in grid:
                rects.extend(row)
            return rects[:n_items]

    def process_flow_layout(self, n_steps: int) -> list[Rect]:
        """Layout for process flow (3-6 steps)."""
        n_steps = min(n_steps, 6)
        content = self.content_rect
        step_height = Inches(2.0)
        centered = self.center_in(content, content.width, step_height)
        return self.split_horizontal(centered, n_steps, Inches(0.15))

    def chart_layout(self) -> Rect:
        """Layout for a chart — fills most of the content area."""
        content = self.content_rect
        return content.shrink(Inches(0.1))

    def table_layout(self) -> Rect:
        """Layout for a table."""
        return self.content_rect

    def bullet_layout(self) -> Rect:
        """Layout for bullet points."""
        content = self.content_rect
        # Indent slightly from left
        return Rect(
            content.left + Inches(0.3),
            content.top,
            content.width - Inches(0.6),
            content.height,
        )

    def two_column_layout(self) -> tuple[Rect, Rect]:
        """Layout for two-column content."""
        cols = self.split_horizontal(self.content_rect, 2, Inches(0.4))
        return cols[0], cols[1]
