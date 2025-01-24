import os
import sys
from document_loader import DocumentLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_load_and_query(query_text: str = "What is this document about?"):
    # Initialize DocumentLoader with the data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    doc_loader = DocumentLoader(data_dir=data_dir)
    
    try:
        # Load documents
        logger.info("Loading documents...")
        documents, chunks = doc_loader.load_documents()
        logger.info(f"Loaded {len(documents)} documents and created {len(chunks)} chunks")
        
        # Delete the collection and create a new one
        doc_loader.chroma_store.client.delete_collection(name="documents")
        doc_loader.chroma_store.collection = doc_loader.chroma_store.client.create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add documents to fresh collection
        doc_loader.chroma_store.add_documents(chunks)
        
        # Get collection stats
        stats = doc_loader.chroma_store.get_collection_stats()
        logger.info(f"Collection stats: {stats}")
        
        # Perform query
        logger.info(f"\nPerforming query: '{query_text}'")
        
        results = doc_loader.chroma_store.query_documents(
            query_text=query_text,
            n_results=3,
            include_fields=["documents", "metadatas"]
        )
        
        # Display results
        if results:
            logger.info(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                logger.info(f"\nResult {i}:")
                if "content" in result:
                    logger.info(f"Content: {result['content'][:200]}...")
                if "metadata" in result:
                    logger.info(f"Metadata: {result['metadata']}")
                if "similarity" in result:
                    logger.info(f"Similarity: {result['similarity']:.2f}")
        else:
            logger.info("No results found")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise

if __name__ == "__main__":
    # Get query from command line argument if provided
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is this document about?"
    test_load_and_query(query)
