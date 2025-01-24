import streamlit as st
import os
from document_loader import DocumentLoader
import chromadb

def initialize_document_loader():
    """Initialize the DocumentLoader with the data directory."""
    # Get the absolute path to the rag_app directory
    rag_app_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(rag_app_dir, "data")
    return DocumentLoader(data_dir=data_dir)

def document_management(doc_loader):
    st.header("Document Loading")
    if st.button("Load Documents", key="load_documents_button"):
        with st.spinner("Loading documents..."):
            try:
                # Load documents and get chunks
                documents, chunks = doc_loader.load_documents()
                
                if documents:
                    # Clear existing collection
                    collection_name = "documents"
                    try:
                        doc_loader.chroma_store.client.delete_collection(name=collection_name)
                    except Exception:
                        pass  # Collection might not exist yet
                        
                    # Create fresh collection
                    doc_loader.chroma_store.collection = doc_loader.chroma_store.client.create_collection(
                        name=collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                    
                    # Add chunks to collection
                    doc_loader.chroma_store.add_documents(chunks)
                    
                    st.success(f"Successfully loaded {len(documents)} documents and created {len(chunks)} chunks")
                else:
                    st.info("No new documents found to process")
            except Exception as e:
                st.error(f"Error loading documents: {str(e)}")

def collection_management(doc_loader):
    st.header("Collection Management")
    
    # Display collection statistics
    try:
        stats = doc_loader.chroma_store.get_collection_stats()
        st.metric("Total Documents in Collection", stats["total_documents"])
    except Exception as e:
        st.error(f"Error getting collection stats: {str(e)}")
    
    # View Collections Dictionary Button
    if st.button("View Collections Details", key="view_collections_button"):
        try:
            collections_dict = doc_loader.chroma_store.get_collections()
            if collections_dict:
                st.subheader("Collections Details")
                st.json(collections_dict)
            else:
                st.info("No collections found")
        except Exception as e:
            st.error(f"Error getting collections details: {str(e)}")
    
    # List and Delete Collections
    try:
        collections_dict = doc_loader.chroma_store.get_collections()
        if collections_dict:
            st.subheader("Available Collections")
            for name, details in collections_dict.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Collection: {name} ({details['count']} documents)")
                with col2:
                    if st.button("Delete", key=f"delete_{name}"):
                        try:
                            doc_loader.chroma_store.client.delete_collection(name=name)
                            st.success(f"Deleted collection: {name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting collection: {str(e)}")
        else:
            st.info("No collections found")
    except Exception as e:
        st.error(f"Error listing collections: {str(e)}")

def main():
    st.title("RAG Document Management")
    
    # Initialize DocumentLoader
    doc_loader = initialize_document_loader()
    
    # Add sidebar navigation
    st.sidebar.title("Navigation")
    menu_selection = st.sidebar.radio(
        "Select a page",
        ["Collection Management", "Document Management", "Query RAG"],
        index=0  # Default to Collection Management
    )
    
    # Display the selected page
    if menu_selection == "Document Management":
        document_management(doc_loader)
    elif menu_selection == "Query RAG":
        query_rag(doc_loader)
    else:  # Collection Management
        collection_management(doc_loader)

def query_rag(doc_loader):
    st.header("Query RAG Database")
    
    # Check if there are documents in the collection
    try:
        stats = doc_loader.chroma_store.get_collection_stats()
        if stats["total_documents"] == 0:
            st.warning("No documents found in the collection. Please load some documents first.")
            return
    except Exception as e:
        st.error(f"Error accessing collection: {str(e)}")
        return

    # Query input
    query_text = st.text_input("Enter your query:")
    
    # Return fields selection
    include_fields = st.multiselect(
        "Select fields to include in results",
        ["documents", "metadatas", "embeddings"],
        default=["documents", "metadatas"]
    )
    
    # Number of results
    n_results = st.slider("Number of results", min_value=1, max_value=10, value=3)
    
    # Query button
    search_button = st.button("Search", key="rag_search_button")
    if search_button:
        if query_text:
            try:
                results = doc_loader.chroma_store.query_documents(
                    query_text=query_text,
                    n_results=n_results,
                    include_fields=include_fields
                )
                
                if results:
                    st.subheader("Search Results")
                    for i, result in enumerate(results, 1):
                        similarity_score = f" (Similarity: {result['similarity']:.2f})" if 'similarity' in result else ""
                        with st.expander(f"Result {i}{similarity_score}"):
                            if "content" in result:
                                st.markdown("**Content:**")
                                st.text(result["content"])
                            if "metadata" in result:
                                st.markdown("**Metadata:**")
                                st.json(result["metadata"])
                            if "embedding" in result:
                                st.markdown("**Embedding:**")
                                st.write(f"Vector dimension: {len(result['embedding'])}")
                                if st.checkbox(f"Show full embedding vector for result {i}", key=f"show_embedding_{i}"):
                                    st.json(result["embedding"])
                else:
                    st.info("No matching documents found")
                    
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")
        else:
            st.warning("Please enter a query")

if __name__ == "__main__":
    main()
