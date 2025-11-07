"""
LLM service for generating chat responses using OpenAI
"""
import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating LLM responses using OpenAI"""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize LLM service

        Args:
            model: OpenAI model to use for chat completions
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized LLM service with model: {model}")

    def generate_response(
        self,
        prompt: str,
        context_chunks: List[Dict],
        language: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a response using retrieved context

        Args:
            prompt: User's question
            context_chunks: List of relevant document chunks
            language: Language code ('en' or 'es')
            max_tokens: Maximum tokens in response

        Returns:
            Generated response text
        """
        try:
            # Build context from chunks
            context_text = self._build_context(context_chunks)

            # Build system message based on language
            system_message = self._get_system_message(language)

            # Build user message
            user_message = self._build_user_message(prompt, context_text)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            # Extract response text
            answer = response.choices[0].message.content

            logger.info(f"Generated response with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    def _build_context(self, context_chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks

        Args:
            context_chunks: List of document chunks with metadata

        Returns:
            Formatted context string
        """
        if not context_chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            doc_name = chunk.get('document_name', 'Unknown')
            text = chunk.get('text_chunk', '')
            score = chunk.get('score', 0.0)

            context_parts.append(
                f"[Document: {doc_name} | Relevance: {score:.2f}]\n{text}"
            )

        return "\n\n".join(context_parts)

    def _get_system_message(self, language: Optional[str] = None) -> str:
        """
        Get system message based on language

        Args:
            language: Language code ('en' or 'es')

        Returns:
            System message string
        """
        if language == 'es':
            return """Eres un asistente útil que responde preguntas basándose en documentos proporcionados.
Tu trabajo es:
1. Analizar el contexto proporcionado de los documentos
2. Responder la pregunta del usuario usando SOLO la información del contexto
3. Si el contexto no contiene información relevante, indica claramente que no puedes responder basándote en los documentos disponibles
4. Ser preciso, conciso y útil
5. Citar las fuentes cuando sea relevante (mencionar el nombre del documento)

NO inventes información que no esté en el contexto. Si no estás seguro, di que no lo sabes."""
        else:
            return """You are a helpful assistant that answers questions based on provided documents.
Your job is to:
1. Analyze the context provided from the documents
2. Answer the user's question using ONLY information from the context
3. If the context doesn't contain relevant information, clearly state that you cannot answer based on the available documents
4. Be accurate, concise, and helpful
5. Cite sources when relevant (mention document name)

DO NOT make up information that isn't in the context. If you're unsure, say you don't know."""

    def _build_user_message(self, prompt: str, context: str) -> str:
        """
        Build user message with context and question

        Args:
            prompt: User's question
            context: Context from retrieved chunks

        Returns:
            Formatted user message
        """
        return f"""Context from documents:

{context}

---

Question: {prompt}

Please answer the question based on the context provided above."""

    def test_connection(self) -> bool:
        """
        Test connection to OpenAI API

        Returns:
            True if connection is successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            logger.info("Successfully connected to OpenAI API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI API: {e}")
            return False
