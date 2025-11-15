# Clooney - Web Cloning Agent

**Project Goal**: Build an agentic system that clones web applications (tested on Asana) using LangGraph, achieving 60%+ accuracy in 1-day MVP.

**Approach**: 70% rules-based, 30% LLM intelligence. Hybrid architecture with iterative refinement (max 5 iterations).

---

## Project Context

### Technology Decisions
- **Backend**: Python 3.13+ with LangGraph for orchestration
- **Package Manager**: uv (modern, fast Python package manager)
- **Build Tool**: Makefile for common tasks
- **Browser Automation**: Playwright (Python)
- **LLM**: OpenAI GPT-4 (can swap to Anthropic Claude)
- **Target Output**: React.js + Tailwind CSS
- **Validation**: CSS property comparison (70%) + DOM structure (30%)

### Core Architecture
```
analyze_dom → detect_components → extract_tokens → generate_code → 
health_checks → validate → [refine → generate_code loop] → finalize
```

### Success Criteria
- ✅ Agent works on any URL (generic, not Asana-specific)
- ✅ Achieves 60%+ similarity score
- ✅ Iterates up to 5 times with top-N fixes
- ✅ Passes health checks (compile, lint)
- ✅ Clear documentation and runnable demo

---

## Phase 1: Foundation & Setup (2 hours)

**Goal**: Get basic infrastructure running and testable

### Tasks

#### 1.1 Project Setup
- [ ] Initialize project with `uv init`
- [ ] Create Python 3.13 virtual environment: `uv venv --python 3.13`
- [ ] Activate virtual environment: `source .venv/bin/activate`
- [ ] Add core dependencies to `pyproject.toml`:
  - langgraph, langchain, langchain-openai
  - playwright, pydantic, python-dotenv
  - fastapi, uvicorn (already present)
- [ ] Sync dependencies: `uv sync`
- [ ] Run setup command: `make setup` (installs Playwright browsers, etc.)
- [ ] Create `.env.template` with required API keys
- [ ] Create `.env` with actual keys (add to `.gitignore`)

**Files Created/Updated**:
- `pyproject.toml` (dependencies managed here)
- `.env.template`
- `.env`
- `Makefile` (add targets: setup, test, lint, format, run, clean)

**Makefile Targets to Create**:
- `setup`: Install uv, sync dependencies, install Playwright browsers
- `test`: Run pytest with coverage
- `lint`: Run ruff check
- `format`: Run ruff format
- `run`: Run the main application
- `clean`: Remove artifacts and build files

**Test**: `python --version` and `uv pip list` shows all packages installed

---

#### 1.2 State Schema
- [ ] Create `src/graph/state.py`
- [ ] Define Pydantic models: `ComponentSpec`, `DesignTokens`, `ValidationFailure`, `HealthCheckResult`
- [ ] Define `AgentState` TypedDict with all fields from design
- [ ] Add docstrings explaining each field

**Files Created**:
- `src/graph/state.py`

**Test**: Import state.py in Python REPL, instantiate models, verify no errors

---

#### 1.3 Logger Utility
- [ ] Create `src/utils/logger.py`
- [ ] Implement structured logging (use Python logging module)
- [ ] Add log levels: DEBUG, INFO, WARNING, ERROR
- [ ] Add timestamp and context to logs
- [ ] Test logging to console and file

**Files Created**:
- `src/utils/logger.py`

**Test**: Run logger, verify output format and file creation

---

#### 1.4 Entry Point Skeleton
- [ ] Create `src/main.py`
- [ ] Add CLI argument parsing (URL input)
- [ ] Add basic error handling
- [ ] Add placeholder for graph invocation
- [ ] Test with `python src/main.py --help`

**Files Created**:
- `src/main.py`

**Test**: `python src/main.py https://example.com` runs without errors (even if does nothing yet)

---

**Phase 1 Complete When**:
- ✅ All dependencies installed via `uv sync`
- ✅ Project structure exists
- ✅ `make setup` completes successfully
- ✅ State models defined and importable
- ✅ Logger works
- ✅ Entry point accepts URL input

