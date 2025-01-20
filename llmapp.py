import streamlit as st
from dotenv import load_dotenv
from models.chat_model import ChatModel
from models.screen_model import ScreenModel
from models.model_settings import ModelSettings
from models.display_model import DisplayModel

def init_models():
    """Initialize all model instances."""
    chat_model = ChatModel()
    screen_model = ScreenModel()
    model_settings = ModelSettings()
    display_model = DisplayModel()
    return chat_model, screen_model, model_settings, display_model

def main():
    load_dotenv()
    
    st.title("AI Chat Interface")
    
    # Initialize all models
    chat_model, screen_model, model_settings, display_model = init_models()
    
    # Set up sidebar with status and model selection
    sidebar, status_container = display_model.setup_sidebar()
    available_models = model_settings.get_available_models()
    selected_model, switch_model = display_model.display_model_selection(
        available_models,
        st.session_state.last_model if 'last_model' in st.session_state else None
    )
    
    # Handle model switching
    if switch_model or not model_settings.get_current_model():
        with display_model.display_loading_spinner(f"Loading {selected_model}..."):
            model = model_settings.run_model(selected_model)
            if model:
                model_settings.set_current_model(model, selected_model)
                st.rerun()
    
    # Set up webpage section
    url, load_webpage = display_model.setup_webpage_section()
    if load_webpage and url:
        try:
            with display_model.display_loading_spinner("Scraping webpage..."):
                screen_model.scrape_webpage(url)
                with st.sidebar:
                    display_model.display_success("Webpage loaded successfully!")
                    screen_model.display_webpage_preview()
        except Exception as e:
            with st.sidebar:
                display_model.display_error(f"Failed to load webpage: {str(e)}")
    
    try:
        current_model = model_settings.get_current_model()
        if not current_model:
            display_model.display_info("Please select and load a model from the sidebar to begin.")
            return
        
        # Update status in sidebar
        display_model.update_status(
            status_container,
            st.session_state.last_model,
            screen_model.get_current_url()
        )
        
        # Display chat messages
        chat_model.display_messages()
        
        # Handle chat input
        if prompt := display_model.display_chat_input():
            if not current_model:
                display_model.display_error("No LLM initialized. Please check your configuration.")
                return
            
            try:
                chat_model.process_chat(
                    prompt,
                    current_model,
                    screen_model.get_webpage_content()
                )
                
            except Exception as e:
                display_model.display_error(f"Error: {str(e)}")
    
    except Exception as e:
        display_model.display_error(str(e))

if __name__ == "__main__":
    main()
