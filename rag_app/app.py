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
    if st.button("Load Documents"):
        with st.spinner("Loading documents..."):
            try:
                documents, chunks = doc_loader.load_documents()
                if documents:
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
    if st.button("View Collections Details"):
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
        ["Collection Management", "Document Management"],
        index=0  # Default to Collection Management
    )
    
    # Display the selected page
    if menu_selection == "Document Management":
        document_management(doc_loader)
    else:  # Collection Management
        collection_management(doc_loader)

if __name__ == "__main__":
    main()
