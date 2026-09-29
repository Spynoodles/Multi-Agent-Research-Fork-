# Quick Start Guide

Let's get you up and running with the Multi-Agent Research Platform. This should only take a few minutes.

## Prerequisites

- Python 3.8+
- Gemini API key
- (Optional) Tavily or Serper API key for web search

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # Optional
```

### 3. Run the Application

```bash
streamlit run frontend/streamlit_app.py
```

The app will open at `http://localhost:8501`

## First Research Query

1. **Open the Research page**
2. **Enter a query**: "What are the latest developments in AI agent architectures?"
3. **Enable options**: Check both "Web Search" and "Document Search"
4. **Click "Start Research"**
5. **Wait for results** (usually 1-2 minutes)
6. **Review the report** with quality scores and citations

## Adding Documents

1. **Go to Documents page**
2. **Upload a PDF** using the file uploader
3. **Click "Load Documents into RAG System"**
4. **Return to Research page** and queries will now search your documents too

## Understanding Results

### Quality Scores
- **Completeness**: How well the query was addressed
- **Accuracy**: Factual correctness
- **Relevance**: Information relevance to query
- **Clarity**: Report readability
- **Source Quality**: Reliability of sources
- **Citation Quality**: Proper citation formatting

### Citations
- Automatically tracked from all sources
- Formatted in APA, MLA, or Chicago style
- Can be exported separately

## Tips for Best Results

1. **Be specific**: More specific queries get better results
2. **Use documents**: Upload relevant PDFs for better context
3. **Enable both sources**: Web + documents gives comprehensive results
4. **Review quality scores**: Low scores indicate areas for improvement
5. **Check citations**: Verify sources are reliable

## Troubleshooting

### "Gemini API key is required"
- Check your `.env` file exists
- Verify `GEMINI_API_KEY` is set correctly
- Restart the Streamlit app after changing `.env`

### "Web search not working"
- Web search is optional
- Research works with documents only
- To enable: Get Tavily API key from https://tavily.com

### "Research takes too long"
- This is normal (multiple agents processing)
- Complex queries take longer
- Check your API rate limits

### "PDF upload failed"
- Ensure PDF is not password-protected
- Try a different PDF file
- Check file size (very large files may timeout)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Explore the code to understand agent implementations
- Customize agents and prompts for your use case

## Example Queries

Try these example queries to get started:

- "What are the benefits and drawbacks of multi-agent AI systems?"
- "Compare RAG and fine-tuning approaches for LLM applications"
- "What are the latest trends in agentic AI research?"
- "Explain how chain-of-thought reasoning improves LLM performance"

That's it! You're ready to start researching. The platform will handle the rest - gathering information, verifying facts, and organizing everything into a coherent report for you.


