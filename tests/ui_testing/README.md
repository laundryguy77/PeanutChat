# PeanutChat UI Testing Framework

## Overview
This framework uses Playwright + Chromium for human-like UI testing with screenshots as primary feedback.
12 parallel threads across 4 sequential sessions, each with 3 concurrent agents.

## Updated Timeout Configuration
Due to multiple model calls and LLM response times, all timeouts have been increased:

| Operation | Timeout |
|-----------|---------|
| Page load | 120,000ms (2 min) |
| Element visibility | 30,000ms (30 sec) |
| LLM response wait | 300,000ms (5 min) |
| Navigation | 60,000ms (1 min) |
| Screenshot capture | 10,000ms (10 sec) |

## Testing Philosophy
- **Screenshot-First**: Every interaction captures visual state
- **Code-Driven**: Learn expected behavior from code, not documentation
- **Investigation Only**: No fixes, just findings with evidence
- **No Assumptions**: Test everything multiple times from different angles
- **Human-Like**: Simulate real user behavior, click paths, timing
- **Sequential LLM Calls**: Agents avoid concurrent LLM requests within same session

## Session Structure
```
Session 1: Foundation & Navigation (run all 3 agents in parallel)
Session 2: Core Chat Features (after Session 1 completes)
Session 3: Profile, Memory & Knowledge (after Session 2 completes)
Session 4: MCP, Models & Edge Cases (after Session 3 completes)
```

## Parallel Safety
Each agent within a session:
- Creates unique test user: `testuser_{agent_id}_{timestamp}`
- Uses isolated browser context
- Tests non-overlapping feature areas
- Staggers LLM requests (wait for previous to complete)
- Records all findings to separate output files

## Output Structure
```
tests/ui_testing/
├── session1/
│   ├── agent1_auth_sidebar/
│   ├── agent2_themes_settings/
│   └── agent3_models_gauges/
├── session2/
│   ├── agent1_messaging_streaming/
│   ├── agent2_edit_fork_regen/
│   └── agent3_attachments_thinking/
├── session3/
│   ├── agent1_profile_adult/
│   ├── agent2_memory_knowledge/
│   └── agent3_parameters_compaction/
└── session4/
    ├── agent1_mcp_models/
    ├── agent2_errors_edge/
    └── agent3_integration/
```

## Key Files Reference (for agents)
- UI Entry: `/static/index.html`
- JavaScript: `/static/js/{app,auth,chat,settings,profile,memory,knowledge,mcp}.js`
- Styles: `/static/css/styles.css`
- Routers: `/app/routers/{auth,chat,settings,user_profile,memory,knowledge,mcp,models}.py`
- Services: `/app/services/*.py`

## Playwright Configuration
Each agent should use these timeout settings:

```python
# Browser launch
browser = await playwright.chromium.launch(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox']
)

# Context with extended timeouts
context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080}
)

# Page-level timeout (5 minutes for LLM responses)
page.set_default_timeout(300000)

# Navigation timeout (2 minutes)
page.set_default_navigation_timeout(120000)
```

## LLM Request Management
To avoid overwhelming the local Ollama instance:
1. **One LLM request at a time per agent** - wait for response before next
2. **Stagger agent starts** - 5 second delay between agent spawns
3. **Use shorter prompts** - minimize token generation time
4. **Screenshot during wait** - capture loading states while waiting

## Running the Tests
Each session prompt should be run in a separate Claude Code session.
Within each session, spawn 3 agents using the Task tool in parallel.
Wait for all agents to complete before starting next session.
