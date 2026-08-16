Deck Architect

Deck Architect turns a one-line topic into a presentation-ready slide deck. Give it a topic —
"AWS Bedrock AgentCore", "kagent for Kubernetes troubleshooting", "LangGraph vs CrewAI" — and it
produces a themed, fully editable `.pptx` (and optional high-fidelity `.pdf`) with:

- an opening problem statement before any concept is explained
- an architecture diagram sourced from the vendor's own official docs, not guessed from memory
- a scenario-based comparison slide against the real alternatives a practitioner would weigh
- a speaker-introduction slide sourced from a LinkedIn profile, if you want one
- curated, verified documentation and GitHub links
- context-aware theming (AWS orange, GCP blue, Azure electric, CNCF teal, multi-cloud, etc.)

Designed for cloud infrastructure, DevOps, platform engineering, and agentic-AI content: AWS
re:Invent talks, KCD and CNCF meetups, GDG events, and internal tech shares.

Usage examples

    /deck-architect AWS Bedrock AgentCore
    /deck-architect LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)
    /deck-architect Platform Engineering with CNCF tooling (fundamentals)
    /deck-architect Azure OpenAI vs Amazon Bedrock (comparison, 15 slides)
    /deck-architect kagent for Kubernetes troubleshooting (speaker: linkedin.com/in/yourprofile)

Features

Problem-first structure: every deck opens with Title, Agenda, then a Problem Statement slide
before any architecture or concept content — never "what is X" first, always "why does X need
to exist" first.

