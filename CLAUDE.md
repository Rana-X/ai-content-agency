# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Project Overview

**AI Content Agency** - A comprehensive LangGraph learning project demonstrating ALL major LangGraph features through a multi-agent blog writing system. Built in 15 phases, currently on Phase 3 (COMPLETE).

### Project Goals
- Learn and implement every LangGraph feature
- Build a functional multi-agent content creation system
- Create reusable patterns for production applications
- Document the learning journey comprehensively

## 📍 Current Status: Phase 4 COMPLETE ✅

### ✅ Completed Phases

#### Phase 1: Foundation Setup
- Python 3.9+ environment (venv)
- Dependencies installed (requirements.txt)
- API connections configured and tested
- GitHub repository: https://github.com/Rana-X/ai-content-agency

#### Phase 2: State Management System
- ContentState TypedDict with all fields for phases 3-12
- StateManager with async CRUD operations
- Supabase tables: project_states, state_history, human_feedback
- Checkpoint/restore functionality for time travel

#### Phase 3: Basic Agent Implementation
- **Manager Agent**: Topic validation, state initialization, workflow routing
- **Research Agent**: Brave Search API integration (replaced DuckDuckGo)
- **Writer Agent**: Gemini 2.0 Flash for 400-800 word blog posts
- **Review Agent**: 0-100 scoring, 3 feedback points, NO content modification

#### Phase 4: Basic Linear Workflow & API ✅ COMPLETE
**Implemented Files:**
- `workflows/basic.py` - Linear workflow with LangGraph StateGraph
- `api/main.py` - FastAPI application with all endpoints

**Key Achievements:**
1. **Linear Workflow Implementation**
   - Connected all 4 agents: Manager → Research → Writer → Review → End
   - Used LangGraph StateGraph with ContentState
   - Added MemorySaver checkpointer for state persistence
   - Created manager_wrapper to handle Manager's special input requirements

2. **FastAPI Application**
   - POST /create - Starts workflow in background, returns project_id immediately
   - GET /status/{project_id} - Shows real-time workflow progress
   - GET /content/{project_id} - Returns generated blog content
   - GET /state/{project_id} - Debug endpoint for full state inspection
   - GET /health - Health check with database connectivity status
   - Background task execution using BackgroundTasks

3. **Database Issue Resolution** 🔧
   - **Problem**: Supabase connection failed with `TypeError: __init__() got an unexpected keyword argument 'proxy'`
   - **Cause**: Version incompatibility between supabase 2.9.0 and supabase_auth/gotrue
   - **Solution**: Upgraded to supabase==2.18.1, supabase_auth==2.12.3, httpx==0.28.1
   - **Result**: Full database persistence working, all CRUD operations functional
   - Created `test_db_fix.py` to verify database connectivity

**Testing Results:**
- Workflow executes end-to-end successfully
- Generated 492-word blog post on "Database Test Blog Post About Python"
- Quality score: 65/100 with 3 review comments
- Research found 5 sources and notes
- Full state persisted to Supabase

### 🔄 Next Phase: Phase 5 - Research Subgraph Implementation
Create modular research component in `workflows/subgraphs/research.py`

## 🏗️ Architecture

### Agent Flow
```
Standard Mode: Topic → Manager → Research → Writer → Review → Complete
Quick Mode:    Topic → Manager → Writer → Review → Complete
```

### Agent Details

| Agent | Purpose | Key Features | APIs Used |
|-------|---------|--------------|-----------|
| **Manager** | Initialize & Route | • Validates topic (2-50 words)<br>• Cleans input<br>• Extracts keywords<br>• Routes by mode | None (Pure Python) |
| **Research** | Gather Information | • Single web search<br>• Extracts descriptions & URLs<br>• Max 5 results | Brave Search API |
| **Writer** | Generate Content | • 400-800 word posts<br>• 200+ line system prompt<br>• Works with/without research | Gemini 2.0 Flash |
| **Review** | Evaluate Quality | • 0-100 score (4×25 points)<br>• 3 feedback comments<br>• NEVER modifies content | Gemini 2.0 Flash |

## 📁 Project Structure

```
ai-content-agency/
├── agents/                 # ✅ Phase 3 - All agents implemented
│   ├── manager.py         # Topic validation & routing
│   ├── research.py        # Brave Search integration
│   ├── writer.py          # Content generation
│   ├── review.py          # Quality evaluation
│   └── test_*.py          # Test files for each agent
├── state/                 # ✅ Phase 2 - Complete
│   ├── models.py          # ContentState TypedDict
│   └── storage.py         # StateManager class
├── workflows/             # 🔄 Phase 4 - Next
│   └── subgraphs/         # ⏳ Phase 5
├── api/                   # 🔄 Phase 4
│   ├── main.py           
│   ├── streaming.py       # ⏳ Phase 11
│   └── human_loop.py      # ⏳ Phase 10
├── database/              
│   └── schema.sql         # Supabase schema
├── config.py              # Configuration & API clients
├── requirements.txt       # Dependencies
└── .env                   # API keys & secrets
```

