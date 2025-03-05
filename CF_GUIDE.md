# CloudFlare Bypass Guide

This scraper uses the `aqua` library to bypass CloudFlare protection without needing proxies. Here's how it works:

## How It Works

The scraper uses CloudFlare bypass techniques to:
1. Handle JavaScript challenges
2. Generate valid cookies
3. Maintain persistent sessions
4. Process requests naturally

## Setup Instructions

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python scraper.py input.xlsx output.xlsx
```

## Best Practices

1. **Rate Limiting**
   - Keep delays between requests (5-10 seconds)
   - Process in small batches (5-10 records)
   - Take breaks between batches
   - Run during off-peak hours

2. **Handle Errors**
   - The scraper automatically refreshes CF cookies
   - Retries with exponential backoff
   - Saves progress regularly
   - Detailed error logging

3. **Optimize Performance**
   - Keep batch sizes small
   - Monitor for rate limiting
   - Adjust delays if needed
   - Check .partial files for progress

## Troubleshooting

If you're getting blocked:

1. **Increase Delays**
```python
# In scraper.py:
class TruePeopleSearchScraper:
    def __init__(self, min_delay: float = 10.0, max_delay: float = 20.0):
        ...
```

2. **Reduce Batch Size**
```bash
python scraper.py input.xlsx output.xlsx --batch-size 5
```

3. **Cookie Issues**
   - The scraper will automatically get new cookies
   - Check CF_Solver connection
   - Try restarting the scraper
   - Clear browser cookies/cache

4. **Rate Limiting**
   - Increase delays between requests
   - Reduce batch size
   - Take longer breaks
   - Run during off-peak hours

## Common Issues

1. "Failed to solve CF challenge"
   - Solution: Increase timeout values, retry later

2. "Rate limited (429)"
   - Solution: Increase delays, reduce batch size

3. "Access forbidden (403)"
   - Solution: Wait for new CF cookie, retry

4. Connection errors
   - Solution: Check internet connection, retry with fresh session

## Tips for Success

1. Start small and scale up slowly
   - Begin with 5 records
   - Monitor success rate
   - Gradually increase if stable
   - Keep batches reasonable

2. Save progress frequently
   - Check .partial files
   - Resume from last success
   - Back up completed results

3. Monitor Performance
   - Watch for rate limiting
   - Check success rates
   - Adjust parameters as needed
   - Keep logs for troubleshooting

4. Be Patient
   - CloudFlare bypass takes time
   - Don't rush requests
   - Let delays work naturally
   - Success rate over speed

## Technical Details

The scraper uses these CloudFlare bypass techniques:

1. **Cookie Generation**
   ```python
   cf = CF_Solver('https://www.truepeoplesearch.com')
   cookie = cf.cookie()
   ```

2. **Request Handling**
   ```python
   # Making requests with CF client
   response = cf.client.get(url=url, timeout=30)
   ```

3. **Error Recovery**
   ```python
   # Refresh CF cookie on errors
   self.cf_cookie = cf.cookie()
   ```

Remember: This is a more reliable approach than using proxies, but it requires patience and proper rate limiting to work effectively.
