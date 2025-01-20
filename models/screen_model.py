import requests
from bs4 import BeautifulSoup
import streamlit as st

class ScreenModel:
    def __init__(self):
        if 'current_url' not in st.session_state:
            st.session_state.current_url = None
        if 'webpage_content' not in st.session_state:
            st.session_state.webpage_content = None

    def scrape_webpage(self, url: str) -> str:
        """Scrape content from a webpage."""
        try:
            # Add http:// if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean it up
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive newlines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Update session state
            st.session_state.webpage_content = text
            st.session_state.current_url = url
            
            return text
            
        except Exception as e:
            raise Exception(f"Error scraping webpage: {str(e)}")

    def get_current_url(self) -> str:
        """Get the currently loaded URL."""
        return st.session_state.current_url

    def get_webpage_content(self) -> str:
        """Get the currently loaded webpage content."""
        return st.session_state.webpage_content

    def display_webpage_preview(self):
        """Display a preview of the scraped webpage content in the sidebar."""
        if st.session_state.webpage_content:
            with st.sidebar:
                with st.expander("View scraped content"):
                    st.text_area("Content", st.session_state.webpage_content, height=200)
