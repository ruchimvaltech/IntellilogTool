# IntelliLog Tool Automation

This project contains Playwright automation tests for the IntelliLog Tool website.

## Test Scenarios

The automation covers the following steps:

1. Access the URL: https://intellilogtool-hes4qgxq42t8bhlv8y77ju.streamlit.app/
2. Upload a log file from the Logdata folder
3. Click "Analyse Latest Log File" button and wait for completion
4. Scroll down and click "Download Summary as a TXT" option

## Files Created

- `tests/intellilog-automation.spec.ts` - Basic automation test
- `tests/intellilog-enhanced.spec.ts` - Enhanced version with better error handling and logging
- `downloads/` - Directory where downloaded summary files will be saved

## Note about Log Files

The test currently uses `CPUMemoryIssue.log` from the Logdata folder since "SpaceIssue 1" was not found. You can:

- Add the "SpaceIssue 1" file to the Logdata folder and update the test
- Or continue using the existing CPUMemoryIssue.log file

## Running the Tests

### Prerequisites

Make sure you have the required dependencies installed:

```bash
npm install
```

Install Playwright browsers:

```bash
npx playwright install
```

Install Chromium extention in chrome

### Run Tests

Run all tests:

```bash
npx playwright test intellilog-streamlined.spec.ts --project=chromium --headed

```

### Test Output

- Downloaded files will be saved in the `downloads/` folder
- Screenshots on error will also be saved in the `downloads/` folder
- Test results and logs will be displayed in the console

## Troubleshooting

If the test fails:

1. Check that the website is accessible
2. Verify the log file exists in the Logdata folder
3. Look at the error screenshot in the downloads folder
4. The enhanced version includes better error handling and logging

## Customization

You may need to adjust:

- File paths if using a different log file
- Selectors if the website UI changes
- Timeout values based on your internet connection and file processing time