Web-sourced architecture diagrams: before drawing any topology, the agent searches the vendor's
own architecture reference (AWS Architecture Center, GCP Architecture Center, Azure Architecture
Center, or the project's own docs/GitHub) and reproduces that real diagram — service names and
data flow are verified, not remembered, and the source URL is logged in speaker notes.

Scenario-based comparison: every deck includes one Comparison slide that pits the topic against
the 2-3 tools a practitioner would actually be choosing between in that scenario — for example, a
kagent deck compares against k8sgpt and a plain kubectl+LLM copilot workflow, not a strawman.
Rows are sourced from each competitor's current docs, not assumed.

Speaker introduction slide: give a LinkedIn profile URL at intake and the deck includes a Speaker
slide with name, role, a paraphrased bio, and contact handles. If the profile can't be fetched
(LinkedIn blocks most scraping), the agent asks you directly instead of inventing details — it
never fabricates a title, employer, or accomplishment.

Context-aware theming: color palette and typography selected automatically by cloud provider or
ecosystem (AWS orange, GCP blue, Azure electric, CNCF teal, multi-cloud neutral).

16 slide archetypes: title, agenda, problem statement, key concepts, architecture/topology, deep
dives, code specs, comparisons, timelines, benchmarks, production gotchas, demos, quotes,
resources, speaker, and calls to action. Decks read as human-designed, not templated — no two
consecutive slides share a layout.

Curated resources: official documentation links and active GitHub repositories, sourced from a
maintained seed file with live web search filling in anything missing or stale. No fabricated
URLs, ever.

Adaptive depth: three difficulty levels (Fundamentals, Intermediate, Advanced) with
ecosystem-specific vocabulary. Content density matches audience expertise.

Speaker notes: included on every relevant slide, including the diagram source URL and comparison
research on the slides that need it.

Offline capable: theme, layout, and profile data ship as static files. Network access is only
needed to refresh resource links, comparison research, diagram sourcing, and the LinkedIn lookup —
everything falls back gracefully to cached data if a search is unavailable.

Works in any agentic IDE

This skill is two things: a Markdown instruction file (`SKILL.md` plus `references/*.md`) and two
plain CLI scripts (`scripts/build_deck.py`, `scripts/deck_engine.js`). Nothing about it requires
Claude specifically — any AI coding assistant that can read a file for instructions and execute
shell commands can drive it. Native plugin support (auto-discovery, `/deck-architect` slash
command) exists today for Claude Code and Claude Desktop; every other tool below works by pointing
its agent at `SKILL.md` and letting it run the two scripts itself.

Claude Code / Claude Desktop (native)
    Auto-discovers SKILL.md — see "Setting up for Claude Code" / "Setting up for Claude Desktop"
    below. Type /deck-architect <topic> directly.

Cursor
    Add a Project Rule that points at this repo's SKILL.md (Settings → Rules → Add Rule, or drop a
    file in .cursor/rules/deck-architect.mdc that says "Follow claude-deck-architect/SKILL.md for
    any slide-deck request"), or just @-mention SKILL.md in chat and ask the agent to follow it.
    Cursor's Agent mode can run the build_deck.py / deck_engine.js commands from its terminal tool.

Kiro
    Drop (or symlink) SKILL.md and references/ into .kiro/steering/ so Kiro's agent loads them as
    steering context automatically, then ask for a deck in chat. Kiro's agent executes the build
    scripts through its own terminal tool the same way it runs any other shell command.

VS Code — GitHub Copilot Chat (Agent mode)
    Reference SKILL.md with #file:SKILL.md in a chat prompt, or add its contents to
    .github/copilot-instructions.md so it's always in context. Agent mode can run terminal
    commands, so it can execute the two scripts directly.

VS Code — Cline / Roo Code / Continue
    Add SKILL.md as a custom rule/instructions file for the extension (each has its own rules
    folder — .clinerules, .roo/rules/, or a Continue config), or paste it into the chat context.
    All three can run shell commands from within the editor.

PyCharm / JetBrains AI Assistant or Junie
    Attach SKILL.md as custom instructions/context, or paste its content into the chat. Junie's
    agent mode (and AI Assistant's terminal access) can run the Python/Node build commands.

Any other agentic tool
    The pattern is always the same: (1) get SKILL.md and references/ into the assistant's context
    — via a rules file, a pinned/attached file, or a direct paste; (2) confirm the assistant has
    shell/terminal execution so it can run scripts/build_deck.py and node scripts/deck_engine.js;
    (3) ask for a deck. If the assistant has no web-search tool, it will fall back to the cached
    data in data/ and references/ per SKILL.md Step 4, and flag resources/diagrams for manual
    verification instead.

Repository Layout

    claude-deck-architect/
    ├── SKILL.md                     # Skill definition (read by Claude Desktop/Code and, per above, any agentic IDE)
    ├── manifest.json                # Claude Desktop plugin manifest
    ├── .claude-plugin/plugin.json   # Claude Code plugin manifest
    ├── package.json                 # pptxgenjs dependency
    ├── requirements.txt             # Python dependencies
    ├── references/
    │   ├── themes.md                # Color palettes and typography per theme
    │   ├── ecosystem-profiles.md    # Technical vocabulary and depth per ecosystem
    │   ├── slide-archetypes.md      # 16 layout patterns, composition rules, and mandatory slides
    │   ├── diagram-guide.md         # Mermaid conventions + required web-sourcing step per provider
    │   ├── content-plan-schema.md   # JSON Schema for deck definitions
    │   └── troubleshooting.md       # Debugging and configuration
    ├── scripts/
    │   ├── build_deck.py            # Orchestrator: validates, renders, builds PPTX/PDF
    │   ├── deck_engine.js           # pptxgenjs renderer for all 16 archetypes
    │   ├── render_mermaid.py        # Mermaid to themed PNG conversion
    │   ├── cli.py                   # Command-line argument parsing
    │   ├── validate_plan.py         # Pre-flight validation (5 second checks)
    │   └── fetch_resources.py       # Refreshes data/topics.json from GitHub API
    ├── data/
    │   ├── themes.json              # Machine-readable theme definitions
    │   ├── topics.json              # Curated documentation and repository links
    │   └── history.jsonl            # Append-only log of generated decks
    ├── examples/
    │   ├── kubernetes-intro.json    # Complete 12-slide Kubernetes example (Speaker + Comparison included)
    │   └── aws-lambda.json          # Complete 11-slide AWS Lambda example
    ├── assets/
    │   ├── logos/deck-architect-icon.svg
    │   ├── icons/                   # Custom icons for slides
    │   └── backgrounds/             # Optional background images
    ├── templates/                   # Optional: base .pptx templates for editing
    ├── LICENSE
    └── README.md

How it Works

1. Invocation: user enters /deck-architect <topic> with optional parameters (slide count,
   provider, difficulty level, output format, speaker LinkedIn URL).

2. Interactive intake: the agent clarifies any missing parameters through a single combined
   prompt (slide count, provider, level, format, speaker info). Sensible defaults apply if
   unanswered; the Speaker slide is simply skipped if no LinkedIn URL or bio is given.

3. Content planning: the agent reads themes, ecosystem profiles, slide archetypes, and curated
   resources, then drafts a JSON content plan following references/content-plan-schema.md. This
   is also where it web-searches the official architecture diagram and the real comparison
   competitors for the topic — see references/diagram-guide.md and
   references/slide-archetypes.md → "Mandatory slides".

4. Build execution: build_deck.py processes the content plan by validating it against the JSON
   schema, rendering Mermaid diagrams to themed PNGs, calling deck_engine.js to generate the
   PPTX file, and optionally converting to PDF via LibreOffice.

5. Quality assurance: the agent runs content validation (markitdown), file schema checks, and
   visual verification before delivering the final files.

The workflow is the same regardless of which agentic IDE is driving it — see "Works in any
agentic IDE" above.

Installation

System Requirements

Node.js: version 18 or higher
Python: version 3.9 or higher
Git: for cloning the repository
pip: Python package manager (usually included with Python)

Step 1: Clone the Repository

macOS and Linux:

    git clone https://github.com/Soumya14041987/claude-deck-architect.git
    cd claude-deck-architect

Windows (Command Prompt or PowerShell):

    git clone https://github.com/Soumya14041987/claude-deck-architect.git
    cd claude-deck-architect

Step 2: Install Node and Python Dependencies

macOS and Linux:

    npm install
    pip install -r requirements.txt --break-system-packages

Windows (Command Prompt):

    npm install
    pip install -r requirements.txt

Windows (PowerShell):

    npm install
    pip install -r requirements.txt

Step 3: Optional Mermaid CLI Setup

For native Mermaid diagram rendering (recommended for best visual quality):

macOS and Linux:

    npm install -g @mermaid-js/mermaid-cli
    npx puppeteer browsers install chrome-headless-shell

Windows (Command Prompt):

    npm install -g @mermaid-js/mermaid-cli
    npx puppeteer browsers install chrome-headless-shell

Without this, diagrams render as simple Pillow-drawn boxes instead of styled Mermaid output.
Both are on-theme and legible, but Mermaid renders are more professional.

Setting up for Claude Desktop

macOS Setup

1. Create the plugins directory if it doesn't exist:

    mkdir -p ~/Library/Application\ Support/Claude/plugins

2. Create a symlink from your cloned repository to Claude Desktop's plugins folder:

    ln -s /path/to/claude-deck-architect \
      ~/Library/Application\ Support/Claude/plugins/claude-deck-architect

   Replace /path/to/claude-deck-architect with the actual path where you cloned it.
   If you cloned it in your home directory:

    ln -s ~/claude-deck-architect \
      ~/Library/Application\ Support/Claude/plugins/claude-deck-architect

3. Restart Claude Desktop completely (quit and reopen).

4. Verify installation: In Claude Desktop, type /deck-architect and you should see the
   command autocomplete.

Windows Setup

1. Open File Explorer and navigate to:

    %APPDATA%\Claude\plugins

   If the plugins folder doesn't exist, create it:
   Right-click in %APPDATA%\Claude and select New > Folder, name it "plugins"

2. Create a symbolic link from your cloned repository to the plugins folder.
   Open Command Prompt as Administrator and run:

    mklink /d "%APPDATA%\Claude\plugins\claude-deck-architect" \
      "C:\path\to\claude-deck-architect"

   Replace C:\path\to\claude-deck-architect with the actual path to your cloned folder.
   Example (if cloned in Documents):

    mklink /d "%APPDATA%\Claude\plugins\claude-deck-architect" \
      "%USERPROFILE%\Documents\claude-deck-architect"

3. Restart Claude Desktop completely (quit and reopen).

4. Verify installation: In Claude Desktop, type /deck-architect and you should see the
   command autocomplete.

Alternative (No Symlink)

If symlinks don't work, copy the folder directly:

macOS:

    cp -r /path/to/claude-deck-architect \
      ~/Library/Application\ Support/Claude/plugins/

Windows:

    xcopy /E /I C:\path\to\claude-deck-architect \
      %APPDATA%\Claude\plugins\claude-deck-architect

Setting up for Claude Code

Option A: Auto-Discovery (Recommended)

1. Open the cloned claude-deck-architect folder in Claude Code:

    code /path/to/claude-deck-architect

2. Claude Code automatically discovers SKILL.md in the working directory.

3. Type /deck-architect in any Claude Code chat and it will work.

Option B: Plugin Registration

1. Navigate to the folder:

    cd /path/to/claude-deck-architect

2. Register as a plugin:

    claude plugin add .

   Or:

    claude plugin install .

3. Restart Claude Code.

4. Type /deck-architect in any chat and it will work.

Setting up for Cursor, Kiro, VS Code, PyCharm, and other agentic IDEs

These tools don't share Claude's plugin format, so there's no auto-discovery step — instead, get
SKILL.md into the assistant's context so its agent treats it as instructions, then let the agent
run the two build scripts through its own terminal/shell tool. See "Works in any agentic IDE"
above for the exact mechanism per tool (Project Rules in Cursor, steering docs in Kiro, custom
instructions in Copilot Chat/Cline/Continue, custom instructions in JetBrains AI Assistant/Junie).
Once SKILL.md is in context, ask for a deck the same way you would in Claude Code — the underlying
workflow (intake → theme/content plan → diagrams → build → QA → deliver) is identical.

Verifying Installation

Test on Claude Desktop

1. Open Claude Desktop.
2. Start a new conversation.
3. Type: /deck-architect AWS Lambda
4. You should see the skill activate and ask clarifying questions.

Test on Claude Code

1. Open Claude Code with the claude-deck-architect folder.
2. Start a new chat.
3. Type: /deck-architect Kubernetes basics
4. You should see the skill activate and ask clarifying questions.

Test on any other agentic IDE

1. Attach or reference SKILL.md as described above.
2. Ask: "Build me a slide deck about Kubernetes basics using SKILL.md."
3. You should see the agent ask the same clarifying questions (provider, slide count, level,
   format, speaker info) before running the build scripts.

Troubleshooting Installation

Command not found after restart

Claude Desktop: Check that the path in the symlink is correct.

    ls -la ~/Library/Application\ Support/Claude/plugins/

   Should show: claude-deck-architect -> /actual/path

Windows: Verify the symlink was created:

    dir %APPDATA%\Claude\plugins

   Should show SYMLINK with the correct target.

Plugin not appearing in Claude Code

Make sure you're in the claude-deck-architect folder when you run claude plugin add.
Restart Claude Code after registration.

Agent isn't following SKILL.md in Cursor/Kiro/VS Code/PyCharm

Confirm the file is actually attached/referenced in the current chat context — these tools don't
auto-discover SKILL.md the way Claude Code does, so it has to be pinned, @-mentioned, or placed in
that tool's own rules/instructions folder each time you start a fresh session (unless you saved it
as a persistent rule).

Mermaid diagrams rendering as boxes

This is normal if you skipped Step 3 (Mermaid CLI setup). To enable Mermaid rendering:

    npm install -g @mermaid-js/mermaid-cli
    npx puppeteer browsers install chrome-headless-shell

Python/Node not found

Ensure Node.js 18+ and Python 3.9+ are installed and in your PATH:

    node --version
    python3 --version

Update if needed from nodejs.org and python.org.

Running validate_plan.py Before First Build

Before using /deck-architect for the first time, validate your setup:

    python3 scripts/validate_plan.py --plan examples/kubernetes-intro.json

Expected output: All checks passed (6/6)

This confirms your Python environment and JSON schema validation are working.

Build Your First Deck

Test the complete workflow:

macOS and Linux:

    python3 scripts/build_deck.py \
      --plan examples/kubernetes-intro.json \
      --out test-deck.pptx \
      --verbose

Windows:

    python3 scripts/build_deck.py ^
      --plan examples/kubernetes-intro.json ^
      --out test-deck.pptx ^
      --verbose

Expected: A test-deck.pptx file is created in the current directory with a 12-slide Kubernetes
deck (including the Speaker and Comparison slides). The --verbose flag shows real-time progress.

Examples

    /deck-architect AWS Bedrock AgentCore
    /deck-architect LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)
    /deck-architect Platform Engineering with CNCF tooling (fundamentals)
    /deck-architect Kubernetes eBPF with Cilium (30 slides, advanced, PDF)
    /deck-architect Azure OpenAI vs Amazon Bedrock (comparison, 15 slides)
    /deck-architect kagent for Kubernetes troubleshooting (speaker: linkedin.com/in/yourprofile)

