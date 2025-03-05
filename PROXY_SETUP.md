# Proxy Setup Guide

TruePeopleSearch blocks datacenter IPs, so residential proxies are required. Here's how to set them up:

## Recommended Proxy Services

1. **Smartproxy** (https://smartproxy.com)
   - Residential proxies with city/state targeting
   - Good for US-based scraping
   - Pricing starts at $75/month for 5GB
   - Example configuration:
   ```
   HTTP_PROXY=http://username:password@us.smartproxy.com:10000
   HTTPS_PROXY=http://username:password@us.smartproxy.com:10000
   ```

2. **Bright Data** (formerly Luminati) (https://brightdata.com)
   - Large residential proxy network
   - Advanced targeting options
   - Pricing starts at $500/month
   - Example configuration:
   ```
   HTTP_PROXY=http://lum-customer-{customer}-zone-residential-country-us:password@zproxy.lum-superproxy.io:22225
   HTTPS_PROXY=http://lum-customer-{customer}-zone-residential-country-us:password@zproxy.lum-superproxy.io:22225
   ```

3. **IPRoyal** (https://iproyal.com)
   - More affordable option
   - Good US coverage
   - Pricing starts at $50/month
   - Example configuration:
   ```
   HTTP_PROXY=http://username:password@proxy.iproyal.com:12321
   HTTPS_PROXY=http://username:password@proxy.iproyal.com:12321
   ```

## Setup Steps

1. Choose a proxy provider and sign up for an account

2. Get your proxy credentials:
   - Username/Customer ID
   - Password
   - Proxy host/IP
   - Port number

3. Create your .env file:
   ```bash
   cp .env.example .env
   ```

4. Edit .env and add your proxy configuration:
   ```
   # Basic format:
   HTTP_PROXY=http://username:password@proxy.provider.com:port
   HTTPS_PROXY=http://username:password@proxy.provider.com:port
   
   # Example with actual values (replace with your credentials):
   HTTP_PROXY=http://user123:pass456@us.smartproxy.com:10000
   HTTPS_PROXY=http://user123:pass456@us.smartproxy.com:10000
   ```

## Testing Your Proxy

1. Create a test.py file:
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

# Test your proxy
try:
    response = requests.get('https://api.ipify.org?format=json', proxies=proxies)
    print(f"Your IP: {response.json()['ip']}")
    print("Proxy is working!")
except Exception as e:
    print(f"Error: {str(e)}")
```

2. Run the test:
```bash
python test.py
```

## Best Practices

1. **Rotate IPs**
   - Most providers automatically rotate IPs
   - Some allow setting rotation intervals
   - Recommended: new IP every 10-15 requests

2. **Geographic Targeting**
   - Use US-based proxies for better success
   - Target states where your searches are focused

3. **Monitor Usage**
   - Track your bandwidth usage
   - Monitor success/failure rates
   - Adjust delays based on block rate

4. **Error Handling**
   - The scraper already includes retry logic
   - Increase MAX_RETRIES in .env if needed
   - Adjust delays if getting frequent blocks

## Troubleshooting

If you're getting blocked:

1. Verify proxy is working:
   ```bash
   python test.py
   ```

2. Check your delays:
   ```
   MIN_DELAY=2.0  # Increase if needed
   MAX_DELAY=5.0  # Increase if needed
   ```

3. Verify proxy type:
   - Must be residential
   - Datacenter IPs will be blocked
   - Mobile IPs also work well

4. Contact provider support:
   - If IPs are being blocked consistently
   - To optimize proxy settings
   - To get US-specific proxies

## Cost-Effective Options

If the recommended services are too expensive:

1. **Rotating Proxy Services**
   - ProxyCrawl (https://proxycrawl.com)
   - ScraperAPI (https://www.scraperapi.com)
   - These handle proxy management for you
   - Pay per successful request

2. **Proxy Packages**
   - WebShare (https://www.webshare.io)
   - More affordable options
   - May need to test multiple IPs

Remember: Using free proxies is not recommended as they are usually blocked and unreliable.
