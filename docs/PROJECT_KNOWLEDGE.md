# present-md — Project Knowledge Base

> **What this file is**: A single source of truth for any AI assistant (or human) working on this project. Read this before doing anything.

---

## 1. PROJECT OVERVIEW

**Project Name**: `present-md`

**One-liner**: An automated, intelligent pipeline that converts Markdown (`.md`) files into structured, visually appealing, non-copyrighted `.pptx` presentations.

**Core Philosophy**: Slides must be **"designed," not just "placed."** The system must employ an **"Infographic-First"** approach — transforming text into structured visual frameworks rather than simple bulleted lists.

---

## 2. SYSTEM ARCHITECTURE & INTERFACE

- **Execution Interface**: A graphical UI is **NOT required**. The system should be executable via CLI, script, or API.
- **Component-Based Pipeline**: Must utilize meaningful logic, reasoning, and orchestration. Solutions that simply wrap a single API call are **strictly prohibited**.
- **Modularity**: Must separate concerns into:
  1. **Parsing** — ingesting and understanding the markdown
  2. **Storylining** — structuring content into a narrative
  3. **Layout Calculation** — grid/alignment/visual decision-making
  4. **Visual Generation** — infographics, charts, tables
  5. **PPTX Rendering** — assembling the final output
- **Tech Stack**: Open to Python, Node.js, AI agent frameworks, LLMs, APIs, and no-code tools.

---

## 3. INPUTS & OUTPUTS

### Inputs
| # | Type | Description | Constraints |
|---|------|-------------|-------------|
| 1 | `.md` file | Markdown text with headers, lists, paragraphs, tables, and potentially embedded base64 images | Max 5 MB |
| 2 | `.pptx` file | Slide Master template defining themes, layouts, fonts, colors, backgrounds | Provided per-presentation |

### Outputs
| # | Type | Description | Constraints |
|---|------|-------------|-------------|
| 1 | `.pptx` file | Valid PowerPoint file | Compatible with MS 365, Google Slides, LibreOffice Impress |
| 2 | — | — | **Slide count: strictly 10–15 slides** |

---

## 4. FUNCTIONAL REQUIREMENTS

### FR1: Input Handling & Content Extraction
- Accept `.md` files up to **5 MB**
- Process content to create a structured narrative: `Title → Agenda → Executive Summary → Sections → Conclusion`
- Dynamically distribute content to enforce a **hard limit of 10–15 slides**
- Extract hierarchy accurately:
  - **Primary Message** = Title
  - **Context** = Subtitle
  - **Supporting Points** = Body
- Enforce **1 key message per slide**

### FR2: Master Slide & Theme Enforcement
- The system **must** inherit and apply the provided Slide Master's design language (fonts, colors, backgrounds)
- If specific content requires a new layout, generate one programmatically — but it **must strictly adhere** to the Master's core design language
- **Custom themes or independent styling are strictly prohibited**

### FR3: "Infographic-First" Visual Generation
- **Decision Gate**: Before rendering text, evaluate: *"Can this be visualized?"*
- **Visual Substitutions** — convert text into:
  - Icons + short labels
  - Process flows
  - Timelines
  - Comparison tables
  - Data visuals
- **Text Fallback**: If content cannot be visualized, text must be kept minimal (**max 6–8 lines**). Strict avoidance of "bullet overload" and paragraphs.

### FR4: Automated Data Visualization (Charts & Tables)
- **Conditional Trigger**: Charts and tables must *only* be generated if the markdown contains numerical or tabular data. If none exists, gracefully skip chart generation.
- **Formatting Rules**:
  - Numbers must be **visually dominant**
  - Table text must be **middle-aligned**
  - Tables must **emphasize trends** rather than looking like raw Excel data

---

## 5. DESIGN & LAYOUT SPECIFICATIONS (Strict Guidelines)

### 5.1 Grid & Alignment System (Non-Negotiable)
- **Fixed Grid**: All elements must snap to the grid
- **Margins**: Elements must strictly respect slide margins with **zero overflow**
- **Spacing**: Consistent padding inside elements and equal spacing between elements. No floating or randomly placed boxes.
- **Baselines**: Align text baselines evenly across different shapes

