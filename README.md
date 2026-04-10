# present-md 🚀
> Automated, Intelligent Pipeline for Markdown → PPTX Conversion

`present-md` is an advanced Python pipeline that automatically transforms raw Markdown documents into beautifully structured, properly formatted PowerPoint (`.pptx`) presentations. It strictly obeys provided Slide Master templates and enforces an "Infographic-First" visual hierarchy over simple bulleted lists.

## 🌟 Key Features
- **Infographic-First Approach**: Automatically replaces walls of text with process flows, icon grids, stat callouts, charts, timelines, and comparisons.
- **LLM-Powered Storylining**: Distills massive 5MB+ markdowns into a strict, flowing 10-15 slide narrative with EXACTLY one key message per slide.
- **Native Charts & Tables**: Parses markdown tables and numerical data into highly readable, native `.pptx` charts (Bar, Pie, Line, Area).
- **Graceful Fallbacks**: Completely resilient. When offline or without an API key, the system uses built-in heuristic parsers to still build full valid presentations.
- **Strict Master Template Compliance**: Inherits fonts, colors, branding, and layouts directly from your Slide Master. No rogue styling.
- **Fully Containerized**: Ready to run with Docker and `docker-compose`.

## 🏗 System Architecture (5 Modules)
The pipeline is designed with a strict component-based architecture:
1. **Parser Engine** (`md_parser.py`): Ingests the `.md` into an AST, separating headings, paragraphs, lists, tables, and images.
2. **Storylining Engine** (`storyliner/engine.py`): Leverages OpenAI's GPT-4o to read the text and produce a narrative structure (Title → Agenda → Exec Summary → Core Insights → Conclusion).
3. **Visual Decision Engine** (`visual/decision.py`): Decides the best layout type for each slide before rendering text (e.g., uses process flow for steps, tables/charts for numbers).
4. **Layout Calculator** (`layout/grid.py`): Implements a rigid grid system enforcing margins, perfect padding, and baseline alignment.
5. **Renderer Engine** (`renderer/builder.py`): Assembles the native PowerPoint objects dynamically onto the Slide Master.

---

## 💻 Setup & Installation

### Option 1: Docker (Requires Docker installed)
```bash
# 1. Set your Groq API key
cp .env.example .env
nano .env  # Add your GROQ_API_KEY
# If using Docker v2+, you might use `docker compose` instead of `docker-compose`

# 2. Build & Convert (Drop into the container)
docker compose run present-md convert -i "Guidelines/Sample Files/Accenture Tech Acquisition Analysis/Accenture Tech Acquisition Analysis.md" -t "Guidelines/Sample Files/Accenture Tech Acquisition Analysis/Template_Accenture Tech Acquisition Analysis.pptx" -o output/final.pptx
```

### Option 2: Local Python Environment (macOS/Linux)
```bash
# 1. Provide Python 3.9+ and create a virtual env
python3 -m venv venv
source venv/bin/activate

# 2. Install Dependencies
python3 -m pip install -r requirements.txt

# 3. Copy the env file
cp .env.example .env
# Edit .env to add GROQ_API_KEY

# 4. Run the Tool (Using an actual provided test file)
PYTHONPATH=src python3 -m present_md convert -i "Guidelines/Sample Files/Accenture Tech Acquisition Analysis/Accenture Tech Acquisition Analysis.md" -t "Guidelines/Sample Files/Accenture Tech Acquisition Analysis/Template_Accenture Tech Acquisition Analysis.pptx" -o output/Accenture.pptx
```

---

## ⚙️ CLI Options
```console
Usage: python -m present_md convert [OPTIONS]

Options:
  -i, --input PATH      Path to the input Markdown (.md) file.  [required]
  -t, --template PATH   Path to the Slide Master template (.pptx) file.  [required]
  -o, --output PATH     Path for the output .pptx file. Defaults to output/<input_name>.pptx.
  --min-slides INTEGER  Minimum number of slides (default: 10).
  --max-slides INTEGER  Maximum number of slides (default: 15).
  --help                Show this message and exit.
```

---

## 🧠 Design Decisions & Constraints Handled

### 1. IP & Copyright Compliance
The system completely abandons internet image scraping (which usually results in copyright violations). Instead, it relies on generated native `.pptx` shapes (via math and grid alignment) to build infographics that are fundamentally non-copyrighted and 100% owned by the user.

### 2. Multi-Stage Pipeline Over Single Prompt
Instead of asking an LLM to blindly generate base64 PPTX bytes, `present-md` relies on standard parsing libraries (`mistune`) connected functionally to deterministic engines (`python-pptx`). GPT-4o only outputs JSON structures representing layout intent and extracted narrative, giving the engine high stability and preventing hallucinated output formats limit crashes.

### 3. Graceful Fallbacks
Every external LLM call is guarded by a Try/Catch that falls back to heuristic algorithms. E.g., if OpenAI encounters a 500 error or is rate-limited, the `_fallback_outline()` generates a perfect 10-slide outline picking up `Level 1/2 Headers` as titles and lists as content without failing the pipeline.

## 🧪 Testing
```bash
# Run the integration test suite across all 24 sample documents
PYTHONPATH=src python3 tests/test_pipeline.py
```
