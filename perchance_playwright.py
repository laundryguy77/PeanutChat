#!/usr/bin/env python3
"""
Perchance Image Generator - Direct Playwright Implementation

A custom implementation that directly controls the Perchance web interface
using Playwright. Works with the browser already installed.
"""

import asyncio
import base64
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page


class PerchanceGenerator:
    """Generate images using Perchance AI via Playwright browser automation."""
    
    GENERATOR_URL = "https://perchance.org/ai-text-to-image-generator"
    # Alternative URLs that might work:
    # "https://perchance.org/free-text-to-image-unfiltered"
    # "https://perchance.org/ai-photo-generator"
    
    def __init__(
        self,
        browser_path: Optional[str] = None,
        headless: bool = True,
        timeout: int = 120000  # 2 minutes
    ):
        self.browser_path = browser_path
        self.headless = headless
        self.timeout = timeout
        self._playwright = None
        self._browser: Optional[Browser] = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, *args):
        await self.close()
        
    async def start(self):
        """Start the browser."""
        self._playwright = await async_playwright().start()
        
        launch_args = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        }
        
        # Try to find and use existing browser
        if self.browser_path:
            launch_args["executable_path"] = self.browser_path
        else:
            # Check for browsers in common locations
            browser_paths = [
                "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                "/opt/pw-browsers/chromium-1200/chrome-linux/chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/bin/google-chrome",
            ]
            for path in browser_paths:
                if os.path.exists(path):
                    launch_args["executable_path"] = path
                    break
        
        self._browser = await self._playwright.chromium.launch(**launch_args)
        
    async def close(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
            
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        shape: str = "square",  # square, portrait, landscape
        style: str = "",
        seed: Optional[int] = None,
        output_path: Optional[str] = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: The text description of the image
            negative_prompt: Things to avoid in the image
            shape: Aspect ratio - "square", "portrait", or "landscape"
            style: Art style to include in the prompt
            seed: Random seed for reproducibility (optional)
            output_path: Path to save the image
            return_base64: Return base64 data instead of saving
            
        Returns:
            dict with success status and image data/path
        """
        if not self._browser:
            await self.start()
            
        context = await self._browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        
        try:
            # Navigate to the generator
            print(f"Loading Perchance...")
            await page.goto(self.GENERATOR_URL, wait_until="networkidle")
            
            # Wait for the page to fully load
            await page.wait_for_timeout(2000)
            
            # Handle any cookie/consent dialogs
            try:
                consent_button = page.locator("text=Accept").first
                if await consent_button.is_visible(timeout=2000):
                    await consent_button.click()
            except:
                pass
            
            # Build the full prompt
            full_prompt = f"{style}, {prompt}" if style else prompt
            
            # Find and fill the prompt input
            # The Perchance text-to-image generators typically have a textarea
            prompt_selectors = [
                'textarea[placeholder*="prompt"]',
                'textarea[placeholder*="describe"]',
                '#prompt',
                'textarea.prompt',
                'textarea[name="prompt"]',
                'textarea',  # Fallback
            ]
            
            prompt_input = None
            for selector in prompt_selectors:
                try:
                    elem = page.locator(selector).first
                    if await elem.is_visible(timeout=1000):
                        prompt_input = elem
                        break
                except:
                    continue
            
            if not prompt_input:
                raise Exception("Could not find prompt input field")
            
            # Clear and fill the prompt
            await prompt_input.click()
            await prompt_input.fill(full_prompt)
            
            # Handle negative prompt if the field exists
            if negative_prompt:
                try:
                    neg_selectors = [
                        'textarea[placeholder*="negative"]',
                        '#negative-prompt',
                        'textarea.negative',
                        'textarea[name="negative"]',
                    ]
                    for selector in neg_selectors:
                        neg_input = page.locator(selector).first
                        if await neg_input.is_visible(timeout=500):
                            await neg_input.fill(negative_prompt)
                            break
                except:
                    pass  # Negative prompt field not found, skip
            
            # Set shape/aspect ratio if available
            try:
                shape_map = {
                    "square": ["square", "1:1", "1024x1024"],
                    "portrait": ["portrait", "2:3", "768x1024"],
                    "landscape": ["landscape", "3:2", "1024x768"],
                }
                for option in shape_map.get(shape, []):
                    selector = f'[value="{option}"], [data-value="{option}"], button:has-text("{option}")'
                    shape_btn = page.locator(selector).first
                    if await shape_btn.is_visible(timeout=500):
                        await shape_btn.click()
                        break
            except:
                pass  # Shape selection not available
            
            # Find and click the generate button
            generate_selectors = [
                'button:has-text("Generate")',
                'button:has-text("Create")',
                'button.generate',
                '#generate',
                'button[type="submit"]',
            ]
            
            generate_btn = None
            for selector in generate_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=1000):
                        generate_btn = btn
                        break
                except:
                    continue
                    
            if not generate_btn:
                raise Exception("Could not find generate button")
            
            print(f"Generating image...")
            await generate_btn.click()
            
            # Wait for the image to be generated
            # Look for an image element that appears after generation
            image_selectors = [
                'img.generated',
                'img[src*="blob:"]',
                'img[src*="data:"]',
                '.output img',
                '.result img',
                '#output img',
                '.image-container img',
            ]
            
            image_elem = None
            for _ in range(60):  # Wait up to 60 seconds
                for selector in image_selectors:
                    try:
                        img = page.locator(selector).first
                        if await img.is_visible(timeout=1000):
                            src = await img.get_attribute("src")
                            if src and (src.startswith("blob:") or src.startswith("data:") or "perchance" in src):
                                image_elem = img
                                break
                    except:
                        continue
                if image_elem:
                    break
                await page.wait_for_timeout(1000)
            
            if not image_elem:
                # Try alternative: take screenshot of the result area
                raise Exception("Image generation timed out or image not found")
            
            # Get the image data
            src = await image_elem.get_attribute("src")
            
            if src.startswith("data:"):
                # Data URL - extract base64
                b64_data = src.split(",", 1)[1]
                image_bytes = base64.b64decode(b64_data)
            elif src.startswith("blob:"):
                # Blob URL - need to convert via canvas
                image_bytes = await page.evaluate('''async (img) => {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
                    return dataUrl.split(',')[1];
                }''', await image_elem.element_handle())
                image_bytes = base64.b64decode(image_bytes)
            else:
                # Regular URL - fetch it
                response = await page.request.get(src)
                image_bytes = await response.body()
            
            # Handle output
            if return_base64:
                return {
                    "success": True,
                    "base64": base64.b64encode(image_bytes).decode('utf-8'),
                    "size_bytes": len(image_bytes),
                    "mime_type": "image/jpeg"
                }
            
            # Save to file
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_prompt = re.sub(r'[^\w]', '_', prompt[:30])
                output_path = f"perchance_{safe_prompt}_{timestamp}.jpg"
            
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(image_bytes)
            
            return {
                "success": True,
                "path": str(path.absolute()),
                "size_bytes": len(image_bytes)
            }
            
        except Exception as e:
            # Take a debug screenshot on error
            try:
                await page.screenshot(path="/tmp/perchance_error.png")
            except:
                pass
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await context.close()


async def main():
    """Test the generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate images with Perchance")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-n", "--negative", default="", help="Negative prompt")
    parser.add_argument("-s", "--shape", choices=["square", "portrait", "landscape"], default="square")
    parser.add_argument("--style", default="", help="Art style prefix")
    parser.add_argument("--browser", help="Path to browser executable")
    parser.add_argument("--base64", action="store_true", help="Output base64 instead of saving")
    
    args = parser.parse_args()
    
    async with PerchanceGenerator(browser_path=args.browser) as gen:
        result = await gen.generate(
            prompt=args.prompt,
            negative_prompt=args.negative,
            shape=args.shape,
            style=args.style,
            output_path=args.output,
            return_base64=args.base64
        )
    
    if result["success"]:
        if args.base64:
            print(result["base64"])
        else:
            print(f"✓ Image saved to: {result['path']}")
            print(f"  Size: {result['size_bytes']:,} bytes")
    else:
        print(f"✗ Error: {result['error']}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
