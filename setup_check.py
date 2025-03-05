import sys
import subprocess
import os
from typing import Tuple, List

def check_chrome_version() -> Tuple[bool, str]:
    """Check if Chrome is installed and get its version."""
    try:
        # Different commands for different platforms
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return True, version
        elif sys.platform == "darwin":  # macOS
            process = subprocess.Popen(
                ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, _ = process.communicate()
            version = output.decode('utf-8').strip().replace('Google Chrome ', '')
            return True, version
        else:  # Linux
            process = subprocess.Popen(
                ['google-chrome', '--version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, _ = process.communicate()
            version = output.decode('utf-8').strip().replace('Google Chrome ', '')
            return True, version
    except Exception as e:
        return False, str(e)

def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher."""
    return sys.version_info >= (3, 8)

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed."""
    import importlib
    
    required_packages = {
        'pandas': 'pandas',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'selenium': 'selenium.webdriver',
        'webdriver_manager': 'webdriver_manager.chrome',
        'fake-useragent': 'fake_useragent',
        'python-dotenv': 'dotenv',
        'openpyxl': 'openpyxl'
    }
    
    missing = []
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(package_name)
        except Exception as e:
            print(f"Warning: Error checking {package_name}: {str(e)}")
            missing.append(package_name)
    
    return not missing, missing

def check_input_files() -> bool:
    """Check for required input files."""
    required_files = ['sample_input.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    return True

def verify_chrome_setup() -> bool:
    """Try to set up ChromeDriver using webdriver-manager."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        import platform
        
        print("Verifying ChromeDriver setup...")
        options = Options()
        options.add_argument('--headless=new')  # Run in headless mode for test
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-proxy-server')
        options.add_argument('--proxy-bypass-list=*')
        
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
            chrome_version = check_chrome_version()[1].split('.')[0]  # Get major version
            print(f"Detected Chrome version: {chrome_version}")
            
            options.binary_location = chrome_binary
            
            # Skip ChromeDriverManager for Apple Silicon and use local driver directly
            service = Service(executable_path=chromedriver_path)
            print(f"Using local ChromeDriver directly for Apple Silicon Mac")
        else:
            service = Service(ChromeDriverManager().install())
            
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.quit()
        return True
    except Exception as e:
        print(f"Error verifying Chrome setup: {str(e)}")
        return False

def main():
    """Run all setup checks."""
    print("Running setup checks...")
    print("-" * 50)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if check_python_version():
        print("✓ Python version OK")
        print(f"  Current version: {sys.version.split()[0]}")
    else:
        print("✗ Python version too old")
        print("  Please install Python 3.8 or higher")
        return False
    
    # Check Chrome installation
    print("\n2. Checking Chrome installation...")
    chrome_installed, chrome_version = check_chrome_version()
    if chrome_installed:
        print("✓ Chrome is installed")
        print(f"  Version: {chrome_version}")
    else:
        print("✗ Chrome not found")
        print("  Error:", chrome_version)
        print("  Please install Google Chrome from: https://www.google.com/chrome/")
        return False
    
    # Check dependencies
    print("\n3. Checking Python dependencies...")
    deps_ok, missing_deps = check_dependencies()
    if deps_ok:
        print("✓ All dependencies are installed")
    else:
        print("✗ Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nTo install missing dependencies, run:")
        print("pip install -r requirements.txt")
        return False
    
    # Verify ChromeDriver setup
    print("\n4. Verifying ChromeDriver setup...")
    if verify_chrome_setup():
        print("✓ ChromeDriver setup successful")
    else:
        print("✗ ChromeDriver setup failed")
        print("  Please check Chrome installation and try again")
        return False
    
    # Check input files
    print("\n5. Checking for required files...")
    if check_input_files():
        print("✓ All required files present")
    else:
        print("  Please make sure sample_input.csv exists")
    
    print("\n" + "-" * 50)
    if deps_ok and chrome_installed and check_python_version():
        print("\nAll checks passed! You can now run the scraper:")
        print("\nTo use CSV input:")
        print("python scraper.py sample_input.csv output.xlsx --batch-size 3")
        print("\nTo use Excel input:")
        print("python scraper.py input.xlsx output.xlsx --batch-size 3")
        return True
    else:
        print("\nPlease fix the above issues before running the scraper")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
