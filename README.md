Deck Architect

Deck Architect is a Claude Skill for generating presentation-ready slide decks from a single topic.
It produces themed PPTX files (native, 16:9 aspect) and optional high-fidelity PDFs, with accurate
architecture diagrams, curated resources, and varied professional layouts.

Designed for cloud infrastructure, DevOps, platform engineering, and agentic AI content.
Common use cases: AWS re:Invent talks, KCD and CNCF meetups, GDG events, and internal tech shares.

Usage examples:

    /deck-architect AWS Bedrock AgentCore
    /deck-architect LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)
    /deck-architect Platform Engineering with CNCF tooling (fundamentals)
    /deck-architect Azure OpenAI vs Amazon Bedrock (comparison, 15 slides)

Features

Context-aware theming: Automatically selects color palette and typography based on cloud provider
or ecosystem (AWS orange, GCP blue, Azure electric, CNCF teal, multi-cloud neutral).

Architecture diagrams: Mermaid diagrams with real service names and flows, rendered to themed PNGs
with numbered callouts. Not generic "Service A to Service B" boxes.

Varied slide layouts: 15 distinct slide archetypes (title, agenda, problem statement, key concepts,
topology, deep dives, code specifications, comparisons, timelines, benchmarks, production gotchas,
demos, quotes, resources, calls to action). Decks read as human-designed, not templated.

Curated resources: Official documentation links and active GitHub repositories, sourced from
maintained seed files with live web search for missing content. No fabricated URLs.

Adaptive depth: Three difficulty levels (Fundamentals, Intermediate, Advanced) with
ecosystem-specific vocabulary. Content density matches audience expertise.

Speaker notes: Included on every relevant slide for presenter guidance.

Offline capable: All theme, layout, and profile data ships as static files. Network access is
optional for refreshing resource links and benchmarks. Graceful fallback to cached data.

Repository Layout

    claude-deck-architect/
    ├── SKILL.md                     # Skill definition (read by Claude Desktop/Code)
    ├── manifest.json                # Claude Desktop plugin manifest
    ├── .claude-plugin/plugin.json   # Claude Code plugin manifest
    ├── package.json                 # pptxgenjs dependency
    ├── requirements.txt             # Python dependencies
    ├── references/
    │   ├── themes.md                # Color palettes and typography per theme
    │   ├── ecosystem-profiles.md    # Technical vocabulary and depth per ecosystem
    │   ├── slide-archetypes.md      # 15 layout patterns and composition rules
    │   ├── diagram-guide.md         # Mermaid conventions per cloud provider
    │   ├── content-plan-schema.md   # JSON Schema for deck definitions
    │   └── troubleshooting.md       # Debugging and configuration
    ├── scripts/
    │   ├── build_deck.py            # Orchestrator: validates, renders, builds PPTX/PDF
    │   ├── deck_engine.js           # pptxgenjs renderer for 15 archetypes
    │   ├── render_mermaid.py        # Mermaid to themed PNG conversion
    │   ├── cli.py                   # Command-line argument parsing
    │   ├── validate_plan.py         # Pre-flight validation (5 second checks)
    │   └── fetch_resources.py       # Refreshes data/topics.json from GitHub API
    ├── data/
    │   ├── themes.json              # Machine-readable theme definitions
    │   ├── topics.json              # Curated documentation and repository links
    │   └── history.jsonl            # Append-only log of generated decks
    ├── examples/
    │   ├── kubernetes-intro.json    # Complete 10-slide Kubernetes example
    │   └── aws-lambda.json          # Complete 11-slide AWS Lambda example
    ├── assets/
    │   ├── logos/deck-architect-icon.svg
    │   ├── icons/                   # Custom icons for slides
    │   └── backgrounds/             # Optional background images
    ├── templates/                   # Optional: base .pptx templates for editing
    ├── LICENSE
    └── README.md

How it Works

1. Invocation: User enters /deck-architect <topic> with optional parameters (slide count, cloud
   provider, difficulty level, output format).

2. Interactive intake: Claude clarifies any missing parameters through a single combined prompt
   (slide count, provider, level, format). Sensible defaults apply if unanswered.

3. Content planning: Claude reads reference files (themes, ecosystem profiles, slide archetypes,
   curated resources) and drafts a JSON content plan following the schema in
   references/content-plan-schema.md.

4. Build execution: The build_deck.py script processes the content plan by:
   - Validating the plan against the JSON schema
   - Rendering Mermaid diagrams to themed PNGs
   - Calling deck_engine.js to generate the PPTX file
   - Optionally converting to PDF via LibreOffice

5. Quality assurance: Claude runs content validation (markitdown), file schema checks, and
   visual verification before delivering the final files.

The workflow is consistent whether running on Claude Desktop or Claude Code. Plugin manifests
handle discovery and invocation in each environment.

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

Expected: A test-deck.pptx file is created in the current directory with a 10-slide Kubernetes
deck. The --verbose flag shows real-time progress.

Examples

    /deck-architect AWS Bedrock AgentCore
    /deck-architect LangGraph + LangSmith (20 slides, advanced, AWS+GCP, PPTX+PDF)
    /deck-architect Platform Engineering with CNCF tooling (fundamentals)
    /deck-architect Kubernetes eBPF with Cilium (30 slides, advanced, PDF)
    /deck-architect Azure OpenAI vs Amazon Bedrock (comparison, 15 slides)

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

Theme, ecosystem vocabulary, and slide composition are determined automatically based on topic
and provider. See references/themes.md, references/ecosystem-profiles.md, and
references/slide-archetypes.md to understand or customize these mappings.

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
