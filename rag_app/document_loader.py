import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langsmith import Client
import logging
import glob

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, data_dir="data"):
        """Initialize the document loader with the data directory path."""
        self.data_dir = data_dir
        self.completed_dir = os.path.join(data_dir, "completed")
        self.langsmith_client = Client()
        
        # Ensure completed directory exists
        if not os.path.exists(self.completed_dir):
            os.makedirs(self.completed_dir)
        
    def move_to_completed(self, file_path):
        """Move a processed file to the completed directory."""
        filename = os.path.basename(file_path)
        destination = os.path.join(self.completed_dir, filename)
        shutil.move(file_path, destination)
        logger.info(f"Moved {filename} to completed folder")
        
    def get_appropriate_loader(self, file_path):
        """Get the appropriate loader based on file extension."""
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.txt':
            return TextLoader(file_path)
        elif ext.lower() in ['.doc', '.docx']:
            return Docx2txtLoader(file_path)
        elif ext.lower() == '.pdf':
            return PyPDFLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
    def load_documents(self):
        """Load all documents from the data directory."""
        try:
            documents = []
            # Get all supported files in the data directory (excluding completed folder)
            files = [f for f in glob.glob(os.path.join(self.data_dir, "*.*")) 
                    if f.lower().endswith(('.txt', '.doc', '.docx', '.pdf')) and 
                    not f.startswith(self.completed_dir)]
            
            for file_path in files:
                try:
                    # Get appropriate loader for the file type
                    loader = self.get_appropriate_loader(file_path)
                    # Load the document(s)
                    # Note: PDF loader might return multiple documents (one per page)
                    docs = loader.load()
                    
                    for doc in docs:
                        char_count = len(doc.page_content)
                        logger.info(f"Loaded document: {file_path}")
                        logger.info(f"Document characters: {char_count}")
                        print(f"\nDocument Content:\n{doc.page_content}")
                        
                        # Log to LangSmith
                        self.langsmith_client.create_run(
                            name="document_loading",
                            run_type="chain",  # Required run_type parameter
                            inputs={"file_path": file_path},
                            outputs={
                                "char_count": char_count,
                                "content_preview": doc.page_content[:100] + "..."
                            }
                        )
                        
                        documents.append(doc)
                    
                    # Move the processed file to completed folder
                    self.move_to_completed(file_path)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
            
            logger.info(f"Loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise

if __name__ == "__main__":
    doc_loader = DocumentLoader()
    doc_loader.load_documents()
