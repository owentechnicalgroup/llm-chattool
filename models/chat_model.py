from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from langchain_ollama import OllamaLLM
import os
from langchain_anthropic import ChatAnthropic
from typing import Union, List

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.placeholder = container.empty()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.placeholder.markdown(self.text)

class ChatModel:
    def __init__(self, rag_model=None):
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'current_model' not in st.session_state:
            st.session_state.current_model = None
        self.rag_model = rag_model

    def _check_and_clear_messages(self, new_model: str):
        """Clear messages if model has changed."""
        if st.session_state.current_model != new_model:
            st.session_state.messages = []
            st.session_state.current_model = new_model

    def add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        st.session_state.messages.append({"role": role, "content": content})

    def get_messages(self):
        """Get all chat messages."""
        return st.session_state.messages

    def display_messages(self):
        """Display all chat messages in the Streamlit interface."""
        for message in self.get_messages():
            role = "assistant" if message["role"] == "AI" else "user"
            st.chat_message(role).write(message["content"])

    def process_chat(self, prompt: str, llm: Union[OllamaLLM, ChatAnthropic], webpage_content: str = None):
        """Process a chat message and generate a response."""
        try:
            # Clear messages if model changes
            current_model = llm.model if isinstance(llm, OllamaLLM) else "anthropic"
            self._check_and_clear_messages(current_model)

            # Add user message
            self.add_message("user", prompt)
            st.chat_message("user").write(prompt)

            # Create chat container for response
            chat_container = st.chat_message("assistant")
            stream_handler = StreamHandler(chat_container)

            # Create streaming LLM instance based on model type
            if isinstance(llm, OllamaLLM):
                streaming_llm = OllamaLLM(
                    model=llm.model,
                    callbacks=[stream_handler],
                    temperature=0.6
                )
            else:  # ChatAnthropic
                # Re-use the existing model's configuration
                streaming_llm = llm
                streaming_llm.callbacks = [stream_handler]

            # Prepare combined context from RAG and webpage if available
            context_parts = []
            system_prompts = []
            
            # Add system prompt for general behavior
            system_prompts.append("""You are a helpful AI assistant. When answering questions:

            Use specific context (like a webpage or document) as your primary source when available.
            
            If that's not possible, use general knowledge to help answer the question.
            
            Sometimes, you may draw from external information.

            Never mention "RAG" in my responses.""")
            
            # Add RAG context if available
            rag_enabled = self.rag_model and self.rag_model.is_enabled()
            if rag_enabled:
                rag_context = self.rag_model.get_rag_context(prompt)
                if rag_context:
                    context_parts.append(rag_context)
                else:
                    system_prompts.append("Note: RAG is enabled but no relevant documents were found for this query.")
            
            # Add webpage context if available    
            if webpage_content:
                context_parts.append(f"Webpage Context:\n{webpage_content[:3000]}...")
            
            # Construct the enhanced prompt
            enhanced_prompt = "\n\n".join([
                *system_prompts,
                *context_parts,
                f"User question: {prompt}",
                "Please provide a concise answer to the users question. Only reference the document if asked for it"
            ])

            # Get AI response with streaming
            if isinstance(streaming_llm, OllamaLLM):
                response = streaming_llm.invoke(enhanced_prompt)
            else:  # ChatAnthropic
                from langchain_core.messages import HumanMessage
                response = streaming_llm.invoke([HumanMessage(content=enhanced_prompt)])
                # Extract content from the response
                response = response.content

            # Add AI response to chat history
            self.add_message("AI", response)

            return response
        except Exception as e:
            st.error(f"Error in chat processing: {str(e)}")
            return None
