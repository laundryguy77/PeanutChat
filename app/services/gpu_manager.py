"""GPU Memory Manager - Handles model loading/unloading to manage VRAM"""
import torch
import gc
import requests
from enum import Enum
from typing import Optional
import threading


class ModelType(Enum):
    IMAGE = "image"


class GPUManager:
    """Manages GPU memory by ensuring only one heavy model is loaded at a time"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._current_model: Optional[ModelType] = None
        self._model_refs = {}
        self._unload_callbacks = {}
        self._model_lock = threading.Lock()
        self._ollama_unloaded = False

    def register_model(self, model_type: ModelType, unload_callback):
        """Register a model's unload callback"""
        self._unload_callbacks[model_type] = unload_callback

    def _unload_ollama(self):
        """Tell Ollama to unload all models from GPU"""
        try:
            # Get list of running models
            response = requests.get("http://localhost:11434/api/ps", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])

                for model in models:
                    model_name = model.get("name", "")
                    if model_name:
                        print(f"Unloading Ollama model: {model_name}")
                        # Send request with keep_alive=0 to unload
                        requests.post(
                            "http://localhost:11434/api/generate",
                            json={"model": model_name, "keep_alive": 0},
                            timeout=10
                        )

                self._ollama_unloaded = True
                print("Ollama models unloaded from GPU")

                # Give it a moment to free memory
                import time
                time.sleep(2)

        except Exception as e:
            print(f"Could not unload Ollama models: {e}")

    def _reload_ollama(self):
        """Hint Ollama to reload model (it will reload on next request anyway)"""
        self._ollama_unloaded = False

    def request_gpu(self, model_type: ModelType) -> bool:
        """Request GPU for a model type. Returns True if granted."""
        with self._model_lock:
            if self._current_model == model_type:
                return True

            # Unload current model if different
            if self._current_model is not None:
                self._unload_current()

            self._current_model = model_type
            return True

    def _unload_current(self):
        """Unload the currently loaded model"""
        if self._current_model and self._current_model in self._unload_callbacks:
            try:
                self._unload_callbacks[self._current_model]()
            except Exception as e:
                print(f"Error unloading {self._current_model}: {e}")

        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

    def release_gpu(self, model_type: ModelType):
        """Release GPU claim (model stays loaded but can be evicted)"""
        pass  # For now, models stay loaded until another needs the GPU

    async def request_model(self, model_type: ModelType) -> bool:
        """Async wrapper for request_gpu - also handles Ollama unloading"""
        # Unload Ollama models to free VRAM for image generation
        if model_type == ModelType.IMAGE and not self._ollama_unloaded:
            self._unload_ollama()
        return self.request_gpu(model_type)

    def get_memory_info(self) -> dict:
        """Get current GPU memory usage"""
        if not torch.cuda.is_available():
            return {"available": False}

        return {
            "available": True,
            "allocated_gb": torch.cuda.memory_allocated() / 1024**3,
            "reserved_gb": torch.cuda.memory_reserved() / 1024**3,
            "total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
            "current_model": self._current_model.value if self._current_model else None
        }


# Global instance
gpu_manager = GPUManager()
