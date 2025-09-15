# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph learning project that demonstrates all major LangGraph features through a multi-agent blog writing system. The project follows a 15-phase development plan documented in `LANGGRAPH_COMPLETE_LEARNING_PROJECT.md`.

## Current Status: Phase 3 COMPLETE ✅

### Completed Phases
- ✅ **Phase 1**: Foundation Setup - Environment, dependencies, API connections
- ✅ **Phase 2**: State Management - ContentState, StateManager, database schema  
- ✅ **Phase 3**: Basic Agent Implementation - All 4 agents working

### Architecture

The system implements a multi-agent workflow for content creation:
- **Manager Agent**: Validates topics, initializes state, routes workflow (standard→research, quick→writer)
- **Research Agent**: Performs web searches using Brave Search API (single search for now)
- **Writer Agent**: Generates 400-800 word blog posts using Gemini 2.0 Flash
- **Review Agent**: Evaluates quality (0-100 score), provides feedback, NEVER modifies content

### Core Flow
Topic Input → Manager → Research (if standard) → Writer → Review → Complete

## Commands

### Development
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Validate setup (checks API connections)
python validate_setup.py

# Run the FastAPI application (when implemented)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
pytest

# Run tests with async support
pytest --asyncio-mode=auto

# Test specific components
python -c "from config import config; print(config.validate())"
python -c "from state import create_initial_state; print(create_initial_state('Test', 'quick'))"
```

## Project Structure

```
ai-content-agency/
├── agents/              # Agent implementations (manager, research, writer, review)
├── workflows/           # Workflow definitions and factory
│   └── subgraphs/      # Reusable workflow components
├── state/              # State management
│   ├── models.py       # ContentState TypedDict
│   └── storage.py      # StateManager for database operations
├── api/                # FastAPI endpoints
│   ├── main.py         # Core API
│   ├── streaming.py    # SSE streaming
│   └── human_loop.py   # Human feedback handling
├── database/           
│   └── schema.sql      # Supabase database schema
└── config.py           # Configuration and API clients
```

## Key Components

### State Management (ContentState)
The core state object contains:
- **Identification**: project_id, thread_id
- **Research Data**: notes, sources, parallel_results
- **Content**: draft, final_content, word_count
- **Quality**: score, revision_count, review_comments
- **Workflow Control**: next_action, enable_research, enable_revision
- **Human Interaction**: feedback, approval status
- **Time Travel**: checkpoint_history

### Database Schema (Supabase)
- `project_states`: Main state storage with JSONB
- `state_history`: Checkpoints for time travel
- `human_feedback`: Human-in-the-loop interactions
- Views: `active_projects`, `project_stats`

### Configuration
- **Gemini API**: Uses gemini-1.5-flash model (60 requests/min free)
- **Supabase**: PostgreSQL database with real-time capabilities
- **LangSmith**: Optional tracing (5000 traces/month free)
- **DuckDuckGo**: Unlimited search API (no key required)

## Development Phases Status

✅ **Phase 1**: Foundation Setup - Environment, dependencies, API connections
✅ **Phase 2**: State Management - ContentState, StateManager, database schema
✅ **Phase 3**: Basic Agent Implementation - Manager, Research, Writer, Review agents
🔄 **Phase 4**: Basic Linear Workflow (Next)
⏳ **Phase 5**: Research Subgraph
⏳ **Phase 6**: Parallel Execution
⏳ **Phase 7**: Complex Routing and Conditionals
⏳ **Phase 8**: Multiple Workflow Variants
⏳ **Phase 9**: Checkpointing and Time Travel
⏳ **Phase 10**: Human-in-the-Loop
⏳ **Phase 11**: Streaming and Real-time Updates
⏳ **Phase 12**: Dynamic Graph Building
⏳ **Phase 13**: Production Enhancements
⏳ **Phase 14**: Testing and Validation
⏳ **Phase 15**: Deployment and Documentation

## Important Notes

### Design Principles
- **Learning Focus**: Prioritize demonstrating LangGraph features over production complexity
- **Simplicity**: Avoid over-engineering; LangSmith handles monitoring
- **Type Safety**: Use TypedDict for state consistency
- **Async by Default**: StateManager uses async/await patterns

### Workflow Modes
- **Standard Mode**: Full workflow with research, revisions, and human review
- **Quick Mode**: Simplified workflow without research or revisions

### Key Settings
- `MAX_RETRIES`: 2 (for research attempts)
- `QUALITY_THRESHOLD`: 60 (minimum quality score)
- `MAX_CHECKPOINT_HISTORY`: 10 (time travel limit)
- `DEFAULT_WORD_COUNT_TARGET`: 1000 words

### API Rate Limits
- Gemini Pro: 60 requests per minute (free tier)
- DuckDuckGo: Unlimited (no API key required)
- Supabase: Based on your plan (free tier available)

## Phase 3 Implementation Details (COMPLETE)

### Agent Implementations

#### 1. Manager Agent (`agents/manager.py`)
- **Purpose**: Initialize projects and route workflows
- **Key Functions**:
  - Validates topic (2-50 words, contains actual words)
  - Cleans topic (removes special chars, title case)
  - Extracts keywords (max 5, removes stop words)
  - Routes: standard mode → research, quick mode → writer
- **No External APIs**: Pure Python processing

#### 2. Research Agent (`agents/research.py`)
- **Purpose**: Gather information from web
- **Uses**: Brave Search API (key: BSArHGdATae0Nala46gDn4e_ck_5ngk)
- **Process**: Single search, max 5 results
- **Extracts**: Descriptions → research_notes, URLs → sources
- **Note**: Replaced DuckDuckGo due to rate limits

#### 3. Writer Agent (`agents/writer.py`)
- **Purpose**: Generate blog posts
- **Uses**: Gemini 2.0 Flash API
- **System Prompt**: 200+ lines of detailed instructions
- **Output**: 400-800 word blog posts
- **Works**: With or without research notes

#### 4. Review Agent (`agents/review.py`)
- **Purpose**: Evaluate quality, NOT revise
- **Scoring**: 0-100 points (4 categories × 25)
- **Feedback**: Exactly 3 actionable points
- **CRITICAL**: Copies draft to final_content unchanged
- **Always**: Routes to complete (no conditional logic)

### Next Phase 4: Basic Linear Workflow
Will create `workflows/basic.py` with:
- Linear flow: Manager → Research → Writer → Review → End
- No conditionals or loops yet
- Basic state passing between agents
- FastAPI endpoints for testing

### API Keys and Configuration
```env
GEMINI_API_KEY=AIzaSyCAuGPeHyGwJdTxgsMP6ynDK1dMzaRMQfs
BRAVE_API_KEY=BSArHGdATae0Nala46gDn4e_ck_5ngk
SUPABASE_URL=https://hyfsgrqyzxlyypyjwipw.supabase.co
SUPABASE_KEY=eyJhbGci...kErY (full key in .env)
```

### Testing
All agents have test files (`test_*.py`) that verify:
- Core functionality
- State updates
- Error handling
- Integration readiness