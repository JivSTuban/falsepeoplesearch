import os
import time
import random
import argparse
import platform
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus, urlencode

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Owner:
    first_name: str
    last_name: str
    property_address: str = None
    property_city: str = None
    property_state: str = None
    property_zip: str = None
    mailing_address: str = None
    mailing_city: str = None
    mailing_state: str = None
    mailing_zip: str = None
    row_index: int = 0

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        if self.property_address and self.property_city and self.property_state:
            return f"{self.property_address}, {self.property_city}, {self.property_state} {self.property_zip if self.property_zip else ''}"
        return f"{self.mailing_address}, {self.mailing_city}, {self.mailing_state} {self.mailing_zip if self.mailing_zip else ''}"

    @property
    def search_address(self) -> str:
        # Prefer property address for searching
        if self.property_address and self.property_city and self.property_state:
            return self.property_address
        return self.mailing_address
        
    @property
    def search_citystatezip(self) -> str:
        # Prefer property city/state for searching
        if self.property_city and self.property_state:
            return f"{self.property_city}, {self.property_state}"
        return f"{self.mailing_city}, {self.mailing_state}"

@dataclass
class ScrapingResult:
    owner: Owner
    current_address: Optional[str] = None
    phone_numbers: List[str] = None
    emails: List[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        self.phone_numbers = self.phone_numbers or []
        self.emails = self.emails or []

class TruePeopleSearchScraper:
    BASE_URL = "https://www.truepeoplesearch.com"
    ADDRESS_SEARCH_URL = f"{BASE_URL}/resultaddress"
    NAME_SEARCH_URL = f"{BASE_URL}/results"
    
    def __init__(self, min_delay: float = 5.0, max_delay: float = 10.0, max_retries: int = 3):
        self.ua = UserAgent()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.driver = self._setup_driver()
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with optimal settings."""
        try:
            # Use environment variables
            chrome_headless = os.getenv('CHROME_HEADLESS', 'true').lower() == 'true'
            chrome_timeout = int(os.getenv('CHROME_TIMEOUT', '30'))

            # Set up Chrome options
            options = Options()
            if chrome_headless:
                options.add_argument('--headless=new')
            
            # Basic options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument(f'user-agent={self.ua.random}')
            
            # Check for proxy settings in environment variables
            http_proxy = os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('HTTPS_PROXY')
            
            if http_proxy or https_proxy:
                print(f"Using proxy configuration from environment variables")
                # Don't disable proxies if environment variables are set
            else:
                # Disable proxy settings if no environment variables
                options.add_argument('--no-proxy-server')
                options.add_argument('--proxy-bypass-list=*')
                print("No proxy configured. TruePeopleSearch may block non-US IPs.")
                print("See PROXY_SETUP.md for instructions on configuring a US-based proxy.")
            
            # Handle macOS ARM64 architecture
            if platform.system() == 'Darwin' and platform.machine() == 'arm64':
                # For macOS ARM, specify both service and binary location
                chrome_binary = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                
                # Check both possible ChromeDriver locations
                homebrew_path = '/opt/homebrew/bin/chromedriver'
                usr_local_path = '/usr/local/bin/chromedriver'
                
                if os.path.exists(homebrew_path):
                    chromedriver_path = homebrew_path
                else:
                    chromedriver_path = usr_local_path
                    
                print(f"Using local ChromeDriver at {chromedriver_path}")
                print(f"Using Chrome binary at {chrome_binary}")
                
                # Get Chrome version to match with ChromeDriver
                from setup_check import check_chrome_version
                chrome_version = check_chrome_version()[1].split('.')[0]  # Get major version
                print(f"Detected Chrome version: {chrome_version}")
                
                options.binary_location = chrome_binary
                
                # Skip ChromeDriverManager for Apple Silicon and use local driver directly
                service = Service(executable_path=chromedriver_path)
                print(f"Using local ChromeDriver directly for Apple Silicon Mac")
            else:
                service = Service(ChromeDriverManager().install())
            
            # Initialize driver with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver = webdriver.Chrome(service=service, options=options)
                    
                    # Set timeouts
                    driver.set_page_load_timeout(chrome_timeout)
                    driver.implicitly_wait(10)
                    
                    # Set window size for better rendering
                    driver.set_window_size(1920, 1080)
                    
                    # Verify driver is responsive
                    driver.current_url
                    
                    return driver
                except Exception as e:
                    print(f"Attempt {attempt + 1}/{max_retries}: Failed to initialize Chrome driver: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    
                    # Clean up failed driver
                    try:
                        if 'driver' in locals():
                            driver.quit()
                    except:
                        pass
                    
                    time.sleep((attempt + 1) * 2)
            
        except Exception as e:
            print(f"Error setting up Chrome driver: {str(e)}")
            print("Make sure Chrome is installed and up to date")
            raise
    
    def _add_delay(self):
        """Add random delay between requests."""
        time.sleep(random.uniform(self.min_delay, self.max_delay))
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """Make request using undetected-chromedriver."""
        full_url = f"{url}?{urlencode(params)}" if params else url
        
        for attempt in range(self.max_retries):
            try:
                self._add_delay()
                
                print(f"Accessing URL: {full_url}")
                self.driver.get(full_url)
                
                # Wait for content to load with better CloudFlare handling
                try:
                    # First wait for body with increased timeout
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Enhanced CloudFlare detection and handling
                    if "challenge" in self.driver.current_url or "captcha" in self.driver.current_url:
                        print("Detected CloudFlare challenge, waiting for completion...")
                        
                        # Initial longer wait for challenge page to load
                        time.sleep(5)
                        
                        # Wait for challenge to complete with multiple checks
                        max_cf_retries = 6  # 30 seconds total
                        for retry in range(max_cf_retries):
                            if "challenge" not in self.driver.current_url and "captcha" not in self.driver.current_url:
                                print("CloudFlare challenge completed successfully")
                                break
                            print(f"Waiting for CloudFlare... (attempt {retry + 1}/{max_cf_retries})")
                            time.sleep(5)
                            
                        # Verify we're past CloudFlare
                        if "challenge" in self.driver.current_url or "captcha" in self.driver.current_url:
                            print("Failed to bypass CloudFlare challenge")
                            return None
                    
                except TimeoutException:
                    print(f"Timeout waiting for page load on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        break
                    continue
                
                # Give extra time for JS to load
                time.sleep(2)
                
                return self.driver.page_source
                
            except Exception as e:
                print(f"Attempt {attempt + 1}/{self.max_retries}: Error accessing {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    break
                
                wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                print(f"Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                
                # Restart driver on errors
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = self._setup_driver()
        
        return None

    def __del__(self):
        """Clean up the driver when done."""
        try:
            self.driver.quit()
        except:
            pass

    def search_by_address(self, owner: Owner) -> Optional[str]:
        """Search by address using the website's search form."""
        # Navigate to homepage first
        html = self._make_request(self.BASE_URL)
        if not html:
            return None

        # Wait for search form to be present and interactive
        try:
            # Wait for form elements with increased timeout and better error handling
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for address input and ensure it's clickable
            address_input = wait.until(
                EC.element_to_be_clickable((By.ID, "id-d-n"))
            )
            
            # Wait for city/state input and ensure it's clickable
            citystatezip_input = wait.until(
                EC.element_to_be_clickable((By.ID, "id-d-loc-name"))
            )
            
            # Wait for search button and ensure it's clickable
            search_button = wait.until(
                EC.element_to_be_clickable((By.ID, "btnSubmit-d-n"))
            )

            # Add small delay before interaction
            time.sleep(2)

            # Clear and fill the address field with retry logic
            for _ in range(3):
                try:
                    address_input.clear()
                    address_input.send_keys(owner.mailing_address)
                    if address_input.get_attribute('value') == owner.mailing_address:
                        break
                except:
                    time.sleep(1)
                    continue

            # Clear and fill the city/state field with retry logic
            citystatezip_value = f"{owner.mailing_city}, {owner.mailing_state}"
            for _ in range(3):
                try:
                    citystatezip_input.clear()
                    citystatezip_input.send_keys(citystatezip_value)
                    if citystatezip_input.get_attribute('value') == citystatezip_value:
                        break
                except:
                    time.sleep(1)
                    continue

            # Add small delay before clicking
            time.sleep(1)

            # Click search button with retry logic
            for _ in range(3):
                try:
                    search_button.click()
                    break
                except:
                    time.sleep(1)
                    continue

            # Wait for results to load with retry logic
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Wait for either search results or "no results" message
                    WebDriverWait(self.driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "card-summary")),
                            EC.presence_of_element_located((By.CLASS_NAME, "no-results"))
                        )
                    )
                    break
                except TimeoutException:
                    if retry == max_retries - 1:
                        print("Timeout waiting for search results")
                        return None
                    print(f"Retry {retry + 1}/{max_retries} waiting for results...")
                    time.sleep(2)

            html = self.driver.page_source
        except Exception as e:
            print(f"Error during search form interaction: {str(e)}")
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot('search_error.png')
                print("Error screenshot saved as search_error.png")
            except:
                pass
            return None

        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', class_='card card-body shadow-form card-summary')
        
        for result in results:
            name_div = result.find('div', class_='h4')
            if not name_div:
                continue
            
            name = name_div.get_text(strip=True).lower()
            owner_name = owner.full_name.lower()
            
            # Check if names match approximately
            if any(part.lower() in name for part in owner_name.split()):
                link = result.find('a', class_='btn btn-success btn-lg detail-link')
                if link and 'href' in link.attrs:
                    return f"{self.BASE_URL}{link['href']}"
        
        return None

    def extract_profile_info(self, profile_url: str) -> Dict[str, any]:
        """Extract information from a profile page."""
        html = self._make_request(profile_url)
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'current_address': None,
            'phone_numbers': [],
            'emails': []
        }
        
        # Extract phone numbers from all sections (including collapsed)
        phone_sections = soup.find_all('div', {'class': 'col', 'bis_skin_checked': '1'})
        for section in phone_sections:
            phone_link = section.find('a', {'data-link-to-more': 'phone'})
            if phone_link:
                phone_span = phone_link.find('span', {'itemprop': 'telephone'})
                if phone_span:
                    phone = phone_span.get_text(strip=True)
                    if phone not in result['phone_numbers']:
                        result['phone_numbers'].append(phone)
                        
                # Get additional phone info
                phone_info = section.find('div', {'class': 'mt-1 dt-ln'})
                if phone_info:
                    info_text = phone_info.get_text(strip=True)
                    if "Possible Primary Phone" in info_text:
                        # Move this phone number to the start of the list
                        result['phone_numbers'].remove(phone)
                        result['phone_numbers'].insert(0, phone)
        
        # Extract emails
        email_divs = soup.find_all('div', {'class': 'col'})
        for div in email_divs:
            email_text = div.get_text(strip=True)
            if '@' in email_text and '.' in email_text:
                email = email_text.strip()
                if email not in result['emails']:
                    result['emails'].append(email)
        
        return result

