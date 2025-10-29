"""Embedding generation utilities supporting multiple providers."""
import os
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using OpenAI or Ollama."""
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: str = None,
        model: str = None,
        dimensions: int = 1536,
        ollama_base_url: str = "http://localhost:11434"
    ):
        """Initialize embedding generator.
        
        Args:
            provider: 'openai', 'ollama', or 'cohere'
            api_key: API key for the provider
            model: Model name
            dimensions: Embedding dimension size
            ollama_base_url: Ollama server URL
        """
        self.provider = provider.lower()
        self.dimensions = dimensions
        
        if self.provider == "openai":
            from openai import OpenAI
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not provided")
            self.model = model or "text-embedding-3-small"
            self.client = OpenAI(api_key=self.api_key)
            
        elif self.provider == "cohere":
            try:
                import cohere
                self.api_key = api_key or os.getenv("COHERE_API_KEY")
                if not self.api_key:
                    raise ValueError("COHERE_API_KEY not provided")
                self.client = cohere.Client(self.api_key)
                self.model = model or "embed-english-v3.0"
                # Cohere embed-english-v3.0 is 1024 dimensions
                if dimensions == 1536:
                    self.dimensions = 1024
                    logger.warning("Cohere uses 1024 dimensions, adjusting from 1536")
            except ImportError:
                raise ImportError("Please install cohere: pip install cohere")
            
        elif self.provider == "ollama":
            try:
                import ollama
                self.client = ollama.Client(host=ollama_base_url)
                # Use a smaller model suitable for embeddings
                self.model = model or "nomic-embed-text"
                # Ollama embeddings are typically 768 dimensions
                if dimensions == 1536:
                    self.dimensions = 768
                    logger.warning("Ollama uses 768 dimensions, adjusting from 1536")
            except ImportError:
                raise ImportError("Please install ollama: pip install ollama")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'cohere', or 'ollama'")
        
        logger.info(f"Embedding generator initialized with {self.provider} ({self.model})")
    
    def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    dimensions=self.dimensions
                )
                embedding = response.data[0].embedding
                
            elif self.provider == "cohere":
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_document"
                )
                embedding = response.embeddings[0]
                
            elif self.provider == "ollama":
                response = self.client.embeddings(
                    model=self.model,
                    prompt=text
                )
                embedding = response['embedding']
            
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        if self.provider == "openai":
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch,
                        dimensions=self.dimensions
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    
                    logger.info(f"Generated embeddings for batch {i//batch_size + 1} "
                              f"({len(batch)} texts)")
                except Exception as e:
                    logger.error(f"Error generating batch embeddings: {e}")
                    raise
        
        elif self.provider == "cohere":
            # Cohere can handle up to 96 texts per request
            batch_size = min(batch_size, 96)
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = self.client.embed(
                        texts=batch,
                        model=self.model,
                        input_type="search_document"
                    )
                    embeddings.extend(response.embeddings)
                    
                    logger.info(f"Generated embeddings for batch {i//batch_size + 1} "
                              f"({len(batch)} texts)")
                except Exception as e:
                    logger.error(f"Error generating batch embeddings: {e}")
                    raise
        
        elif self.provider == "ollama":
            # Ollama processes one at a time
            for i, text in enumerate(texts, 1):
                embedding = self.generate(text)
                embeddings.append(embedding)
                if i % 10 == 0:
                    logger.info(f"Generated embeddings for {i}/{len(texts)} texts")
        
        return embeddings
    
    def generate_workflow_embedding(
        self,
        title: str,
        description: str,
        content: str,
        tags: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None
    ) -> List[float]:
        """Generate embedding for a workflow by combining its components.
        
        Args:
            title: Workflow title
            description: Workflow description
            content: Full workflow content
            tags: Optional list of tags
            use_cases: Optional list of use cases
            
        Returns:
            Embedding vector
        """
        # Combine workflow components with weighted importance
        text_parts = [
            f"Title: {title}",
            f"Description: {description}",
        ]
        
        if tags:
            text_parts.append(f"Tags: {', '.join(tags)}")
        
        if use_cases:
            text_parts.append(f"Use Cases: {', '.join(use_cases)}")
        
        # Include a truncated version of content
        content_preview = content[:1000] if len(content) > 1000 else content
        text_parts.append(f"Content: {content_preview}")
        
        combined_text = "\n\n".join(text_parts)
        
        return self.generate(combined_text)


# Global embedding generator instance
_embedding_generator: EmbeddingGenerator = None


def init_embeddings(
    provider: str = None,
    api_key: str = None,
    model: str = None
) -> EmbeddingGenerator:
    """Initialize global embedding generator.
    
    Args:
        provider: 'openai', 'cohere', or 'ollama' (auto-detect from env if not specified)
        api_key: API key for the provider
        model: Model name
        
    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    
    # Auto-detect provider from environment
    if provider is None:
        provider = os.getenv("EMBEDDING_PROVIDER")
        if not provider:
            # Try to auto-detect based on available API keys
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("COHERE_API_KEY"):
                provider = "cohere"
            elif os.getenv("OLLAMA_API_KEY"):
                provider = "ollama"
            else:
                raise ValueError("No embedding provider configured. Set EMBEDDING_PROVIDER in .env")
    
    model = model or os.getenv("EMBEDDING_MODEL")
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    
    _embedding_generator = EmbeddingGenerator(
        provider=provider,
        api_key=api_key,
        model=model,
        dimensions=dimensions
    )
    return _embedding_generator


def get_embeddings() -> EmbeddingGenerator:
    """Get global embedding generator instance.
    
    Returns:
        EmbeddingGenerator instance
        
    Raises:
        RuntimeError: If embeddings not initialized
    """
    if _embedding_generator is None:
        raise RuntimeError("Embeddings not initialized. Call init_embeddings() first.")
    return _embedding_generator
