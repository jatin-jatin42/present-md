# Software Requirements Specification (SRS) for `present-md`

## 1. Project Overview
* **Project Name**: present-md
* **Purpose**: An automated, intelligent pipeline that converts Markdown (.md) text into a structured, visually appealing, non-copyrighted `.pptx` file. 
* **Core Philosophy**: Slides must be "designed," not just "placed." The system must employ an "Infographic-First" approach, transforming text into structured visual frameworks rather than simple bulleted lists.

## 2. System Architecture & Interface
* **Execution Interface**: A graphical User Interface (UI) is **not required**. The system should be executable via a clear interface such as a CLI, script, or API.
* **Component-Based Pipeline**: The system must utilize meaningful logic, reasoning, and orchestration. Solutions that simply wrap a single API call are strictly prohibited.
* **Modularity**: Must separate concerns into parsing, storylining, layout calculation, visual generation, and PPTX rendering.
* **Tech Stack**: Open to Python, Node.js, AI agent frameworks, LLMs, APIs, and no-code tools.

## 3. Functional Requirements (FRs)

### FR1: Input Handling & Content Extraction
* **Input Limits**: Accept `.md` files up to 5 MB.
* **Storylining**: Process content to create a structured narrative (Title -> Agenda -> Executive Summary -> Sections -> Conclusion).
* **Slide Count Limits**: Dynamically distribute the content to enforce a hard limit of **10 to 15 slides** per presentation.
* **Hierarchy Extraction**: Accurately extract the Primary Message (Title), Context (Subtitle), and Supporting Points (Body), enforcing a strict limit of **1 key message per slide**.

### FR2: Master Slide & Theme Enforcement
* **Mandatory Master Usage**: The system **must** inherit and apply the provided Slide Master’s design language (fonts, colors, backgrounds).
* **Dynamic Layout Generation**: If specific content requires a new layout, the system may generate one programmatically, but it **must strictly adhere** to the Master’s core design language. Custom themes or independent styling are strictly prohibited.

### FR3: "Infographic-First" Visual Generation
* **Decision Gate**: Before rendering text, the system must evaluate: *"Can this be visualized?"*
* **Visual Substitutions**: Convert text into Icons + short labels, Process flows, Timelines, Comparison tables, or Data visuals.
* **Text Fallback**: If content cannot be visualized, text must be kept minimal (**maximum 6-8 lines**). Strict avoidance of "bullet overload" and paragraphs.

### FR4: Automated Data Visualization (Charts & Tables)
* **Conditional Trigger**: Charts and tables must *only* be generated if the markdown contains numerical or tabular data. If none exists, the system must gracefully skip chart generation.
* **Formatting Rules**: 
  * Numbers must be visually dominant.
  * Table text must be middle-aligned.
  * Tables must emphasize trends rather than looking like raw Excel data.

## 4. Design & Layout Specifications (Strict Guidelines)

### 4.1 Grid & Alignment System (Non-Negotiable)
* **Fixed Grid**: Implement a fixed grid system where all elements snap to the grid.
* **Margins**: Elements must strictly respect slide margins with zero overflow.
* **Spacing**: Maintain consistent padding inside elements and equal spacing between elements. No floating or randomly placed boxes.
* **Baselines**: Align text baselines evenly across different shapes.

### 4.2 Typography & Styling
* **Fonts**: Maximum of 2 fonts per presentation. Font sizes must clearly differentiate visual hierarchy.
* **Colors**: Use the theme-based palette exclusively. No random colors. Ensure high contrast for readability.
* **Shapes**: Clean containers, minimal borders, consistent corner radii. Do not add internal margins to text boxes that lack a fill color. 
* **Empty Space**: Utilize negative space properly; slides should look balanced, not crowded or awkwardly empty.

## 5. Non-Functional Requirements (NFRs)
* **Output Compatibility**: The `.pptx` must open flawlessly in Microsoft 365 PowerPoint, Google Slides, and LibreOffice Impress.
* **Robustness & Validation**: The system must not crash on malformed markdown or missing data; it must use graceful fallbacks. The system must be validated against *all* provided test cases.

## 6. Constraints, Legal & Deliverables
* **Copyright Restrictions**: Absolutely no downloading of copyrighted images or use of commercial PPT templates. All infographics and charts must be programmatically generated and non-copyrighted.
* **IP Transfer**: Full Intellectual Property rights of the submitted codebase must be transferred to EZ.
* **Submission Requirements**:
  1. A GitHub Repository with a clean, well-documented codebase.
  2. A comprehensive `README.md` detailing setup, run steps, system architecture, and design decisions.
  3. A demo video (3-8 minutes) showcasing the conversion of at least **two different markdown inputs** demonstrating logic, varying slide counts, and system complexity.