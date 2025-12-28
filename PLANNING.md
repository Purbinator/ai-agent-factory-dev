# AI Agent Factory - Project Planning

## 🏗️ Architecture Overview

This is an AI Agent Factory built on:
- **Pydantic AI**: Core agent framework
- **Python 3.10+**: Language runtime
- **PostgreSQL + PGVector**: Database with vector search
- **Rich**: CLI tooling
- **pytest**: Testing framework

## 📁 Project Structure

```
ai-agent-factory-dev/
├── agent-factory/              # Main agent factory implementation
│   ├── agents/                 # Production agents
│   │   ├── rag_agent/          # Reference RAG agent implementation
│   │   └── video_analysis_agent/  # Video analysis agent (NEW)
│   ├── examples/               # Example implementations
│   ├── CLAUDE.md              # Orchestration rules
│   └── README.md              # Documentation
├── venv_linux/                 # Python virtual environment
├── CLAUDE.md                   # Root orchestration file
├── PLANNING.md                 # This file
└── TASK.md                     # Task tracking
```

## 🎨 Agent Structure Pattern

Every agent follows this canonical structure (see `rag_agent` as reference):

```
agents/[agent_name]/
├── __init__.py                 # Package initialization
├── agent.py                    # Main agent definition (Pydantic AI Agent instance)
├── prompts.py                  # System prompts for agent
├── tools.py                    # Tool functions registered with agent
├── providers.py                # LLM/API provider initialization
├── dependencies.py             # Dependency injection (dataclass with initialization)
├── settings.py                 # Configuration (Pydantic Settings)
├── cli.py                      # CLI entry points (Rich-based)
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and usage documentation
├── planning/                   # Planning documents (INITIAL.md, etc.)
├── ingestion/                  # Processing pipeline modules
│   ├── __init__.py
│   └── [pipeline_modules].py
├── tests/                      # Pytest test suite
│   ├── conftest.py             # Shared test fixtures
│   └── test_*.py               # Test modules
└── utils/                      # Shared utility modules (optional)
```

## 🧩 Standard Agent Components

### 1. `settings.py`
- Uses `pydantic-settings` for configuration
- Loads from `.env` file using `python-dotenv`
- Defines all configurable parameters
- Includes validation and defaults
- Pattern: `class Settings(BaseSettings)` with `model_config`

### 2. `dependencies.py`
- Uses `@dataclass` for dependency injection
- Contains `initialize()` and `cleanup()` methods
- Manages external connections (DB, APIs, etc.)
- Passed to agent via `deps_type` parameter

### 3. `providers.py`
- Initializes LLM providers (OpenAI, Anthropic, Gemini, etc.)
- Returns Pydantic AI model instances
- Supports OpenAI-compatible APIs via base_url
- Pattern: `get_llm_model()` factory function

### 4. `prompts.py`
- Contains system prompts as string constants
- May include dynamic prompt generators
- Documents agent capabilities and behavior
- Pattern: `MAIN_SYSTEM_PROMPT = """..."""`

### 5. `tools.py`
- Defines tool functions for agent
- Each tool receives `RunContext[AgentDependencies]`
- Uses type hints for parameter validation
- Returns structured data (Pydantic models or dicts)
- Pattern: `async def tool_name(ctx: RunContext[AgentDependencies], ...)`

### 6. `agent.py`
- Creates Pydantic AI `Agent` instance
- Registers tools with `agent.tool()`
- Minimal orchestration logic
- Pattern: `agent = Agent(model, deps_type=..., system_prompt=...)`

### 7. `cli.py`
- Rich-based interactive CLI
- Async/await for streaming responses
- Handles initialization and cleanup
- Pattern: Uses `rich.console.Console` for output

### 8. `ingestion/`
- Pipeline modules for data processing
- Each module is self-contained (< 500 lines)
- Uses async/await where appropriate
- Pattern: Classes or functions with clear interfaces

## 🧪 Testing Standards

### Test Structure
- One test file per module: `test_[module_name].py`
- Shared fixtures in `conftest.py`
- Mock external dependencies (APIs, databases)

### Test Coverage Requirements
- At least 3 tests per function:
  1. Expected use case
  2. Edge case
  3. Failure case
- Integration tests for full workflows
- Requirement validation tests

### Test Fixtures
- Use pytest fixtures for dependencies
- Mock Pydantic AI models with `TestModel` or `FunctionModel`
- Mock database connections with `asyncpg.create_pool`
- Mock API clients with appropriate mocking libraries

## 🎯 Code Style & Conventions

### Python Style
- **PEP8 compliant**
- **Type hints on all functions**
- **Google-style docstrings**
- **Black formatting** (88 char line length)
- **Relative imports within packages**

### File Size Limit
- **Maximum 500 lines per file**
- Refactor into modules if approaching limit
- Split by feature or responsibility

### Naming Conventions
- **snake_case** for files, functions, variables
- **PascalCase** for classes
- **UPPER_CASE** for constants
- **agent_name** format: `[purpose]_agent` (e.g., `rag_agent`, `video_analysis_agent`)

### Documentation
- Every function has a docstring
- Non-obvious logic has inline comments
- README.md for setup and usage
- .env.example for configuration

## 🔧 Development Workflow

### Environment
- Use `venv_linux` virtual environment for all Python commands
- Install dependencies: `pip install -r requirements.txt`
- Use `python-dotenv` to load `.env` files

### Testing
- Run tests: `pytest agents/[agent_name]/tests/`
- Run with coverage: `pytest --cov=agents/[agent_name]`
- All tests must pass before committing

### Dependencies
- Add to `requirements.txt` with version pins
- Document API keys needed in `.env.example`
- Use official Python packages only (no hallucinated libraries)

## 🚀 Agent Factory Workflow (from CLAUDE.md)

When building a new agent:
1. **Phase 0**: Clarification (ask user questions)
2. **Phase 1**: Requirements documentation
3. **Phase 2**: Design (prompts, tools, dependencies)
4. **Phase 3**: Implementation
5. **Phase 4**: Validation & testing
6. **Phase 5**: Documentation & delivery

## 📝 Key Principles

1. **Modularity**: Clear separation of concerns
2. **Simplicity**: MVP mindset, avoid over-engineering
3. **Testability**: Mock external dependencies, comprehensive tests
4. **Documentation**: Clear setup instructions, usage examples
5. **Type Safety**: Use Pydantic models and type hints everywhere
6. **Async-First**: Use async/await for I/O operations
7. **Error Handling**: Graceful degradation, informative error messages

## 🔗 Key Dependencies

### Core
- `pydantic-ai`: Agent framework
- `pydantic`: Data validation
- `pydantic-settings`: Configuration management
- `python-dotenv`: Environment variables

### CLI & Output
- `rich`: Terminal formatting and interactive CLI

### Database (if needed)
- `asyncpg`: PostgreSQL async driver
- `pgvector`: Vector similarity extension

### Testing
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting

### LLM Providers
- `openai`: OpenAI API (also used for OpenAI-compatible APIs)
- `google-generativeai`: Gemini API
- Provider-specific SDKs as needed

## 🎓 Learning Resources

- **Reference Implementation**: `agents/rag_agent/` - Study this for patterns
- **Orchestration Rules**: `agent-factory/CLAUDE.md` - Factory workflow
- **Pydantic AI Docs**: Official documentation for agent framework
