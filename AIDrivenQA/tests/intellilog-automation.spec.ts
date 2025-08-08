import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('IntelliLog Tool Automation', () => {
  test('should upload log file and download summary', async ({ page }) => {
    // Set longer timeout for this test
    test.setTimeout(120000); // 2 minutes
    
    try {
      console.log('Step 1: Accessing the IntelliLog Tool URL...');
    // Step 1: Access the URL
    await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
    
    // Wait for the page to load completely - Streamlit apps need more time
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000); // Additional wait for Streamlit to fully initialize
    
    console.log('Step 2: Looking for file upload element...');
    // Step 2: Click on "Browse File" button and upload the file
    const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
    
    // Try multiple selectors for Streamlit file uploader
    let fileInput;
    try {
      // Try standard file input
      fileInput = page.locator('input[type="file"]').first();
      await expect(fileInput).toBeVisible({ timeout: 10000 });
    } catch {
      try {
        // Try Streamlit specific selectors
        fileInput = page.locator('[data-testid="stFileUploader"] input[type="file"]').first();
        await expect(fileInput).toBeVisible({ timeout: 5000 });
      } catch {
        try {
          // Try by class or other attributes
          fileInput = page.locator('.uploadedFile input, [class*="upload"] input[type="file"]').first();
          await expect(fileInput).toBeVisible({ timeout: 5000 });
        } catch {
          // Last resort - any file input on page
          fileInput = page.locator('input').filter({ hasText: '' }).and(page.locator('[type="file"]')).first();
          await expect(fileInput).toBeVisible({ timeout: 5000 });
        }
      }
    }
    
    console.log('File input found, uploading CPUMemoryIssue.log...');
    // Upload the file
    await fileInput.setInputFiles(filePath);
    
    // Wait for file to be processed
    await page.waitForTimeout(3000);
    
    console.log('Step 3: Looking for Analyse Latest Log File button...');
    // Step 3: Click "Analyse Latest Log File" button and wait until the page gets loaded completely
    let analyzeButton;
    try {
      analyzeButton = page.getByRole('button', { name: /analyse latest log file/i });
      await expect(analyzeButton).toBeVisible({ timeout: 10000 });
    } catch {
      try {
        // Try alternative text patterns
        analyzeButton = page.getByRole('button', { name: /analyse/i });
        await expect(analyzeButton).toBeVisible({ timeout: 5000 });
      } catch {
        try {
          // Try by button text content
          analyzeButton = page.locator('button:has-text("Analyse")').first();
          await expect(analyzeButton).toBeVisible({ timeout: 5000 });
        } catch {
          // Try any button that might contain analyze/analyse
          analyzeButton = page.locator('button').filter({ hasText: /analys/i }).first();
          await expect(analyzeButton).toBeVisible({ timeout: 5000 });
        }
      }
    }
    
    console.log('Clicking Analyse button...');
    await analyzeButton.click();
    
    console.log('Waiting for analysis to complete...');
    // Wait for the analysis to complete - this might take some time
    await page.waitForTimeout(10000); // Initial wait for processing to start
    
    // Wait for the page to be fully loaded after analysis
    await page.waitForLoadState('networkidle', { timeout: 60000 });
    
    // Additional wait to ensure analysis is complete
    await page.waitForTimeout(5000);
    
    console.log('Step 4: Scrolling down and looking for download button...');
    // Step 4: Scroll the Page down and click "Download Summary as a TXT" option
    // First scroll down to make sure the download button is visible
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    
    // Wait a moment after scrolling
    await page.waitForTimeout(2000);
    
    // Look for the download button with multiple selector strategies
    let downloadButton;
    try {
      downloadButton = page.getByRole('button', { name: /download summary as a txt/i });
      await expect(downloadButton).toBeVisible({ timeout: 10000 });
    } catch {
      try {
        // Try simpler download text
        downloadButton = page.getByRole('button', { name: /download.*txt/i });
        await expect(downloadButton).toBeVisible({ timeout: 5000 });
      } catch {
        try {
          // Try by button text content
          downloadButton = page.locator('button:has-text("Download")').first();
          await expect(downloadButton).toBeVisible({ timeout: 5000 });
        } catch {
          try {
            // Try any button with download text
            downloadButton = page.locator('button').filter({ hasText: /download/i }).first();
            await expect(downloadButton).toBeVisible({ timeout: 5000 });
          } catch {
            // Last resort - look for any clickable element with download text
            downloadButton = page.locator('[role="button"], button, a').filter({ hasText: /download/i }).first();
            await expect(downloadButton).toBeVisible({ timeout: 5000 });
          }
        }
      }
    }
    
    console.log('Download button found, setting up download handling...');
    // Set up download promise before clicking
    const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
    
    // Click the download button
    await downloadButton.click();
    console.log('Download button clicked, waiting for download...');
    
    // Wait for download to complete
    const download = await downloadPromise;
    
    // Verify the download was successful
    const filename = download.suggestedFilename();
    expect(filename).toBeTruthy();
    console.log(`Download initiated: ${filename}`);
    
    // Create downloads directory if it doesn't exist and save the file
    const downloadPath = path.join(__dirname, '..', 'downloads', filename);
    await download.saveAs(downloadPath);
    
    console.log(`✅ Test completed successfully! File downloaded: ${filename}`);
    console.log(`📁 File saved to: ${downloadPath}`);
    
    // Take a success screenshot
    const screenshotPath = path.join(__dirname, '..', 'downloads', `success-screenshot-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 Success screenshot saved to: ${screenshotPath}`);
    
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      
      // Take a screenshot for debugging
      const errorScreenshotPath = path.join(__dirname, '..', 'downloads', `error-screenshot-${Date.now()}.png`);
      await page.screenshot({ path: errorScreenshotPath, fullPage: true });
      console.log(`📸 Error screenshot saved to: ${errorScreenshotPath}`);
      
      throw error;
    }
  });
});
