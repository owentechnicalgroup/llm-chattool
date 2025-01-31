import os
import requests
import streamlit as st
import anthropic
from langchain_ollama import OllamaLLM
from langchain_anthropic import ChatAnthropic
from typing import Union

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
        """Get list of available models including both Ollama and Claude."""
        models = []
        
        # Get Ollama models
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                data = response.json()
                if data.get('models', []):
                    models.extend(model['name'] for model in data['models'])
        except:
            pass
            
        # Get Claude models through the API if key is available
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                # Initialize Anthropic client
                client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                # Fetch available models
                available_models = client.models.list()
                for model in available_models.data:
                    if model.id.startswith('claude'):  # Only add Claude models
                        models.append(model.id)
                st.sidebar.success(f"✓ Found {len(models)} Claude models")
            except Exception as e:
                st.sidebar.warning(f"Failed to fetch Claude models: {str(e)}")
                
        return sorted(list(set(models)))

    def run_model(self, model_name: str) -> Union[OllamaLLM, ChatAnthropic]:
        """Initialize and test a model."""
        try:
            if model_name.startswith('claude'):
                return self._init_claude_model(model_name)
            else:
                return self._init_ollama_model(model_name)
        except Exception as e:
            st.error(f"Error starting model: {str(e)}")
            return None

    def _init_claude_model(self, model_name: str) -> ChatAnthropic:
        """Initialize Claude model."""
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
        # Initialize single model instance with streaming
        test_container = st.empty()
        from models.chat_model import StreamHandler
        stream_handler = StreamHandler(test_container)
        
        model = ChatAnthropic(
            model_name=model_name,
            temperature=0.7,
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            streaming=True,
            max_tokens=1000,
            callbacks=[stream_handler]
        )
        
        # Test the model
        from langchain_core.messages import HumanMessage
        test_response = model.invoke([HumanMessage(content="Hello")])
        response = test_response.content
        st.success(f"Successfully started model: {model_name}")
        return model

    def _init_ollama_model(self, model_name: str) -> OllamaLLM:
        """Initialize Ollama model."""
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

    def get_current_model(self) -> Union[OllamaLLM, ChatAnthropic]:
        """Get the currently loaded model."""
        return st.session_state.current_llm

    def set_current_model(self, model: Union[OllamaLLM, ChatAnthropic], model_name: str):
        """Set the current model and update session state."""
        st.session_state.current_llm = model
        st.session_state.last_model = model_name
