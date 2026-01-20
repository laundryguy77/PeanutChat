# PeanutChat UI Testing Framework

## Overview
This framework uses Playwright + Chromium for human-like UI testing with screenshots as primary feedback.
20 parallel threads across 4 sequential sessions, each with 5 concurrent agents.

## Testing Philosophy
- **Screenshot-First**: Every interaction captures visual state
- **Code-Driven**: Learn expected behavior from code, not documentation
- **Investigation Only**: No fixes, just findings with evidence
- **No Assumptions**: Test everything multiple times from different angles
- **Human-Like**: Simulate real user behavior, click paths, timing

## Session Structure
```
Session 1: Foundation & Navigation (run all 5 agents in parallel)
Session 2: Core Chat Features (after Session 1 completes)
Session 3: Profile, Memory & Knowledge (after Session 2 completes)
Session 4: MCP, Models & Edge Cases (after Session 3 completes)
```

## Parallel Safety
Each agent within a session:
- Creates unique test user: `testuser_{agent_id}_{timestamp}`
- Uses isolated browser context
- Tests non-overlapping feature areas
- Records all findings to separate output files

## Output Structure
```
tests/ui_testing/
├── session1/
│   ├── agent1_auth/
│   ├── agent2_sidebar/
│   ├── agent3_themes/
│   ├── agent4_settings/
│   └── agent5_models/
├── session2/
│   ├── agent1_messaging/
│   ├── agent2_streaming/
│   ├── agent3_edit_fork/
│   ├── agent4_attachments/
│   └── agent5_thinking/
├── session3/
│   ├── agent1_profile/
│   ├── agent2_adult_mode/
│   ├── agent3_memory/
│   ├── agent4_knowledge/
│   └── agent5_parameters/
└── session4/
    ├── agent1_mcp/
    ├── agent2_model_switch/
    ├── agent3_compaction/
    ├── agent4_errors/
    └── agent5_integration/
```

## Key Files Reference (for agents)
- UI Entry: `/static/index.html`
- JavaScript: `/static/js/{app,auth,chat,settings,profile,memory,knowledge,mcp}.js`
- Styles: `/static/css/styles.css`
- Routers: `/app/routers/{auth,chat,settings,user_profile,memory,knowledge,mcp,models}.py`
- Services: `/app/services/*.py`

## Running the Tests
Each session prompt should be run in a separate Claude Code session.
Within each session, spawn 5 agents using the Task tool in parallel.
