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
            
            return st.sidebar, status_container
            
    def update_status(self, status_container, model_name: str = None, url: str = None):
        """Update status information in the sidebar."""
        with status_container:
            status_html = """
            <div style='
                padding: 0.5em;
                background-color: #f0f2f6;
                border-radius: 5px;
                margin-bottom: 1em;
            '>
            """
            
            if model_name:
                status_html += f"🤖 Running: <code>{model_name}</code>"
            
            if url:
                status_html += f"<br>📄 Analyzing: <code>{url}</code>"
                
            status_html += "</div>"
            
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
