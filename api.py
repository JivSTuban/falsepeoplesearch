import os
import json
import time
import random
import re
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus

from flask import Flask, request, jsonify
from flask_cors import CORS
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global API instance
api_instance = None

@app.before_first_request
def initialize_api():
    """Initialize the API instance before the first request."""
    global api_instance
    if api_instance is None:
        api_instance = TruePeopleSearchAPI()
        print("API instance initialized")

@app.route('/search', methods=['POST'])
def search():
    """Main search endpoint that handles all search types."""
    try:
        # Get JSON data from request
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Initialize results dictionary
        results = {}
        max_results = data.get('max_results', 1)
        
        # Process name searches
        if 'name' in data and data['name']:
            name_results = []
            for name_query in data['name']:
                # Initialize API if needed
                global api_instance
                if api_instance is None:
                    api_instance = TruePeopleSearchAPI()
                    
                # Perform search
                search_results = api_instance.search_by_name(name_query, max_results=max_results)
                name_results.extend([result.to_dict() for result in search_results])
            results['name_results'] = name_results
        
        # Process address searches
        if 'street_citystatezip' in data and data['street_citystatezip']:
            address_results = []
            for address_query in data['street_citystatezip']:
                # Initialize API if needed
                if api_instance is None:
                    api_instance = TruePeopleSearchAPI()
                    
                # Perform search
                search_results = api_instance.search_by_address(address_query, max_results=max_results)
                address_results.extend([result.to_dict() for result in search_results])
            results['address_results'] = address_results
        
        # Process phone searches
        if 'phone_number' in data and data['phone_number']:
            phone_results = []
            for phone_query in data['phone_number']:
                # Initialize API if needed
                if api_instance is None:
                    api_instance = TruePeopleSearchAPI()
                    
                # Perform search
                search_results = api_instance.search_by_phone(phone_query, max_results=max_results)
                phone_results.extend([result.to_dict() for result in search_results])
            results['phone_results'] = phone_results
        
        # Return results
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API is running"}), 200

@dataclass
class SearchQuery:
    """Represents a search query for TruePeopleSearch"""
    query: str
    search_type: str  # 'name', 'address', 'phone'
    city_state: Optional[str] = None  # For name searches with city/state
    max_results: int = 1

