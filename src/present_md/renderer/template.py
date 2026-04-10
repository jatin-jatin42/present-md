"""Template reader — extracts theme, fonts, colors, and layouts from Slide Master."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

logger = logging.getLogger(__name__)


@dataclass
class ThemeConfig:
    """Extracted theme configuration from a Slide Master."""
    colors: list[RGBColor] = field(default_factory=list)
    fonts: list[str] = field(default_factory=list)
    title_font: str = "Calibri"
    body_font: str = "Calibri"
    title_font_size: int = 28
    body_font_size: int = 14
    accent_colors: list[RGBColor] = field(default_factory=list)
    background_color: Optional[RGBColor] = None
    slide_width: int = 0
    slide_height: int = 0
    layout_names: list[str] = field(default_factory=list)


class TemplateReader:
    """Reads a Slide Master PPTX and extracts theme configuration."""

    def read(self, template_path: str) -> ThemeConfig:
        """Read a template PPTX and extract theme config."""
        logger.info(f"Reading template: {template_path}")
        prs = Presentation(template_path)
        theme = ThemeConfig()

        # Slide dimensions
        theme.slide_width = prs.slide_width
        theme.slide_height = prs.slide_height

        # Extract colors from theme
        theme.colors = self._extract_theme_colors(prs)
        theme.accent_colors = theme.colors[4:10] if len(theme.colors) > 4 else theme.colors

        # Extract fonts
        theme.fonts = self._extract_fonts(prs)
        if theme.fonts:
            theme.title_font = theme.fonts[0]
            theme.body_font = theme.fonts[1] if len(theme.fonts) > 1 else theme.fonts[0]

        # Extract layout names
        for layout in prs.slide_layouts:
            theme.layout_names.append(layout.name)

        logger.info(
            f"  Extracted: {len(theme.colors)} colors, "
            f"fonts: {theme.fonts}, "
            f"{len(theme.layout_names)} layouts"
        )
        return theme

    def _extract_theme_colors(self, prs: Presentation) -> list[RGBColor]:
        """Extract theme colors from the presentation."""
        colors = []
        try:
            # Access the theme element via the slide master
            slide_master = prs.slide_masters[0]
            theme_element = slide_master.element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}theme')

            if theme_element is None:
                # Try getting colors from the XML
                ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
                color_scheme = slide_master.element.find('.//a:clrScheme', ns)

                if color_scheme is not None:
                    color_names = [
                        'dk1', 'lt1', 'dk2', 'lt2',
                        'accent1', 'accent2', 'accent3', 'accent4',
                        'accent5', 'accent6', 'hlink', 'folHlink'
                    ]
                    for name in color_names:
                        elem = color_scheme.find(f'a:{name}', ns)
                        if elem is not None:
                            # Try srgbClr first, then sysClr
                            srgb = elem.find('a:srgbClr', ns)
                            if srgb is not None:
                                val = srgb.get('val', '000000')
                                colors.append(RGBColor.from_string(val))
                            else:
                                sys_clr = elem.find('a:sysClr', ns)
                                if sys_clr is not None:
                                    val = sys_clr.get('lastClr', '000000')
                                    colors.append(RGBColor.from_string(val))
        except Exception as e:
            logger.warning(f"Could not extract theme colors: {e}")

        # Fallback to professional defaults
        if not colors:
            colors = [
                RGBColor(0x2C, 0x3E, 0x50),  # Dark blue
                RGBColor(0xFF, 0xFF, 0xFF),  # White
                RGBColor(0x34, 0x49, 0x5E),  # Dark blue-gray
                RGBColor(0xEC, 0xF0, 0xF1),  # Light gray
                RGBColor(0x27, 0xAE, 0x60),  # Green (accent1)
                RGBColor(0x29, 0x80, 0xB9),  # Blue (accent2)
                RGBColor(0xE7, 0x4C, 0x3C),  # Red (accent3)
                RGBColor(0xF3, 0x9C, 0x12),  # Orange (accent4)
                RGBColor(0x8E, 0x44, 0xAD),  # Purple (accent5)
                RGBColor(0x16, 0xA0, 0x85),  # Teal (accent6)
            ]
        return colors

    def _extract_fonts(self, prs: Presentation) -> list[str]:
        """Extract font families from the theme."""
        fonts = []
        try:
            slide_master = prs.slide_masters[0]
            ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

            font_scheme = slide_master.element.find('.//a:fontScheme', ns)
            if font_scheme is not None:
                # Major font (titles)
                major = font_scheme.find('.//a:majorFont/a:latin', ns)
                if major is not None:
                    typeface = major.get('typeface', '')
                    if typeface:
                        fonts.append(typeface)

                # Minor font (body)
                minor = font_scheme.find('.//a:minorFont/a:latin', ns)
                if minor is not None:
                    typeface = minor.get('typeface', '')
                    if typeface:
                        fonts.append(typeface)
        except Exception as e:
            logger.warning(f"Could not extract fonts: {e}")

        # Fallback
        if not fonts:
            fonts = ["Calibri", "Calibri"]
        return fonts[:2]  # Max 2 fonts