def read_input_file(file_path: str) -> List[Owner]:
    """Read input file (Excel or CSV) and extract owner information."""
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    owners = []
    
    for idx, row in df.iterrows():
        # Process Owner #1
        if pd.notna(row.get('Owner #1 First Name')) and pd.notna(row.get('Owner #1 Last Name')):
            owners.append(Owner(
                first_name=str(row['Owner #1 First Name']).strip(),
                last_name=str(row['Owner #1 Last Name']).strip(),
                property_address=str(row.get('Property Address', '')).strip() if pd.notna(row.get('Property Address')) else None,
                property_city=str(row.get('Property City', '')).strip() if pd.notna(row.get('Property City')) else None,
                property_state=str(row.get('Property State', '')).strip() if pd.notna(row.get('Property State')) else None,
                property_zip=str(row.get('Property Zip', '')).strip() if pd.notna(row.get('Property Zip')) else None,
                mailing_address=str(row.get('Mailing Address', '')).strip() if pd.notna(row.get('Mailing Address')) else None,
                mailing_city=str(row.get('Mailing City', '')).strip() if pd.notna(row.get('Mailing City')) else None,
                mailing_state=str(row.get('Mailing State', '')).strip() if pd.notna(row.get('Mailing State')) else None,
                mailing_zip=str(row.get('Mailing Zip', '')).strip() if pd.notna(row.get('Mailing Zip')) else None,
                row_index=idx
            ))
        
        # Process Owner #2 if exists
        if pd.notna(row.get('Owner #2 First Name')) and pd.notna(row.get('Owner #2 Last Name')):
            owners.append(Owner(
                first_name=str(row['Owner #2 First Name']).strip(),
                last_name=str(row['Owner #2 Last Name']).strip(),
                property_address=str(row.get('Property Address', '')).strip() if pd.notna(row.get('Property Address')) else None,
                property_city=str(row.get('Property City', '')).strip() if pd.notna(row.get('Property City')) else None,
                property_state=str(row.get('Property State', '')).strip() if pd.notna(row.get('Property State')) else None,
                property_zip=str(row.get('Property Zip', '')).strip() if pd.notna(row.get('Property Zip')) else None,
                mailing_address=str(row.get('Mailing Address', '')).strip() if pd.notna(row.get('Mailing Address')) else None,
                mailing_city=str(row.get('Mailing City', '')).strip() if pd.notna(row.get('Mailing City')) else None,
                mailing_state=str(row.get('Mailing State', '')).strip() if pd.notna(row.get('Mailing State')) else None,
                mailing_zip=str(row.get('Mailing Zip', '')).strip() if pd.notna(row.get('Mailing Zip')) else None,
                row_index=idx
            ))
    
    return owners

