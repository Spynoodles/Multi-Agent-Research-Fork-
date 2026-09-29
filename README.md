#  Multi-Agent Research Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://www.langchain.com/)
[![GitHub stars](https://img.shields.io/github/stars/josephsenior/Multi-Agent-Research-Platform.svg?style=social)](https://github.com/josephsenior/Multi-Agent-Research-Platform)
[![GitHub forks](https://img.shields.io/github/forks/josephsenior/Multi-Agent-Research-Platform.svg?style=social)](https://github.com/josephsenior/Multi-Agent-Research-Platform)
[![GitHub issues](https://img.shields.io/github/issues/josephsenior/Multi-Agent-Research-Platform.svg)](https://github.com/josephsenior/Multi-Agent-Research-Platform)

A research platform where multiple specialized AI agents work together to conduct thorough research, verify facts, synthesize information, and generate well-structured reports with proper citations. Think of it as having a team of research assistants, each with their own expertise, collaborating on your research questions.

## What This Platform Does

I built this platform to demonstrate how different agentic design patterns can work together. Here's what makes it tick:

- **Multi-Agent Architecture**: Specialized agents (Researcher, Fact-Checker, Synthesizer, Evaluator) work together
- **RAG System**: Document retrieval and knowledge base integration
- **Tool Use**: Web search, PDF parsing, citation extraction
- **Guardrails**: Fact-checking and verification
- **Evaluation**: Quality scoring and assessment
- **Routing**: Intelligent research strategy determination
- **Memory**: Session management and context retention

## Features

### Core Capabilities

- **Multi-Source Research**: Combines web search and document retrieval
- **Fact-Checking**: Automatic verification and cross-referencing
- **Report Generation**: Structured, well-formatted research reports
- **Quality Evaluation**: Multi-dimensional quality scoring
- **Citation Management**: Automatic citation tracking and formatting
- **Session Management**: Save and continue research sessions
- **Document Management**: Upload and manage PDF documents

### User Interface

- **Streamlit Web UI**: Easy-to-use interface
- **Document Upload**: Drag-and-drop PDF uploads
- **Research History**: View and manage past research sessions
- **Export Options**: Export reports and citations

## Installation

### Prerequisites

- Python 3.8 or higher
- Gemini API key
- (Optional) Tavily API key or Serper API key for web search

### Setup

Getting started is pretty straightforward:

1. **Navigate to the project directory:**
```bash
cd research_platform
```

2. **Install the dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your environment variables:**
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys. You'll need at least the Gemini key:
```
GEMINI_API_KEY=your_GEMINI_API_KEY_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional - for web search
SERPER_API_KEY=your_serper_api_key_here   # Optional - alternative to Tavily
```

4. **Start the application:**
```bash
streamlit run frontend/streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`. If it doesn't, just navigate there manually.

## Usage

### Basic Research

1. **Enter a research query** in the Research page
2. **Choose options**: Enable/disable web search and document search
3. **Click "Start Research"** and wait for the agents to complete their work
4. **Review the report** with quality scores and citations
5. **Export** the report or citations as needed

### Document Management

1. **Go to Documents page**
2. **Upload PDF files** using the file uploader
3. **Click "Load Documents into RAG System"**
4. Documents are now available for research queries

### Session History

1. **Go to History page** to view past research sessions
2. **Load a previous session** to review or continue research
3. **Delete sessions** you no longer need

## Architecture

### Agent Workflow

```
User Query
    ↓
Router → Determines research strategy
    ↓
Researcher Agent → Gathers information (Web + RAG)
    ↓
Fact-Checker Agent → Verifies facts and cross-references
    ↓
Synthesizer Agent → Creates structured report
    ↓
Evaluator Agent → Assesses quality
    ↓
Final Report + Citations + Quality Scores
```

### Components

- **Backend**: Agent implementations, core systems, tools
- **Frontend**: Streamlit UI and components
- **Data**: Document storage, sessions, vector store

## Project Structure

```
research_platform/
├── backend/
│   ├── agents/          # Agent implementations
│   ├── core/            # Core systems (RAG, Router, Memory, Citations)
│   ├── tools/           # Tools (Web Search, PDF Parser, Citation Extractor)
│   ├── orchestrator.py  # Main orchestration logic
│   └── models.py        # Data models
├── frontend/
│   ├── components/      # UI components
│   ├── streamlit_app.py # Main Streamlit app
│   └── utils.py         # UI utilities
├── data/                # Data storage
│   ├── documents/        # Uploaded documents
│   ├── sessions/        # Research sessions
│   └── vectorstore/    # FAISS vector store
└── requirements.txt     # Python dependencies
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Required. Your Gemini API key for LLM access
- `TAVILY_API_KEY`: Optional. For web search via Tavily API
- `SERPER_API_KEY`: Optional. Alternative to Tavily for web search
- `GEMINI_MODEL`: Optional. Default: "gpt-4"
- `Gemini_TEMPERATURE`: Optional. Default: 0.7

### Model Configuration

You can customize the models used by editing the orchestrator initialization in `streamlit_app.py`:

```python
orchestrator = ResearchOrchestrator(
    model_name="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.7
)
```

## API Usage

You can also use the orchestrator programmatically:

```python
from backend.orchestrator import ResearchOrchestrator

# Initialize
orchestrator = ResearchOrchestrator()

# Load documents (optional)
orchestrator.load_documents(["Document text 1", "Document text 2"])

# Conduct research
result = orchestrator.research(
    query="Your research question",
    use_web_search=True,
    use_rag=True
)

# Access results
print(result["report"])
print(result["quality_scores"])
print(result["citations"])
```

## Troubleshooting

If you run into issues, here are some common problems and how to fix them:

**"Gemini API key is required"**
- Make sure your `.env` file exists in the project root
- Double-check that `GEMINI_API_KEY` is set correctly (no extra spaces or quotes)
- Restart the Streamlit app after changing the `.env` file

**"Web search not working"**
- Web search is completely optional - the platform works fine with just documents
- If you want web search, you'll need either a Tavily or Serper API key
- You can get a Tavily key from https://tavily.com or Serper from https://serper.dev

**"PDF parsing failed"**
- Make sure the PDF isn't password-protected
- Try a different PDF file to see if it's file-specific
- Very large PDFs might take longer or timeout

**"Research takes too long"**
- This is normal - the platform uses multiple agents that need to process sequentially
- Complex queries naturally take longer than simple ones
- Check your Gemini API rate limits if it's consistently slow

## Contributing

This is a portfolio project I built to showcase agentic AI patterns in action. If you find it useful or want to improve it, feel free to:
- Report any issues you encounter
- Suggest improvements or new features
- Fork it and make it your own

##  Tech Stack

- **LangChain**: Agent framework and orchestration
- **Gemini API**: LLM access
- **Streamlit**: Web UI
- **FAISS**: Vector storage for RAG
- **Tavily/Serper**: Web search APIs
- **Python 3.8+**: Core language

##  Use Cases

- **Academic Research**: Conduct thorough research with fact-checking
- **Business Intelligence**: Research market trends and competitors
- **Content Creation**: Research-backed content generation
- **Fact-Checking**: Verify information with multiple sources
- **Report Generation**: Create well-structured research reports

##  Contributing

This is a portfolio project built to showcase agentic AI patterns in action. If you find it useful or want to improve it, feel free to:
- Report any issues you encounter
- Suggest improvements or new features
- Fork it and make it your own

##  License

This project is built for educational and portfolio purposes. Use it as a learning resource or starting point for your own projects.

##  Acknowledgments

Built using:
- LangChain for agent framework
- Gemini for LLM access
- Streamlit for UI
- FAISS for vector storage
- Tavily/Serper for web search


