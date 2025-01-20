from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from langchain_ollama import OllamaLLM

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.placeholder = container.empty()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.placeholder.markdown(self.text)

class ChatModel:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []

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

    def process_chat(self, prompt: str, llm: OllamaLLM, webpage_content: str = None):
        """Process a chat message and generate a response."""
        try:
            # Add user message
            self.add_message("user", prompt)
            st.chat_message("user").write(prompt)

            # Create chat container for response
            chat_container = st.chat_message("assistant")
            stream_handler = StreamHandler(chat_container)

            # Create streaming LLM instance
            streaming_llm = OllamaLLM(
                model=llm.model,
                callbacks=[stream_handler],
                temperature=0.7
            )

            # Prepare prompt with webpage content if available
            if webpage_content:
                enhanced_prompt = f"""Context from webpage:
{webpage_content[:3000]}...

User question: {prompt}

Please provide a response based on the webpage content above."""
            else:
                enhanced_prompt = prompt

            # Get AI response with streaming
            response = streaming_llm.invoke(enhanced_prompt)

            # Add AI response to chat history
            self.add_message("AI", response)

            return response
        except Exception as e:
            st.error(f"Error in chat processing: {str(e)}")
            return None
