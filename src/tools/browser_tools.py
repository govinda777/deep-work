import asyncio
import os
import json
from playwright.async_api import async_playwright

class BrowserTools:
    """
    Browser automation tools using Playwright.
    """
    def __init__(self, session_file="session_state.json"):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_file = session_file

    async def start_browser(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)

        # Load session state if it exists
        storage_state = None
        if os.path.exists(self.session_file):
            print(f"Loading session state from {self.session_file}")
            storage_state = self.session_file

        self.context = await self.browser.new_context(
            viewport={'width': 1024, 'height': 768},
            storage_state=storage_state
        )
        self.page = await self.context.new_page()

    async def stop_browser(self):
        # Save session state before closing
        if self.context:
            print(f"Saving session state to {self.session_file}")
            await self.context.storage_state(path=self.session_file)

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str):
        if not self.page:
            await self.start_browser()
        await self.page.goto(url, wait_until="networkidle")
        return f"Navigated to {url}"

    async def click_element(self, selector: str):
        if not self.page:
            return "Error: Browser not started"
        await self.page.click(selector)
        await self.page.wait_for_load_state("networkidle")
        return f"Clicked element {selector}"

    async def input_text(self, selector: str, text: str):
        if not self.page:
            return "Error: Browser not started"
        await self.page.fill(selector, text)
        await self.page.wait_for_load_state("networkidle")
        return f"Entered text into {selector}"

    async def take_screenshot(self, path="screenshot.png"):
        if not self.page:
            return "Error: Browser not started"
        await self.page.screenshot(path=path)
        return f"Screenshot saved to {path}"

    async def get_screenshot_base64(self):
        if not self.page:
            return None
        import base64
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode('utf-8')

    async def hover(self, selector: str):
        if not self.page:
            return "Error: Browser not started"
        await self.page.hover(selector)
        return f"Hovered over element {selector}"

    async def double_click(self, selector: str):
        if not self.page:
            return "Error: Browser not started"
        await self.page.dblclick(selector)
        await self.page.wait_for_load_state("networkidle")
        return f"Double-clicked element {selector}"

    async def scroll(self, direction: str = "down", amount: int = 500):
        if not self.page:
            return "Error: Browser not started"
        if direction == "down":
            await self.page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            await self.page.evaluate(f"window.scrollBy(0, -{amount})")
        return f"Scrolled {direction} by {amount} pixels"

    async def get_page_content(self):
        if not self.page:
            return "Error: Browser not started"
        return await self.page.content()

    async def get_page_summary(self):
        """
        Extracts a clean, text-based representation of the page,
        filtering for interactive and meaningful elements.
        """
        if not self.page:
            return "Error: Browser not started"

        # Simple extraction script to get text and interactive elements
        summary_script = """
        () => {
            const items = [];
            const walk = (node) => {
                if (node.nodeType === Node.TEXT_NODE) {
                    const text = node.textContent.trim();
                    if (text) items.push(text);
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    const style = window.getComputedStyle(node);
                    if (style.display === 'none' || style.visibility === 'hidden') return;

                    const tagName = node.tagName.toLowerCase();
                    const isInteractive = ['a', 'button', 'input', 'select', 'textarea'].includes(tagName) ||
                                          node.hasAttribute('onclick') ||
                                          node.getAttribute('role') === 'button';

                    if (isInteractive) {
                        const label = node.innerText || node.value || node.placeholder || node.getAttribute('aria-label') || '';
                        items.push(`[${tagName.toUpperCase()}: ${label.trim()}]`);
                    }

                    for (let child of node.childNodes) {
                        walk(child);
                    }
                }
            };
            walk(document.body);
            return items.join('\\n');
        }
        """
        return await self.page.evaluate(summary_script)
