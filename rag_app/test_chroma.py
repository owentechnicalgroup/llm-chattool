from document_loader import DocumentLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize document loader
    doc_loader = DocumentLoader()
    
    # Load and process documents
    logger.info("Loading and processing documents...")
    documents, chunks = doc_loader.load_documents()
    
    if not chunks:
        logger.info("No documents were processed. Please ensure there are documents in the data directory.")
        return
        
    # Test querying similar chunks
    test_queries = [
        "What is the main topic?",
        "Can you summarize the key points?",
        "What are the important details?"
    ]
    
    logger.info("\nTesting similarity search with example queries:")
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        results = doc_loader.query_similar_chunks(query)
        
        if results:
            logger.info(f"Found {len(results)} relevant chunks:")
            for i, result in enumerate(results, 1):
                logger.info(f"\nResult {i} (Similarity: {result['similarity']:.2f}):")
                logger.info("-" * 40)
                logger.info(result['content'].strip())
                logger.info("-" * 40)
        else:
            logger.info("No relevant chunks found for this query.")
            
    # Get collection statistics
    stats = doc_loader.chroma_store.get_collection_stats()
    logger.info(f"\nChroma collection statistics:")
    logger.info(f"Total documents in collection: {stats['total_documents']}")

if __name__ == "__main__":
    main()
