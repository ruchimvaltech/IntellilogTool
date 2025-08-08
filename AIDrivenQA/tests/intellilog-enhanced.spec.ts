import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

test.describe('IntelliLog Tool Automation - Enhanced Version', () => {
  test('should upload log file, analyze, and download summary', async ({ page }) => {
    // Set longer timeout for this test as it involves file processing
    test.setTimeout(120000); // 2 minutes
    
    try {
      // Step 1: Access the URL
      console.log('Step 1: Navigating to IntelliLog Tool...');
      await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
      
      // Wait for the Streamlit app to load completely
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000); // Additional wait for Streamlit initialization
      
      // Step 2: Upload the log file
      console.log('Step 2: Uploading log file...');
      
      // Check if the log file exists
      const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
      if (!fs.existsSync(filePath)) {
        throw new Error(`Log file not found at: ${filePath}`);
      }
      
      // Look for file input - Streamlit file uploader
      const fileInput = await page.locator('input[type="file"]').first();
      await expect(fileInput).toBeVisible({ timeout: 10000 });
      
      // Upload the file
      await fileInput.setInputFiles(filePath);
      console.log('File uploaded successfully');
      
      // Wait for file to be processed
      await page.waitForTimeout(3000);
      
      // Step 3: Click "Analyse Latest Log File" button
      console.log('Step 3: Starting log analysis...');
      
      // Try multiple selectors for the analyze button
      let analyzeButton;
      try {
        analyzeButton = page.getByRole('button', { name: /analyse latest log file/i });
        await expect(analyzeButton).toBeVisible({ timeout: 5000 });
      } catch {
        // Try alternative selectors
        analyzeButton = page.locator('button:has-text("Analyse")').first();
        await expect(analyzeButton).toBeVisible({ timeout: 5000 });
      }
      
      await analyzeButton.click();
      console.log('Analysis started');
      
      // Wait for analysis to complete - look for completion indicators
      // This is a long-running operation, so we need to wait appropriately
      await page.waitForTimeout(10000); // Initial wait
      
      // Wait for network activity to settle
      await page.waitForLoadState('networkidle', { timeout: 60000 });
      
      // Look for indicators that analysis is complete (adjust based on actual UI)
      // You might need to customize this based on what appears after analysis
      console.log('Waiting for analysis to complete...');
      await page.waitForTimeout(5000);
      
      // Step 4: Scroll down and download summary
      console.log('Step 4: Downloading summary...');
      
      // Scroll to bottom of page
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
      
      await page.waitForTimeout(2000);
      
      // Look for download button with multiple possible text variations
      let downloadButton;
      try {
        downloadButton = page.getByRole('button', { name: /download summary as a txt/i });
        await expect(downloadButton).toBeVisible({ timeout: 10000 });
      } catch {
        try {
          downloadButton = page.getByRole('button', { name: /download.*txt/i });
          await expect(downloadButton).toBeVisible({ timeout: 5000 });
        } catch {
          downloadButton = page.locator('button:has-text("Download")').first();
          await expect(downloadButton).toBeVisible({ timeout: 5000 });
        }
      }
      
      // Set up download handling
      const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
      
      // Click download button
      await downloadButton.click();
      console.log('Download button clicked');
      
      // Wait for download to complete
      const download = await downloadPromise;
      
      // Verify download
      const filename = download.suggestedFilename();
      expect(filename).toBeTruthy();
      console.log(`Download initiated: ${filename}`);
      
      // Save the downloaded file
      const downloadsDir = path.join(__dirname, '..', 'downloads');
      if (!fs.existsSync(downloadsDir)) {
        fs.mkdirSync(downloadsDir, { recursive: true });
      }
      
      const downloadPath = path.join(downloadsDir, filename);
      await download.saveAs(downloadPath);
      
      // Verify file was saved
      expect(fs.existsSync(downloadPath)).toBeTruthy();
      
      console.log(`✅ Test completed successfully! File saved to: ${downloadPath}`);
      
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      
      // Take a screenshot for debugging
      const screenshotPath = path.join(__dirname, '..', 'downloads', `error-screenshot-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Screenshot saved to: ${screenshotPath}`);
      
      throw error;
    }
  });
  
  // Alternative test using the existing CPUMemoryIssue.log file
  test('alternative - upload CPUMemoryIssue.log file', async ({ page }) => {
    test.setTimeout(120000);
    
    console.log('Running alternative test with CPUMemoryIssue.log...');
    
    await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
    
    const fileInput = await page.locator('input[type="file"]').first();
    await expect(fileInput).toBeVisible({ timeout: 10000 });
    await fileInput.setInputFiles(filePath);
    
    console.log('CPUMemoryIssue.log file uploaded - proceeding with analysis...');
    
    // Continue with the same steps as the main test
    // (rest of the automation steps would be the same)
  });
});
