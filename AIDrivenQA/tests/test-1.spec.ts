import { test, expect } from '@playwright/test';
import path from 'path';

test('IntelliLog Tool - Complete Automation Flow', async ({ page }) => {
  // Navigate to the application
  await page.goto('https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/');

  // Wait for page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000);

  // Get the Streamlit iframe
  const streamlitFrame = page.locator('iframe[title="streamlitApp"]').contentFrame();

  // File path for CPUMemoryIssue.log
  const filePath = path.join(__dirname, '..', 'Logdata', 'CPUMemoryIssue.log');

  // Upload the file
  const fileInput = streamlitFrame.locator('input[type="file"]').first();
  await fileInput.setInputFiles(filePath);

  // Click Analyse button
  await streamlitFrame.getByTestId('stButton').getByTestId('stBaseButton-secondary').click();

  // Wait for analysis to complete - check for Raw Logs section
  await expect(streamlitFrame.getByText('📜 Raw Logs').nth(1)).toBeVisible({ timeout: 60000 });

  // Verify the analysis results contain expected content
  await expect(streamlitFrame.locator('[data-testid="stCustomComponentV1"]').contentFrame().getByRole('grid')).toContainText('Payment gateway response failed. Payment declined by issuing bank (BankErrorCode: 57 - Transaction not permitted to cardholder).');

  // Verify download button is available
  await expect(streamlitFrame.getByTestId('stDownloadButton').getByTestId('stBaseButton-secondary')).toBeVisible();

  // Set up download and click download button
  const downloadPromise = page.waitForEvent('download');
  await streamlitFrame.getByTestId('stDownloadButton').getByTestId('stBaseButton-secondary').click();

  // Handle the download
  const download = await downloadPromise;
  const downloadPath = path.join(__dirname, '..', 'downloads', download.suggestedFilename());
  await download.saveAs(downloadPath);

  console.log(`File downloaded successfully: ${download.suggestedFilename()}`);
});