**Estimated Time**: 2 hours

---

## Phase 2: DOM/CSS Extraction (2 hours)

**Goal**: Extract DOM structure and computed CSS from any URL

### Tasks

#### 2.1 DOM Extractor
- [ ] Create `src/extractors/dom_extractor.py`
- [ ] Implement `DOMExtractor` class
- [ ] Method: `extract(url: str) -> Dict`
  - Launch Playwright browser
  - Navigate to URL
  - Wait for networkidle
  - Execute JavaScript to extract DOM as JSON (hierarchical)
  - Extract: tag, classes, id, role, aria-label, bounds (x, y, width, height)
  - Filter out hidden elements (width/height = 0)
  - Return nested structure
- [ ] Add error handling for navigation failures
- [ ] Add timeout handling (30s default)

**Files Created**:
- `src/extractors/dom_extractor.py`

**Test**: 
```python
extractor = DOMExtractor()
result = extractor.extract("https://example.com")
assert "tag" in result
assert "children" in result
```

---

#### 2.2 CSS Extractor
- [ ] Create `src/extractors/css_extractor.py`
- [ ] Implement `CSSExtractor` class
- [ ] Method: `extract(url: str) -> Dict`
  - Use Playwright to navigate
  - Execute JavaScript to get `getComputedStyle()` for all visible elements
  - Extract properties: backgroundColor, color, padding, margin, width, height, fontSize, fontWeight, fontFamily, borderRadius, boxShadow, display
  - Store as: `{selector: string, properties: {prop: value}}`
  - Generate unique selectors (prefer id > class > tag+position)
- [ ] Filter out transparent/inherit values
- [ ] Normalize values (rgb to consistent format)

**Files Created**:
- `src/extractors/css_extractor.py`

**Test**:
```python
extractor = CSSExtractor()
result = extractor.extract("https://example.com")
assert len(result) > 0
assert "backgroundColor" in result[list(result.keys())[0]]
```

---

#### 2.3 Screenshot Capture
- [ ] Add screenshot capability to DOM extractor
- [ ] Method: `capture_screenshot(url: str, output_path: str)`
- [ ] Full page screenshot
- [ ] Save to artifacts directory
- [ ] Return path to saved screenshot

**Test**: Screenshot file exists at specified path and is valid PNG

---

#### 2.4 Analyze DOM Node (First Real Node)
- [ ] Create `src/graph/nodes/analyze_dom.py`
- [ ] Implement `AnalyzeDOMNode.execute(state: AgentState)`
  - Create session directory: `artifacts/session_{timestamp}/`
  - Call DOM extractor with state['url']
  - Call CSS extractor with state['url']
  - Capture screenshot
  - Save all to JSON files in session directory
  - Update state with results
  - Set `analysis_complete = True`
- [ ] Add error handling and logging

**Files Created**:
- `src/graph/nodes/analyze_dom.py`

**Test**: 
- Run node with mock state
- Verify artifacts directory created
- Verify JSON files contain expected data
- Check screenshot exists

---

**Phase 2 Complete When**:
- ✅ Can extract DOM from any URL
- ✅ Can extract CSS from any URL
- ✅ Can capture screenshots
- ✅ Analyze DOM node works end-to-end
- ✅ Data saved to artifacts directory

**Estimated Time**: 2 hours

---

## Phase 3: Rules Implementation (2 hours)

**Goal**: Implement rule-based component detection

### Tasks

#### 3.1 Semantic Detection Rule
- [ ] Create `src/rules/semantic_detection.py`
- [ ] Implement `SemanticDetector.detect(dom_structure: Dict)`
- [ ] Detect by tags: `<header>`, `<nav>`, `<aside>`, `<main>`, `<footer>`
- [ ] Create `ComponentSpec` for each detected element
- [ ] Set `type = 'layout'`
- [ ] Set `reason = 'Rule 1: Semantic tag detection'`
- [ ] Return list of ComponentSpec objects

**Files Created**:
- `src/rules/semantic_detection.py`

