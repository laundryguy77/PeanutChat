"""Image generation service using Stable Diffusion XL"""
import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

from app.services.gpu_manager import gpu_manager, ModelType

# Get project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class ImageGenerator:
    """Handles image generation using SDXL"""

    def __init__(self):
        self.pipe = None
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        self.output_dir = PROJECT_ROOT / "generated_images"
        self.output_dir.mkdir(exist_ok=True)
        self._loading = False

    async def load_model(self):
        """Load the SDXL model"""
        if self.pipe is not None:
            return

        if self._loading:
            while self._loading:
                await asyncio.sleep(0.5)
            return

        self._loading = True
        try:
            # Register with GPU manager (this also unloads Ollama)
            await gpu_manager.request_model(ModelType.IMAGE)

            # Clear CUDA cache before loading
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            print(f"Loading SDXL model: {self.model_id}")

            # Load in fp16 for efficiency
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16"
            )

            # Use efficient scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )

            # Enable memory optimizations
            self.pipe.enable_model_cpu_offload()

            # Enable VAE slicing for lower memory
            self.pipe.enable_vae_slicing()

            print("SDXL model loaded successfully")

        except Exception as e:
            print(f"Failed to load SDXL: {e}")
            self.pipe = None
            raise
        finally:
            self._loading = False

    def unload_model(self):
        """Unload the model to free VRAM"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            torch.cuda.empty_cache()
            print("SDXL model unloaded")

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate an image from a prompt"""

        try:
            # Load model if needed
            await self.load_model()

            # Set random seed if not provided
            if seed is None:
                seed = torch.randint(0, 2**32 - 1, (1,)).item()

            # Use CPU generator when using cpu_offload - pipeline handles device placement
            generator = torch.Generator(device="cpu").manual_seed(seed)

            # Default negative prompt for better quality
            if negative_prompt is None:
                negative_prompt = (
                    "blurry, bad quality, worst quality, low quality, "
                    "normal quality, lowres, watermark, text, error"
                )

            print(f"Generating image: {prompt[:50]}...")

            # Generate in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            image = await loop.run_in_executor(
                None,
                lambda: self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                ).images[0]
            )

            # Save the image
            image_id = str(uuid.uuid4())[:8]
            filename = f"{image_id}.png"
            filepath = self.output_dir / filename
            image.save(filepath)

            print(f"Image saved: {filepath}")

            return {
                "success": True,
                "image_id": image_id,
                "filename": filename,
                "path": str(filepath),
                "url": f"/generated_images/{filename}",
                "seed": seed,
                "prompt": prompt
            }

        except Exception as e:
            print(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
image_generator = ImageGenerator()
