from typing import Annotated, List
from semantic_kernel.functions import kernel_function
from pymongo import MongoClient
import PyPDF2
import os

class conditions_plugin:
    def __init__(self):
        self.pdf_chunks = []
        self.pdf_filename = ""
        self.loaded = False
        self.chunk_size = 1000
        self.client = None
        self.db = None
        self.conditions_collection = None
        self.connected = False
    
    def _connect(self):
        """Internal method to establish database connection."""
        if self.connected:
            return True
        
        try:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            if not connection_string:
                return False
            
            self.client = MongoClient(connection_string)
            self.client.admin.command('ping')
            
            self.db = self.client[os.getenv("DB_NAME")]
            self.conditions_collection = self.db["policy_conditions"]
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            return False
    
    def _chunk_text(self, text: str) -> List[dict]:
        """Split text into overlapping chunks for better context."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= self.chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'size': len(chunk_text)
                })
                current_chunk = current_chunk[-100:]
                current_size = sum(len(w) + 1 for w in current_chunk)
        
        if current_chunk:
            chunks.append({
                'text': ' '.join(current_chunk),
                'size': len(' '.join(current_chunk))
            })
        
        return chunks
    
    @kernel_function(
        name="load_conditions_by_category",
        description="Loads insurance policy conditions PDF from storage based on the policy category (e.g., Auto, Casa, Infortuni). Retrieves the document from database storage and prepares it for analysis.",
    )
    def load_conditions_by_category(
        self,
        category: Annotated[str, "The insurance policy category (e.g., Car, Injuries, Home)"],
    ) -> str:
        """Loads conditions PDF from database storage by category."""
        if not self._connect():
            return "Error: Cannot connect to database. Please check your MongoDB connection string."
        
        try:
            result = self.conditions_collection.find_one({
                "category": {"$regex": f"^{category}$", "$options": "i"}
            })
            
            if not result:
                return f"No conditions found for category '{category}'. Available categories can be checked in the database."
            
            storage_url = result.get("storage_url")
            conditions_name = result.get("name_conditions", "Unknown")
            
            if not storage_url or not os.path.exists(storage_url):
                return f"Conditions '{conditions_name}' found but PDF file not accessible at: {storage_url}"
            
            with open(storage_url, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                full_text = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    full_text.append(f"[Page {page_num + 1}] {page_text}")
                
                combined_text = "\n".join(full_text)
                self.pdf_chunks = self._chunk_text(combined_text)
                self.pdf_filename = conditions_name
                self.loaded = True
                
                return f"Successfully loaded conditions: {conditions_name} ({num_pages} pages, {len(self.pdf_chunks)} chunks). Ready for analysis!"
        
        except Exception as e:
            return f"Error loading conditions: {str(e)}"
    
    @kernel_function(
        name="search_pdf_content",
        description="Searches the PDF for relevant content based on keywords. Returns only the most relevant chunks (not the entire document). Use this to find specific information efficiently.",
    )
    def search_pdf_content(
        self,
        query: Annotated[str, "Keywords or question to search for in the PDF"],
    ) -> str:
        """Searches and returns only relevant chunks from the PDF."""
        if not self.loaded:
            return "No conditions loaded. Please use load_conditions_by_category first to load a policy conditions document."
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_chunks = []
        for idx, chunk in enumerate(self.pdf_chunks):
            chunk_lower = chunk['text'].lower()
            
            matches = sum(1 for word in query_words if word in chunk_lower)
            
            if matches > 0:
                scored_chunks.append({
                    'index': idx,
                    'score': matches,
                    'text': chunk['text']
                })
        
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        top_chunks = scored_chunks[:3]
        
        if not top_chunks:
            return f"No relevant content found for '{query}' in {self.pdf_filename}"
        
        result = f"Found {len(top_chunks)} relevant section(s) in {self.pdf_filename}:\n\n"
        for i, chunk in enumerate(top_chunks, 1):
            result += f"--- Section {i} (Relevance: {chunk['score']} matches) ---\n"
            result += chunk['text'] + "\n\n"
        
        return result
    
    @kernel_function(
        name="get_pdf_info",
        description="Returns information about the currently loaded PDF (filename, chunks, loaded status).",
    )
    def get_pdf_info(self) -> str:
        """Returns information about the loaded PDF."""
        if not self.loaded:
            return "No PDF currently loaded."
        
        total_chars = sum(chunk['size'] for chunk in self.pdf_chunks)
        
        return f"PDF Information:\n- Filename: {self.pdf_filename}\n- Chunks: {len(self.pdf_chunks)}\n- Total characters: {total_chars}\n- Status: Loaded and ready\n- Tip: Use search_pdf_content to find relevant sections efficiently"