**Test**:
```python
detector = SemanticDetector()
mock_dom = {"tag": "header", "children": [...]}
specs = detector.detect(mock_dom)
assert len(specs) > 0
assert specs[0].type == "layout"
```

---

#### 3.2 Reusability Detection Rule
- [ ] Create `src/rules/reusability_detection.py`
- [ ] Implement `ReusabilityDetector.detect_reusable(dom_structure: Dict)`
- [ ] Algorithm:
  - Traverse DOM tree
  - Track structure patterns (same classes + similar hierarchy)
  - Count occurrences of each pattern
  - If pattern appears 3+ times → mark as reusable component
- [ ] Create ComponentSpec for reusable patterns
- [ ] Set `type = 'reusable'`
- [ ] Set `reason = 'Rule 3: Pattern appears N times'`

**Files Created**:
- `src/rules/reusability_detection.py`

**Test**: Feed DOM with repeated elements, verify detection of reusable components

---

#### 3.3 Hierarchy Analysis Rule
- [ ] Create `src/rules/hierarchy_rules.py`
- [ ] Implement `HierarchyAnalyzer.analyze(dom_structure: Dict)`
- [ ] Calculate nesting depth for each element
- [ ] If depth > 3 → suggest splitting into sub-component
- [ ] If parent has 5+ direct children → suggest splitting
- [ ] Annotate ComponentSpecs with hierarchy recommendations

**Files Created**:
- `src/rules/hierarchy_rules.py`

**Test**: Feed deeply nested DOM, verify split suggestions

---

#### 3.4 Design Token Extraction
- [ ] Create `src/rules/design_token_rules.py`
- [ ] Implement `DesignTokenExtractor.extract(css_data: Dict)`
- [ ] Extract colors:
  - Collect all backgroundColor and color values
  - Count occurrences
  - Keep colors appearing 2+ times
  - Return as `{primary: "#hex", secondary: "#hex", ...}`
- [ ] Extract spacing:
  - Collect all padding/margin values
  - Count occurrences
  - Keep spacing appearing 3+ times
  - Return as `{sm: "8px", md: "16px", ...}`
- [ ] Extract typography:
  - Font families, sizes, weights
  - Return grouped values

**Files Created**:
- `src/rules/design_token_rules.py`

**Test**: Feed CSS data, verify extracted tokens match frequency rules

---

#### 3.5 Detect Components Node
- [ ] Create `src/graph/nodes/detect_components.py`
- [ ] Implement `DetectComponentsNode.execute(state: AgentState)`
  - Load original_dom from state
  - Run all rule detectors
  - Merge results (avoid duplicates)
  - Save component_specs to state
  - Save to `artifacts/session_xxx/component_specs.json`

**Files Created**:
- `src/graph/nodes/detect_components.py`

**Test**: Run with real DOM data, verify component specs generated

---

#### 3.6 Extract Tokens Node
- [ ] Create `src/graph/nodes/extract_tokens.py`
- [ ] Implement `ExtractTokensNode.execute(state: AgentState)`
  - Load original_css from state
  - Run design token extractor
  - Save design_tokens to state
  - Save to `artifacts/session_xxx/design_tokens.json`

**Files Created**:
- `src/graph/nodes/extract_tokens.py`

**Test**: Run with CSS data, verify design tokens extracted

---

**Phase 3 Complete When**:
- ✅ All rules implemented and tested individually
- ✅ Component detection node works
- ✅ Token extraction node works
- ✅ JSON contracts saved correctly

**Estimated Time**: 2 hours

---

## Phase 4: LLM Code Generation (3 hours)

**Goal**: Generate React components using LLM

### Tasks

#### 4.1 Prompt Builder
- [ ] Create `src/generators/prompt_builder.py`
- [ ] Implement `PromptBuilder` class
- [ ] Method: `build_generation_prompt(component_specs, design_tokens, css_baseline)`
  - Load prompt template from `src/templates/prompts/generation.txt`
  - Inject component_specs as JSON
  - Inject design_tokens as JSON
  - Inject CSS baseline for validation reference
  - Return complete prompt string
