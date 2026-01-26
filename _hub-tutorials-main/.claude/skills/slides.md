---
description: Generate Reveal.js presentation slides from tutorial scripts, markdown files, or topics
---

# Presentation Slides Generator

Generate professional Reveal.js presentation slides from tutorial content, script files, or topic descriptions.

## Input

$ARGUMENTS

If no argument provided, ask the user what content to convert to slides.

**Accepted inputs:**
- Path to a SCRIPT.md or markdown file
- Path to a notebook (.ipynb)
- Topic name from TUTORIAL_IDEAS.md
- Free-form topic description

## Process

1. **Determine input type** and read source content
2. **Parse the content** extracting:
   - Title and subtitle
   - Main sections (H2 headings)
   - Code blocks with language
   - Architecture diagrams (ASCII art or descriptions)
   - Tables
   - Key concepts and takeaways
   - Learning outcomes

3. **Structure into slides** following these rules:
   - **Title slide**: Centered title + subtitle + series info
   - **Section slides**: Each H2 becomes a new horizontal slide
   - **Content density**: Max 5-7 bullet points OR 1 code block OR 1 diagram per slide
   - **Code slides**: Large code blocks get dedicated slides
   - **Diagram slides**: Convert ASCII/text diagrams to Rough.js hand-drawn style
   - **Concept slides**: Use colored callout blocks for key concepts
   - **Summary slide**: Key takeaways at the end

4. **Output path**: Save to `slides/{project-name}/{slug}.html`
   - Create directories if needed
   - Use kebab-case for filenames

