# TruePeopleSearch Scraper

A Python scraper for TruePeopleSearch.com that uses automated Chrome browser to extract contact information. Works without proxies!

## Requirements

- Python 3.8 or higher
- Google Chrome browser (latest version)
- Excel file with owner information

## Quick Setup

1. Install Chrome:
   - Download from https://www.google.com/chrome/
   - Install and make sure it runs

2. Set up Python environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it (choose one):
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

3. Check setup:
```bash
python setup_check.py
```
This will verify:
- Chrome installation
- Python version
- Required packages
- Input file presence

4. Prepare input file:
   ```bash
   # Option 1: Use sample CSV file
   cp sample_input.csv input.csv   # Use as-is
   
   # Option 2: Convert to Excel
   # Open sample_input.csv in Excel and save as input.xlsx
   ```

5. Run scraper:
   ```bash
   # For CSV input:
   python scraper.py input.csv output.xlsx --batch-size 3
   
   # For Excel input:
   python scraper.py input.xlsx output.xlsx --batch-size 3
   ```

## How It Works

The scraper uses Chrome automation to:
1. Handle CloudFlare protection naturally
2. Process pages like a real browser
3. Extract contact details reliably
4. Save progress automatically

## Features

- Uses real Chrome browser
- Handles CloudFlare automatically
- Extracts:
  - Phone numbers
  - Email addresses
  - Current addresses
- Smart processing:
  - Batch operations
  - Progress saving
  - Error recovery
  - Auto-retry

## Excel File Format

Required columns:
```
Owner #1 First Name
Owner #1 Last Name
Owner #2 First Name (optional)
Owner #2 Last Name (optional)
Mailing Address
Mailing City
Mailing State
Mailing Zip
```

## Documentation

- SELENIUM_GUIDE.md: Complete setup and troubleshooting guide
- MAC_ARM.md: Special setup for Apple Silicon (M1/M2) Macs
- setup_check.py: Verifies all requirements
- sample_input.csv: Example input format

Note: macOS users with Apple Silicon chips should check MAC_ARM.md for important setup instructions.

## Key Features

1. **Smart Automation**
   - Uses Selenium WebDriver
   - Automatic ChromeDriver management
   - Built-in retry logic
   - Progress saving

2. **Data Extraction**
   - Phone numbers
   - Email addresses
   - Addresses
   - Batch processing

3. **Safety Features**
   - Automatic cleanup
   - Error recovery
   - Progress tracking
   - Partial saves

## Before Running

1. Install Chrome browser:
   - Windows/Intel Mac: Standard Chrome installation
   - Apple Silicon Mac: See MAC_ARM.md

2. Run setup check:
```bash
python setup_check.py
```

3. If issues occur:
   - Standard setup: See SELENIUM_GUIDE.md
   - Apple Silicon: See MAC_ARM.md

## Common Issues

If you encounter problems:
1. Verify setup with setup_check.py
2. Follow troubleshooting in SELENIUM_GUIDE.md
3. Use recommended batch sizes and delays
4. Check .partial files for progress

## Note

Educational purposes only. Please respect:
- Website terms of service
- Rate limiting guidelines
- Local data protection laws
- Fair use policies
