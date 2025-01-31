from document_loader import DocumentLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_document_loading():
    """Test the document loading and Chroma integration."""
    print("\nTesting Document Loader and Chroma Integration...")
    print("-" * 80)
    
    # Initialize loader
    loader = DocumentLoader()
    
    # Print paths for debugging
    print(f"Data Directory: {loader.data_dir}")
    print(f"Completed Directory: {loader.completed_dir}")
    print(f"Chroma DB Path: {loader.chroma_store.persist_directory}")
    print("-" * 80)
    
    # Load documents
    documents, chunks = loader.load_documents()
    
    print(f"\nProcessed Documents: {len(documents)}")
    print(f"Total Chunks: {len(chunks)}")
    
    if documents:
        print("\nDocument Sources:")
        for doc in documents:
            print(f"- {doc.metadata.get('source', 'Unknown source')}")
            
    if chunks:
        print("\nSample Chunks:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\nChunk {i}:")
            print("-" * 40)
            print(f"Size: {chunk.metadata.get('chunk_size')} characters")
            print(f"Source: {chunk.metadata.get('source_document')}")
            print(f"Section: {chunk.metadata.get('section')}")
            print("-" * 40)
            print(chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content)
            print("-" * 40)
        
        # Add chunks to Chroma
        print("\nAdding chunks to Chroma...")
        loader.chroma_store.add_documents(chunks)
        
        # Test querying
        print("\nTesting Chroma queries...")
        test_queries = [
            "What is Tippecanoe Lake?",
            "Tell me about the marina",
            "What activities are available?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 40)
            results = loader.chroma_store.query_documents(query)
            for i, result in enumerate(results, 1):
                print(f"\nMatch {i} (Similarity: {result.get('similarity', 0):.2f}):")
                print(result.get('content', '')[:200] + "...")

if __name__ == "__main__":
    test_document_loading()
