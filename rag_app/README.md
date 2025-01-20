# RAG Document Loader

A Python-based document loader implementation for RAG (Retrieval-Augmented Generation) systems. This application serves as the first component of a two-part RAG implementation, focusing on document loading and processing.

## Features

### Multi-Format Support
- Text files (.txt)
- Microsoft Word documents (.doc, .docx)
- PDF documents (.pdf)
- Extensible architecture for adding more formats

### Document Processing
- Automatic format detection
- Content extraction with formatting preservation
- Character count calculation
- Multi-page PDF handling
- Automatic file organization (moves processed files to completed folder)

### Logging and Monitoring
- Integration with LangSmith for activity tracking
- Detailed console logging
- Processing statistics
- Error handling and reporting

## Project Structure

```
rag_app/
├── data/               # Document storage directory
│   └── completed/     # Processed files directory
├── document_loader.py  # Main loader implementation
├── create_test_files.py# Test file creation utility
├── requirements.txt    # Project dependencies
├── .env               # Environment configuration
└── .gitignore         # Version control exclusions
```

## Prerequisites

- Python 3.8 or higher
- pip package manager
- LangSmith API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rag_app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   # Create .env file and add your LangSmith API key
   echo "LANGSMITH_API_KEY=your_api_key_here" > .env
   ```

5. Create required directories:
   ```bash
   mkdir -p data/completed
   ```

## Usage

1. Place documents in the `data` directory:
   - Supported formats: .txt, .doc, .docx, .pdf
   - Files will be automatically processed when the loader runs

2. Run the document loader:
   ```bash
   python document_loader.py
   ```

3. Monitor the output:
   - Console will display processing status
   - Check LangSmith dashboard for detailed logs
   - Processed files move to data/completed directory

## Testing

The project includes a utility script to create test documents:

```bash
python create_test_files.py
```

This will generate sample files in different formats to test the loader's functionality.

## Configuration

The application uses environment variables for configuration:
- `LANGSMITH_API_KEY`: Your LangSmith API key for logging and monitoring

## Future Enhancements

This is part one of a two-part RAG implementation. Future components will include:
1. Text splitting functionality
2. Vector storage integration
3. Additional document format support
4. Enhanced metadata extraction
5. Customizable processing pipelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
