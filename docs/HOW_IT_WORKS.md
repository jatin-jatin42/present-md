# present-md — How It Works
## System Design & Walkthrough

---

## 1. What is present-md?

`present-md` is an **agentic pipeline** that converts a raw Markdown `.md` file into a
structured, branded PowerPoint `.pptx` presentation — without any manual editing.

You give it:
- A `.md` document (can be 5KB or 5MB)
- A corporate PowerPoint template (defines colors, fonts, layouts)

It produces:
- A complete `.pptx` file with 10–15 slides, branded to your template

---

## 2. The Command

```bash
PYTHONPATH=src python3 -m present_md convert \
  -i "input.md"          # Source Markdown file
  -t "template.pptx"     # Corporate slide master template
  -o "output/result.pptx" # Where to save the output
  --min-slides 10         # (optional) minimum slide count
  --max-slides 15         # (optional) maximum slide count
```

**What `PYTHONPATH=src` does:** Tells Python to look in the `src/` folder for the
`present_md` package. Required because our code is in a `src/` layout (best practice
for Python packages — keeps source separate from config and docs).

**What `-m present_md` does:** Runs `src/present_md/__main__.py`, which loads the CLI.

---

## 3. The 5-Stage Pipeline Explained

### Entry point: `src/present_md/cli.py`
The CLI reads flags (`-i`, `-t`, `-o`), loads the `.env` file to get the API key,
detects whether you are using OpenAI or Groq, sets the correct base URL, then calls
`PresentationPipeline.run()`.

```
cli.py → pipeline.py → [parser → storyliner → visual → layout → renderer]
```

---

### Stage 1 — Parser  `src/present_md/parser/md_parser.py`

**What it does:** Reads the entire Markdown file and converts it into a structured
Python object called a `Document`.

**How it handles complexity:**
- Uses **Mistune v3** which produces an AST (Abstract Syntax Tree). Every heading,
  paragraph, list, table, and image gets its own typed node.
- Walks the AST recursively. Each `heading` node starts a new `Section`. Everything
  inside that heading until the next heading is attached as content blocks.
- Tables get a dedicated `TableData` extractor — it reads headers and rows separately
  so the downstream chart renderer knows exactly what numbers to plot.

**Output:** `Document(title, sections[], tables[], images[])`

Example — for Accenture doc: `39 sections, 4 tables, 2 images`

---

### Stage 2 — Storyliner  `src/present_md/storyliner/engine.py`

**What it does:** Calls an LLM (Groq / Llama 3.3-70B) with a highly compressed
representation of the document and asks it to produce a presentation narrative.

**How it handles complexity:**
- Only sends section *titles and content types* to the LLM (not full text bodies).
  This keeps every request under 4,000 tokens — fitting within Groq's free tier.
- The system prompt is tightly structured: forces mandatory slide flow
  (Title → Agenda → Exec Summary → Content → Conclusion), max 5 bullets per slide.
- If the LLM fails (rate limit, network error), `_fallback_outline()` automatically
  kicks in — it reads heading levels directly from the parsed sections to produce a
  valid outline without any AI at all. **The pipeline never crashes due to LLM failure.**

**Output:** `SlideOutline(slides[])` — each slide has a type, title, key_message,
bullet_points, and flags like `has_numeric_data`.

---

### Stage 3 — Visual Decision Engine  `src/present_md/visual/decision.py`

**What it does:** Decides the *best visual representation* for each slide's content.
This is the "Infographic-First" step.

**How intelligent decision-making works:**
- Calls the LLM again (separate request) with a compact description of each slide.
- The LLM picks from: `stat_callout`, `icon_grid`, `process_flow`, `timeline`,
  `comparison`, `chart_bar`, `chart_pie`, `chart_line`, `table`, `bullet_list`,
  `key_message_box`
- If a slide has `has_numeric_data=true` → LLM is guided toward chart types.
- If bullet points are short phrases → `icon_grid` preferred over bullet list.
- Fallback: `_fallback_decision()` applies heuristics (e.g. if all bullets < 50
  chars → icon_grid; title slide → key_message_box; has table → chart_bar).

**Output:** `PresentationPlan(slides[])` — each slide now has a `visual_type`
and a list of `VisualElement` objects with structured `content` dicts.

---

### Stage 4 — Template Reader  `src/present_md/renderer/template.py`

**What it does:** Opens the provided `.pptx` template and extracts the brand system.

**What it extracts:**
- `colors[]` — 10 theme colors from the XML color scheme (`dk1, lt1, accent1–6…`)
- `fonts[]` — major font (titles) and minor font (body) from the font scheme XML
- `layout_names[]` — names of all slide layouts: e.g. `["1_Cover", "Blank", "Title only"]`
- `slide_width`, `slide_height` — used to validate positioning

This means the output presentation will always use **the exact same colors and fonts**
as the corporate template — no rogue styling.

---

### Stage 5 — Builder  `src/present_md/renderer/builder.py`

**What it does:** Creates the actual `.pptx` file slide by slide.

**How it handles complexity:**

1. **Layout selection:** For title slides it picks `1_Cover`. For content slides it
   picks `Title only` or `Divider`. It scans layout names intelligently, not by index.

2. **Placeholder hydration:** Instead of drawing floating text boxes from math
   coordinates, it finds the native `slide.shapes.title` placeholder and sets
   `.text = plan.title`. This means the title inherits *the template designer's
   exact font, size, color, and position* — no layout divergence.

3. **Ghost placeholder purging:** After populating the title, ALL other placeholders
   (`idx != 0`) are removed immediately — preventing "Double-click to edit" ghost boxes.

4. **Visual renderer dispatch:** Based on `visual_type`, the builder calls the correct
   render method:
   - `_render_icon_grid()` → draws colored oval + number + label for each item
   - `_render_stat_callout()` → draws large-number callout boxes
   - `_render_process_flow()` → draws left-to-right connected steps
   - `_render_chart()` → calls `add_chart_to_slide()` to embed a native pptx chart
   - `_render_bullet_list()` → draws a structured text box in the content zone

5. **Safe content zone:** All drawn elements stay within `top=0.4"` to `top=4.2"` —
   above the decorative overlay panel that most corporate templates place in the
   lower half of the slide.

---

## 4. Output Structure

```
output/
├── Accenture Tech Acquisition Analysis/
│   ├── Accenture Tech Acquisition Analysis.md      ← source
│   └── Accenture Tech Acquisition Analysis.pptx   ← generated
│
├── UAE Progress toward 2050 Solar Energy Targets/
│   ├── UAE Progress toward 2050 Solar Energy Targets.md
│   └── UAE Progress toward 2050 Solar Energy Targets.pptx
│
└── AI Bubble Detection Prevention Investment Strategies/
    ├── AI Bubble Detection Prevention Investment Strategies.md
    └── AI Bubble Detection Prevention Investment Strategies.pptx
```

---

## 5. How Complexity is Handled — Summary Table

| Challenge | How present-md handles it |
|---|---|
| 5MB markdown with 64 sections | Sends only titles+content-types to LLM (not body text) |
| LLM rate limit or failure | Automatic fallback to heuristic outline — never crashes |
| Non-dict content from LLM | `content` is validated; if not a dict it's auto-wrapped |
| Template overlay blocking content | Content capped at 4.2" from top of slide |
| Ghost placeholder text | All non-title placeholders purged before drawing |
| Template font/color compliance | Fonts and colors extracted from template's XML, applied everywhere |
| Varies per template layout names | Layout selection by name keyword search, not hardcoded index |
| Large table data → visual | `has_numeric_data` flag triggers chart renderer over bullet list |
