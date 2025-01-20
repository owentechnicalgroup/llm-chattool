import requests
import streamlit as st
from langchain_ollama import OllamaLLM

class ModelSettings:
    def __init__(self):
        if 'current_llm' not in st.session_state:
            st.session_state.current_llm = None
        if 'last_model' not in st.session_state:
            st.session_state.last_model = None

    def get_running_models(self) -> list:
        """Get list of currently running Ollama models."""
        try:
            response = requests.get('http://localhost:11434/api/ps')
            if response.status_code == 200:
                data = response.json()
                if not data.get('models', []):
                    return []
                return sorted(list(set(model['name'] for model in data['models'])))
            return []
        except:
            return []

    def get_available_models(self) -> list:
        """Get list of available Ollama models."""
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                data = response.json()
                if not data.get('models', []):
                    return []
                return sorted(list(set(model['name'] for model in data['models'])))
            return []
        except:
            return []

    def run_model(self, model_name: str) -> OllamaLLM:
        """Initialize and test a model."""
        try:
            # Initialize model with LangChain
            model = OllamaLLM(
                model=model_name,
                temperature=0.7
            )
            # Test the model
            test_container = st.empty()
            from models.chat_model import StreamHandler
            stream_handler = StreamHandler(test_container)
            model_test = OllamaLLM(
                model=model_name,
                callbacks=[stream_handler],
                temperature=0.7
            )
            response = model_test.invoke("Hello")
            st.success(f"Successfully started model: {model_name}")
            return model
        except Exception as e:
            st.error(f"Error starting model: {str(e)}")
            return None

    def setup_ollama(self, model_name: str) -> OllamaLLM:
        """Set up and initialize Ollama with specified model."""
        try:
            print(f"Attempting to initialize Ollama with model: {model_name}")
            # Strip ':latest' suffix if present
            base_model = model_name.split(':')[0] if ':' in model_name else model_name
            model = OllamaLLM(
                model=base_model,
                temperature=0.7
            )
            # Test the model with a simple prompt
            response = model.invoke("Hello")
            print(f"Test response received: {response[:100]}...")
            return model
        except Exception as e:
            print(f"Error initializing Ollama: {str(e)}")
            raise

    def get_current_model(self) -> OllamaLLM:
        """Get the currently loaded model."""
        return st.session_state.current_llm

    def set_current_model(self, model: OllamaLLM, model_name: str):
        """Set the current model and update session state."""
        st.session_state.current_llm = model
        st.session_state.last_model = model_name
