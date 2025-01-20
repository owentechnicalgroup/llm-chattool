# LLM ChatTool

A powerful Python-based desktop application for interacting with Large Language Models (LLMs). This tool provides a streamlined interface for managing conversations with AI models while offering advanced features like webpage context integration and streaming responses.

## Features

- **Multiple LLM Support**: Compatible with various LLM providers including OpenAI, Anthropic, and Ollama
- **Streaming Responses**: Real-time streaming of AI responses for better interaction
- **Webpage Context**: Ability to scrape and incorporate webpage content into conversations
- **User-Friendly Interface**: Built with Streamlit for a clean and intuitive user experience
- **Model Switching**: Seamlessly switch between different LLM providers
- **Session Management**: Persistent chat history within sessions
- **Modular Architecture**: Well-organized codebase with separate models for different functionalities

## Requirements

- Python 3.x
- Dependencies:
  - langchain >= 0.1.0
  - langchain-community >= 0.0.10
  - langchain-ollama >= 0.0.1
  - python-dotenv >= 0.19.0
  - anthropic >= 0.3.0
  - openai >= 0.27.0
  - ollama >= 0.1.0
  - streamlit >= 1.32.0
  - beautifulsoup4 >= 4.12.0
  - requests >= 2.31.0

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

3. Set up environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Usage

1. Start the application:
```bash
streamlit run llmapp.py
```

2. Select your preferred LLM provider from the sidebar
3. Optionally enter a webpage URL for context
4. Start chatting with the AI!

## Project Structure

```
├── llmapp.py              # Main application entry point
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables
└── models/
    ├── chat_model.py     # Chat interaction handling
    ├── display_model.py  # UI display management
    ├── model_settings.py # LLM configuration
    └── screen_model.py   # Webpage scraping and preview
```

## Components

- **ChatModel**: Handles chat interactions, message history, and LLM responses
- **ScreenModel**: Manages webpage scraping and content preview
- **ModelSettings**: Controls LLM provider configuration and selection
- **DisplayModel**: Manages the Streamlit interface and UI components

## Features in Detail

### Chat Interface
- Real-time streaming responses
- Persistent chat history within sessions
- Error handling and user feedback

### Webpage Integration
- URL input and validation
- Content scraping and preview
- Context integration with chat

### Model Management
- Dynamic model switching
- Multiple provider support
- Configuration persistence

## Error Handling

The application includes comprehensive error handling for:
- LLM API failures
- Webpage scraping issues
- Invalid configurations
- Network problems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]
