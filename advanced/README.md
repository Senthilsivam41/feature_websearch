# Ollama-Powered Web Crawler and Search Service

## Project Overview

This project is an advanced web crawling and search service that leverages local Large Language Models (LLMs) through Ollama for intelligent content analysis, semantic search, and natural language interaction.

## Key Features

- 🌐 Web Crawling
  - Crawl websites with configurable depth
  - Concurrent URL processing
  - Robust URL validation

- 🤖 Local LLM Integration
  - Multiple Ollama model support
  - Semantic query understanding
  - Natural language search and interaction

- 💾 Persistent Storage
  - SQLite database for storing crawled content
  - Thread-safe data management

- 🔍 Advanced Search Capabilities
  - Semantic search beyond keyword matching
  - Contextual result ranking
  - Relevance-based result presentation

## Supported Ollama Models

- Llama3.1
- Mistral
- Neural Chat
- OpenHermes
- Zephyr

## Prerequisites

### System Requirements
- Python 3.8+
- 16GB RAM
- Modern CPU
- 10GB+ disk space for models

### Installation

1. Install Ollama
```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

2. Pull Ollama Models
```bash
ollama pull llama3.1
ollama pull mistral
ollama pull neural-chat
ollama pull openhermes
ollama pull zephyr
```

3. Install Python Dependencies
```bash
pip install requests beautifulsoup4
```

## Usage

1. Start Ollama server
2. Run the Python script
3. Select:
   - Ollama model
   - Website to crawl
4. Interact through menu-driven interface

### Interaction Modes

1. **Ask a Question**
   - Natural language query
   - LLM generates comprehensive response
   - Contextual insights from crawled data

2. **Semantic Search**
   - Retrieve and rank relevant web content
   - View URL, title, and content snippets

## Technical Architecture

```
Web URL → Crawler → BeautifulSoup 
           ↓          Parsing
    SQLite Database ← Content Storage
           ↓
    Ollama LLM ← Semantic Analysis
           ↓
    Natural Language Interface
```

## Workflow

1. Website Crawling
   - Validate and sanitize URLs
   - Extract text, titles, images
   - Store in SQLite database
   - Concurrent processing

2. Semantic Search
   - Query intent extraction
   - Database search
   - LLM-powered relevance ranking

3. Interactive Chat
   - Contextual search results
   - LLM generates human-like responses

## Potential Improvements

- Enhanced error handling
- Advanced caching mechanisms
- More configurable model parameters
- Support for additional Ollama models

## Limitations

- Requires local Ollama setup
- Performance depends on model and system resources
- Crawling limited by website policies

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

[Specify your license, e.g., MIT]

## Disclaimer

Respect website terms of service and robots.txt when crawling.

## Contact

[Your Contact Information]