- [ ] Method: `build_refinement_prompt(top_n_failures, iteration)`
  - Load template from `src/templates/prompts/refinement.txt`
  - Inject failures with suggestions
  - Explain priority of each failure
  - Return refinement prompt

**Files Created**:
- `src/generators/prompt_builder.py`
- `src/templates/prompts/generation.txt` (the full prompt text from earlier)
- `src/templates/prompts/refinement.txt`

**Test**: Build prompt with mock data, verify all placeholders filled

---

#### 4.2 LLM Client
- [ ] Create `src/generators/llm_client.py`
- [ ] Implement `LLMClient` class
- [ ] Support OpenAI API (primary)
- [ ] Method: `generate(prompt: str, model: str = "gpt-4o") -> str`
  - Call OpenAI chat completion API
  - Set temperature = 0 (deterministic)
  - Add retry logic (3 attempts with exponential backoff)
  - Handle rate limits
  - Return response content
- [ ] Add token usage logging

**Files Created**:
- `src/generators/llm_client.py`

**Test**: Call with simple prompt, verify response received

---

#### 4.3 Code Parser
- [ ] Create `src/generators/code_parser.py`
- [ ] Implement `CodeParser` class
- [ ] Method: `parse_components(llm_response: str) -> List[Dict]`
  - Parse `<COMPONENT path="...">...</COMPONENT>` tags using regex
  - Extract file path from path attribute
  - Extract code content between tags
  - Handle nested angle brackets in code
  - Validate closing tags match opening tags
  - Return list of `{path: str, code: str}`
- [ ] Handle malformed XML gracefully
- [ ] Detect truncation (incomplete tags)

**Files Created**:
- `src/generators/code_parser.py`

**Test**: Parse mock LLM response with multiple components, verify extraction

---

#### 4.4 File Writer
- [ ] Create `src/generators/file_writer.py`
- [ ] Implement `FileWriter` class
- [ ] Method: `write_components(components: List[Dict], output_dir: str)`
  - Create output directory structure: `output/src/components`
  - For each component: create parent directories if needed
  - Write code to file at specified path
  - Ensure UTF-8 encoding
  - Log each file written
- [ ] Method: `setup_react_project(output_dir: str)`
  - Create `package.json` with React + Vite dependencies
  - Create `vite.config.js`
  - Create `tailwind.config.js` with custom design tokens
  - Create `index.html` and `src/main.jsx`
  - Create `.gitignore`
  - Run `npm install` in output directory

**Files Created**:
- `src/generators/file_writer.py`

**Test**: Write mock components, verify files created at correct paths

---

#### 4.5 Generate Code Node
- [ ] Create `src/graph/nodes/generate_code.py`
- [ ] Implement `GenerateCodeNode.execute(state: AgentState)`
  - Check iteration count:
    - If iteration == 0: initial generation (no feedback)
    - If iteration > 0: refinement (include top_n_failures)
  - Build appropriate prompt using PromptBuilder
  - Call LLM using LLMClient
  - Parse response using CodeParser
  - If iteration == 0: setup React project first
  - Write components using FileWriter
  - Update state: generated_files, generation_count
  - Save to `artifacts/session_xxx/generation_result.json`

**Files Created**:
- `src/graph/nodes/generate_code.py`

**Test**: 
- Run with mock component specs
- Verify LLM called
- Verify files written to output/
- Check generation_result.json created

---

**Phase 4 Complete When**:
- ✅ Prompt builder works for both generation and refinement
- ✅ LLM client successfully calls API
- ✅ Code parser extracts components from LLM response
- ✅ File writer creates React project structure
- ✅ Generate code node orchestrates full generation flow

**Estimated Time**: 3 hours

---

## Phase 5: Health Checks & Dev Server (1.5 hours)

**Goal**: Validate generated code compiles and runs

### Tasks

#### 5.1 Dev Server Manager
- [ ] Create `src/utils/dev_server.py`
- [ ] Implement `DevServer` class
- [ ] Method: `start(output_dir: str, port: int = 3000)`
  - Run `npm run dev` in output directory as subprocess
  - Capture stdout/stderr
  - Store process reference
