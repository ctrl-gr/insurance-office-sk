from typing import Annotated, List
from semantic_kernel.functions import kernel_function
import PyPDF2
import os

class conditions_plugin:
    def __init__(self):
        self.pdf_chunks = []
        self.pdf_filename = ""
        self.loaded = False
        self.chunk_size = 1000
    
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
        name="load_pdf",
        description="Loads a PDF file and splits it into searchable chunks. Use this before answering questions about a PDF document.",
    )
    def load_pdf(
        self,
        file_path: Annotated[str, "The path to the PDF file to load"],
    ) -> str:
        """Loads and chunks a PDF file for efficient searching."""
        try:
            if not os.path.exists(file_path):
                return f"Error: PDF file not found at {file_path}"
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                full_text = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    full_text.append(f"[Page {page_num + 1}] {page_text}")
                
                combined_text = "\n".join(full_text)
                self.pdf_chunks = self._chunk_text(combined_text)
                self.pdf_filename = os.path.basename(file_path)
                self.loaded = True
                
                return f"Successfully loaded PDF: {self.pdf_filename} ({num_pages} pages, {len(self.pdf_chunks)} chunks). Ready for questions!"
        
        except Exception as e:
            return f"Error loading PDF: {str(e)}"
    
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
            return "No PDF loaded. Please use load_pdf first."
        
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
