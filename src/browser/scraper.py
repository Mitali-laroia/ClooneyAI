"""Browser scraping service using Playwright."""

from pathlib import Path

from playwright.async_api import async_playwright

# Viewport configurations for different devices
VIEWPORTS = {
	"mobile": {"width": 375, "height": 812, "device_scale_factor": 2},  # iPhone 12/13
	"tablet": {"width": 768, "height": 1024, "device_scale_factor": 2},  # iPad
	"desktop": {"width": 1920, "height": 1080, "device_scale_factor": 1},  # Desktop
}


async def scrape_page(url: str, screenshot_dir: str = "output/screenshots") -> dict:
	"""Scrape a webpage and extract DOM, CSS, and screenshots.

	Args:
		url: The URL to scrape
		screenshot_dir: Directory to save screenshots

	Returns:
		Dictionary containing scraped data
	"""
	# Create screenshot directory
	screenshot_path = Path(screenshot_dir)
	screenshot_path.mkdir(parents=True, exist_ok=True)

	# Generate base filename from URL
	domain = url.replace("https://", "").replace("http://", "").replace("/", "_")

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		screenshots = {}

		try:
			# Capture screenshots and data for each viewport
			for viewport_name, viewport_config in VIEWPORTS.items():
				page = await browser.new_page(viewport=viewport_config)

				try:
					# Navigate to page
					await page.goto(url, wait_until="domcontentloaded", timeout=60000)
					# Wait for dynamic content
					await page.wait_for_timeout(2000)

					# Take screenshot
					screenshot_file = screenshot_path / f"{domain}_{viewport_name}.png"
					await page.screenshot(path=str(screenshot_file), full_page=True)
					screenshots[viewport_name] = str(screenshot_file)

					# Extract data only once (from desktop viewport for consistency)
					if viewport_name == "desktop":
						# Extract full DOM
						dom = await page.content()

						# Extract simplified/semantic DOM
						dom_simplified = await page.evaluate("""
							() => {
								// Remove scripts, tracking, and non-visual elements
								const clone = document.documentElement.cloneNode(true);

								// Remove unwanted elements
								const unwanted = clone.querySelectorAll(
									'script, noscript, iframe[src*="ads"], ' +
									'[id*="cookie"], [class*="cookie"], ' +
									'[id*="tracking"], [class*="tracking"], ' +
									'[id*="analytics"], [class*="analytics"]'
								);
								unwanted.forEach(el => el.remove());

								return clone.outerHTML;
							}
						""")

						# Extract all CSS
						css_content = await page.evaluate("""
							() => {
								const styles = [];
								// Get inline styles from style tags
								document.querySelectorAll('style').forEach(style => {
									styles.push(style.textContent);
								});
								// Get linked stylesheets
								for (const sheet of document.styleSheets) {
									try {
										for (const rule of sheet.cssRules) {
											styles.push(rule.cssText);
										}
									} catch (e) {
										// CORS blocked stylesheet
										console.log('Could not access stylesheet:', e);
									}
								}
								return styles.join('\\n');
							}
						""")

				finally:
					await page.close()

			return {
				"dom": dom,
				"dom_simplified": dom_simplified,
				"css": css_content,
				"screenshots": screenshots,
			}

		finally:
			await browser.close()