- [ ] Method: `wait_for_ready(timeout: int = 30)`
  - Poll localhost:3000 until responds
  - Timeout if not ready in time
  - Return True when ready
- [ ] Method: `stop()`
  - Terminate the subprocess
  - Clean up resources

**Files Created**:
- `src/utils/dev_server.py`

**Test**: Start server, verify localhost:3000 accessible, stop cleanly

---

#### 5.2 Health Checker
- [ ] Create `src/utils/health_checker.py`
- [ ] Implement `HealthChecker` class
- [ ] Method: `check_compile(output_dir: str) -> List[str]`
  - Run `npm run build` in output directory
  - Capture errors from stderr
  - Parse error messages
  - Return list of error strings
- [ ] Method: `check_lint(output_dir: str) -> List[str]`
  - Run `npx eslint src/` in output directory
  - Parse linting errors
  - Return list of errors
- [ ] Method: `run_all_checks(output_dir: str) -> HealthCheckResult`
  - Run all checks
  - Combine results
  - Return HealthCheckResult object with passed/failed status

**Files Created**:
- `src/utils/health_checker.py`

**Test**: Run against known good/bad React projects, verify error detection

---

#### 5.3 Health Checks Node
- [ ] Create `src/graph/nodes/health_checks.py`
- [ ] Implement `HealthChecksNode.execute(state: AgentState)`
  - Run all health checks using HealthChecker
  - Update state with health_status
  - Set health_check_passed = True/False
  - Log all errors found
  - If failed: prepare feedback for regeneration (save to state for next iteration)

**Files Created**:
- `src/graph/nodes/health_checks.py`

**Test**: Run with generated code, verify checks execute

---

**Phase 5 Complete When**:
- ✅ Dev server can start and stop cleanly
- ✅ Health checker detects compile/lint errors
- ✅ Health checks node integrates all checks
- ✅ State updated with health status

**Estimated Time**: 1.5 hours

---

## Phase 6: Validation & Comparison (3 hours)

**Goal**: Compare generated app to original and calculate score

### Tasks

#### 6.1 CSS Comparator
- [ ] Create `src/validators/css_comparator.py`
- [ ] Implement `CSSComparator` class
- [ ] Define properties to compare (list from design)
- [ ] Method: `compare(original_css: Dict, generated_css: Dict) -> Dict`
  - Match elements by selector (use fuzzy matching if needed)
  - For each matched element pair:
    - Compare all defined CSS properties
    - Exact match = +1 to matches
    - Any difference = add to failures list with details
  - Calculate: matches / total
  - Return: `{matches: int, total: int, failures: List[ValidationFailure]}`
- [ ] Normalize CSS values before comparison (rgb formats, spacing shorthands)

**Files Created**:
- `src/validators/css_comparator.py`

**Test**: Compare two CSS datasets, verify correct match counting

---

#### 6.2 Structure Comparator
- [ ] Create `src/validators/structure_comparator.py`
- [ ] Implement `StructureComparator` class
- [ ] Method: `compare(original_dom: Dict, generated_dom: Dict, expected_components: List) -> Dict`
  - Count components in generated vs expected
  - Calculate max hierarchy depth in both
  - Check parent-child relationships
  - Calculate structure score (weighted average of metrics)
  - Return: `{component_count_match: bool, hierarchy_depth_match: bool, score: float}`

**Files Created**:
- `src/validators/structure_comparator.py`

**Test**: Compare DOM structures, verify scoring logic

---

#### 6.3 Scorer
- [ ] Create `src/validators/scorer.py`
- [ ] Implement `Scorer` class
- [ ] Method: `calculate_score(css_result: Dict, structure_result: Dict) -> Dict`
  - CSS score = (matches / total) * 100
  - Structure score = from structure_result
  - Final score = (css_score * 0.7) + (structure_score * 0.3)
  - Return breakdown with all scores

**Files Created**:
- `src/validators/scorer.py`

**Test**: Calculate with mock results, verify weighted average

---

