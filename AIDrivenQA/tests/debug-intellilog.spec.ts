import { test, expect } from '@playwright/test';

test.describe('IntelliLog Tool Debug', () => {
  test('debug page elements', async ({ page }) => {
    test.setTimeout(60000);
    
    console.log('Navigating to IntelliLog Tool...');
    await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(10000); // Give Streamlit time to fully load
    
    console.log('Taking screenshot of initial page...');
    await page.screenshot({ path: 'downloads/debug-initial-page.png', fullPage: true });
    
    console.log('Getting page content...');
    const pageContent = await page.content();
    console.log('Page title:', await page.title());
    
    console.log('Looking for all input elements...');
    const inputs = await page.locator('input').all();
    console.log(`Found ${inputs.length} input elements`);
    
    for (let i = 0; i < inputs.length; i++) {
      try {
        const input = inputs[i];
        const type = await input.getAttribute('type');
        const id = await input.getAttribute('id');
        const className = await input.getAttribute('class');
        const isVisible = await input.isVisible();
        console.log(`Input ${i}: type="${type}", id="${id}", class="${className}", visible=${isVisible}`);
      } catch (e) {
        console.log(`Input ${i}: Error getting attributes - ${e.message}`);
      }
    }
    
    console.log('Looking for all button elements...');
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} button elements`);
    
    for (let i = 0; i < Math.min(buttons.length, 10); i++) {
      try {
        const button = buttons[i];
        const text = await button.textContent();
        const id = await button.getAttribute('id');
        const className = await button.getAttribute('class');
        const isVisible = await button.isVisible();
        console.log(`Button ${i}: text="${text}", id="${id}", class="${className}", visible=${isVisible}`);
      } catch (e) {
        console.log(`Button ${i}: Error getting attributes - ${e.message}`);
      }
    }
    
    console.log('Looking for file upload related elements...');
    // Look for common Streamlit file uploader patterns
    const streamlitFileElements = await page.locator('[data-testid*="file"], [class*="file"], [class*="upload"]').all();
    console.log(`Found ${streamlitFileElements.length} potential file upload elements`);
    
    for (let i = 0; i < streamlitFileElements.length; i++) {
      try {
        const element = streamlitFileElements[i];
        const tagName = await element.evaluate(el => el.tagName);
        const id = await element.getAttribute('id');
        const className = await element.getAttribute('class');
        const dataTestId = await element.getAttribute('data-testid');
        const isVisible = await element.isVisible();
        console.log(`File element ${i}: tag="${tagName}", id="${id}", class="${className}", data-testid="${dataTestId}", visible=${isVisible}`);
      } catch (e) {
        console.log(`File element ${i}: Error getting attributes - ${e.message}`);
      }
    }
    
    console.log('Debug test completed');
  });
});
