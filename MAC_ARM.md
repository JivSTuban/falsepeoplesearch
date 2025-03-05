# macOS ARM (Apple Silicon) Setup Guide

For users with M1/M2 Macs, you need to install the correct ChromeDriver version. Follow these steps:

## Quick Setup

1. Install Chrome for Apple Silicon:
   - Download from: https://www.google.com/chrome/
   - Make sure you get the Apple Silicon version
   - Verify by clicking Chrome > About Google Chrome

2. Install ChromeDriver using Homebrew:
```bash
# Install Homebrew if you haven't
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ChromeDriver
brew install --cask chromedriver

# Verify installation
chromedriver --version
```

3. Fix Security Settings:
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /usr/local/bin/chromedriver

# Make executable
chmod +x /opt/homebrew/bin/chromedriver    
```

4. Test Setup:
```bash
python setup_check.py
```

## Manual Installation

If Homebrew installation doesn't work:

1. Download ChromeDriver manually:
   - Go to: https://chromedriver.chromium.org/downloads
   - Choose the Mac ARM64 version matching your Chrome version
   - Extract the downloaded file

2. Move to correct location:
```bash
# Move ChromeDriver to /usr/local/bin
sudo mv ~/Downloads/chromedriver /usr/local/bin/

# Set permissions
sudo chown root:wheel /usr/local/bin/chromedriver
sudo chmod 755 /usr/local/bin/chromedriver
```

3. Fix security:
```bash
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

## Troubleshooting

1. If ChromeDriver fails to start:
```bash
# Check ChromeDriver location
which chromedriver

# Verify permissions
ls -l /usr/local/bin/chromedriver

# Test ChromeDriver
chromedriver --version
```

2. If Chrome version mismatch:
   - Update Chrome to latest version
   - Download matching ChromeDriver version
   - Replace existing ChromeDriver

3. Security blocks:
   - Open System Preferences > Security & Privacy
   - Allow ChromeDriver if blocked
   - Run security fix commands again

4. Try without headless mode:
   - Edit .env file:
```bash
CHROME_HEADLESS=false
```

## Version Management

To handle multiple Chrome versions:

1. Check Chrome version:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

2. Match ChromeDriver version:
   - Use browser version number (e.g., 133.0.6943.142)
   - Download matching ChromeDriver

3. Keep both updated:
   - Update Chrome regularly
   - Update ChromeDriver to match

## Testing

1. Basic test:
```bash
# Run setup check
python setup_check.py

# Try scraper with small batch
python scraper.py sample_input.csv test_output.xlsx --batch-size 2
```

2. Monitor process:
```bash
# Check running Chrome processes
ps aux | grep Chrome

# Check ChromeDriver processes
ps aux | grep chromedriver
```

Remember:
- Keep Chrome updated
- Match ChromeDriver version
- Run security fixes after updates
- Use non-headless mode for troubleshooting
- Check system logs if issues persist