### 5.2 Typography & Styling
- **Fonts**: Maximum of **2 fonts** per presentation. Font sizes must clearly differentiate visual hierarchy.
- **Colors**: Use the **theme-based palette exclusively**. No random colors. Ensure high contrast for readability.
- **Shapes**: Clean containers, minimal borders, consistent corner radii. Do NOT add internal margins to text boxes that lack a fill color.
- **Empty Space**: Utilize negative space properly. Slides should look balanced — not crowded or awkwardly empty.

---

## 6. NON-FUNCTIONAL REQUIREMENTS

- **Output Compatibility**: `.pptx` must open flawlessly in Microsoft 365, Google Slides, and LibreOffice Impress
- **Robustness**: Must not crash on malformed markdown or missing data — use graceful fallbacks
- **Validation**: Must be validated against **all** provided test cases (24 markdown files)

---

## 7. CONSTRAINTS & LEGAL

| Constraint | Detail |
|-----------|--------|
| **Copyright** | Absolutely NO downloading copyrighted images or using commercial PPT templates. All infographics and charts must be programmatically generated and non-copyrighted. |
| **IP Transfer** | Full Intellectual Property rights of the submitted codebase must be transferred to EZ. |
| **Architecture** | Solutions wrapping a single API call are strictly prohibited. Meaningful system design, extraction logic, and orchestration are mandatory. |

---

## 8. DELIVERABLES

1. **GitHub Repository** — clean, well-documented codebase
2. **Comprehensive `README.md`** — setup instructions, run steps, system architecture, and design decisions
3. **Demo Video (3–8 minutes)** — showcasing the conversion of at least **two different markdown inputs**, demonstrating logic, varying slide counts, and system complexity

---

## 9. SAMPLE FILES (Reference Implementations)

Located in `Guidelines/Sample Files/`. Each sample has:

| File | Purpose |
|------|---------|
| `<Topic>.md` | **Input** markdown (the source content) |
| `Template_<Topic>.pptx` | **Slide Master** template (defines visual styling) |
| `<Topic>.pptx` | **Expected output** (reference result to aspire to) |

### Available Samples:

1. **AI Bubble: Detection, Prevention, and Investment Strategies**
   - MD: ~2.3 MB (very large, includes base64 images)
   - Template: ~4.4 MB
   - Output: ~40 MB

2. **Accenture Tech Acquisition Analysis**
   - MD: ~149 KB (moderate size)
   - Template: ~15.8 MB
   - Output: ~43 MB

3. **UAE Progress toward 2050 Solar Energy Targets**
   - MD: ~1.1 MB (includes base64 images)
   - Template: ~8.2 MB
   - Output: ~58 MB
   - Also has a reference PDF export

---

## 10. TEST CASES (24 Markdown Files)

Located in `Guidelines/Test Cases/`. These are input-only `.md` files of varying topics and sizes for validation:

| File | Size |
|------|------|
| Clinical Trial Diversity Mandates_ FDA Requirements vs Economics.md | 26.4 MB |
| Used Commercial Taxi Market in India.md | 20.2 MB |
| AI Bubble_ Detection, Prevention, and Investment Strategies.md | 2.3 MB |
| The Rise of Green Hydrogen Hubs in Africa.md | 2.0 MB |
| Solar PV and Battery Storage Market Cost Trends.md | 1.9 MB |
| UAE Progress toward 2050 Solar Energy Targets.md | 1.1 MB |
| NYSE Stock Valuation Multiples Analysis.md | 585 KB |
| CREDIT CARD MARKET ENTRY STRATEGY FOR INDONESIA.md | 475 KB |
| Telecom & Media Convergence in Africa.md | 474 KB |
| TPT PLATFORM MARKET RESEARCH FUTURE TRENDS.md | 488 KB |
| Automobile Industry Supply Chain Disruptions.md | 466 KB |
| Osteoarthritis Market Global Competitive Analysis.md | 378 KB |
| Semiconductor Manufacturing Reshoring.md | 357 KB |
| Schneider Electric in Data Center Cooling Market.md | 221 KB |
| Deep Tech in Healthcare Equipment.md | 216 KB |
| Smart Pet Collar Business Evaluation.md | 201 KB |
| Precision-Nutrition Startups and Biotech Workforce.md | 188 KB |
| Marketing Research Proposal_ Sree MK Nawaab Rice.md | 179 KB |
| Accenture Tech Acquisition Analysis.md | 149 KB |
| Gilsonite Market Analysis_ Romania and Eastern Europe.md | 150 KB |
| Key Players in Water Treatment and Chemical Industry.md | 120 KB |
| The Rise of AI Freelance Jobs in India.md | 92 KB |
| Digital Banking and Talent Shortage in Central Asia.md | 72 KB |
| Banking ROE Competitive Benchmarking Analysis.md | 67 KB |

