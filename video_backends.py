#!/usr/bin/env python3
"""
Video Generation Backends

Implements specific video generation workflows for different Hugging Face Spaces.
Each backend handles a specific space's UI and workflow.
"""

import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

from gradio_automation import GradioAutomation


class VideoGeneratorBackend(ABC):
    """Abstract base class for video generation backends."""
    
    name: str = "base"
    supports_text_to_video: bool = False
    supports_image_to_video: bool = False
    
    @abstractmethod
    async def generate(self, **kwargs) -> dict:
        """Generate video. Implementation varies by backend."""
        pass


class HuggingFaceImageToVideo(GradioAutomation, VideoGeneratorBackend):
    """
    Image-to-Video generation using Hugging Face Spaces.
    
    Primary: Heartsync/NSFW-Uncensored-video
    Fallback: Other image-to-video spaces
    """
    
    name = "huggingface_img2vid"
    supports_text_to_video = False
    supports_image_to_video = True
    
    # Space URLs to try in order
    SPACE_URLS = [
        "https://huggingface.co/spaces/Heartsync/NSFW-Uncensored-video",
        "https://huggingface.co/spaces/Justforailolomg/NSFW-Uncensored-video-duplicate",
    ]
    
    def __init__(self, space_url: Optional[str] = None, **kwargs):
        super().__init__(
            space_url=space_url or self.SPACE_URLS[0],
            **kwargs
        )
        
    async def generate(
        self,
        image_path: str,
        prompt: str = "",
        negative_prompt: str = "",
        duration: float = 3.0,
        output_path: Optional[str] = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate video from an image.
        
        Args:
            image_path: Path to the source image
            prompt: Motion/action prompt describing what should happen
            negative_prompt: Things to avoid
            duration: Video duration in seconds (if supported)
            output_path: Where to save the video
            return_base64: Return base64 data instead of saving
            
        Returns:
            dict with success status and path/base64/error
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image not found: {image_path}"}
        
        context = await self.new_context()
        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        
        try:
            print(f"Loading space: {self.space_url}")
            await page.goto(self.space_url, wait_until="networkidle")
            await self.wait_for_gradio_load(page)
            
            # Handle any popups/modals
            await self._dismiss_popups(page)
            
            # Upload the image
            print("Uploading image...")
            await self.upload_file(page, image_path, index=0)
            await page.wait_for_timeout(2000)
            
            # Fill in prompts if the space supports them
            if prompt:
                try:
                    await self.fill_textbox(page, prompt, index=0)
                except:
                    pass  # Prompt field may not exist
                    
            if negative_prompt:
                try:
                    await self.fill_textbox(page, negative_prompt, label="negative")
                except:
                    pass
            
            # Click generate button
            print("Starting generation...")
            await self.click_button(page, text="Generate")
            
            # Wait for generation
            print("Waiting for video generation (this may take several minutes)...")
            await self.wait_for_generation(page, timeout=self.timeout)
            
            # Generate output path if not provided
            if output_path is None and not return_base64:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"video_img2vid_{timestamp}.mp4"
            
            if return_base64:
                # TODO: Implement base64 return for video
                output_path = f"/tmp/video_temp_{datetime.now().timestamp()}.mp4"
                result = await self.download_output(page, output_path)
                if result["success"]:
                    import base64
                    video_bytes = Path(output_path).read_bytes()
                    os.remove(output_path)
                    return {
                        "success": True,
                        "base64": base64.b64encode(video_bytes).decode('utf-8'),
                        "size_bytes": len(video_bytes),
                        "mime_type": "video/mp4"
                    }
                return result
            else:
                return await self.download_output(page, output_path)
                
        except Exception as e:
            # Take debug screenshot
            try:
                await page.screenshot(path="/tmp/video_gen_error.png")
            except:
                pass
            return {"success": False, "error": str(e)}
            
        finally:
            await context.close()
            
    async def _dismiss_popups(self, page):
        """Dismiss any cookie banners or popups."""
        popup_selectors = [
            "button:has-text('Accept')",
            "button:has-text('OK')",
            "button:has-text('Close')",
            "button:has-text('Got it')",
            "[aria-label='Close']",
        ]
        for selector in popup_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await page.wait_for_timeout(500)
            except:
                pass


class HuggingFaceTextToVideo(GradioAutomation, VideoGeneratorBackend):
    """
    Text-to-Video generation using Hugging Face Spaces.
    
    Uses spaces running models like LTX-Video, Wan, etc.
    """
    
    name = "huggingface_txt2vid"
    supports_text_to_video = True
    supports_image_to_video = False
    
    # Space URLs to try - these run various T2V models
    SPACE_URLS = [
        "https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled",
        "https://huggingface.co/spaces/Wan-AI/Wan2.1-T2V-1.3B",
        "https://huggingface.co/spaces/multimodalart/LTX-Video",
    ]
    
    def __init__(self, space_url: Optional[str] = None, **kwargs):
        super().__init__(
            space_url=space_url or self.SPACE_URLS[0],
            **kwargs
        )
        
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        duration: float = 3.0,
        width: int = 512,
        height: int = 512,
        output_path: Optional[str] = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description of the video to generate
            negative_prompt: Things to avoid
            duration: Video duration in seconds (if supported)
            width: Video width (if supported)
            height: Video height (if supported)
            output_path: Where to save the video
            return_base64: Return base64 data instead of saving
            
        Returns:
            dict with success status and path/base64/error
        """
        context = await self.new_context()
        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        
        try:
            print(f"Loading space: {self.space_url}")
            await page.goto(self.space_url, wait_until="networkidle")
            await self.wait_for_gradio_load(page)
            
            # Handle any popups
            await self._dismiss_popups(page)
            
            # Fill in the prompt
            print("Entering prompt...")
            await self.fill_textbox(page, prompt, index=0)
            
            # Try to fill negative prompt
            if negative_prompt:
                try:
                    # Try various ways to find negative prompt field
                    neg_selectors = [
                        "textarea[placeholder*='negative']",
                        "textarea[placeholder*='Negative']",
                        "input[placeholder*='negative']",
                    ]
                    for selector in neg_selectors:
                        elem = page.locator(selector).first
                        if await elem.is_visible(timeout=1000):
                            await elem.fill(negative_prompt)
                            break
                except:
                    pass
            
            # Try to set duration/dimensions if available
            # (These vary widely between spaces)
            
            # Click generate button
            print("Starting generation...")
            generate_buttons = [
                "button:has-text('Generate')",
                "button:has-text('Create')",
                "button:has-text('Run')",
                "button:has-text('Submit')",
                "button.primary",
            ]
            for btn_selector in generate_buttons:
                try:
                    btn = page.locator(btn_selector).first
                    if await btn.is_visible(timeout=1000):
                        await btn.click()
                        break
                except:
                    continue
            
            # Wait for generation
            print("Waiting for video generation (this may take several minutes)...")
            await self.wait_for_generation(page, timeout=self.timeout)
            
            # Generate output path if not provided
            if output_path is None and not return_base64:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_prompt = re.sub(r'[^\w]', '_', prompt[:30])
                output_path = f"video_txt2vid_{safe_prompt}_{timestamp}.mp4"
            
            if return_base64:
                output_path = f"/tmp/video_temp_{datetime.now().timestamp()}.mp4"
                result = await self.download_output(page, output_path)
                if result["success"]:
                    import base64
                    video_bytes = Path(output_path).read_bytes()
                    os.remove(output_path)
                    return {
                        "success": True,
                        "base64": base64.b64encode(video_bytes).decode('utf-8'),
                        "size_bytes": len(video_bytes),
                        "mime_type": "video/mp4"
                    }
                return result
            else:
                return await self.download_output(page, output_path)
                
        except Exception as e:
            try:
                await page.screenshot(path="/tmp/video_gen_error.png")
            except:
                pass
            return {"success": False, "error": str(e)}
            
        finally:
            await context.close()
            
    async def _dismiss_popups(self, page):
        """Dismiss any cookie banners or popups."""
        popup_selectors = [
            "button:has-text('Accept')",
            "button:has-text('OK')",
            "button:has-text('Close')",
            "button:has-text('Got it')",
            "[aria-label='Close']",
        ]
        for selector in popup_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await page.wait_for_timeout(500)
            except:
                pass


class VideoGenerator:
    """
    Unified video generator that supports both text-to-video and image-to-video.
    Automatically selects the appropriate backend based on the input type.
    """
    
    def __init__(
        self,
        text_to_video_url: Optional[str] = None,
        image_to_video_url: Optional[str] = None,
        headless: bool = True,
        timeout: int = 300000
    ):
        self.headless = headless
        self.timeout = timeout
        
        # Initialize backends
        self._txt2vid = HuggingFaceTextToVideo(
            space_url=text_to_video_url,
            headless=headless,
            timeout=timeout
        )
        self._img2vid = HuggingFaceImageToVideo(
            space_url=image_to_video_url,
            headless=headless,
            timeout=timeout
        )
        
    async def start(self):
        """Start both backends."""
        await self._txt2vid.start()
        await self._img2vid.start()
        
    async def close(self):
        """Close both backends."""
        await self._txt2vid.close()
        await self._img2vid.close()
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, *args):
        await self.close()
        
    async def text_to_video(
        self,
        prompt: str,
        negative_prompt: str = "",
        duration: float = 3.0,
        output_path: Optional[str] = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description of the video
            negative_prompt: Things to avoid
            duration: Video duration in seconds
            output_path: Where to save (auto-generated if None)
            return_base64: Return base64 instead of saving
            
        Returns:
            dict with success, path/base64, size_bytes, error
        """
        return await self._txt2vid.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            output_path=output_path,
            return_base64=return_base64
        )
        
    async def image_to_video(
        self,
        image_path: str,
        prompt: str = "",
        negative_prompt: str = "",
        duration: float = 3.0,
        output_path: Optional[str] = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate video from an image.
        
        Args:
            image_path: Path to source image
            prompt: Motion/action description
            negative_prompt: Things to avoid
            duration: Video duration in seconds
            output_path: Where to save (auto-generated if None)
            return_base64: Return base64 instead of saving
            
        Returns:
            dict with success, path/base64, size_bytes, error
        """
        return await self._img2vid.generate(
            image_path=image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            output_path=output_path,
            return_base64=return_base64
        )


# CLI for testing
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate videos with AI")
    subparsers = parser.add_subparsers(dest="command", help="Generation mode")
    
    # Text to video
    txt_parser = subparsers.add_parser("text", help="Text to video generation")
    txt_parser.add_argument("prompt", help="Text prompt describing the video")
    txt_parser.add_argument("-o", "--output", help="Output file path")
    txt_parser.add_argument("-n", "--negative", default="", help="Negative prompt")
    txt_parser.add_argument("--duration", type=float, default=3.0, help="Duration in seconds")
    
    # Image to video
    img_parser = subparsers.add_parser("image", help="Image to video generation")
    img_parser.add_argument("image", help="Path to source image")
    img_parser.add_argument("-p", "--prompt", default="", help="Motion prompt")
    img_parser.add_argument("-o", "--output", help="Output file path")
    img_parser.add_argument("-n", "--negative", default="", help="Negative prompt")
    img_parser.add_argument("--duration", type=float, default=3.0, help="Duration in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    async with VideoGenerator() as gen:
        if args.command == "text":
            result = await gen.text_to_video(
                prompt=args.prompt,
                negative_prompt=args.negative,
                duration=args.duration,
                output_path=args.output
            )
        else:  # image
            result = await gen.image_to_video(
                image_path=args.image,
                prompt=args.prompt,
                negative_prompt=args.negative,
                duration=args.duration,
                output_path=args.output
            )
    
    if result.get("success"):
        print(f"✓ Video saved to: {result.get('path')}")
        if "size_bytes" in result:
            print(f"  Size: {result['size_bytes']:,} bytes")
        return 0
    else:
        print(f"✗ Error: {result.get('error')}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
