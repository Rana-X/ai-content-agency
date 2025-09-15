# AI Content Agency - LangGraph Learning Project

A comprehensive multi-agent blog writing system that demonstrates ALL major LangGraph features including parallel execution, human-in-the-loop, subgraphs, streaming, time travel, and more.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- API Keys (free tiers available):
  - Gemini Pro API key
  - Supabase account
  - LangSmith API key (optional)

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd ai-content-agency
```

2. **Run the setup script:**
```bash
python setup.py
```

3. **Configure your API keys:**
Edit the `.env` file with your actual API keys:
```env
GEMINI_API_KEY=your_actual_gemini_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
LANGCHAIN_API_KEY=your_langsmith_key  # Optional
```

4. **Activate the virtual environment:**
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

5. **Validate your setup:**
```bash
python validate_setup.py
```

## 📁 Project Structure

```
ai-content-agency/
├── agents/              # Individual agent implementations
│   ├── manager.py      # Orchestrates workflow
│   ├── research.py     # Performs web research
│   ├── writer.py       # Generates content
│   └── review.py       # Reviews and scores content
├── workflows/          # Workflow definitions
│   ├── subgraphs/     # Reusable workflow components
│   ├── standard.py    # Full-featured workflow
│   ├── quick.py       # Simplified workflow
│   └── factory.py     # Workflow creation factory
├── state/             # State management
│   ├── models.py      # State definitions
│   ├── storage.py     # Database operations
│   └── checkpoints.py # Time travel functionality
├── api/               # FastAPI application
│   ├── main.py        # Main API endpoints
│   ├── streaming.py   # SSE streaming
│   └── human_loop.py  # Human feedback handling
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## 🔑 Getting API Keys

### Gemini Pro (Free - 60 requests/minute)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key
4. Copy and paste into `.env`

### Supabase (Free tier)
1. Sign up at [Supabase](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the Project URL and anon/public key
5. Paste into `.env`

### LangSmith (Optional - 5000 traces/month free)
1. Sign up at [LangSmith](https://smith.langchain.com)
2. Go to Settings → API Keys
3. Create a new API key
4. Paste into `.env`

## 🎯 Features Demonstrated

This project implements all major LangGraph features:

- ✅ **Parallel Execution** - Multiple simultaneous searches
- ✅ **Human-in-the-Loop** - Pause for human review/feedback
- ✅ **Subgraphs** - Modular workflow components
- ✅ **Streaming** - Real-time progress updates
- ✅ **Time Travel** - Checkpoint and restore states
- ✅ **Dynamic Graphs** - Runtime graph construction
- ✅ **Complex Routing** - Conditional paths and retry logic
- ✅ **Multiple Workflows** - Different workflow variants

## 📚 Development Phases

The project is organized into 15 sequential development phases:

1. **Foundation Setup** ✅ (Current)
2. State Management System
3. Basic Agent Implementation
4. Basic Linear Workflow
5. Research Subgraph Implementation
6. Parallel Execution
7. Complex Routing and Conditionals
8. Multiple Workflow Variants
9. Checkpointing and Time Travel
10. Human-in-the-Loop
11. Streaming and Real-time Updates
12. Dynamic Graph Building
13. Production Enhancements
14. Testing and Validation
15. Deployment and Documentation

## 🧪 Testing

Run the validation script to ensure everything is set up correctly:
```bash
python validate_setup.py
```

## 📖 Documentation

Detailed documentation for each phase is available in the main project document:
- [LANGGRAPH_COMPLETE_LEARNING_PROJECT.md](../LANGGRAPH_COMPLETE_LEARNING_PROJECT.md)

## 🤝 Contributing

This is a learning project designed to demonstrate LangGraph features. Feel free to explore, modify, and extend it for your learning purposes.

## 📝 License

This project is for educational purposes.