import { test, expect } from '@playwright/test';

test.describe('IntelliLog Tool Extended Debug', () => {
  test('wait for dynamic content and find elements', async ({ page }) => {
    test.setTimeout(120000);
    
    console.log('Navigating to IntelliLog Tool...');
    await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Wait longer for Streamlit to fully initialize
    console.log('Waiting 15 seconds for Streamlit app to fully load...');
    await page.waitForTimeout(15000);
    
    console.log('Taking screenshot after extended wait...');
    await page.screenshot({ path: 'downloads/debug-after-wait.png', fullPage: true });
    
    // Check for Streamlit-specific elements that indicate the app has loaded
    console.log('Looking for Streamlit app elements...');
    const streamlitElements = await page.locator('[data-testid*="stApp"], [class*="stApp"], .stApp').all();
    console.log(`Found ${streamlitElements.length} Streamlit app elements`);
    
    // Look for any interactive elements
    console.log('Looking for all interactive elements...');
    const allInputs = await page.locator('input, button, [role="button"], [type="file"]').all();
    console.log(`Found ${allInputs.length} interactive elements after wait`);
    
    for (let i = 0; i < allInputs.length; i++) {
      try {
        const element = allInputs[i];
        const tagName = await element.evaluate(el => el.tagName);
        const type = await element.getAttribute('type');
        const role = await element.getAttribute('role');
        const text = await element.textContent();
        const isVisible = await element.isVisible();
        console.log(`Interactive ${i}: tag="${tagName}", type="${type}", role="${role}", text="${text?.substring(0, 50)}", visible=${isVisible}`);
      } catch (e) {
        console.log(`Interactive ${i}: Error - ${e.message}`);
      }
    }
    
    // Look for any clickable elements that might be the file upload
    console.log('Looking for clickable elements with file-related text...');
    const clickableElements = await page.locator('div, span, p, label').filter({ hasText: /browse|file|upload|choose/i }).all();
    console.log(`Found ${clickableElements.length} clickable elements with file-related text`);
    
    for (let i = 0; i < clickableElements.length; i++) {
      try {
        const element = clickableElements[i];
        const tagName = await element.evaluate(el => el.tagName);
        const text = await element.textContent();
        const isVisible = await element.isVisible();
        console.log(`File-related ${i}: tag="${tagName}", text="${text?.substring(0, 100)}", visible=${isVisible}`);
      } catch (e) {
        console.log(`File-related ${i}: Error - ${e.message}`);
      }
    }
    
    // Try to find elements by looking at the entire DOM
    console.log('Getting page HTML for analysis...');
    const html = await page.content();
    
    // Check if there are any hidden file inputs
    const hiddenInputs = await page.locator('input[type="file"]').all();
    console.log(`Found ${hiddenInputs.length} file input elements (including hidden)`);
    
    // Look for any elements with data-testid attributes (common in Streamlit)
    const dataTestIdElements = await page.locator('[data-testid]').all();
    console.log(`Found ${dataTestIdElements.length} elements with data-testid`);
    
    for (let i = 0; i < Math.min(dataTestIdElements.length, 20); i++) {
      try {
        const element = dataTestIdElements[i];
        const testId = await element.getAttribute('data-testid');
        const tagName = await element.evaluate(el => el.tagName);
        const isVisible = await element.isVisible();
        console.log(`TestId ${i}: data-testid="${testId}", tag="${tagName}", visible=${isVisible}`);
      } catch (e) {
        console.log(`TestId ${i}: Error - ${e.message}`);
      }
    }
    
    console.log('Extended debug test completed');
  });
});