## 🔑 Configuration & API Keys

### Environment Variables (.env)
```bash
# Gemini API (Google AI Studio)
GEMINI_API_KEY=your_actual_gemini_key  # Get from Google AI Studio

# Brave Search API (2000 requests/month free)
BRAVE_API_KEY=your_brave_api_key  # Get from Brave Search API

# Supabase (Database)
SUPABASE_URL=your_supabase_url  # From Supabase project settings
SUPABASE_KEY=your_supabase_anon_key  # From Supabase API settings

# LangSmith (Optional - Monitoring)
LANGCHAIN_API_KEY=your_langsmith_key  # Optional for tracing
LANGCHAIN_TRACING_V2=false  # Set true to enable
LANGCHAIN_PROJECT=ai-content-agency  # Project name in LangSmith
```

## 🔧 Configuration Module Details

### Config.py Structure
- **API Clients**: Methods to get Gemini and Supabase clients
- **Validation**: `config.validate()` checks all required API keys
- **LangSmith Setup**: Automatic tracing configuration if enabled
- **Rate Limiting**: GEMINI_REQUESTS_PER_MINUTE (default: 60)
- **Workflow Settings**: MAX_RETRIES (2), QUALITY_THRESHOLD (60)
- **Directory Paths**: Automatic path resolution for all project directories

### Workflow Status Constants
- CREATED, STARTED, RESEARCHING, WRITING, REVIEWING
- PENDING_HUMAN_REVIEW, REVISING, COMPLETED, FAILED

### Agent Names Constants
- MANAGER, RESEARCH, WRITER, REVIEW

## 💻 Commands

### Development Setup
```bash
# Navigate to project
cd /Users/rana/Downloads/cli-ai/ai-content-agency

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Validate configuration
python -c "from config import config; print(config.validate())"
```

### Testing Agents
```bash
# Test individual agents (all test files available)
python agents/test_manager.py
python agents/test_research.py
python agents/test_writer.py
python agents/test_review.py

# Test state management
python -c "from state.models import create_initial_state; print(create_initial_state('Test Topic', 'standard'))"

# Validate complete setup
python validate_setup.py  # If available
```

### Git Operations
```bash
# Check status
git status

# Commit changes
git add -A
git commit -m "Your message"

# Push to GitHub
git push origin master
```

## 📊 State Management

### ContentState Fields
The state includes all fields needed for phases 3-12:

**Core Fields**
- `project_id`, `thread_id`, `topic`, `mode`, `status`

**Research Data**
- `research_notes`, `sources`, `research_attempts`, `parallel_results`

**Content**
- `draft`, `final_content`, `word_count`

**Quality & Review**
- `quality_score`, `revision_count`, `review_comments`

**Workflow Control**
- `next_action`, `assigned_agent`, `enable_research`, `enable_revision`

**Human Interaction**
- `human_feedback`, `human_approved`

**Time Travel**
- `checkpoint_history`, `current_checkpoint`

## 🚦 Development Phases

| Phase | Status | Description | Key Features |
|-------|--------|-------------|--------------|
| 1 | ✅ | Foundation Setup | Environment, dependencies, APIs |
| 2 | ✅ | State Management | ContentState, StateManager, database |
| 3 | ✅ | Basic Agents | Manager, Research, Writer, Review |
| **4** | **🔄 Next** | **Basic Linear Workflow** | **Simple flow, FastAPI endpoints** |
| 5 | ⏳ | Research Subgraph | Modular research component |
| 6 | ⏳ | Parallel Execution | 3 simultaneous searches |
| 7 | ⏳ | Complex Routing | Retry logic, conditionals |
| 8 | ⏳ | Multiple Workflows | Standard vs Quick modes |
| 9 | ⏳ | Checkpointing | Time travel functionality |
| 10 | ⏳ | Human-in-the-Loop | Review interruption |
| 11 | ⏳ | Streaming | Real-time updates |
| 12 | ⏳ | Dynamic Graphs | Runtime construction |
| 13 | ⏳ | Production Enhancements | Error handling, monitoring |
| 14 | ⏳ | Testing & Validation | Comprehensive test suite |
| 15 | ⏳ | Deployment | Production deployment |

## ⚠️ Important Notes