#### 6.4 Failure Ranker
- [ ] Create `src/validators/failure_ranker.py`
- [ ] Implement `FailureRanker` class
- [ ] Define severity weights (high=10, medium=5, low=1)
- [ ] Method: `rank(failures: List[ValidationFailure]) -> List[ValidationFailure]`
  - For each failure, calculate priority score:
    - Base score from severity
    - Add bonus for layout components
    - Add bonus for repeated components
    - Add bonus for visual properties
  - Sort by priority score (descending)
  - Return sorted list
- [ ] Method: `select_top_n(ranked: List, n: int) -> List`
  - Return first N from ranked list

**Files Created**:
- `src/validators/failure_ranker.py`

**Test**: Rank mock failures, verify priority ordering

---

#### 6.5 Validate Node
- [ ] Create `src/graph/nodes/validate.py`
- [ ] Implement `ValidateNode.execute(state: AgentState)`
  - Start dev server using DevServer utility
  - Extract DOM from localhost:3000 using DOM extractor
  - Extract CSS from localhost:3000 using CSS extractor
  - Compare CSS using CSSComparator
  - Compare structure using StructureComparator
  - Calculate final score using Scorer
  - Rank failures using FailureRanker
  - Select top N failures (N = state['top_n_fixes'])
  - Update state with all results
  - Increment iteration counter
  - Stop dev server
  - Save validation results to `artifacts/session_xxx/validation_result.json`

**Files Created**:
- `src/graph/nodes/validate.py`

**Test**: Run full validation on generated app, verify score calculation

---

**Phase 6 Complete When**:
- ✅ CSS comparison works correctly
- ✅ Structure comparison calculates scores
- ✅ Final score calculated with proper weights
- ✅ Failures ranked by priority
- ✅ Validate node orchestrates full validation

**Estimated Time**: 3 hours

---

## Phase 7: Iteration & Refinement (1.5 hours)

**Goal**: Implement feedback loop for improvements

### Tasks

#### 7.1 Iteration Tracker
- [ ] Create `src/utils/iteration_tracker.py`
- [ ] Implement `IterationTracker` class (from design)
- [ ] Track history of all iterations
- [ ] Calculate improvement between iterations
- [ ] Implement stop conditions:
  - Score >= 60%
  - Iteration >= 5
  - Score plateaued (< 1% improvement for 2 iterations)
- [ ] Return summary statistics

**Files Created**:
- `src/utils/iteration_tracker.py`

**Test**: Track mock iterations, verify stop conditions work

---

#### 7.2 Refine Node
- [ ] Create `src/graph/nodes/refine.py`
- [ ] Implement `RefineNode.execute(state: AgentState)`
  - Log current iteration results
  - Group top_n_failures by component
  - Log priority breakdown
  - Prepare context for next generation
  - No state changes (just logging and analysis)

**Files Created**:
- `src/graph/nodes/refine.py`

**Test**: Run with validation failures, verify logging

---

#### 7.3 Finalize Node
- [ ] Create `src/graph/nodes/finalize.py`
- [ ] Implement `FinalizeNode.execute(state: AgentState)`
  - Find best iteration (highest score)
  - Compile summary statistics
  - Generate final report with:
    - Best score achieved
    - Total iterations used
    - Full iteration history
    - Final failures breakdown
    - Top issues remaining
  - Save to `artifacts/session_xxx/final_report.json`
  - Update state with final_report

**Files Created**:
- `src/graph/nodes/finalize.py`

**Test**: Run with mock iteration history, verify report generated

---

**Phase 7 Complete When**:
- ✅ Iteration tracker works
- ✅ Refine node prepares for next iteration
- ✅ Finalize node generates complete report

**Estimated Time**: 1.5 hours

---

## Phase 8: LangGraph Integration (2 hours)

**Goal**: Wire all nodes together in LangGraph

### Tasks

#### 8.1 Graph Definition
- [ ] Create `src/graph/graph.py`
- [ ] Define the complete workflow (from design)
- [ ] Add all nodes to graph
- [ ] Define edges between nodes
- [ ] Implement conditional routing functions:
  - `route_after_health_check`: validate vs regenerate
  - `route_after_validation`: refine vs finalize
