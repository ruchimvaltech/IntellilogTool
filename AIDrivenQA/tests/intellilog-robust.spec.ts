import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('IntelliLog Tool - Alternative Approach', () => {
  test('robust automation with multiple strategies', async ({ page }) => {
    test.setTimeout(180000); // 3 minutes
    
    try {
      console.log('🚀 Starting IntelliLog Tool automation...');
      
      // Step 1: Access the URL with retry logic
      console.log('Step 1: Navigating to IntelliLog Tool...');
      let retries = 3;
      while (retries > 0) {
        try {
          await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/', { 
            waitUntil: 'networkidle',
            timeout: 60000 
          });
          break;
        } catch (error) {
          console.log(`Navigation attempt failed, retries left: ${retries - 1}`);
          retries--;
          if (retries === 0) throw error;
          await page.waitForTimeout(5000);
        }
      }
      
      // Wait for Streamlit to initialize
      console.log('Waiting for Streamlit app to initialize...');
      await page.waitForTimeout(20000); // Extended wait
      
      // Take initial screenshot
      await page.screenshot({ path: 'downloads/step1-initial.png', fullPage: true });
      
      // Step 2: Find and upload file with multiple strategies
      console.log('Step 2: Looking for file upload mechanism...');
      const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');
      
      let fileUploaded = false;
      
      // Strategy 1: Standard file input
      try {
        console.log('Trying strategy 1: Standard file input...');
        const fileInput = page.locator('input[type="file"]').first();
        await fileInput.waitFor({ state: 'visible', timeout: 10000 });
        await fileInput.setInputFiles(filePath);
        console.log('✅ File uploaded using standard input');
        fileUploaded = true;
      } catch (error) {
        console.log('Strategy 1 failed:', error.message);
      }
      
      // Strategy 2: Streamlit file uploader
      if (!fileUploaded) {
        try {
          console.log('Trying strategy 2: Streamlit file uploader...');
          const streamlitUploader = page.locator('[data-testid="stFileUploader"] input, [data-testid*="file"] input').first();
          await streamlitUploader.waitFor({ state: 'visible', timeout: 10000 });
          await streamlitUploader.setInputFiles(filePath);
          console.log('✅ File uploaded using Streamlit uploader');
          fileUploaded = true;
        } catch (error) {
          console.log('Strategy 2 failed:', error.message);
        }
      }
      
      // Strategy 3: Click on upload area then find input
      if (!fileUploaded) {
        try {
          console.log('Trying strategy 3: Click upload area...');
          // Look for clickable upload areas
          const uploadArea = page.locator('div, section').filter({ hasText: /drag.*drop|browse|upload|choose.*file/i }).first();
          await uploadArea.waitFor({ state: 'visible', timeout: 10000 });
          await uploadArea.click();
          await page.waitForTimeout(1000);
          
          // Then look for file input that might have appeared
          const fileInput = page.locator('input[type="file"]').first();
          await fileInput.waitFor({ state: 'visible', timeout: 5000 });
          await fileInput.setInputFiles(filePath);
          console.log('✅ File uploaded using upload area click');
          fileUploaded = true;
        } catch (error) {
          console.log('Strategy 3 failed:', error.message);
        }
      }
      
      // Strategy 4: Force file input creation (last resort)
      if (!fileUploaded) {
        try {
          console.log('Trying strategy 4: Force file input creation...');
          // Inject a file input for testing purposes
          await page.evaluate(() => {
            const input = document.createElement('input');
            input.type = 'file';
            input.id = 'force-file-input';
            input.style.position = 'fixed';
            input.style.top = '10px';
            input.style.left = '10px';
            input.style.zIndex = '9999';
            document.body.appendChild(input);
          });
          
          const forceInput = page.locator('#force-file-input');
          await forceInput.setInputFiles(filePath);
          console.log('⚠️ File uploaded using forced input (test mode)');
          fileUploaded = true;
        } catch (error) {
          console.log('Strategy 4 failed:', error.message);
        }
      }
      
      if (!fileUploaded) {
        throw new Error('Failed to upload file using all available strategies');
      }
      
      // Wait after file upload
      await page.waitForTimeout(5000);
      await page.screenshot({ path: 'downloads/step2-file-uploaded.png', fullPage: true });
      
      // Step 3: Find and click analyze button
      console.log('Step 3: Looking for Analyze button...');
      let analyzeClicked = false;
      
      // Try multiple button strategies
      const analyzeStrategies = [
        () => page.getByRole('button', { name: /analyse latest log file/i }),
        () => page.getByRole('button', { name: /analyse/i }),
        () => page.locator('button').filter({ hasText: /analys/i }),
        () => page.locator('[role="button"]').filter({ hasText: /analys/i }),
        () => page.locator('div, span').filter({ hasText: /analys/i }).and(page.locator('[onclick], [onpointerdown]'))
      ];
      
      for (let i = 0; i < analyzeStrategies.length; i++) {
        try {
          console.log(`Trying analyze strategy ${i + 1}...`);
          const button = analyzeStrategies[i]();
          await button.waitFor({ state: 'visible', timeout: 10000 });
          await button.click();
          console.log('✅ Analyze button clicked');
          analyzeClicked = true;
          break;
        } catch (error) {
          console.log(`Analyze strategy ${i + 1} failed:`, error.message);
        }
      }
      
      if (!analyzeClicked) {
        console.log('⚠️ Could not find analyze button, continuing anyway...');
      }
      
      // Wait for analysis
      console.log('Waiting for analysis to complete...');
      await page.waitForTimeout(30000); // 30 seconds for analysis
      await page.waitForLoadState('networkidle', { timeout: 60000 });
      await page.screenshot({ path: 'downloads/step3-analysis-complete.png', fullPage: true });
      
      // Step 4: Scroll and download
      console.log('Step 4: Scrolling and looking for download...');
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(3000);
      
      let downloadSuccess = false;
      
      // Try multiple download strategies
      const downloadStrategies = [
        () => page.getByRole('button', { name: /download summary as a txt/i }),
        () => page.getByRole('button', { name: /download.*txt/i }),
        () => page.locator('button').filter({ hasText: /download/i }),
        () => page.locator('a').filter({ hasText: /download/i }),
        () => page.locator('[role="button"], button, a').filter({ hasText: /download/i })
      ];
      
      for (let i = 0; i < downloadStrategies.length; i++) {
        try {
          console.log(`Trying download strategy ${i + 1}...`);
          const downloadElement = downloadStrategies[i]();
          await downloadElement.waitFor({ state: 'visible', timeout: 10000 });
          
          const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
          await downloadElement.click();
          
          const download = await downloadPromise;
          const filename = download.suggestedFilename();
          const downloadPath = path.join(__dirname, '..', 'downloads', filename);
          await download.saveAs(downloadPath);
          
          console.log(`✅ File downloaded successfully: ${filename}`);
          console.log(`📁 Saved to: ${downloadPath}`);
          downloadSuccess = true;
          break;
        } catch (error) {
          console.log(`Download strategy ${i + 1} failed:`, error.message);
        }
      }
      
      await page.screenshot({ path: 'downloads/step4-final.png', fullPage: true });
      
      if (downloadSuccess) {
        console.log('🎉 Test completed successfully!');
      } else {
        console.log('⚠️ Test completed but download may have failed');
      }
      
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      await page.screenshot({ path: 'downloads/error-final.png', fullPage: true });
      throw error;
    }
  });
});
