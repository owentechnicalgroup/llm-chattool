# RAG Document Loader

A Python-based document loader implementation for RAG (Retrieval-Augmented Generation) systems. This application serves as the first component of a two-part RAG implementation, focusing on document loading, processing, and text splitting.

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

### Text Splitting
- Recursive character text splitting
- Configurable chunk sizes (default: 500 characters)
- Adjustable chunk overlap (default: 50 characters)
- Smart separator handling (\n\n, \n, ., space)
- Chunk statistics and visualization
- Maintains context across chunks

### Logging and Monitoring
- Integration with LangSmith for activity tracking
- Detailed console logging
- Processing statistics
- Error handling and reporting
- Chunk analytics (count, size, distribution)

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
   - Original document content
   - Generated text chunks with character counts
   - Processing statistics
   - LangSmith dashboard logs
   - Processed files in data/completed directory

## Text Splitting Configuration

The text splitter can be configured by modifying the following parameters in `document_loader.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Maximum characters per chunk
    chunk_overlap=50,    # Overlap between chunks
    length_function=len, # Function to measure text length
    separators=[         # Text separation hierarchy
        "\n\n",         # Prefer splitting on double newlines
        "\n",           # Then single newlines
        ".",            # Then periods
        " ",           # Then spaces
        ""             # Finally, character by character
    ]
)
```

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
1. Vector storage integration
2. Additional document format support
3. Enhanced metadata extraction
4. Customizable processing pipelines
5. Advanced chunk optimization strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