- [ ] Compile graph

**Files Created**:
- `src/graph/graph.py`

**Test**: Import and compile graph, verify no errors

---

#### 8.2 Routing Logic
- [ ] Implement `route_after_health_check(state: AgentState)`
  - If health_check_passed == True → "validate"
  - Else → "generate_code"
- [ ] Implement `route_after_validation(state: AgentState)`
  - If score >= 60% → "finalize"
  - If iteration >= 5 → "finalize"
  - If plateaued → "finalize"
  - Else → "refine"

**Test**: Test routing with various state configurations

---

#### 8.3 Main Integration
- [ ] Update `src/main.py`
- [ ] Create initial state from CLI args
- [ ] Invoke compiled graph
- [ ] Handle graph execution errors
- [ ] Print progress during execution
- [ ] Print final results after completion
- [ ] Show path to final report

**Files Updated**:
- `src/main.py`

**Test**: Run full pipeline with simple URL (like example.com)

---

**Phase 8 Complete When**:
- ✅ Graph compiles without errors
- ✅ All nodes connected correctly
- ✅ Conditional routing works
- ✅ Can execute full pipeline end-to-end

**Estimated Time**: 2 hours

---

## Phase 9: Testing & Refinement (2 hours)

**Goal**: Test on Asana, fix issues, optimize

### Tasks

#### 9.1 End-to-End Test on Asana
- [ ] Create Asana trial account
- [ ] Run: `python src/main.py https://app.asana.com/home`
- [ ] Monitor execution, log any errors
- [ ] Verify all phases execute
- [ ] Check artifacts directory for outputs
- [ ] Check output/ directory for generated app
- [ ] Review final score and report

**Expected Issues**:
- Authentication walls (may need to handle login)
- Complex components not detected correctly
- CSS mismatches on first iteration
- Health checks may fail initially

---

#### 9.2 Bug Fixes
- [ ] Fix any crashes or errors found
- [ ] Improve error messages
- [ ] Add missing error handling
- [ ] Fix CSS comparison edge cases
- [ ] Improve component detection rules if needed

---

#### 9.3 Optimization
- [ ] Review LLM prompts, improve clarity
- [ ] Tune top_n_fixes parameter (try 10, 15, 20)
- [ ] Optimize CSS property matching (normalize values)
- [ ] Add progress indicators for long operations
- [ ] Improve logging (show current phase clearly)

---

#### 9.4 Documentation
- [ ] Create README.md with:
  - Project overview
  - Setup instructions (using uv and Makefile)
  - Usage examples
  - Architecture diagram (text-based)
  - Configuration options
  - Troubleshooting guide
  - Available make commands
- [ ] Create ARCHITECTURE.md explaining design decisions
- [ ] Document Makefile targets and their purposes
- [ ] Add docstrings to all major functions
- [ ] Comment complex logic

**Files Created**:
- `README.md`
- `ARCHITECTURE.md`

---

**Phase 9 Complete When**:
- ✅ Successfully runs on Asana home page
- ✅ Achieves 60%+ score (or close to it)
- ✅ All bugs fixed
- ✅ Documentation complete

**Estimated Time**: 2 hours

---

## Phase 10: Demo Preparation (1 hour)

**Goal**: Prepare submission artifacts

### Tasks

#### 10.1 Test on Multiple Pages
- [ ] Test on Asana Home page
- [ ] Test on Asana Projects page (if time permits)
- [ ] Test on Asana Tasks page (if time permits)
- [ ] Document results for each

---

#### 10.2 Create Demo Artifacts
- [ ] Capture screenshots: original vs generated vs diff
- [ ] Record terminal output of full run
- [ ] Save example final_report.json
- [ ] Create comparison images showing accuracy

---

#### 10.3 Final Polish
- [ ] Clean up code (remove debug prints)
- [ ] Ensure .env.template is complete
- [ ] Verify .gitignore covers secrets and build artifacts
- [ ] Test setup from scratch in clean directory using `uv` and `make setup`
- [ ] Verify all Makefile targets work correctly
- [ ] Write clear error messages for common issues

