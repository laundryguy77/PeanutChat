"""Ollama embedding API wrapper with retry logic."""

import time
from typing import Callable, List, Optional

import requests

from config import OLLAMA_MODEL, get_ollama_url


class OllamaConnectionError(Exception):
    """Raised when Ollama server is unreachable."""
    pass


class OllamaModelError(Exception):
    """Raised when the embedding model is not available."""
    pass


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have failed."""
    pass


class OllamaEmbedder:
    """Wrapper for Ollama embedding API with retry logic."""

    def __init__(self, max_retries: int = 3, base_timeout: float = 30.0):
        """
        Initialize the embedder and verify connection.

        Args:
            max_retries: Maximum number of retry attempts
            base_timeout: Base timeout in seconds for API calls
        """
        self.url = get_ollama_url()
        self.model = OLLAMA_MODEL
        self.max_retries = max_retries
        self.base_timeout = base_timeout

        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify Ollama server is reachable and model is available."""
        try:
            # Test with a simple embedding request
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": "test"},
                timeout=10
            )

            if response.status_code == 404:
                raise OllamaModelError(
                    f"Model '{self.model}' not found. "
                    f"Please run: ollama pull {self.model}"
                )

            response.raise_for_status()

            # Verify we get a valid embedding
            data = response.json()
            if "embedding" not in data:
                raise OllamaModelError(
                    f"Invalid response from Ollama: {data}"
                )

        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.url}\n"
                f"Please ensure Ollama is running on the server."
            )
        except requests.exceptions.Timeout:
            raise OllamaConnectionError(
                f"Timeout connecting to Ollama at {self.url}"
            )

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with retry logic.

        Args:
            text: The text to embed

        Returns:
            768-dimensional embedding vector

        Raises:
            RetryExhaustedError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Exponential backoff timeout
                timeout = self.base_timeout * (2 ** attempt)

                response = requests.post(
                    self.url,
                    json={"model": self.model, "prompt": text},
                    timeout=timeout
                )
                response.raise_for_status()

                return response.json()["embedding"]

            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff sleep
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)

            except requests.exceptions.RequestException as e:
                last_error = e
                break

        raise RetryExhaustedError(
            f"Failed to embed text after {self.max_retries} attempts: {last_error}"
        )

    def embed_batch(
        self,
        texts: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            progress_callback: Optional callback(current, total) for progress

        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)

        for i, text in enumerate(texts):
            try:
                embedding = self.embed(text)
                embeddings.append(embedding)
            except RetryExhaustedError as e:
                print(f"Warning: Failed to embed chunk {i+1}/{total}: {e}")
                # Use zero vector as placeholder for failed embeddings
                embeddings.append([0.0] * 768)

            if progress_callback:
                progress_callback(i + 1, total)

        return embeddings
