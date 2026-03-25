import asyncio
from playwright.async_api import async_playwright

class BrowserTools:
    """
    Browser automation tools using Playwright.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start_browser(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def stop_browser(self):
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

    async def get_page_content(self):
        if not self.page:
            return "Error: Browser not started"
        return await self.page.content()
