import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('IntelliLog Tool Automation - Streamlined', () => {
  test('should upload CPUMemoryIssue.log file and download summary', async ({ page }) => {
    // Set longer timeout for this test since it involves file processing
    test.setTimeout(120000); // 2 minutes
    
    try {
      console.log('🚀 Starting IntelliLog Tool automation...');
      
      // Step 1: Navigate to the IntelliLog Tool
      console.log('Step 1: Accessing the URL...');
      await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
      
      // Wait for the iframe to load
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(5000); // Allow Streamlit to fully initialize
      
      // Get the Streamlit iframe
      const streamlitFrame = page.locator('iframe[title="streamlitApp"]').contentFrame();
      
      // Step 2: Upload the CPUMemoryIssue.log file
      console.log('Step 2: Uploading CPUMemoryIssue.log file...');
      const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
      
      // Find the actual file input within the dropzone
      const fileInput = streamlitFrame.locator('input[type="file"]').first();
      await fileInput.setInputFiles(filePath);
      console.log('✅ File uploaded successfully');
      
      // Wait for file to be processed
      await page.waitForTimeout(3000);
      
      // Step 3: Click "Analyse Latest Log File" button
      console.log('Step 3: Clicking Analyse Latest Log File button...');
      await streamlitFrame.getByTestId('stButton').getByTestId('stBaseButton-secondary').click();
      console.log('✅ Analysis started');
      
      // Step 4: Wait for analysis to complete
      console.log('Step 4: Waiting for analysis to complete...');
      // Wait for the "Raw Logs" section to appear, indicating analysis is complete
      await expect(streamlitFrame.getByText('📜 Raw Logs').nth(1)).toBeVisible({ timeout: 60000 });
      console.log('✅ Analysis completed - Raw Logs section visible');
      
      // Additional wait for all results to load
      await page.waitForTimeout(5000);
      
      // Step 5: Scroll down and download summary
      console.log('Step 5: Scrolling and downloading summary...');
      
      // Scroll to ensure download button is visible
      await streamlitFrame.locator('body').evaluate(body => {
        body.scrollTo(0, body.scrollHeight);
      });
      
      await page.waitForTimeout(2000);
      
      // Verify download button is visible
      await expect(streamlitFrame.getByTestId('stDownloadButton').getByTestId('stBaseButton-secondary')).toBeVisible();
      
      // Set up download handling
      const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
      
      // Click the download button
      await streamlitFrame.getByTestId('stDownloadButton').getByTestId('stBaseButton-secondary').click();
      console.log('✅ Download button clicked');
      
      // Wait for download to complete
      const download = await downloadPromise;
      
      // Save the downloaded file
      const filename = download.suggestedFilename() || 'log-summary.txt';
      const downloadPath = path.join(__dirname, '..', 'downloads', filename);
      await download.saveAs(downloadPath);
      
      console.log(`🎉 Test completed successfully!`);
      console.log(`📁 File downloaded: ${filename}`);
      console.log(`💾 Saved to: ${downloadPath}`);
      
      // Take a success screenshot
      const screenshotPath = path.join(__dirname, '..', 'downloads', `success-${Date.now()}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`📸 Success screenshot: ${screenshotPath}`);
      
      // Verify file download
      expect(filename).toBeTruthy();
      
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      
      // Take error screenshot
      const errorScreenshotPath = path.join(__dirname, '..', 'downloads', `error-${Date.now()}.png`);
      await page.screenshot({ path: errorScreenshotPath, fullPage: true });
      console.log(`📸 Error screenshot: ${errorScreenshotPath}`);
      
      throw error;
    }
  });
  
  // Additional test for verification - checks that all elements are visible after analysis
  test('should verify analysis results are displayed correctly', async ({ page }) => {
    test.setTimeout(120000);
    
    console.log('🔍 Running verification test...');
    
    // Navigate and perform analysis
    await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(15000);
    
    const streamlitFrame = page.locator('iframe[title="streamlitApp"]').contentFrame();
    const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
    
    // Upload and analyze
    const fileInput = streamlitFrame.locator('input[type="file"]').first();
    await fileInput.setInputFiles(filePath);
    await page.waitForTimeout(3000);
    await streamlitFrame.getByTestId('stButton').getByTestId('stBaseButton-secondary').click();
    
    // Wait for analysis completion
    await expect(streamlitFrame.getByText('📜 Raw Logs').nth(1)).toBeVisible({ timeout: 60000 });
    
    // Verify all expected elements are present
    console.log('✅ Verifying Raw Logs section...');
    await expect(streamlitFrame.getByText('📜 Raw Logs').nth(1)).toBeVisible();
    
    console.log('✅ Verifying Event Summary Table...');
    await expect(streamlitFrame.getByText('📌 Event Summary Table')).toBeVisible();
    
    console.log('✅ Verifying Log Event Distribution...');
    await expect(streamlitFrame.getByText('📊 Log Event Distribution')).toBeVisible();
    
    console.log('✅ Verifying Download button...');
    await expect(streamlitFrame.getByTestId('stDownloadButton')).toBeVisible();
    
    console.log('🎉 All verification checks passed!');
  });
});
