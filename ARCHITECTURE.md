# Multi-Agent Research Platform - Architecture Documentation

## System Architecture

### High-Level Overview

I designed this platform with a modular architecture where specialized agents work together to handle research tasks. Think of it like a research team where each member has a specific role - one gathers information, another verifies facts, someone else organizes everything, and finally someone evaluates the quality of the work.

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│  (Document Upload, Query Input, Results Display)       │
└──────────────────────┬──────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Research Orchestrator                      │
│         (Coordinates all agents and workflow)           │
└──────────────────────┬──────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Router     │  │   RAG        │  │   Memory     │
│              │  │   System     │  │   Manager    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Researcher   │  │ Fact-Checker │  │ Synthesizer  │
│   Agent      │  │    Agent     │  │    Agent     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ↓
                 ┌──────────────┐
                 │  Evaluator   │
                 │    Agent     │
                 └──────────────┘
```

## Agent Roles and Responsibilities

### Router
- **Purpose**: Determines research strategy
- **Input**: User query
- **Output**: Research strategy (complexity, sources to use, fact-check level)
- **Pattern**: Routing Pattern

### Researcher Agent
- **Purpose**: Gather information from multiple sources
- **Input**: Query, strategy
- **Output**: Raw findings with sources
- **Tools**: Web Search Tool, RAG System
- **Pattern**: Tool Use Pattern, RAG Pattern

### Fact-Checker Agent
- **Purpose**: Verify information accuracy
- **Input**: Research findings, sources
- **Output**: Verified facts with confidence scores
- **Pattern**: Guardrails Pattern

### Synthesizer Agent
- **Purpose**: Organize and structure information
- **Input**: Verified findings
- **Output**: Structured research report
- **Pattern**: Reflection Pattern (organizes and improves)

### Evaluator Agent
- **Purpose**: Assess research quality
- **Input**: Research report, query
- **Output**: Quality scores and feedback
- **Pattern**: Evaluation Pattern (LLM-as-a-Judge)

## Data Flow

### Research Pipeline

1. **User Input**: Query entered via Streamlit UI
2. **Routing**: Router analyzes query and determines strategy
3. **Research**: Researcher Agent gathers information
   - Web search (if enabled)
   - RAG document retrieval (if enabled)
   - Citation tracking
4. **Verification**: Fact-Checker Agent verifies findings
   - Cross-references sources
   - Identifies contradictions
   - Provides confidence scores
5. **Synthesis**: Synthesizer Agent creates structured report
   - Organizes by topic
   - Creates coherent narrative
   - Includes citations
6. **Evaluation**: Evaluator Agent assesses quality
   - Scores multiple dimensions
   - Provides feedback
7. **Storage**: Memory Manager saves session
8. **Display**: Results shown in UI

## Core Systems

### RAG System
- **Technology**: FAISS vector store
- **Embeddings**: Gemini embeddings
- **Chunking**: RecursiveCharacterTextSplitter
- **Features**: Metadata tracking, persistent storage

### Citation Manager
- **Purpose**: Track and format citations
- **Formats**: APA, MLA, Chicago
- **Sources**: Web URLs, document references

### Memory Manager
- **Purpose**: Session management
- **Storage**: JSON files (upgradeable to database)
- **Features**: Session history, user preferences

### Web Search Tool
- **APIs**: Tavily (primary), Serper (alternative)
- **Features**: Result formatting, error handling

### PDF Parser
- **Libraries**: pdfplumber (primary), PyPDF2 (fallback)
- **Features**: Text extraction, metadata extraction

## Error Handling Strategy

### Fallback Mechanisms

1. **Agent Failure**: Fallback to simpler workflow
2. **Web Search Failure**: Continue with RAG only
3. **RAG Failure**: Continue with web search only
4. **PDF Parser Failure**: Try alternative parser
5. **API Timeout**: Retry with exponential backoff

### Error Recovery

- Graceful degradation at each step
- User-friendly error messages
- Detailed logging for debugging

## Performance Considerations

### Optimization Strategies

- **Caching**: Vector store persistence
- **Batch Processing**: Document loading
- **Async Potential**: Can be upgraded for parallel agent execution
- **Rate Limiting**: Respects API rate limits

### Scalability

- **Current**: Single-user, local deployment
- **Future**: Can be upgraded to:
  - Database for sessions
  - Multi-user support
  - API endpoints
  - Cloud deployment

## Security Considerations

- API keys stored in `.env` file (not committed)
- Input validation on all user inputs
- Safe PDF parsing (no code execution)
- Error messages don't expose sensitive information

## Extension Points

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement `process()` method
3. Add to orchestrator workflow
4. Update UI if needed

### Adding New Tools

1. Create tool class in `backend/tools/`
2. Integrate with relevant agent
3. Update requirements if needed

### Adding New Features

- Database integration: Replace JSON storage
- Authentication: Add user management
- API endpoints: Create REST API
- Advanced analytics: Add metrics dashboard

## Testing Strategy

### Unit Tests
- Test each agent independently
- Test core systems (RAG, Memory, Citations)
- Test tools (PDF parser, web search)

### Integration Tests
- Test orchestrator workflow
- Test agent collaboration
- Test error handling

### End-to-End Tests
- Test complete research pipeline
- Test UI interactions
- Test session management

## Deployment Considerations

### Local Deployment
- Streamlit runs locally
- Data stored in `data/` directory
- Suitable for development and personal use

### Production Deployment
- Use Streamlit Cloud, Railway, or Render
- Set environment variables in deployment platform
- Consider database for sessions
- Add authentication if multi-user

## Future Enhancements

1. **Advanced Features**
   - Multi-language support
   - Research templates
   - Collaborative features
   - Advanced analytics

2. **Technical Improvements**
   - Database migration
   - API endpoints
   - Async processing
   - Caching improvements

3. **User Experience**
   - Better UI/UX
   - Mobile support
   - Export to more formats
   - Real-time progress updates