### Critical Implementation Details
1. **Review Agent NEVER modifies content** - It only evaluates and scores
2. **Manager routes based on mode** - standard → research, quick → writer
3. **Research uses Brave API** - DuckDuckGo was replaced due to rate limits
4. **State is pre-built for all phases** - No schema changes needed
5. **All agents are standalone** - Ready for LangGraph orchestration

### Design Principles
- **Learning Focus**: Demonstrate LangGraph features clearly
- **Simplicity**: Avoid over-engineering
- **Type Safety**: Use TypedDict for state consistency
- **Async by Default**: StateManager uses async/await
- **Error Handling**: All agents handle failures gracefully

### Common Issues & Solutions
- **SSL Warning**: Ignore "NotOpenSSLWarning" - it's harmless
- **Rate Limits**: Brave allows 2000 requests/month (free tier)
- **Gemini Errors**: Check API key and internet connection
- **Import Errors**: Ensure venv is activated with `source venv/bin/activate`
- **Supabase Connection**: Verify URL and anon key are correct
- **Missing Dependencies**: Run `pip install -r requirements.txt`

## 📝 Quick Reference

### Test Any Agent
```python
from agents.manager import ManagerAgent
from state.models import create_initial_state

state = create_initial_state("AI in Healthcare", "standard")
agent = ManagerAgent()
result = agent.process("AI in Healthcare", "standard")
print(result["next_action"])  # Should be "research"
```

### Check Database Connection
```python
from config import config
client = config.get_supabase_client()
print("Connected!" if client else "Failed")
```

### Generate Sample Content
```python
from agents.writer import WriterAgent
from state.models import create_initial_state

state = create_initial_state("Python Programming", "quick")
agent = WriterAgent()
result = agent.process(state)
print(f"Generated {result['word_count']} words")
```

## 🛠️ Phase 4 Implementation Details (For Next Claude Instance)

### Critical Implementation Notes:

#### 1. Manager Agent Wrapper Required
```python
def manager_wrapper(state: ContentState) -> ContentState:
    """Manager expects (topic, mode) not ContentState"""
    manager = ManagerAgent()
    topic = state.get("topic", "")
    mode = state.get("mode", "standard")
    return manager.process(topic, mode)
```

#### 2. StateManager Initialization
```python
# MUST initialize with Supabase client
state_manager = StateManager(config.get_supabase_client())
# NOT just StateManager() - will fail!
```

#### 3. API Startup Database Handling
```python
@app.on_event("startup")
async def startup_event():
    global state_manager
    try:
        state_manager = StateManager(config.get_supabase_client())
        print("✅ Database connection established")
    except Exception as db_error:
        # Fallback to mock for demo if DB fails
        state_manager = MockStateManager()
```

#### 4. Working Package Versions (CRITICAL)
```
supabase==2.18.1
supabase_auth==2.12.3
httpx==0.28.1
postgrest==1.1.1
storage3==0.12.1
```

#### 5. Test Commands
```bash
# Test workflow directly
python workflows/basic.py

# Start API server
uvicorn api.main:app --reload --port 8001

# Test API endpoints
curl -X POST http://localhost:8001/create \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your Topic Here", "mode": "quick"}'
```

## 🎯 Next Steps for Phase 5 - Research Subgraph Implementation

1. **Create Research Subgraph** (`workflows/subgraphs/research.py`)
   - Move research logic to modular component
   - Create three-node subgraph:
     - Search node - performs searches
     - Extract node - extracts facts
     - Summarize node - creates summary
   - Make it reusable across workflows

2. **Integrate Subgraph into Main Workflow**
   - Replace single research agent with subgraph
   - Test subgraph isolation
   - Verify data flow through subgraph
   - Ensure state updates properly

3. **Test Modular Architecture**
   - Verify subgraph can run independently
   - Test integration with main workflow
   - Ensure no state leakage between components

---

## 📚 Additional Resources

### Dependencies (requirements.txt)
- **Core**: langgraph>=0.2.0, langchain>=0.3.0, langchain-google-genai>=2.0.0
- **API**: fastapi>=0.115.0, uvicorn>=0.32.0
- **Database**: supabase>=2.9.0
- **Search**: duckduckgo-search>=6.3.0 (backup option)
- **Development**: pytest>=8.3.0, black>=24.10.0

### Database Schema
- Located in `database/schema.sql`
- Tables: project_states, state_history, human_feedback
- Views: active_projects, project_stats

---

**Last Updated**: Phase 4 Complete - Linear workflow and API fully functional with database
**GitHub**: https://github.com/Rana-X/ai-content-agency
**Next Session**: Start with Phase 5 - Research Subgraph Implementation