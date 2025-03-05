# Free Scraping Guide

Instead of using paid proxies, this scraper now uses advanced browser simulation to avoid blocking. Here's how to use it effectively:

## How It Works

The scraper implements several techniques to mimic real browser behavior:

1. **Browser Identity Rotation**
   - Randomizes User-Agent strings
   - Sets realistic viewport dimensions
   - Rotates between common platforms
   - Simulates different browsers

2. **Natural Browsing Patterns**
   - Adds random delays between requests
   - Makes occasional favicon requests
   - Uses proper referrer headers
   - Maintains session cookies

3. **Batch Processing**
   - Processes records in small batches
   - Saves partial results frequently
   - Takes longer breaks between batches
   - Handles rate limiting gracefully

## Usage Instructions

1. Prepare your environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Prepare your Excel file with owner information

3. Run the scraper with small batches:
```bash
python scraper.py input.xlsx output.xlsx
```

## Best Practices

1. **Start Small**
   - Begin with 5-10 records to test
   - Monitor for any blocking issues
   - Gradually increase batch size if successful

2. **Timing**
   - Run during off-peak hours (late night/early morning)
   - Take breaks between large batches
   - Don't run continuous requests for hours

3. **Handle Blocks**
   If you get blocked:
   - Wait 30-60 minutes before retrying
   - Try running at a different time
   - Reduce batch size
   - Increase delays between requests

4. **Configure Delays**
   Edit scraper.py to adjust timing:
   ```python
   # Increase these values if getting blocked
   min_delay = 5.0  # Minimum seconds between requests
   max_delay = 10.0 # Maximum seconds between requests
   batch_size = 10  # Number of records per batch
   ```

## Tips for Success

1. **Be Patient**
   - The free approach is slower than using proxies
   - But it's reliable if you're not in a hurry
   - Consider running overnight for large datasets

2. **Save Progress**
   - The scraper automatically saves partial results
   - You can resume from where you left off
   - Check the .partial file in your directory

3. **Monitor Results**
   - Check output quality regularly
   - Look for patterns in failed requests
   - Adjust delays if needed

4. **Stay Under Radar**
   - Don't make too many requests too quickly
   - Use natural, random delays
   - Avoid running multiple instances

## Troubleshooting

If you're getting blocked frequently:

1. Increase delays in scraper.py:
```python
class TruePeopleSearchScraper:
    def __init__(self):
        self.min_delay = 10.0  # Try increasing to 10-15 seconds
        self.max_delay = 20.0  # Try increasing to 20-30 seconds
```

2. Reduce batch size:
```bash
# Try with smaller batches
python scraper.py input.xlsx output.xlsx --batch-size 5
```

3. Add longer delays between batches:
```python
# In scraper.py, find the batch processing section
delay = random.uniform(20, 30)  # Increase to 20-30 seconds
```

4. Run during off-peak hours:
   - Late night or early morning
   - Weekends might have less traffic
   - Avoid business hours

Remember: The free approach requires patience but can be just as effective as using paid proxies if you're willing to wait longer for results.
