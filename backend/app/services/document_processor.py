"""
Document processing service for handling file uploads and text chunking
"""
import os
import tiktoken
import PyPDF2
import aiofiles
from typing import List, Tuple, Optional
from datetime import datetime
import logging

from app.models.document import DocumentChunk
from app.services.language_detector import LanguageDetector

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents and creating chunks"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the document processor

        Args:
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.language_detector = LanguageDetector()
    
    async def process_file(self, file_path: str, user_id: str, document_name: str) -> Tuple[List[DocumentChunk], str]:
        """
        Process a file and return document chunks with detected language

        Args:
            file_path: Path to the uploaded file
            user_id: User ID who uploaded the file
            document_name: Name of the document

        Returns:
            Tuple of (List of DocumentChunk objects, detected language code)
        """
        try:
            # Read file content based on file type
            content = await self._read_file_content(file_path)

            # Detect language
            language = self.language_detector.detect_language(content)
            logger.info(f"Detected language: {language} for document {document_name}")

            # Create chunks
            chunks = self._create_chunks(content, user_id, document_name, language)

            logger.info(f"Processed {document_name} into {len(chunks)} chunks for user {user_id}")
            return chunks, language

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    async def _read_file_content(self, file_path: str) -> str:
        """
        Read content from a file based on its type
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.txt':
            return await self._read_text_file(file_path)
        elif file_extension == '.pdf':
            return await self._read_pdf_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    async def _read_text_file(self, file_path: str) -> str:
        """Read content from a text file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                content = await f.read()
            return content
    
    async def _read_pdf_file(self, file_path: str) -> str:
        """Read content from a PDF file"""
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"
            return content
        except Exception as e:
            logger.error(f"Failed to read PDF file {file_path}: {e}")
            raise
    
    def _create_chunks(self, content: str, user_id: str, document_name: str, language: Optional[str] = None) -> List[DocumentChunk]:
        """
        Create chunks from document content

        Args:
            content: Document content as string
            user_id: User ID
            document_name: Document name
            language: Detected language code

        Returns:
            List of DocumentChunk objects
        """
        # Tokenize the content
        tokens = self.encoding.encode(content)

        if len(tokens) <= self.chunk_size:
            # Content fits in one chunk
            chunk_text = content
            chunk = DocumentChunk(
                user_id=user_id,
                document_name=document_name,
                chunk_index=0,
                text_chunk=chunk_text,
                chunk_size=len(tokens),
                created_at=datetime.utcnow(),
                metadata={
                    'total_tokens': len(tokens),
                    'chunk_method': 'single_chunk',
                    'language': language
                }
            )
            return [chunk]
        
        # Create overlapping chunks
        chunks = []
        start_idx = 0
        chunk_index = 0
        
        while start_idx < len(tokens):
            # Calculate end index
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            
            # Extract tokens for this chunk
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode tokens back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk object
            chunk = DocumentChunk(
                user_id=user_id,
                document_name=document_name,
                chunk_index=chunk_index,
                text_chunk=chunk_text,
                chunk_size=len(chunk_tokens),
                created_at=datetime.utcnow(),
                metadata={
                    'total_tokens': len(tokens),
                    'chunk_method': 'overlapping',
                    'start_token': start_idx,
                    'end_token': end_idx,
                    'language': language
                }
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start_idx = end_idx - self.chunk_overlap
            chunk_index += 1
            
            # Prevent infinite loop
            if start_idx >= len(tokens) - self.chunk_overlap:
                break
        
        logger.info(f"Created {len(chunks)} chunks from {len(tokens)} tokens")
        return chunks
    
    def get_chunk_stats(self, chunks: List[DocumentChunk]) -> dict:
        """
        Get statistics about the chunks
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_tokens': 0,
                'avg_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0
            }
        
        chunk_sizes = [chunk.chunk_size for chunk in chunks]
        total_tokens = sum(chunk_sizes)
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'avg_chunk_size': total_tokens / len(chunks),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes)
        }