Parameters

Slide count
    Any number from 10 to 60. Common choices: 10, 20, 30. Default: 15.

Cloud provider(s)
    AWS, GCP, Azure, Multi-cloud, or none (for CNCF/agentic-AI topics).
    Inferred from topic when possible.

Difficulty level
    Fundamentals, Intermediate, or Advanced. Default: Intermediate.

Output format
    PPTX, PDF, or both. Default: PPTX.

Speaker info
    A LinkedIn profile URL, or "skip". Adds a Speaker slide with name, role, bio, and contact
    handles sourced from the profile (or asked for directly if the profile can't be fetched).
    Default: skipped if not provided.

Theme, ecosystem vocabulary, and slide composition are determined automatically based on topic
and provider. See references/themes.md, references/ecosystem-profiles.md, and
references/slide-archetypes.md to understand or customize these mappings.

Mandatory content rules

Every generated deck, regardless of level or slide count, follows three fixed rules — see
references/slide-archetypes.md → "Mandatory slides" for full detail:

1. The Problem Statement (ProblemFriction) slide always comes right after the agenda — no deck
   opens with "what is X" before explaining why X matters.
2. A Comparison slide is always included, contrasting the topic against the real tools a
   practitioner would be choosing between in that scenario, sourced from current docs.
3. A Speaker slide is included whenever speaker info was provided at intake.

Customization

Add topic resources

Edit data/topics.json to add curated documentation and repository links for a topic.
Refresh GitHub star counts and last-updated timestamps:

    python3 scripts/fetch_resources.py --topic your-topic-key

Add a new theme

1. Add an entry to data/themes.json with color definitions and typography.
2. Document the theme in references/themes.md following the existing format.

Add a slide archetype

1. Implement a render<Name> function in scripts/deck_engine.js.
2. Register it in the RENDERERS map at the bottom of that file.
3. Document the archetype's content-plan shape in references/content-plan-schema.md and
   references/slide-archetypes.md.

Troubleshooting

Refer to references/troubleshooting.md for detailed guidance. Common issues:

Diagrams render as simple boxes instead of styled Mermaid output
    The Mermaid CLI (mmdc) requires headless Chrome. Install with:
    npx puppeteer browsers install chrome-headless-shell
    
    The tool automatically falls back to Pillow-rendered diagrams without headless Chrome.
    These are still on-theme and legible, just simpler in appearance.

Architecture diagram doesn't match the vendor's current docs
    The agent may not have had web-search access when it drafted the plan. Ask it to re-verify
    the topology slide against the official architecture center for that provider (see
    references/diagram-guide.md) and rebuild.

Speaker slide has placeholder or missing info
    LinkedIn blocks most unauthenticated scraping, so the agent may not have been able to fetch
    the profile. Provide name, role, and a short bio directly instead of a URL.

PPTX reports as corrupt or won't open
    Validate the file:
    python3 scripts/office/validate.py your-deck.pptx
    
    Fix issues in the content plan or deck_engine.js, then rebuild. Do not hand-edit the PPTX
    XML directly.

GitHub API rate limiting
    Set a GITHUB_TOKEN environment variable to increase the rate limit from 60/hour to
    5,000/hour:
    export GITHUB_TOKEN=your_github_token

Pre-flight validation

Before building a deck, run the validation script to catch errors in 5 seconds instead of
waiting for a 15+ minute build:

    python3 scripts/validate_plan.py --plan my-deck.json

This checks file existence, JSON syntax, required fields, theme validity, and full schema
compliance, with clear remediation steps if any check fails.

License

This project is licensed under the MIT License. See LICENSE for details.
