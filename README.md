# LLM ChatTool

A powerful Python-based desktop application for interacting with Large Language Models (LLMs). This tool provides a streamlined interface for managing conversations with AI models while offering advanced features like RAG (Retrieval-Augmented Generation), webpage context integration, and streaming responses.

## Features

- **Multiple LLM Support**: Compatible with various LLM providers including Ollama (local) and Claude (API)
- **Streaming Responses**: Real-time streaming of AI responses for better interaction
- **RAG Integration**: 
  - ChromaDB-powered document retrieval
  - Configurable number of results
  - Relevance scoring and metadata tracking
  - Enhances responses with context from stored documents
- **Webpage Context**: 
  - Scrapes and incorporates webpage content into conversations
  - Provides webpage content previews
  - Integrates web context with chat responses
- **User-Friendly Interface**: 
  - Built with Streamlit for a clean and intuitive experience
  - Dynamic model switching through sidebar
  - Real-time status updates
  - RAG controls and configuration
- **Session Management**: 
  - Persistent chat history within sessions
  - Automatic chat history clearing when switching models
- **Modular Architecture**: Well-organized codebase with separate models for different functionalities

## Requirements

- Python 3.x
- Dependencies:
  - langchain >= 0.1.0
  - langchain-community >= 0.0.10
  - langchain-ollama >= 0.0.1
  - python-dotenv >= 0.19.0
  - anthropic >= 0.3.0
  - ollama >= 0.1.0
  - streamlit >= 1.32.0
  - beautifulsoup4 >= 4.12.0
  - requests >= 2.31.0
  - chromadb

## Installation

1. Clone the repository:
```bash
git clone https://github.com/owenmarkb/llm-chattool.git
cd llm-chattool
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   2. Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Required for Claude models
   ```

## Usage

1. Start the application:
```bash
streamlit run llmapp.py
```

2. Configure LLM providers:
   - **Ollama**: Local models will be automatically detected
   - **Claude**: Set up your API key in `.env` to use Claude models
3. Select your preferred model from the sidebar (available models depend on your configuration)
4. Configure RAG settings if desired:
   - Enable/disable RAG functionality
   - Set number of results to retrieve
   - View document collection statistics
5. Optionally enter a webpage URL for additional context
6. Start chatting with the AI!

### Available Models

- **Ollama Models**: Any locally installed Ollama models will be automatically detected and available for use
- **Claude Models**: When configured with an API key, the following models are available:
  - claude-3-sonnet-20240229: Latest Claude 3 model with excellent performance

## Project Structure

```
├── llmapp.py              # Main application entry point
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables
├── models/
│   ├── chat_model.py     # Chat interaction handling
│   ├── display_model.py  # UI display management
│   ├── model_settings.py # LLM configuration
│   ├── rag_model.py      # RAG functionality
│   └── screen_model.py   # Webpage scraping and preview
└── rag_app/
    ├── chroma_store.py   # ChromaDB integration
    ├── document_loader.py # Document processing
    └── data/             # Document storage
```

## Components

- **ChatModel**: Handles chat interactions, message history, and LLM responses
- **RagModel**: Manages document retrieval and context integration using ChromaDB
- **ScreenModel**: Handles webpage scraping and content preview
- **ModelSettings**: Controls LLM provider configuration and selection
- **DisplayModel**: Manages the Streamlit interface and UI components

## Features in Detail

### Chat Interface
- Real-time streaming responses
- Persistent chat history within sessions
- Dynamic model switching with automatic chat history clearing
- Error handling and user feedback

### RAG Integration
- ChromaDB-powered document storage and retrieval
- Configurable result count
- Relevance scoring
- Document metadata tracking
- Context-enhanced responses

### Webpage Integration
- URL input and validation
- Content scraping and preview
- Context integration with chat

### Model Management
- Dynamic model switching between local and API models
- Multiple provider support (Ollama and Claude)
- Configuration persistence
- Automatic model detection

## Error Handling

The application includes comprehensive error handling for:
- LLM API failures
- RAG database connection issues
- Webpage scraping problems
- Invalid configurations
- Network errors
- Missing API keys or configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]
