# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Project Overview

**AI Content Agency** - A comprehensive LangGraph learning project demonstrating ALL major LangGraph features through a multi-agent blog writing system. Built in 15 phases, currently on Phase 3 (COMPLETE).

### Project Goals
- Learn and implement every LangGraph feature
- Build a functional multi-agent content creation system
- Create reusable patterns for production applications
- Document the learning journey comprehensively

## 📍 Current Status: Phase 3 COMPLETE ✅

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

### 🔄 Next Phase: Phase 4 - Basic Linear Workflow
Create `workflows/basic.py` with:
- Linear flow: Manager → Research → Writer → Review → End
- No conditionals or loops yet
- Basic state passing between agents
- FastAPI endpoints for testing

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
GEMINI_API_KEY=AIzaSyCAuGPeHyGwJdTxgsMP6ynDK1dMzaRMQfs

# Brave Search API (2000 requests/month free)
BRAVE_API_KEY=BSArHGdATae0Nala46gDn4e_ck_5ngk

# Supabase (Database)
SUPABASE_URL=https://hyfsgrqyzxlyypyjwipw.supabase.co
SUPABASE_KEY=eyJhbGci...kErY  # Full key in .env

# LangSmith (Optional - Monitoring)
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=false  # Set true to enable
```

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
# Test individual agents
python agents/test_manager.py
python agents/test_research.py
python agents/test_writer.py
python agents/test_review.py

# Test state management
python -c "from state import create_initial_state; print(create_initial_state('Test Topic', 'standard'))"
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
- **Import Errors**: Ensure venv is activated

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

## 🎯 Next Steps for Phase 4

1. Create `workflows/basic.py` with StateGraph
2. Implement linear flow: Manager → Research → Writer → Review
3. Add `api/main.py` with FastAPI endpoints:
   - POST /create - Start new project
   - GET /status/{project_id} - Check status
   - GET /content/{project_id} - Get final content
4. Test end-to-end workflow
5. Verify state persistence

---

**Last Updated**: Phase 3 Complete - All agents implemented and tested
**GitHub**: https://github.com/Rana-X/ai-content-agency
**Next Session**: Start with Phase 4 - Basic Linear Workflow