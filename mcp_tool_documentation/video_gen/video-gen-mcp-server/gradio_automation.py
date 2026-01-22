#!/usr/bin/env python3
"""
Gradio Space Automation - Base class for automating Hugging Face Gradio spaces

Gradio has a relatively consistent DOM structure which makes automation easier
than arbitrary websites. This module provides utilities for interacting with
common Gradio components.
"""

import asyncio
import base64
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class GradioAutomation:
    """Base class for automating Gradio-based Hugging Face Spaces."""
    
    def __init__(
        self,
        space_url: str,
        browser_path: Optional[str] = None,
        headless: bool = True,
        timeout: int = 480000  # 8 minutes default for video gen (increased for multiple model calls)
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
                "--disable-web-security",  # May help with some spaces
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
    
    async def wait_for_gradio_load(self, page: Page, timeout: int = 120000):
        """Wait for Gradio interface to fully load."""
        # Wait for the Gradio app container
        await page.wait_for_selector(".gradio-container", timeout=timeout)
        # Wait for any loading spinners to disappear
        await page.wait_for_timeout(3000)
        try:
            await page.wait_for_selector(".loading", state="hidden", timeout=10000)
        except:
            pass
            
    async def fill_textbox(self, page: Page, text: str, label: Optional[str] = None, index: int = 0):
        """
        Fill a Gradio textbox component.
        
        Args:
            page: Playwright page
            text: Text to enter
            label: Optional label text to find the right textbox
            index: Index if multiple textboxes (0-based)
        """
        if label:
            # Find by label
            label_elem = page.locator(f"label:has-text('{label}'), span:has-text('{label}')").first
            parent = label_elem.locator("xpath=ancestor::*[contains(@class, 'block')]").first
            textbox = parent.locator("textarea, input[type='text']").first
        else:
            # Find by index
            textbox = page.locator(".gradio-textbox textarea, .gradio-textbox input").nth(index)
        
        await textbox.click()
        await textbox.fill(text)
        
    async def upload_file(self, page: Page, file_path: str, label: Optional[str] = None, index: int = 0):
        """
        Upload a file to a Gradio file/image upload component.
        
        Args:
            page: Playwright page
            file_path: Path to file to upload
            label: Optional label to find the right upload
            index: Index if multiple uploads
        """
        file_path = str(Path(file_path).absolute())
        
        if label:
            # Find upload area by label
            container = page.locator(f"*:has(> label:has-text('{label}')), *:has(> span:has-text('{label}'))").first
            file_input = container.locator("input[type='file']").first
        else:
            # Find by index
            file_input = page.locator("input[type='file']").nth(index)
        
        await file_input.set_input_files(file_path)
        # Wait for upload to complete
        await page.wait_for_timeout(4000)
        
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
            # Usually the primary/submit button
            button = page.locator("button.primary, button[type='submit'], button.lg").nth(index)
        
        await button.click()
        
    async def wait_for_generation(self, page: Page, timeout: Optional[int] = None):
        """
        Wait for generation to complete.
        Watches for loading indicators to appear and then disappear.
        """
        timeout = timeout or self.timeout

        # Wait for processing to start (loading indicator appears)
        try:
            await page.wait_for_selector(
                ".generating, .loading, .progress, [class*='loading'], [class*='progress']",
                timeout=20000
            )
        except:
            pass  # May have already started

        # Wait for processing to complete
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            # Check if still loading
            loading = await page.query_selector(
                ".generating, .loading:not(.hidden), .progress:not([style*='display: none'])"
            )
            if not loading:
                # Double-check by waiting a moment
                await page.wait_for_timeout(4000)
                loading = await page.query_selector(".generating, .loading:not(.hidden)")
                if not loading:
                    break
            await page.wait_for_timeout(3000)
        else:
            raise TimeoutError(f"Generation did not complete within {timeout}ms")
            
    async def get_output_video_url(self, page: Page) -> Optional[str]:
        """
        Get the URL of the generated video from the output component.
        Returns the video source URL or None if not found.
        """
        # Try various selectors for video output
        selectors = [
            "video source",
            "video[src]",
            ".output-video video",
            ".gradio-video video",
            "[data-testid='video'] video",
            "a[download][href*='.mp4']",
            "a[download][href*='file=']",
        ]
        
        for selector in selectors:
            try:
                elem = page.locator(selector).first
                if await elem.is_visible(timeout=5000):
                    # Try src attribute
                    src = await elem.get_attribute("src")
                    if src:
                        return src
                    # Try href for download links
                    href = await elem.get_attribute("href")
                    if href:
                        return href
            except:
                continue

        return None
        
    async def download_output(self, page: Page, output_path: str) -> dict:
        """
        Download the output video/file.
        
        Args:
            page: Playwright page
            output_path: Where to save the file
            
        Returns:
            dict with success status and path/error
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Method 1: Get video source URL and download
        video_url = await self.get_output_video_url(page)
        if video_url:
            try:
                # Handle blob URLs
                if video_url.startswith("blob:"):
                    # Need to convert blob to data
                    video_data = await page.evaluate('''async (videoSelector) => {
                        const video = document.querySelector(videoSelector);
                        if (!video) return null;
                        const response = await fetch(video.src);
                        const blob = await response.blob();
                        return new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result.split(',')[1]);
                            reader.readAsDataURL(blob);
                        });
                    }''', "video")
                    if video_data:
                        output_path.write_bytes(base64.b64decode(video_data))
                        return {"success": True, "path": str(output_path.absolute())}
                        
                # Handle data URLs
                elif video_url.startswith("data:"):
                    b64_data = video_url.split(",", 1)[1]
                    output_path.write_bytes(base64.b64decode(b64_data))
                    return {"success": True, "path": str(output_path.absolute())}
                    
                # Handle regular URLs
                else:
                    # Make URL absolute if needed
                    if video_url.startswith("/"):
                        parsed = urlparse(page.url)
                        video_url = f"{parsed.scheme}://{parsed.netloc}{video_url}"
                    
                    response = await page.request.get(video_url)
                    output_path.write_bytes(await response.body())
                    return {"success": True, "path": str(output_path.absolute())}
                    
            except Exception as e:
                return {"success": False, "error": f"Failed to download video: {e}"}
        
        # Method 2: Try clicking download button
        try:
            async with page.expect_download(timeout=30000) as download_info:
                download_btn = page.locator("button:has-text('Download'), a:has-text('Download'), [download]").first
                await download_btn.click()
            download = await download_info.value
            await download.save_as(str(output_path))
            return {"success": True, "path": str(output_path.absolute())}
        except:
            pass

        return {"success": False, "error": "Could not find or download output video"}
