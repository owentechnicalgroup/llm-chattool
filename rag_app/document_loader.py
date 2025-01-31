import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
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
        # Ensure we use the correct path relative to the rag_app directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, data_dir)
        self.completed_dir = os.path.join(self.data_dir, "completed")
        self.langsmith_client = Client()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            length_function=len,
            separators=[
                "\n## ",     # Section headers
                "\n### ",    # Subsection headers
                "\n\n",      # Paragraphs
                ". ",        # Sentences
                "? ",        # Questions
                "! ",        # Exclamations
                "\n",        # Lines
                " ",         # Words
                ""          # Characters
            ]
        )
        
        # Initialize Chroma store with absolute path
        chroma_db_path = os.path.join(self.data_dir, "chroma_db")
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
        
    def _detect_section(self, content):
        """Detect section from content based on headers."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('##'):
                return line.strip('# ').strip()
        return None

    def _validate_chunk(self, chunk):
        """Validate chunk quality."""
        min_chunk_size = 30  # Minimum characters
        content = chunk.page_content.strip()
        
        # Immediately reject unwanted content
        if any([
            content.startswith('http'),  # URLs
            content.startswith('Retrieved from'),  # Wikipedia footer
            'References' in content and len(content) < 100,  # Short reference sections
            'External links' in content and len(content) < 100  # Short external links sections
        ]):
            return False
            
        # Check size
        if len(content) < min_chunk_size:
            return False
            
        # Split into lines and words
        lines = content.split('\n')
        words = content.split()
        
        # Reject if too few words
        if len(words) < 5:
            return False
            
        # Accept if it's a complete paragraph
        if len(words) > 20 and content[-1] in '.!?':
            return True
            
        # Accept if it contains meaningful location or feature descriptions
        location_indicators = ['shore', 'lake', 'bay', 'park', 'marina', 'resort']
        if any(indicator in content.lower() for indicator in location_indicators):
            return True
            
        # Accept if it's a multi-line description without too many special characters
        if len(lines) > 1 and len(words) > 10:
            special_chars = sum(1 for c in content if c in '[](){}:/')
            if special_chars <= 3:  # Allow some formatting but not too much
                return True
                
        return False

    def split_text(self, document):
        """Split document into chunks with enhanced metadata."""
        if not document.page_content or len(document.page_content.strip()) == 0:
            logger.warning("Empty document content, skipping text splitting")
            return []
            
        chunks = self.text_splitter.split_documents([document])
        valid_chunks = []
        
        # Enhance chunks with metadata
        for i, chunk in enumerate(chunks):
            if self._validate_chunk(chunk):
                # Ensure all metadata values are valid types (str, int, float, bool)
                chunk.metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_size': len(chunk.page_content),
                    'source_document': document.metadata.get('source', ''),
                    'section': self._detect_section(chunk.page_content) or 'unknown',  # Default if None
                    'created_at': datetime.now().isoformat(),
                    'content_type': 'text'  # Default content type
                })
                valid_chunks.append(chunk)
            else:
                logger.warning(f"Chunk {i} failed validation, skipping")
                
        return valid_chunks
        
    def process_document(self, doc, file_path):
        """Process a single document with enhanced metadata."""
        try:
            char_count = len(doc.page_content)
            if char_count == 0:
                logger.warning(f"Empty document content in {file_path}")
                return []
                
            # Add document metadata
            doc_metadata = {
                'source': file_path,
                'doc_type': os.path.splitext(file_path)[1].lstrip('.') or 'unknown',
                'created_at': datetime.now().isoformat(),
                'total_chars': char_count,
                'language': 'en'  # Default language
            }
            doc.metadata.update(doc_metadata)
            
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
        
    def _get_files(self):
        """Get all supported files from the data directory."""
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
                
        return files

    def _process_file(self, file_path):
        """Process a single file."""
        try:
            loader = self.get_appropriate_loader(file_path)
            docs = loader.load()
            
            if not docs:
                logger.warning(f"No content loaded from {file_path}")
                return None
            
            file_chunks = []
            file_docs = []
            for doc in docs:
                doc_chunks = self.process_document(doc, file_path)
                if doc_chunks:
                    file_chunks.extend(doc_chunks)
                    file_docs.append(doc)
            
            if file_chunks:
                self.move_to_completed(file_path)
                return (file_docs, file_chunks)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
        return None

    def load_documents(self):
        """Load all documents from the data directory with parallel processing."""
        try:
            files = self._get_files()
            
            if not files:
                logger.info("No files found to process")
                return [], []
            
            documents = []
            chunks = []
            
            # Process files in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self._process_file, file_path) 
                          for file_path in files]
                
                for future in futures:
                    result = future.result()
                    if result:
                        docs, doc_chunks = result
                        documents.extend(docs)
                        chunks.extend(doc_chunks)
            
            logger.info(f"Successfully loaded {len(documents)} documents")
            logger.info(f"Created {len(chunks)} total chunks")
            
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
