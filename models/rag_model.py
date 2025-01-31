import os
from typing import Optional, List, Dict, Any
from rag_app.chroma_store import ChromaStore
import streamlit as st

class RagModel:
    def __init__(self):
        """Initialize RAG model with disabled state."""
        if 'rag_enabled' not in st.session_state:
            st.session_state.rag_enabled = False
        if 'rag_n_results' not in st.session_state:
            st.session_state.rag_n_results = 3
        self.chroma_store: Optional[ChromaStore] = None

    def initialize_rag(self) -> None:
        """Initialize ChromaDB connection."""
        try:
            # Get the absolute path to the rag_app directory
            rag_app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rag_app'))
            data_dir = os.path.join(rag_app_dir, "data")
            persist_directory = os.path.join(data_dir, "chroma_db")
            
            self.chroma_store = ChromaStore(persist_directory=persist_directory)
            return True
        except Exception as e:
            st.error(f"Failed to initialize RAG database: {str(e)}")
            return False

    def is_enabled(self) -> bool:
        """Check if RAG functionality is enabled."""
        return st.session_state.rag_enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable RAG functionality."""
        st.session_state.rag_enabled = enabled

    def set_n_results(self, n: int) -> None:
        """Set number of RAG results to return."""
        st.session_state.rag_n_results = n

    def get_n_results(self) -> int:
        """Get current number of RAG results setting."""
        return st.session_state.rag_n_results

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the document collection."""
        if not self.chroma_store:
            return {"total_documents": 0}
        try:
            return self.chroma_store.get_collection_stats()
        except Exception:
            return {"total_documents": 0}

    def get_rag_context(self, query: str) -> Optional[str]:
        """
        Retrieve relevant documents for a query and format them as context.
        
        Args:
            query: The user's query text
            
        Returns:
            Formatted context string or None if RAG is disabled or no results found
        """
        if not self.is_enabled():
            return None
            
        if not self.chroma_store:
            st.warning("RAG is enabled but the database connection is not initialized.")
            return None

        try:
            results = self.chroma_store.query_documents(
                query_text=query,
                n_results=self.get_n_results(),
                include_fields=["documents", "metadatas"]
            )

            if not results:
                st.info("No relevant documents found in the RAG database for this query.")
                return None

            # Format results into context string with relevance information
            context_parts = []
            for i, result in enumerate(results, 1):
                # Start with document header and metadata
                context_parts_doc = [f"Document {i}:"]
                
                # Add metadata if available
                if "metadata" in result and result["metadata"]:
                    source = result["metadata"].get("source", "Unknown source")
                    page = result["metadata"].get("page", "")
                    metadata_str = f"Source: {source}"
                    if page:
                        metadata_str += f" (Page {page})"
                    context_parts_doc.append(metadata_str)
                
                # Add content if available
                if "content" in result:
                    context_parts_doc.append(result["content"])
                    
                # Add any distance/similarity scores if available
                if "distance" in result:
                    similarity = 1 - result["distance"]  # Convert distance to similarity
                    context_parts_doc.append(f"Relevance Score: {similarity:.2%}")
                
                context_parts.append("\n".join(context_parts_doc))

            if context_parts:
                header = f"RAG Context (showing top {len(results)} relevant documents):"
                return header + "\n\n" + "\n\n".join(context_parts)
            return None

        except Exception as e:
            st.error(f"Error retrieving RAG context: {str(e)}")
            return None
