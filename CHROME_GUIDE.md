# Chrome Setup Guide

This scraper uses undetected-chromedriver to bypass CloudFlare protection. Here's how to set it up:

## Prerequisites

1. **Install Chrome Browser**
   - Download from: https://www.google.com/chrome/
   - Install the latest stable version

2. **Set up Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip and install setuptools
pip install --upgrade pip
pip install setuptools wheel

# Install other dependencies
pip install -r requirements.txt
```

3. **Verify Chrome Installation**
   - Open Chrome and check version:
     - Click menu (⋮) > Help > About Google Chrome
   - Make sure you have the latest stable version
   - Note: undetected-chromedriver will download matching chromedriver automatically

## How It Works

The scraper uses undetected-chromedriver to:
1. Launch an automated Chrome instance
2. Handle CloudFlare challenges automatically
3. Maintain persistent sessions
4. Process requests naturally

## Configuration

The scraper comes with default settings optimized for reliability:
```python
# Default settings in scraper.py
min_delay = 5.0  # Seconds between requests
max_delay = 10.0 # Maximum delay
batch_size = 5   # Records per batch
```

## Usage

1. Run with default settings:
```bash
python scraper.py input.xlsx output.xlsx
```

2. Specify batch size:
```bash
python scraper.py input.xlsx output.xlsx --batch-size 3
```

## Best Practices

1. **Chrome Settings**
   - Keep Chrome updated
   - Don't interfere with automated window
   - Allow notifications if prompted

2. **Processing Settings**
   - Use small batch sizes (3-5 records)
   - Keep delays between requests (5-10 seconds)
   - Allow longer delays between batches
   - Run during off-peak hours

3. **Handle Interruptions**
   - The scraper saves progress automatically
   - Check .partial files for interim results
   - Can resume from where you left off

## Troubleshooting

1. **Chrome Launch Issues**
   ```
   Error: Chrome failed to start
   ```
   Solutions:
   - Update Chrome to latest version
   - Clear Chrome user data directory
   - Check Chrome installation path

2. **CloudFlare Challenges**
   ```
   Detected challenge page...
   ```
   Solutions:
   - Increase wait times
   - Reduce batch size
   - Run without headless mode for testing

3. **Timeout Errors**
   ```
   Timeout waiting for page load
   ```
   Solutions:
   - Check internet connection
   - Increase page load timeout
   - Reduce concurrent requests

4. **Memory Issues**
   - The scraper automatically cleans up Chrome processes
   - If you see high memory usage:
     1. Reduce batch size
     2. Add longer delays
     3. Restart scraper more frequently

## Advanced Configuration

1. **Disable Headless Mode**
For troubleshooting, you can see the browser:
```python
def _setup_driver(self) -> uc.Chrome:
    options = uc.ChromeOptions()
    # options.add_argument('--headless')  # Comment this line
    return uc.Chrome(options=options)
```

2. **Adjust Timeouts**
```python
def _setup_driver(self) -> uc.Chrome:
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(45)  # Increase timeout
    driver.implicitly_wait(15)        # Increase wait time
    return driver
```

3. **Fine-tune Delays**
```python
# Increase delays if getting blocked
scraper = TruePeopleSearchScraper(
    min_delay=10.0,
    max_delay=20.0,
    max_retries=5
)
```

## Performance Tips

1. **Optimal Batch Sizes**
   - Start with 3 records per batch
   - Monitor success rate
   - Increase if stable
   - Decrease if blocked

2. **Delay Settings**
   - Minimum: 5 seconds
   - Maximum: 10 seconds
   - Between batches: 15-30 seconds
   - Adjust based on results

3. **Error Recovery**
   - Automatic retry on failure
   - Exponential backoff
   - New Chrome session on errors
   - Progress saving

4. **Resource Usage**
   - Cleans up Chrome processes
   - Manages memory efficiently
   - Handles interruptions gracefully
   - Saves progress regularly

## Error Messages and Solutions

1. ```
   Message: chrome not reachable
   ```
   - Update Chrome
   - Clear user data
   - Check Chrome permissions

2. ```
   TimeoutException: Message: timeout waiting for page load
   ```
   - Increase page load timeout
   - Check internet connection
   - Reduce concurrent requests

3. ```
   WebDriverException: unknown error: Chrome failed to start
   ```
   - Update Chrome
   - Check system resources
   - Verify Chrome installation

4. ```
   Error: failed to solve CloudFlare challenge
   ```
   - Increase wait times
   - Reduce request frequency
   - Check for Chrome updates

Remember: The scraper is designed to work slowly but reliably. Patience and proper configuration are key to successful scraping.
