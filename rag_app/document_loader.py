import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langsmith import Client
import logging
import glob
from chroma_store import ChromaStore

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
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20,
            length_function=len,
            separators=[". ", ".\n", "? ", "! ", "\n\n", "\n", " ", ""]
        )
        
        # Initialize Chroma store with absolute path
        chroma_db_path = os.path.abspath(os.path.join(data_dir, "chroma_db"))
        self.chroma_store = ChromaStore(persist_directory=chroma_db_path)
        
        # Ensure completed directory exists
        if not os.path.exists(self.completed_dir):
            os.makedirs(self.completed_dir)
        
    def move_to_completed(self, file_path):
        """Move a processed file to the completed directory."""
        try:
            filename = os.path.basename(file_path)
            destination = os.path.join(self.completed_dir, filename)
            shutil.move(file_path, destination)
            logger.info(f"Moved {filename} to completed folder")
        except Exception as e:
            logger.error(f"Error moving file {file_path} to completed folder: {str(e)}")
            
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
        
    def split_text(self, document):
        """Split document into chunks."""
        if not document.page_content or len(document.page_content.strip()) == 0:
            logger.warning("Empty document content, skipping text splitting")
            return []
        return self.text_splitter.split_documents([document])
        
    def process_document(self, doc, file_path):
        """Process a single document."""
        try:
            char_count = len(doc.page_content)
            if char_count == 0:
                logger.warning(f"Empty document content in {file_path}")
                return []
                
            logger.info(f"Processing document: {file_path}")
            logger.info(f"Document characters: {char_count}")
            print(f"\nOriginal Document Content:\n{'-' * 80}\n{doc.page_content}\n{'-' * 80}")
            
            # Split the document into chunks
            doc_chunks = self.split_text(doc)
            
            if doc_chunks:
                # Print chunks with character counts
                print(f"\nDocument Chunks ({len(doc_chunks)}):")
                for i, chunk in enumerate(doc_chunks, 1):
                    chunk_chars = len(chunk.page_content)
                    print(f"\nChunk {i} ({chunk_chars} characters):")
                    print("-" * 40)
                    print(chunk.page_content.strip())
                    print("-" * 40)
                
                # Log to LangSmith
                try:
                    avg_chunk_size = sum(len(c.page_content) for c in doc_chunks) / len(doc_chunks)
                    self.langsmith_client.create_run(
                        name="document_loading",
                        run_type="chain",
                        inputs={"file_path": file_path},
                        outputs={
                            "char_count": char_count,
                            "content_preview": doc.page_content[:100] + "...",
                            "num_chunks": len(doc_chunks),
                            "avg_chunk_size": avg_chunk_size
                        }
                    )
                except Exception as e:
                    logger.error(f"Error logging to LangSmith: {str(e)}")
            
            return doc_chunks
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return []
        
    def load_documents(self):
        """Load all documents from the data directory."""
        try:
            documents = []
            chunks = []
            
            # Get all supported files in the data directory
            files = []
            
            # Check main data directory
            main_dir_files = [f for f in glob.glob(os.path.join(self.data_dir, "*.*")) 
                            if f.lower().endswith(('.txt', '.doc', '.docx', '.pdf')) and 
                            not os.path.dirname(f).endswith('completed')]
            files.extend(main_dir_files)
            
            # Check completed directory and move files back if needed
            completed_files = [f for f in glob.glob(os.path.join(self.completed_dir, "*.*"))
                             if f.lower().endswith(('.txt', '.doc', '.docx', '.pdf'))]
            
            # Move completed files back to main directory for reprocessing
            for completed_file in completed_files:
                try:
                    filename = os.path.basename(completed_file)
                    destination = os.path.join(self.data_dir, filename)
                    shutil.move(completed_file, destination)
                    files.append(destination)
                    logger.info(f"Moved {filename} back for reprocessing")
                except Exception as e:
                    logger.error(f"Error moving file back for reprocessing: {str(e)}")
            
            if not files:
                logger.info("No files found to process")
                return [], []
            
            for file_path in files:
                try:
                    # Get appropriate loader for the file type
                    loader = self.get_appropriate_loader(file_path)
                    # Load the document(s)
                    docs = loader.load()
                    
                    if not docs:
                        logger.warning(f"No content loaded from {file_path}")
                        continue
                    
                    file_chunks = []
                    for doc in docs:
                        doc_chunks = self.process_document(doc, file_path)
                        if doc_chunks:
                            file_chunks.extend(doc_chunks)
                            documents.append(doc)
                    
                    if file_chunks:
                        chunks.extend(file_chunks)
                        # Only move file if processing was successful
                        self.move_to_completed(file_path)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
            
            logger.info(f"Successfully loaded {len(documents)} documents")
            logger.info(f"Created {len(chunks)} total chunks")
            # Add chunks to Chroma if any were created
            if chunks:
                try:
                    self.chroma_store.add_documents(chunks)
                    stats = self.chroma_store.get_collection_stats()
                    logger.info(f"Chroma collection now has {stats['total_documents']} total documents")
                except Exception as e:
                    logger.error(f"Error adding documents to Chroma: {str(e)}")
            
            return documents, chunks
            
        except Exception as e:
            logger.error(f"Error in load_documents: {str(e)}")
            return [], []
            
    def query_similar_chunks(self, query_text: str, n_results: int = 3):
        """Query Chroma for similar chunks of text."""
        try:
            return self.chroma_store.query_documents(query_text, n_results)
        except Exception as e:
            logger.error(f"Error querying similar chunks: {str(e)}")
            return []
