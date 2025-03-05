# Selenium Setup Guide

The scraper uses Chrome browser automation with Selenium and webdriver-manager. Here's how to set it up:

## Prerequisites

1. **Chrome Browser**
   - Download latest Chrome: https://www.google.com/chrome/
   - Install and run once to complete setup
   - Keep browser updated

2. **Python Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements (includes webdriver-manager)
pip install -r requirements.txt
```

## How It Works

The scraper uses:
1. Selenium for browser automation
2. webdriver-manager for ChromeDriver management
3. Automated waits and retries
4. Progress saving and error recovery

## Configuration

Default settings are optimized for reliability:
```python
# Default settings
min_delay = 5.0  # Seconds between requests
max_delay = 10.0 # Maximum delay
batch_size = 3   # Records per batch
```

## Running the Scraper

1. Basic usage:
```bash
python scraper.py input.csv output.xlsx --batch-size 3
```

2. Test setup first:
```bash
python setup_check.py
```

## Best Practices

1. **Browser Management**
   - Keep Chrome updated
   - Clear browser cache if issues occur
   - Don't interfere with automated window
   - Let scraper handle browser cleanup

2. **Processing Settings**
   - Start with small batches (3 records)
   - Use longer delays initially
   - Monitor for any blocking
   - Check progress in .partial files

3. **Error Handling**
   - Scraper automatically retries on errors
   - Progress is saved after each record
   - Can resume from interruptions
   - Browser is cleaned up properly

## Troubleshooting

1. **ChromeDriver Issues**
   ```
   Error: Chrome failed to start
   ```
   Solutions:
   - Update Chrome to latest version
   - Clear Chrome data and cache
   - Check Chrome installation
   - Run setup_check.py again

2. **Page Loading**
   ```
   Timeout waiting for page load
   ```
   Solutions:
   - Increase page load timeout
   - Check internet connection
   - Reduce batch size
   - Add longer delays

3. **Memory Usage**
   If browser uses too much memory:
   - Reduce batch size
   - Add longer delays between batches
   - Let scraper clean up automatically
   - Monitor system resources

4. **Blocking Detection**
   If you see access denied:
   - Increase delays between requests
   - Use smaller batch sizes
   - Try different times of day
   - Check proxy settings if using any

## Advanced Settings

1. **Adjust Timeouts**
```python
# In scraper.py:
def _setup_driver(self):
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(45)  # Longer timeout
    driver.implicitly_wait(15)        # Longer wait
    return driver
```

2. **Change Window Size**
```python
# For better rendering
driver.set_window_size(1920, 1080)
```

3. **User Agent Rotation**
```python
# Random user agent per session
options.add_argument(f'user-agent={self.ua.random}')
```

## Common Issues

1. **"Chrome not reachable"**
   - Chrome was force-closed
   - Solution: Let scraper handle cleanup
   - Check process manager

2. **"Unable to locate element"**
   - Page didn't load completely
   - Solution: Increase wait times
   - Check page structure

3. **High CPU Usage**
   - Too many concurrent requests
   - Solution: Increase delays
   - Reduce batch size

4. **Memory Leaks**
   - Browser not cleaning up
   - Solution: Let scraper handle cleanup
   - Monitor with task manager

Remember:
- Let the scraper manage the browser
- Don't manually close Chrome windows
- Check .partial files for progress
- Use setup_check.py to verify environment

The scraper is designed for reliability over speed, using Selenium's built-in wait mechanisms and proper cleanup procedures.
