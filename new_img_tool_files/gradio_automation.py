#!/usr/bin/env python3
"""
Gradio Space Automation - Base class for automating Hugging Face Gradio spaces

Provides utilities for interacting with common Gradio components used in
image generation interfaces.
"""

import asyncio
import base64
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, List
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class GradioAutomation:
    """Base class for automating Gradio-based Hugging Face Spaces."""
    
    def __init__(
        self,
        space_url: str,
        browser_path: Optional[str] = None,
        headless: bool = True,
        timeout: int = 180000  # 3 minutes default for image gen
    ):
        self.space_url = space_url
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
                "--disable-gpu",
                "--disable-web-security",
            ]
        }
        
        # Find browser
        if self.browser_path:
            launch_args["executable_path"] = self.browser_path
        else:
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
    
    async def new_context(self) -> BrowserContext:
        """Create a new browser context."""
        if not self._browser:
            await self.start()
        return await self._browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080}
        )
    
    async def wait_for_gradio_load(self, page: Page, timeout: int = 60000):
        """Wait for Gradio interface to fully load."""
        await page.wait_for_selector(".gradio-container", timeout=timeout)
        await page.wait_for_timeout(2000)
        try:
            await page.wait_for_selector(".loading", state="hidden", timeout=5000)
        except:
            pass
    
    async def dismiss_popups(self, page: Page):
        """Dismiss any cookie banners or popups."""
        popup_selectors = [
            "button:has-text('Accept')",
            "button:has-text('OK')",
            "button:has-text('Close')",
            "button:has-text('Got it')",
            "button:has-text('I agree')",
            "[aria-label='Close']",
            ".modal button.close",
        ]
        for selector in popup_selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await page.wait_for_timeout(500)
            except:
                pass
            
    async def fill_textbox(self, page: Page, text: str, label: Optional[str] = None, 
                          placeholder: Optional[str] = None, index: int = 0):
        """
        Fill a Gradio textbox component.
        
        Args:
            page: Playwright page
            text: Text to enter
            label: Optional label text to find the right textbox
            placeholder: Optional placeholder text to match
            index: Index if multiple textboxes (0-based)
        """
        if label:
            # Find by label
            label_elem = page.locator(f"label:has-text('{label}'), span:has-text('{label}')").first
            parent = label_elem.locator("xpath=ancestor::*[contains(@class, 'block')]").first
            textbox = parent.locator("textarea, input[type='text']").first
        elif placeholder:
            textbox = page.locator(f"textarea[placeholder*='{placeholder}'], input[placeholder*='{placeholder}']").first
        else:
            # Find by index
            textbox = page.locator(".gradio-textbox textarea, .gradio-textbox input, textarea, input[type='text']").nth(index)
        
        await textbox.click()
        await textbox.fill(text)
        
    async def upload_image(self, page: Page, file_path: str, label: Optional[str] = None, index: int = 0):
        """
        Upload an image to a Gradio image upload component.
        
        Args:
            page: Playwright page
            file_path: Path to image file to upload
            label: Optional label to find the right upload
            index: Index if multiple uploads
        """
        file_path = str(Path(file_path).absolute())
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found: {file_path}")
        
        # Find file input
        if label:
            container = page.locator(f"*:has(> label:has-text('{label}')), *:has(> span:has-text('{label}'))").first
            file_input = container.locator("input[type='file']").first
        else:
            file_input = page.locator("input[type='file'][accept*='image']").nth(index)
            # Fallback to any file input
            if not await file_input.count():
                file_input = page.locator("input[type='file']").nth(index)
        
        await file_input.set_input_files(file_path)
        await page.wait_for_timeout(2000)  # Wait for upload processing
        
    async def set_slider(self, page: Page, value: float, label: Optional[str] = None, index: int = 0):
        """
        Set a Gradio slider value.
        
        Args:
            page: Playwright page
            value: Value to set
            label: Optional label to find the right slider
            index: Index if multiple sliders
        """
        if label:
            container = page.locator(f"*:has(> label:has-text('{label}'))").first
            slider_input = container.locator("input[type='range'], input[type='number']").first
        else:
            slider_input = page.locator("input[type='range']").nth(index)
        
        # Try setting via number input if available
        try:
            number_input = page.locator(f"input[type='number']").nth(index)
            if await number_input.is_visible(timeout=1000):
                await number_input.fill(str(value))
                return
        except:
            pass
        
        # Set range slider
        await slider_input.fill(str(value))
        
    async def select_dropdown(self, page: Page, value: str, label: Optional[str] = None, index: int = 0):
        """
        Select a value from a Gradio dropdown.
        
        Args:
            page: Playwright page
            value: Value to select
            label: Optional label to find the right dropdown
            index: Index if multiple dropdowns
        """
        if label:
            container = page.locator(f"*:has(> label:has-text('{label}'))").first
            dropdown = container.locator("select, [role='listbox'], .dropdown").first
        else:
            dropdown = page.locator("select, [role='listbox']").nth(index)
        
        # Try native select
        try:
            await dropdown.select_option(value=value)
            return
        except:
            pass
        
        # Try Gradio custom dropdown
        try:
            await dropdown.click()
            await page.wait_for_timeout(300)
            option = page.locator(f"[role='option']:has-text('{value}'), .dropdown-item:has-text('{value}')").first
            await option.click()
        except:
            pass
        
    async def click_button(self, page: Page, text: Optional[str] = None, index: int = 0):
        """
        Click a Gradio button.
        
        Args:
            page: Playwright page
            text: Button text to match
            index: Button index if no text specified
        """
        if text:
            button = page.locator(f"button:has-text('{text}')").first
        else:
            button = page.locator("button.primary, button.lg, button[type='submit']").nth(index)
        
        await button.click()
        
    async def wait_for_generation(self, page: Page, timeout: Optional[int] = None):
        """
        Wait for image generation to complete.
        Watches for loading indicators to appear and then disappear.
        """
        timeout = timeout or self.timeout
        
        # Wait for processing to start
        try:
            await page.wait_for_selector(
                ".generating, .loading, .progress, [class*='loading'], [class*='progress'], .eta-bar",
                timeout=10000
            )
        except:
            pass
        
        # Wait for processing to complete
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            loading = await page.query_selector(
                ".generating, .loading:not(.hidden), .progress:not([style*='display: none']), .eta-bar"
            )
            if not loading:
                await page.wait_for_timeout(1500)
                loading = await page.query_selector(".generating, .loading:not(.hidden)")
                if not loading:
                    break
            await page.wait_for_timeout(1000)
        else:
            raise TimeoutError(f"Generation did not complete within {timeout}ms")
            
    async def get_output_image(self, page: Page, index: int = 0) -> Optional[bytes]:
        """
        Get the generated image data from the output component.
        
        Args:
            page: Playwright page
            index: Index if multiple output images
            
        Returns:
            Image bytes or None if not found
        """
        # Try various selectors for image output
        selectors = [
            ".output-image img",
            ".gradio-image img",
            ".image-container img",
            "[data-testid='image'] img",
            ".gallery img",
            "#output img",
            ".output img",
            "img[src*='blob:']",
            "img[src*='data:']",
            "img[src*='file=']",
        ]
        
        for selector in selectors:
            try:
                images = page.locator(selector)
                count = await images.count()
                if count > index:
                    img = images.nth(index)
                    if await img.is_visible(timeout=1000):
                        src = await img.get_attribute("src")
                        if src:
                            return await self._fetch_image_data(page, src)
            except:
                continue
        
        return None
    
    async def _fetch_image_data(self, page: Page, src: str) -> Optional[bytes]:
        """Fetch image data from various source types."""
        try:
            if src.startswith("data:"):
                # Data URL
                b64_data = src.split(",", 1)[1]
                return base64.b64decode(b64_data)
                
            elif src.startswith("blob:"):
                # Blob URL - convert via canvas
                b64_data = await page.evaluate('''async (src) => {
                    const img = document.querySelector(`img[src="${src}"]`);
                    if (!img) return null;
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    return canvas.toDataURL('image/png').split(',')[1];
                }''', src)
                if b64_data:
                    return base64.b64decode(b64_data)
                    
            else:
                # Regular URL
                if src.startswith("/"):
                    parsed = urlparse(page.url)
                    src = f"{parsed.scheme}://{parsed.netloc}{src}"
                response = await page.request.get(src)
                return await response.body()
                
        except Exception as e:
            print(f"Error fetching image: {e}")
            return None
            
    async def get_all_output_images(self, page: Page) -> List[bytes]:
        """Get all output images from a gallery or multiple outputs."""
        images = []
        
        # Try gallery first
        gallery_imgs = page.locator(".gallery img, .grid img, [role='group'] img")
        count = await gallery_imgs.count()
        
        if count > 0:
            for i in range(count):
                try:
                    img = gallery_imgs.nth(i)
                    if await img.is_visible(timeout=500):
                        src = await img.get_attribute("src")
                        if src:
                            data = await self._fetch_image_data(page, src)
                            if data:
                                images.append(data)
                except:
                    continue
        
        # Fallback to single image
        if not images:
            single = await self.get_output_image(page)
            if single:
                images.append(single)
                
        return images
    
    async def save_image(self, image_data: bytes, output_path: str) -> dict:
        """Save image data to file."""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(image_data)
            return {
                "success": True,
                "path": str(path.absolute()),
                "size_bytes": len(image_data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def click_download_button(self, page: Page, output_path: str) -> dict:
        """Try to download via the download button."""
        try:
            async with page.expect_download(timeout=10000) as download_info:
                download_btn = page.locator(
                    "button:has-text('Download'), a:has-text('Download'), [download], "
                    "button[title*='download'], a[title*='download']"
                ).first
                await download_btn.click()
            download = await download_info.value
            await download.save_as(output_path)
            return {
                "success": True,
                "path": str(Path(output_path).absolute()),
                "size_bytes": Path(output_path).stat().st_size
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