## HTML Template

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLIDE_TITLE</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
    :root {
      --r-background-color: #fafafa;
      --r-main-font: 'Inter', system-ui, -apple-system, sans-serif;
      --r-main-font-size: 32px;
      --r-main-color: #333333;
      --r-heading-font: 'Inter', system-ui, -apple-system, sans-serif;
      --r-heading-color: #111111;
      --r-heading-font-weight: 600;
      --r-link-color: #2563eb;
    }
    .reveal { font-size: 32px; }
    .reveal h1 { font-size: 2.4em; font-weight: 600; letter-spacing: -0.03em; margin-bottom: 0.3em; }
    .reveal h2 { font-size: 1.5em; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 0.8em; text-align: left; }
    .reveal h3 { font-size: 1em; font-weight: 600; margin-bottom: 0.5em; color: #555; }
    .reveal pre { width: 100%; box-shadow: none; margin: 0.8em 0; }
    .reveal code { font-family: 'Fira Code', monospace; font-size: 0.65em; }
    .reveal pre code {
      padding: 1.2em 1.4em;
      border-radius: 8px;
      background: #f4f4f5;
      border: 1px solid #e4e4e7;
      line-height: 1.5;
      max-height: 450px;
    }
    .reveal :not(pre) > code {
      background: #f4f4f5;
      padding: 0.15em 0.4em;
      border-radius: 4px;
      font-size: 0.85em;
      color: #e11d48;
    }
    .reveal ul, .reveal ol { display: block; text-align: left; margin-left: 1em; }
    .reveal li { margin: 0.5em 0; line-height: 1.5; }
    .reveal strong { font-weight: 600; color: #111; }
    .reveal p { line-height: 1.6; text-align: left; }
    .reveal section { text-align: left; }
    .reveal .center { text-align: center; }

    /* Concept block (green) */
    .reveal .concept {
      background: #f0fdf4;
      padding: 1em 1.2em;
      border-radius: 8px;
      border-left: 4px solid #22c55e;
      margin: 1em 0;
    }
    .reveal .concept-title {
      font-weight: 600;
      color: #166534;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Warning block (red) */
    .reveal .warning {
      background: #fef2f2;
      padding: 1em 1.2em;
      border-radius: 8px;
      border-left: 4px solid #ef4444;
      margin: 1em 0;
    }
    .reveal .warning-title {
      font-weight: 600;
      color: #dc2626;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Tip block (blue) */
    .reveal .tip {
      background: #eff6ff;
      padding: 1em 1.2em;
      border-radius: 8px;
      border-left: 4px solid #3b82f6;
      margin: 1em 0;
    }
    .reveal .tip-title {
      font-weight: 600;
      color: #2563eb;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Pattern block (purple) - for architectural patterns */
    .reveal .pattern {
      background: #faf5ff;
      padding: 1em 1.2em;
      border-radius: 8px;
      border-left: 4px solid #a855f7;
      margin: 1em 0;
    }
    .reveal .pattern-title {
      font-weight: 600;
      color: #7c3aed;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Output block (dark terminal) */
    .reveal .output {
      background: #18181b;
      color: #a1a1aa;
      padding: 1em 1.2em;
      border-radius: 8px;
      margin: 1em 0;
      font-family: 'Fira Code', monospace;
      font-size: 0.6em;
      white-space: pre-wrap;
      line-height: 1.5;
    }
    .reveal .output-title {
      font-weight: 500;
      color: #71717a;
      font-family: 'Inter', sans-serif;
      font-size: 0.85em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5em;
      display: block;
    }

    /* Diagrams */
    .reveal .diagram {
      display: flex;
      justify-content: center;
      margin: 1em 0;
    }
    .reveal .diagram svg { max-width: 100%; }
    .reveal .diagram-caption {
      text-align: center;
      font-size: 0.75em;
      color: #71717a;
      margin-top: 0.5em;
    }

    /* Images */
    .reveal .figure {
      text-align: center;
      margin: 1em 0;
    }
    .reveal .figure img {
      max-height: 380px;
      border-radius: 8px;
      border: 1px solid #e4e4e7;
    }
    .reveal .figure-caption {
      font-size: 0.75em;
      color: #71717a;
      margin-top: 0.8em;
    }

    /* Tables */
    .reveal table {
      margin: 1em auto;
      border-collapse: collapse;
      font-size: 0.8em;
    }
    .reveal table th {
      background: #f4f4f5;
      font-weight: 600;
      border-bottom: 2px solid #d4d4d8;
      padding: 0.6em 1em;
      text-align: left;
    }
    .reveal table td {
      border-bottom: 1px solid #e4e4e7;
      padding: 0.6em 1em;
    }

    /* Two column layout */
    .reveal .columns { display: flex; gap: 1.5em; }
    .reveal .column { flex: 1; }
    .reveal .column-60 { flex: 1.5; }
    .reveal .column-40 { flex: 1; }

    /* Code comparison */
    .reveal .code-compare { display: flex; gap: 1em; }
    .reveal .code-compare > div { flex: 1; }
    .reveal .code-compare h4 {
      font-size: 0.8em;
      margin-bottom: 0.4em;
      color: #71717a;
      font-weight: 500;
    }

    /* Slide number */
    .reveal .slide-number {
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      color: #a1a1aa;
      background: transparent;
    }

    /* Agent badges */
    .reveal .agent-badge {
      display: inline-block;
      font-family: 'Fira Code', monospace;
      padding: 0.2em 0.6em;
      border-radius: 4px;
      font-size: 0.7em;
      font-weight: 500;
      background: #dbeafe;
      color: #1d4ed8;
      margin: 0.2em;
    }
    .reveal .agent-badge.triage { background: #fef3c7; color: #92400e; }
    .reveal .agent-badge.specialist { background: #dcfce7; color: #166534; }
    .reveal .agent-badge.aggregator { background: #fae8ff; color: #a21caf; }

    /* Tool badges */
    .reveal .tool-badge {
      display: inline-block;
      font-family: 'Fira Code', monospace;
      padding: 0.15em 0.4em;
      border-radius: 4px;
      font-size: 0.65em;
      font-weight: 500;
      background: #f4f4f5;
      color: #71717a;
      border: 1px solid #e4e4e7;
    }

    /* Subtitle */
    .reveal .subtitle {
      color: #71717a;
      font-size: 0.9em;
      margin-top: -0.3em;
    }

    /* Series tag */
    .reveal .series-tag {
      font-size: 0.6em;
      color: #a1a1aa;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <!-- SLIDES GO HERE -->
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/roughjs@4.6.6/bundled/rough.js"></script>
  <script>
    // ===== DIAGRAM COLOR PALETTE =====
    const colors = {
      primary: '#3b82f6',    // Blue - main elements
      secondary: '#93c5fd',  // Light blue - secondary
      accent: '#a855f7',     // Purple - highlights
      success: '#22c55e',    // Green - success states
      warning: '#f59e0b',    // Amber - warnings
      dark: '#1f2937',       // Dark gray - text, borders
      gray: '#9ca3af',       // Gray - arrows, subtle
      light: '#e5e7eb',      // Light gray - backgrounds
    };

    // ===== HELPER: Draw text on SVG =====
    function drawText(svg, x, y, text, opts = {}) {
      const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('x', x);
      t.setAttribute('y', y);
      t.setAttribute('text-anchor', opts.anchor || 'middle');
      t.setAttribute('font-family', 'Inter, system-ui, sans-serif');
      t.setAttribute('font-size', opts.size || '14px');
      t.setAttribute('font-weight', opts.weight || '500');
      t.setAttribute('fill', opts.fill || '#333');
      t.textContent = text;
      svg.appendChild(t);
    }

    // ===== HELPER: Draw arrow =====
    function drawArrow(rc, svg, x1, y1, x2, y2, color = colors.dark) {
      svg.appendChild(rc.line(x1, y1, x2, y2, { stroke: color, strokeWidth: 2 }));
      const angle = Math.atan2(y2 - y1, x2 - x1);
      const headLen = 10;
      svg.appendChild(rc.polygon([
        [x2 - headLen * Math.cos(angle - Math.PI / 6), y2 - headLen * Math.sin(angle - Math.PI / 6)],
        [x2, y2],
        [x2 - headLen * Math.cos(angle + Math.PI / 6), y2 - headLen * Math.sin(angle + Math.PI / 6)]
      ], { fill: color, fillStyle: 'solid', stroke: 'none' }));
    }

    // ===== HELPER: Draw agent box =====
    function drawAgentBox(rc, svg, x, y, width, height, label, type = 'default') {
      const fillColors = {
        triage: colors.warning,
        specialist: colors.primary,
        aggregator: colors.accent,
        default: colors.secondary
      };
      svg.appendChild(rc.rectangle(x, y, width, height, {
        fill: fillColors[type] || fillColors.default,
        fillStyle: 'solid',
        stroke: colors.dark,
        strokeWidth: 2
      }));
      const textColor = type === 'default' ? colors.dark : 'white';
      drawText(svg, x + width/2, y + height/2 + 5, label, { fill: textColor, weight: '600' });
    }

    // ===== DIAGRAM CODE GOES HERE =====
    // Each diagram wrapped in IIFE targeting its SVG id

    Reveal.initialize({
      hash: true,
      slideNumber: 'c/t',
      plugins: [RevealHighlight],
      transition: 'none'
    });
  </script>
</body>
</html>
```

## Slide Syntax Examples

### Title Slide
```html
<section class="center">
  <p class="series-tag">AI Agents Tutorial Series</p>
  <h1>Slide Title</h1>
  <p class="subtitle" style="text-align: center;">Building Multi-Agent Systems</p>
</section>
```

### Agenda/Overview Slide
```html
<section>
  <h2>What We'll Cover</h2>
  <ol>
    <li>Architecture patterns</li>
    <li>Agent design</li>
    <li>Handoff mechanisms</li>
    <li>Shared context</li>
    <li>Live demo</li>
  </ol>
</section>
```

### Content Slide
```html
<section>
  <h2>Section Title</h2>
  <ul>
    <li>Point one</li>
    <li>Point two with <code>inline code</code></li>
    <li><strong>Bold point</strong> — with explanation</li>
  </ul>
</section>
```

### Code Slide
```html
<section>
  <h2>Defining an Agent</h2>
  <pre><code class="language-python">from agents import Agent

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route requests to specialists.",
    handoffs=[faq_agent, booking_agent]
)</code></pre>
</section>
```

### Code + Output Slide
```html
<section>
  <h2>Running the Agent</h2>
  <pre><code class="language-python">result = await Runner.run(triage_agent, "What's the baggage policy?")</code></pre>
  <div class="output"><span class="output-title">Output</span>Handoff to FAQ Agent...
Carry-on bags must be under 22x14x9 inches.</div>
</section>
```

### Pattern Block (for architectural patterns)
```html
<section>
  <h2>Hub-Spoke Pattern</h2>
  <div class="pattern">
    <span class="pattern-title">Architecture Pattern</span><br>
    Central <strong>triage agent</strong> routes to specialized agents. Each specialist can hand back to triage for re-routing.
  </div>
</section>
```

### Concept Block
```html
<section>
  <h2>Key Concept</h2>
  <div class="concept">
    <span class="concept-title">Handoff Description</span><br>
    The <code>handoff_description</code> tells other agents when to route here. Be specific—vague descriptions cause misrouting.
  </div>
</section>
```

### Warning Block
```html
<div class="warning">
  <span class="warning-title">Common Pitfall</span><br>
  Don't forget escape hatches. Every agent needs a way to hand off when it can't handle a request.
</div>
```

### Tip Block
```html
<div class="tip">
  <span class="tip-title">Pro Tip</span><br>
  Use numbered routines in agent instructions. Steps like "1. Identify intent 2. Call tool 3. Hand off if needed" improve reliability.
</div>
```

### Agent Badges
```html
<section>
  <h2>System Agents</h2>
  <p>
    <span class="agent-badge triage">Triage</span>
    <span class="agent-badge specialist">FAQ Agent</span>
    <span class="agent-badge specialist">Booking Agent</span>
    <span class="agent-badge aggregator">Summarizer</span>
  </p>
</section>
```

### Tool Badges
```html
<section>
  <h2>Available Tools</h2>
  <ul>
    <li><span class="tool-badge">faq_lookup</span> — Search knowledge base</li>
    <li><span class="tool-badge">update_seat</span> — Modify reservation</li>
    <li><span class="tool-badge">send_email</span> — Notify customer</li>
  </ul>
</section>
```

### Two Column Layout
```html
<section>
  <h2>Single vs Multi-Agent</h2>
  <div class="columns">
    <div class="column">
      <h3>Single Agent</h3>
      <ul>
        <li>Simple Q&A</li>
        <li>< 5 tools</li>
        <li>Low latency</li>
      </ul>
    </div>
    <div class="column">
      <h3>Multi-Agent</h3>
      <ul>
        <li>Domain specialists</li>
        <li>Complex workflows</li>
        <li>Better isolation</li>
      </ul>
    </div>
  </div>
</section>
```

### Comparison Table
```html
<section>
  <h2>Pattern Comparison</h2>
  <table>
    <thead>
      <tr><th>Pattern</th><th>Use Case</th><th>Complexity</th></tr>
    </thead>
    <tbody>
      <tr><td>Hub-Spoke</td><td>Customer service</td><td>Medium</td></tr>
      <tr><td>Sequential</td><td>Pipelines</td><td>Low</td></tr>
      <tr><td>Parallel</td><td>Code review</td><td>High</td></tr>
    </tbody>
  </table>
</section>
```

### Code Comparison (Before/After)
```html
<section>
  <h2>Adding Handoffs</h2>
  <div class="code-compare">
    <div>
      <h4>Without Handoffs</h4>
      <pre><code class="language-python">agent = Agent(
    name="Support",
    tools=[faq, booking]
)</code></pre>
    </div>
    <div>
      <h4>With Handoffs</h4>
      <pre><code class="language-python">agent = Agent(
    name="Triage",
    handoffs=[faq_agent, booking_agent]
)</code></pre>
    </div>
  </div>
</section>
```

### Diagram Slide
```html
<section>
  <h2>Architecture</h2>
  <div class="diagram">
    <svg id="arch-diagram" width="750" height="300"></svg>
  </div>
  <p class="diagram-caption">Hub-spoke pattern with triage routing to specialists</p>
</section>
```

### Summary/Takeaways Slide
```html
<section>
  <h2>Key Takeaways</h2>
  <ol>
    <li><strong>Handoff descriptions</strong> — Be specific about when to route</li>
    <li><strong>Routines</strong> — Numbered steps in instructions</li>
    <li><strong>Escape hatches</strong> — Always allow hand-back</li>
    <li><strong>Shared context</strong> — Pass state through handoffs</li>
  </ol>
</section>
```

### Resources Slide
```html
<section>
  <h2>Resources</h2>
  <ul>
    <li><a href="https://github.com/...">GitHub Repository</a></li>
    <li><a href="https://docs...">SDK Documentation</a></li>
    <li><a href="https://...">Template File</a></li>
  </ul>
  <p style="margin-top: 2em; font-size: 0.8em; color: #71717a;">
    Questions? Comments below or @handle
  </p>
</section>
```

## Rough.js Diagrams for Agent Architectures

### Hub-Spoke Pattern
```javascript
(function() {
  const svg = document.getElementById('hub-spoke');
  const rc = rough.svg(svg);

  // Triage (center)
  drawAgentBox(rc, svg, 315, 20, 120, 50, 'Triage', 'triage');

  // Specialists
  drawAgentBox(rc, svg, 100, 150, 120, 50, 'FAQ Agent', 'specialist');
  drawAgentBox(rc, svg, 315, 150, 120, 50, 'Booking', 'specialist');
  drawAgentBox(rc, svg, 530, 150, 120, 50, 'Support', 'specialist');

  // Arrows down
  drawArrow(rc, svg, 350, 70, 160, 150, colors.gray);
  drawArrow(rc, svg, 375, 70, 375, 150, colors.gray);
  drawArrow(rc, svg, 400, 70, 590, 150, colors.gray);

  // Arrows back up (dashed)
  svg.appendChild(rc.line(160, 150, 350, 70, { stroke: colors.gray, strokeWidth: 1.5, strokeLineDash: [5,5] }));
})();
```

### Sequential Pipeline
```javascript
(function() {
  const svg = document.getElementById('sequential');
  const rc = rough.svg(svg);

  const stages = ['Classifier', 'Extractor', 'Validator', 'Processor'];
  stages.forEach((label, i) => {
    const x = 50 + i * 180;
    drawAgentBox(rc, svg, x, 100, 130, 50, label, 'specialist');
    if (i < stages.length - 1) {
      drawArrow(rc, svg, x + 130, 125, x + 180, 125, colors.gray);
    }
  });
})();
```

### Parallel Fan-Out
```javascript
(function() {
  const svg = document.getElementById('parallel');
  const rc = rough.svg(svg);

  // Dispatcher
  drawAgentBox(rc, svg, 315, 20, 120, 50, 'Dispatcher', 'triage');

  // Parallel workers
  const workers = ['Security', 'Style', 'Perf', 'Tests'];
  workers.forEach((label, i) => {
    const x = 50 + i * 175;
    drawAgentBox(rc, svg, x, 120, 110, 50, label, 'specialist');
    drawArrow(rc, svg, 375, 70, x + 55, 120, colors.gray);
  });

  // Aggregator
  drawAgentBox(rc, svg, 315, 220, 120, 50, 'Aggregator', 'aggregator');
  workers.forEach((_, i) => {
    const x = 50 + i * 175 + 55;
    drawArrow(rc, svg, x, 170, 375, 220, colors.gray);
  });
})();
```

## Content Guidelines

### From SCRIPT.md Files
- **Hook section** → Title slide + overview
- **Main sections (H2)** → Individual slides
- **Code blocks** → Dedicated code slides
- **ASCII diagrams** → Convert to Rough.js
- **Tables** → HTML tables
- **Numbered lists** → Keep as-is with fragments

### From Tutorial Ideas
- **Architecture diagram** → Rough.js visualization
- **Agents list** → Agent badge slide
- **Tools list** → Tool badge slide
- **Learning outcomes** → Takeaways slide

### General Rules
- **One idea per slide** — Don't overcrowd
- **Max 5-7 bullets** — Split if more
- **Code ≤ 15 lines** — Break up longer blocks
- **Use fragments** — `class="fragment"` for progressive reveal
- **Speaker notes** — `<aside class="notes">` for verbal points

## Converting ASCII Diagrams

When source has ASCII architecture diagrams like:
```
     ┌─────────────┐
     │   Triage    │
     └──────┬──────┘
            │
   ┌────────┴────────┐
   ▼                 ▼
┌─────────┐   ┌─────────┐
│  Agent1 │   │  Agent2 │
└─────────┘   └─────────┘
```

Convert to Rough.js using:
1. Parse box positions and labels
2. Identify connection lines and arrows
3. Generate JavaScript using helper functions
4. Use appropriate agent types (triage/specialist/aggregator)

## After Generation

1. Report output path
2. Provide preview command: `open slides/path/to/file.html`
3. Mention serve option: `npx serve slides/` for live reload
4. List slide count and any diagrams generated