---

## 11. INPUT MARKDOWN FORMAT PATTERNS

Based on analysis of sample/test files, inputs typically follow this structure:

```markdown
# Title

### Subtitle

## Table of Contents
[1. Section Name](#anchor)
[1.1. Sub-section](#anchor)
...

## Executive Summary
(A dense paragraph summarizing the entire report)

## 1. Section Name
### 1.1. Sub-section
(Paragraphs, bullet lists, tables)

Title: Table Name
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| data    | data    | data    |

![Visualization](data:image/png;base64,...)

## N. References and Source Documentation
(Citations with markdown links)
```

### Key Content Patterns:
- **Headers**: `#`, `##`, `###` for hierarchy
- **Tables**: Standard markdown tables with alignment markers, often preceded by `Title: <name>`
- **Embedded images**: Base64-encoded PNG images via `![Visualization](data:image/png;base64,...)`
- **Bullet lists**: `-` for unordered, numbered for ordered
- **Citations**: Inline links `[N](url)` throughout text
- **Table of Contents**: Markdown anchor links at the top
- **Large files**: Some inputs are 20+ MB, largely due to base64 images

---

## 12. SLIDE MASTER TEMPLATES

Located in `Guidelines/Slide Master/` — these are the 3 template PPTXs (same as in the sample folders):
- `Template_AI Bubble_ Detection, Prevention, and Investment Strategies.pptx` (4.4 MB)
- `Template_Accenture Tech Acquisition Analysis.pptx` (15.8 MB)
- `Template_UAE Progress toward 2050 Solar Energy Targets.pptx` (8.2 MB)

The system needs to **read** these templates and extract:
- Color palettes
- Fonts (max 2 per presentation)
- Background styles
- Slide layouts and placeholder positions

---

## 13. RECOMMENDED TECH STACK

Based on the requirements, here are strong technology choices:

| Component | Recommended | Why |
|-----------|-------------|-----|
| Language | **Python** | Best ecosystem for PPTX manipulation and LLM integration |
| PPTX Library | **python-pptx** | Industry-standard Python library for creating/modifying PowerPoint files |
| Markdown Parsing | **markdown-it-py** or **mistune** | Fast, extensible markdown parsers |
| LLM Orchestration | **OpenAI API** / **LangChain** | For content structuring, storylining, and visual decision-making |
| Chart Generation | **python-pptx** (native charts) | Native PPTX charts preferred for editability |
| Infographics | **python-pptx** shapes | Programmatic shape creation with grid alignment |
| Grid System | Custom module | Fixed grid, margin enforcement, spacing calculations |

---

## 14. QUICK-START DEVELOPMENT CHECKLIST

1. [ ] Set up project structure (CLI entry point, modular package layout)
2. [ ] Implement Module 1: Markdown Parser (headers, lists, tables, images, hierarchy extraction)
3. [ ] Implement Module 2: LLM Storylining (content → 10-15 slide narrative, 1 key message per slide)
4. [ ] Implement Module 3: Visual Decision Engine ("Infographic-First" gate, chart/table detection)
5. [ ] Implement Module 4: Layout Calculator (grid system, margins, spacing, alignment)
6. [ ] Implement Module 5: PPTX Renderer (template reading, slide assembly, theme enforcement)
7. [ ] Test with small sample (Accenture, ~149 KB markdown)
8. [ ] Test with medium sample (UAE Solar, ~1.1 MB)
9. [ ] Test with large sample (AI Bubble, ~2.3 MB)
10. [ ] Run full validation against 24 test case markdowns
11. [ ] Write comprehensive README.md
12. [ ] Record demo video (3-8 min, 2+ inputs)
13. [ ] Final polish, edge case handling, and robustness testing