def save_results(results: List[ScrapingResult], output_file: str):
    """Save scraping results to Excel file."""
    data = []
    for result in results:
        data.append({
            'First Name': result.owner.first_name,
            'Last Name': result.owner.last_name,
            'Property Address': result.owner.property_address,
            'Property City': result.owner.property_city,
            'Property State': result.owner.property_state,
            'Property Zip': result.owner.property_zip,
            'Mailing Address': result.owner.mailing_address,
            'Mailing City': result.owner.mailing_city,
            'Mailing State': result.owner.mailing_state,
            'Mailing Zip': result.owner.mailing_zip,
            'Current Address': result.current_address,
            'Phone Numbers': '; '.join(result.phone_numbers),
            'Emails': '; '.join(result.emails),
            'Error': result.error,
            'Row Index': result.owner.row_index
        })
    
    df = pd.DataFrame(data)
    df.sort_values('Row Index', inplace=True)
    df.to_excel(output_file, index=False)

def main(input_file: str, output_file: str, batch_size: int = 5):
    """Main function to orchestrate the scraping process with batching."""
    print(f"Reading data from {input_file}...")
    try:
        owners = read_input_file(input_file)
        total_owners = len(owners)
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        print("Make sure the file exists and has the correct format")
        return
    print(f"Found {total_owners} owners to process")
    
    scraper = TruePeopleSearchScraper()
    results = []
    
    try:
        # Process in smaller batches
        for batch_start in range(0, total_owners, batch_size):
            batch_end = min(batch_start + batch_size, total_owners)
            batch = owners[batch_start:batch_end]
            
            print(f"\nProcessing batch {batch_start//batch_size + 1} ({batch_start + 1} to {batch_end} of {total_owners})")
            
            # Process each owner in the batch
            for i, owner in enumerate(batch, 1):
                print(f"\nProcessing owner {batch_start + i}/{total_owners}: {owner.full_name}")
                result = ScrapingResult(owner=owner)
                
                try:
                    profile_url = scraper.search_by_address(owner)
                    if not profile_url:
                        result.error = "Profile not found"
                        results.append(result)
                        print("No profile found, moving to next owner...")
                        continue
                    
                    print(f"Found profile: {profile_url}")
                    profile_info = scraper.extract_profile_info(profile_url)
                    
                    result.current_address = profile_info.get('current_address')
                    result.phone_numbers = profile_info.get('phone_numbers', [])
                    result.emails = profile_info.get('emails', [])
                    
                    # Save partial results after each successful scrape
                    if results:
                        print("Saving partial results...")
                        save_results(results, f"{output_file}.partial")
                    
                except Exception as e:
                    result.error = str(e)
                    print(f"Error processing {owner.full_name}: {str(e)}")
                
                results.append(result)
            
            # Add longer delay between batches
            if batch_end < total_owners:
                delay = random.uniform(15, 30)
                print(f"\nCompleted batch. Waiting {delay:.1f} seconds before next batch...")
                time.sleep(delay)
    
    finally:
        # Ensure we save results even if interrupted
        if results:
            print(f"\nSaving results to {output_file}...")
            save_results(results, output_file)
            print("Done!")
        
        # Clean up
        scraper.__del__()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TruePeopleSearch Scraper")
    parser.add_argument("input_file", help="Path to input file (Excel or CSV)")
    parser.add_argument("output_file", help="Path to output Excel file")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of records to process in each batch")
    args = parser.parse_args()
    
    main(args.input_file, args.output_file, args.batch_size)