@dataclass
class SearchResult:
    """Represents a search result from TruePeopleSearch"""
    search_option: str
    input_given: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[str] = None
    lives_in: Optional[str] = None
    street_address: Optional[str] = None
    address_locality: Optional[str] = None
    address_region: Optional[str] = None
    postal_code: Optional[str] = None
    country_name: Optional[str] = None
    emails: List[str] = None
    phones: List[Dict[str, str]] = None
    person_link: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        self.emails = self.emails or []
        self.phones = self.phones or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with flattened phone and email fields"""
        result = {
            "Search Option": self.search_option,
            "Input Given": self.input_given,
            "First Name": self.first_name,
            "Last Name": self.last_name,
            "Age": self.age,
            "Lives in": self.lives_in,
            "Street Address": self.street_address,
            "Address Locality": self.address_locality,
            "Address Region": self.address_region,
            "Postal Code": self.postal_code,
            "Country Name": self.country_name,
            "Person Link": self.person_link
        }
        
        # Add emails (up to 5)
        for i, email in enumerate(self.emails[:5], 1):
            result[f"Email {i}"] = email
        
        # Fill remaining email slots with empty strings
        for i in range(len(self.emails) + 1, 6):
            result[f"Email {i}"] = ""
        
        # Add phones (up to 5)
        for i, phone_data in enumerate(self.phones[:5], 1):
            result[f"Phone {i}"] = phone_data.get("number", "")
            result[f"Phone {i} Type"] = phone_data.get("type", "")
            result[f"Phone {i} Last Reported"] = phone_data.get("last_reported", "")
            result[f"Phone {i} Provider"] = phone_data.get("provider", "")
        
        # Fill remaining phone slots with empty strings
        for i in range(len(self.phones) + 1, 6):
            result[f"Phone {i}"] = ""
            result[f"Phone {i} Type"] = ""
            result[f"Phone {i} Last Reported"] = ""
            result[f"Phone {i} Provider"] = ""
            
        return result

class TruePeopleSearchAPI:
    BASE_URL = "https://www.truepeoplesearch.com"
    NAME_SEARCH_URL = f"{BASE_URL}/results"
    ADDRESS_SEARCH_URL = f"{BASE_URL}/resultaddress"
    PHONE_SEARCH_URL = f"{BASE_URL}/resultphone"
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0, max_retries: int = 3):
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
            
            # Initialize driver with retry logic
            service = Service(ChromeDriverManager().install())
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
    
    def _make_request(self, url: str) -> Optional[str]:
        """Make request using selenium."""
        for attempt in range(self.max_retries):
            try:
                self._add_delay()
                
                print(f"Accessing URL: {url}")
                self.driver.get(url)
                
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
    
    def _extract_profile_info(self, profile_url: str) -> Dict[str, Any]:
        """Extract detailed information from a profile page."""
        html = self._make_request(profile_url)
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'first_name': None,
            'last_name': None,
            'age': None,
            'lives_in': None,
            'street_address': None,
            'address_locality': None,
            'address_region': None,
            'postal_code': None,
            'country_name': None,
            'emails': [],
            'phones': []
        }
        
        # Extract name and age
        name_header = soup.find('h1', {'class': 'h2'})
        if name_header:
            name_text = name_header.get_text(strip=True)
            # Parse name and age (e.g., "John Smith, 45")
            name_parts = name_text.split(',', 1)
            if len(name_parts) > 0:
                full_name = name_parts[0].strip()
                name_split = full_name.split(' ', 1)
                if len(name_split) > 0:
                    result['first_name'] = name_split[0]
                if len(name_split) > 1:
                    result['last_name'] = name_split[1]
                
                if len(name_parts) > 1:
                    age_text = name_parts[1].strip()
                    age_match = re.search(r'\d+', age_text)
                    if age_match:
                        result['age'] = age_match.group()
        
        # Extract current address
        address_section = soup.find('div', {'itemtype': 'https://schema.org/PostalAddress'})
        if address_section:
            street = address_section.find('span', {'itemprop': 'streetAddress'})
            if street:
                result['street_address'] = street.get_text(strip=True)
                
            locality = address_section.find('span', {'itemprop': 'addressLocality'})
            if locality:
                result['address_locality'] = locality.get_text(strip=True)
                
            region = address_section.find('span', {'itemprop': 'addressRegion'})
            if region:
                result['address_region'] = region.get_text(strip=True)
                
            postal = address_section.find('span', {'itemprop': 'postalCode'})
            if postal:
                result['postal_code'] = postal.get_text(strip=True)
                
            # Combine city and state for "Lives in" field
            if result['address_locality'] and result['address_region']:
                result['lives_in'] = f"{result['address_locality']}, {result['address_region']}"
            
            # Try to find county name
            address_text = address_section.get_text(strip=True)
            county_match = re.search(r'([A-Za-z\s]+County)', address_text)
            if county_match:
                result['country_name'] = county_match.group(1)
        
        # Extract phone numbers
        phone_sections = soup.find_all('div', {'class': 'col', 'bis_skin_checked': '1'})
        for section in phone_sections:
            phone_link = section.find('a', {'data-link-to-more': 'phone'})
            if phone_link:
                phone_span = phone_link.find('span', {'itemprop': 'telephone'})
                if phone_span:
                    phone_number = phone_span.get_text(strip=True)
                    phone_data = {
                        'number': phone_number,
                        'type': 'Unknown',
                        'last_reported': '',
                        'provider': ''
                    }
                    
                    # Get additional phone info
                    phone_info = section.find('div', {'class': 'mt-1 dt-ln'})
                    if phone_info:
                        info_text = phone_info.get_text(strip=True)
                        
                        # Extract phone type
                        if "Landline" in info_text:
                            phone_data['type'] = "Landline"
                        elif "Wireless" in info_text or "Cell" in info_text or "Mobile" in info_text:
                            phone_data['type'] = "Wireless"
                        
                        # Extract last reported date
                        last_reported_match = re.search(r'Last reported ([A-Za-z]+ \d{4})', info_text)
                        if last_reported_match:
                            phone_data['last_reported'] = f"Last reported {last_reported_match.group(1)}"
                        
                        # Extract provider
                        provider_lines = [line for line in info_text.split('\n') if 'Last reported' not in line and 'Primary' not in line and 'Landline' not in line and 'Wireless' not in line]
                        if provider_lines:
                            phone_data['provider'] = provider_lines[-1].strip()
                    
                    result['phones'].append(phone_data)
        
        # Extract emails
        email_divs = soup.find_all('div', {'class': 'col'})
        for div in email_divs:
            email_text = div.get_text(strip=True)
            if '@' in email_text and '.' in email_text:
                # Simple regex to extract email addresses
                email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', email_text)
                for email in email_matches:
                    if email not in result['emails']:
                        result['emails'].append(email)
        
        return result

    def search_by_name(self, name: str, city_state: Optional[str] = None, max_results: int = 1) -> List[SearchResult]:
        """Search by name and optionally city/state."""
        results = []
        search_option = "Name Search"
        
        # Parse name and location if provided in format "Name; City, State"
        if ";" in name and not city_state:
            parts = name.split(";", 1)
            name = parts[0].strip()
            city_state = parts[1].strip() if len(parts) > 1 else None
        
        # Construct search URL
        url = f"{self.NAME_SEARCH_URL}?name={quote_plus(name)}"
        if city_state:
            url += f"&citystatezip={quote_plus(city_state)}"
        
        # Make the request
        html = self._make_request(url)
        if not html:
            result = SearchResult(
                search_option=search_option,
                input_given=name + (f"; {city_state}" if city_state else ""),
                error="Failed to retrieve search results"
            )
            return [result]
        
        # Parse search results
        soup = BeautifulSoup(html, 'html.parser')
        person_cards = soup.find_all('div', class_='card card-body shadow-form card-summary')
        
        if not person_cards:
            result = SearchResult(
                search_option=search_option,
                input_given=name + (f"; {city_state}" if city_state else ""),
                error="No results found"
            )
            return [result]
        
        # Process each result up to max_results
        for i, card in enumerate(person_cards[:max_results]):
            # Extract person link
            link_elem = card.find('a', class_='btn btn-success btn-lg detail-link')
            if not link_elem or 'href' not in link_elem.attrs:
                continue
                
            person_link = f"{self.BASE_URL}{link_elem['href']}"
            
            # Get detailed profile info
            profile_info = self._extract_profile_info(person_link)
            if not profile_info:
                continue
                
            # Create search result
            result = SearchResult(
                search_option=search_option,
                input_given=name + (f"; {city_state}" if city_state else ""),
                first_name=profile_info.get('first_name'),
                last_name=profile_info.get('last_name'),
                age=profile_info.get('age'),
                lives_in=profile_info.get('lives_in'),
                street_address=profile_info.get('street_address'),
                address_locality=profile_info.get('address_locality'),
                address_region=profile_info.get('address_region'),
                postal_code=profile_info.get('postal_code'),
                country_name=profile_info.get('country_name'),
                emails=profile_info.get('emails', []),
                phones=profile_info.get('phones', []),
                person_link=person_link
            )
            
            results.append(result)
        
        # If no valid results were found
        if not results:
            result = SearchResult(
                search_option=search_option,
                input_given=name + (f"; {city_state}" if city_state else ""),
                error="No valid results could be processed"
            )
            return [result]
            
        return results

# Run the Flask app when executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default 5000
    port = int(os.environ.get("PORT", 5000))
    # Run with host set to 0.0.0.0 to make it accessible externally
    app.run(host="0.0.0.0", port=port, debug=False)
        
    def search_by_address(self, address: str, max_results: int = 1) -> List[SearchResult]:
        """Search by street address and city/state."""
        results = []
        search_option = "Address Search"
        
        # Parse address if provided in format "Street; City, State Zip"
        street = address
        city_state = None
        
        if ";" in address:
            parts = address.split(";", 1)
            street = parts[0].strip()
            city_state = parts[1].strip() if len(parts) > 1 else None
        
        # Construct search URL
        url = f"{self.ADDRESS_SEARCH_URL}?streetaddress={quote_plus(street)}"
        if city_state:
            url += f"&citystatezip={quote_plus(city_state)}"
        
        # Make the request
        html = self._make_request(url)
        if not html:
            result = SearchResult(
                search_option=search_option,
                input_given=address,
                error="Failed to retrieve search results"
            )
            return [result]
        
        # Parse search results
        soup = BeautifulSoup(html, 'html.parser')
        person_cards = soup.find_all('div', class_='card card-body shadow-form card-summary')
        
        if not person_cards:
            result = SearchResult(
                search_option=search_option,
                input_given=address,
                error="No results found"
            )
            return [result]
        
        # Process each result up to max_results
        for i, card in enumerate(person_cards[:max_results]):
            # Extract person link
            link_elem = card.find('a', class_='btn btn-success btn-lg detail-link')
            if not link_elem or 'href' not in link_elem.attrs:
                continue
                
            person_link = f"{self.BASE_URL}{link_elem['href']}"
            
            # Get detailed profile info
            profile_info = self._extract_profile_info(person_link)
            if not profile_info:
                continue
                
            # Create search result
            result = SearchResult(
                search_option=search_option,
                input_given=address,
                first_name=profile_info.get('first_name'),
                last_name=profile_info.get('last_name'),
                age=profile_info.get('age'),
                lives_in=profile_info.get('lives_in'),
                street_address=profile_info.get('street_address'),
                address_locality=profile_info.get('address_locality'),
                address_region=profile_info.get('address_region'),
                postal_code=profile_info.get('postal_code'),
                country_name=profile_info.get('country_name'),
                emails=profile_info.get('emails', []),
                phones=profile_info.get('phones', []),
                person_link=person_link
            )
            
            results.append(result)
        
        # If no valid results were found
        if not results:
            result = SearchResult(
                search_option=search_option,
                input_given=address,
                error="No valid results could be processed"
            )
            return [result]
            
        return results

# Run the Flask app when executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default 5000
    port = int(os.environ.get("PORT", 5000))
    # Run with host set to 0.0.0.0 to make it accessible externally
    app.run(host="0.0.0.0", port=port, debug=False)
    
    def search_by_phone(self, phone: str, max_results: int = 1) -> List[SearchResult]:
        """Search by phone number."""
        results = []
        search_option = "Phone Search"
        
        # Clean phone number - remove non-digits
        clean_phone = re.sub(r'\D', '', phone)
        
        # Construct search URL
        url = f"{self.PHONE_SEARCH_URL}?phoneno={clean_phone}"
        
        # Make the request
        html = self._make_request(url)
        if not html:
            result = SearchResult(
                search_option=search_option,
                input_given=phone,
                error="Failed to retrieve search results"
            )
            return [result]
        
        # Parse search results
        soup = BeautifulSoup(html, 'html.parser')
        person_cards = soup.find_all('div', class_='card card-body shadow-form card-summary')
        
        if not person_cards:
            result = SearchResult(
                search_option=search_option,
                input_given=phone,
                error="No results found"
            )
            return [result]
        
        # Process each result up to max_results
        for i, card in enumerate(person_cards[:max_results]):
            # Extract person link
            link_elem = card.find('a', class_='btn btn-success btn-lg detail-link')
            if not link_elem or 'href' not in link_elem.attrs:
                continue
                
            person_link = f"{self.BASE_URL}{link_elem['href']}"
            
            # Get detailed profile info
            profile_info = self._extract_profile_info(person_link)
            if not profile_info:
                continue
                
            # Create search result
            result = SearchResult(
                search_option=search_option,
                input_given=phone,
                first_name=profile_info.get('first_name'),
                last_name=profile_info.get('last_name'),
                age=profile_info.get('age'),
                lives_in=profile_info.get('lives_in'),
                street_address=profile_info.get('street_address'),
                address_locality=profile_info.get('address_locality'),
                address_region=profile_info.get('address_region'),
                postal_code=profile_info.get('postal_code'),
                country_name=profile_info.get('country_name'),
                emails=profile_info.get('emails', []),
                phones=profile_info.get('phones', []),
                person_link=person_link
            )
            
            results.append(result)
        
        # If no valid results were found
        if not results:
            result = SearchResult(
                search_option=search_option,
                input_given=phone,
                error="No valid results could be processed"
            )
            return [result]
            
        return results

# Run the Flask app when executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default 5000
    port = int(os.environ.get("PORT", 5000))
    # Run with host set to 0.0.0.0 to make it accessible externally
    app.run(host="0.0.0.0", port=port, debug=False)