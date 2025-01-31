import streamlit as st

class DisplayModel:
    def __init__(self):
        pass

    def setup_sidebar(self):
        """Set up the sidebar with headers and status information."""
        with st.sidebar:
            # Status section
            st.header("Status")
            status_container = st.container()
            
            # Model selection section
            st.header("Model Selection")
            
            # RAG controls section
            st.header("RAG Settings")
            rag_container = st.container()
            
            return st.sidebar, status_container, rag_container
            
    def setup_rag_controls(self, rag_container, rag_model):
        """Set up RAG controls in the sidebar."""
        with rag_container:
            # RAG Status and Info
            st.markdown("""
            RAG (Retrieval-Augmented Generation)
                       """)
            
            # Enable/disable toggle with clear status
            enabled = st.toggle("🔄 Enable RAG", value=rag_model.is_enabled())
            if enabled != rag_model.is_enabled():
                rag_model.set_enabled(enabled)
            
            # Show current status
            if enabled:
                st.success("RAG is currently ENABLED")
            else:
                st.warning("RAG is currently DISABLED")
            
            # Display collection stats
            stats = rag_model.get_collection_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📚 Documents", stats["total_documents"])
            
            # Controls when enabled
            if enabled:
                st.markdown("---")
                st.markdown("**RAG Settings**")
                
                # Number of results slider with explanation
                st.markdown("""
                Select how many relevant documents to include in the context.
                More documents provide broader context but may increase noise.
                """)
                n_results = st.slider(
                    "Number of RAG results",
                    min_value=1,
                    max_value=5,
                    value=rag_model.get_n_results(),
                    help="Adjust how many relevant documents to include in the context"
                )
                if n_results != rag_model.get_n_results():
                    rag_model.set_n_results(n_results)

    def update_status(self, status_container, model_name: str = None, url: str = None, rag_enabled: bool = False):
        """Update status information in the sidebar."""
        with status_container:
            status_html = """
            <div style='
                padding: 1em;
                background-color: #f0f2f6;
                border-radius: 10px;
                margin-bottom: 1em;
                border-left: 4px solid #4CAF50;
            '>
            """
            
            if model_name:
                status_html += f"🤖 <b>Model:</b> <code>{model_name}</code>"
            
            if url:
                status_html += f"<br>📄 <b>Webpage:</b> <code>{url}</code>"
            
            if rag_enabled:
                status_html += "<br>📚 <b>RAG Status:</b> <code style='color: #4CAF50;'>ENABLED</code>"
            else:
                status_html += "<br>📚 <b>RAG Status:</b> <code style='color: #FFA500;'>DISABLED</code>"
                
            status_html += "</div>"
            
            # Add explanation of current mode
            if rag_enabled:
                status_html += """
                <div style='font-size: 0.9em; color: #666; margin-top: 0.5em;'>
                ℹ️ The LLM will use both RAG context and its general knowledge to provide comprehensive answers.
                </div>
                """
            else:
                status_html += """
                <div style='font-size: 0.9em; color: #666; margin-top: 0.5em;'>
                ℹ️ The LLM will use only its general knowledge to answer questions.
                </div>
                """
            
            st.markdown(status_html, unsafe_allow_html=True)

    def display_model_selection(self, available_models: list, current_model: str = None):
        """Display model selection dropdown in sidebar."""
        if available_models:
            selected_model = st.selectbox(
                "Select Model:",
                available_models,
                index=available_models.index(current_model) if current_model in available_models else 0
            )
            switch_button = st.button("Switch Model")
            return selected_model, switch_button
        else:
            st.warning("No models available. Pull models using 'ollama pull <model_name>'")
            return None, False

    def setup_webpage_section(self):
        """Set up the webpage input section in sidebar."""
        with st.sidebar:
            st.header("Webpage Context")
            url = st.text_input("Enter URL to analyze:", key="url_input")
            load_button = st.button("Load Webpage")
            return url, load_button

    def display_chat_input(self):
        """Display chat input field."""
        return st.chat_input("Type your message here...")

    def display_loading_spinner(self, text: str):
        """Display a loading spinner with custom text."""
        return st.spinner(text)

    def display_success(self, message: str):
        """Display a success message."""
        st.success(message)

    def display_error(self, message: str):
        """Display an error message."""
        st.error(message)

    def display_info(self, message: str):
        """Display an info message."""
        st.info(message)