---

#### 10.4 Submission Package
- [ ] Create zip or GitHub repo
- [ ] Ensure README has clear run instructions
- [ ] Include example outputs in artifacts/
- [ ] Add screenshots showing results
- [ ] Write submission notes explaining approach

---

**Phase 10 Complete When**:
- ✅ Can run on Asana successfully
- ✅ Demo artifacts ready
- ✅ Documentation clear and complete
- ✅ Submission package ready

**Estimated Time**: 1 hour

---

## Progress Tracking

### Overall Progress
- [ ] Phase 1: Foundation & Setup (2h)
- [ ] Phase 2: DOM/CSS Extraction (2h)
- [ ] Phase 3: Rules Implementation (2h)
- [ ] Phase 4: LLM Code Generation (3h)
- [ ] Phase 5: Health Checks & Dev Server (1.5h)
- [ ] Phase 6: Validation & Comparison (3h)
- [ ] Phase 7: Iteration & Refinement (1.5h)
- [ ] Phase 8: LangGraph Integration (2h)
- [ ] Phase 9: Testing & Refinement (2h)
- [ ] Phase 10: Demo Preparation (1h)

**Total Estimated Time**: 20 hours (flexible for 1-2 day MVP)

---

## Session Recovery Points

If session breaks, resume by:

1. **Check last completed phase** - Review checkboxes above
2. **Verify artifacts** - Check which JSON files exist in artifacts/
3. **Test last working component** - Run isolated tests for last completed module
4. **Continue from next unchecked task** - Follow phase order

### Quick Recovery Commands
```bash
# Check what's been done
ls -la src/graph/nodes/  # See which nodes exist
ls -la artifacts/        # See test outputs
make test               # Run existing tests (or: pytest)

# Test specific components
python -c "from src.extractors.dom_extractor import DOMExtractor; print('DOM extractor OK')"
python -c "from src.graph.state import AgentState; print('State OK')"

# Reinstall dependencies if needed
uv sync                 # Sync from pyproject.toml
make setup             # Run full setup
```

---

## Key Decisions & Trade-offs

**Recorded for context when resuming:**

1. **Hybrid approach**: 70% rules, 30% LLM (not 100% LLM)
2. **Python for agent**: Better LLM libs, easier scripting
3. **Top-N fixes**: Fix 10-15 highest priority issues per iteration
4. **Hard stop at 5 iterations**: Prevent infinite loops
5. **60% target score**: Achievable in MVP timeframe
6. **CSS weight 70%, Structure 30%**: Visual accuracy prioritized
7. **Health checks required**: Must compile before validation
8. **No screenshot comparison yet**: CSS comparison sufficient for MVP

---

## Dependencies Between Phases

```
Phase 1 (Setup) 
  ↓ 
Phase 2 (Extraction) - requires Phase 1
  ↓
Phase 3 (Rules) - requires Phase 2
  ↓
Phase 4 (Generation) - requires Phase 3
  ↓
Phase 5 (Health) - requires Phase 4
  ↓
Phase 6 (Validation) - requires Phase 2, 5
  ↓
Phase 7 (Iteration) - requires Phase 6
  ↓
Phase 8 (Integration) - requires ALL previous phases
  ↓
Phase 9 (Testing) - requires Phase 8
  ↓
Phase 10 (Demo) - requires Phase 9
```

Cannot skip phases. Must complete in order.

---

## Success Metrics Per Phase

- **Phase 1**: All imports work, no dependency errors
- **Phase 2**: Can extract DOM/CSS from real websites
- **Phase 3**: Rules detect components correctly (test on mock data)
- **Phase 4**: LLM generates valid React code
- **Phase 5**: Generated code compiles without errors
- **Phase 6**: Validation produces score and failures
- **Phase 7**: Iteration loop improves scores
- **Phase 8**: Full pipeline runs without crashes
- **Phase 9**: Achieves 60%+ on Asana
- **Phase 10**: Submission ready