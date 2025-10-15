"""
SuccessFactors WebDriver Backend
A Selenium-based scraper for SuccessFactors login and data extraction
"""

import os
import time
import logging
import traceback
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('successfactors_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SuccessFactorsScraper:
    """
    A Selenium WebDriver-based scraper for SuccessFactors
    """

    def __init__(self, username=None, password=None, company_id=None):
        """Initialize the SuccessFactors scraper"""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.base_url = "https://salesdemo.successfactors.eu"
        
        # Configuration - use parameters or environment variables
        self.username = username or os.getenv('SF_USERNAME', '')
        self.password = password or os.getenv('SF_PASSWORD', '')
        self.company_id = company_id or os.getenv('SF_COMPANY_ID', '')
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.implicit_wait = int(os.getenv('IMPLICIT_WAIT', '10'))
        self.page_load_timeout = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

        logger.info("SuccessFactors scraper initialized")

    def setup_driver(self) -> None:
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless')

            # Performance optimizations for faster loading
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

            # Setup Chrome service with faster options
            service = Service(ChromeDriverManager().install())

            # Initialize WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(self.implicit_wait)
            self.driver.set_page_load_timeout(self.page_load_timeout)

            # Initialize WebDriverWait with shorter timeout
            self.wait = WebDriverWait(self.driver, self.implicit_wait)

            logger.info("WebDriver setup completed successfully")

        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise

    def navigate_to_login(self) -> bool:
        """Navigate to the SuccessFactors login page"""
        try:
            logger.info(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)

            # Wait for page to load
            self.wait.until(EC.presence_of_element_located(
                (By.TAG_NAME, "body")))

            logger.info("Successfully navigated to SuccessFactors")
            return True

        except TimeoutException:
            logger.error("Timeout while loading SuccessFactors page")
            return False
        except Exception as e:
            logger.error(f"Error navigating to SuccessFactors: {str(e)}")
            return False

    def handle_company_entry(self) -> bool:
        """
        Handle the company entry page (first step in SuccessFactors login)
        Returns True if successfully navigated to login page, False otherwise
        """
        try:
            if not self.company_id:
                logger.error("Company ID not provided in environment variables")
                return False

            logger.info("Handling company entry page")

            # Check if we're on the company entry page
            try:
                # Look for the company ID input field (fast check)
                company_input = self.fast_wait_for_element(By.ID, "__input0-inner", 2)
                if not company_input:
                    # Try alternative selector
                    company_input = self.fast_wait_for_element(By.CSS_SELECTOR, "input[placeholder*='Company' i]", 1)
                
                if company_input:
                    logger.info("Found company entry page")
                    
                    # Fast input using JavaScript
                    self.fast_send_keys(company_input, self.company_id)
                    logger.info(f"Company ID entered")
                    
                    # Find and click the Continue button (fast)
                    continue_button = self.fast_wait_for_element(By.ID, "continueToLoginBtn", 2)
                    if not continue_button:
                        continue_button = self.fast_wait_for_element(By.CSS_SELECTOR, "button:contains('Continue')", 1)
                    
                    if continue_button:
                        continue_button.click()
                        logger.info("Continue clicked")
                    else:
                        logger.warning("Continue button not found")
                else:
                    logger.info("No company entry page found")
                
                # Wait for navigation to login page (faster check)
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda driver: "login" in driver.current_url.lower() or 
                                     len(driver.find_elements(By.CSS_SELECTOR, "input[type='password']")) > 0
                    )
                except TimeoutException:
                    pass  # Continue anyway, might already be ready
                
                return True
                
            except TimeoutException:
                logger.info("Company entry page not found - might already be on login page")
                return True
                
        except Exception as e:
            logger.error(f"Error handling company entry: {str(e)}")
            return False

    def login(self) -> bool:
        """
        Perform login to SuccessFactors
        Returns True if login is successful, False otherwise
        """
        try:
            if not self.username or not self.password:
                logger.error(
                    "Username or password not provided in environment variables")
                return False

            logger.info("Attempting to login to SuccessFactors")

            # First, handle company entry if present
            if not self.handle_company_entry():
                logger.error("Failed to handle company entry page")
                return False

            # Common selectors for SuccessFactors login elements
            username_selectors = [
                "input[name='username']",
                "input[id='username']",
                "input[name='j_username']",
                "input[id='j_username']",
                "#username",
                "#j_username",
                "input[placeholder*='username']",
                "input[placeholder*='Username']"
            ]

            password_selectors = [
                "input[name='password']",
                "input[id='password']",
                "input[name='j_password']",
                "input[id='j_password']",
                "#password",
                "#j_password",
                "input[type='password']"
            ]

            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[id*='login']",
                "input[value*='Login']",
                "input[value*='Sign In']",
                ".login-button",
                "#loginButton",
                "button:contains('Login')",
                "button:contains('Sign In')"
            ]

            # Fast approach: Find all input fields at once
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input")))
            except TimeoutException:
                logger.error("No input fields found on page")
                return False

            # Find username field (try most common first, then fallback)
            username_element = None
            username_selectors = [
                "input[type='text']:first-of-type",  # Usually first text input
                "input[name*='user']", "input[id*='user']",  # Common patterns
                "input[placeholder*='user' i]", "input[placeholder*='User']",
                "input[type='text']", "input[type='email']"  # Generic fallbacks
            ]
            
            for selector in username_selectors:
                username_element = self.fast_wait_for_element(By.CSS_SELECTOR, selector, 1)
                if username_element:
                    break

            if not username_element:
                logger.error("Could not find username field")
                return False

            # Find password field (faster - just look for password type)
            password_element = self.fast_wait_for_element(By.CSS_SELECTOR, "input[type='password']", 2)
            if not password_element:
                logger.error("Could not find password field")
                return False

            # Fast input: Clear and fill both fields quickly
            self.fast_send_keys(username_element, self.username)
            self.fast_send_keys(password_element, self.password)

            # Find login button (fast approach)
            login_button = None
            button_selectors = [
                "button[type='submit']",  # Most common
                "input[type='submit']",   # Traditional submit
                "button:contains('Login')", "button:contains('Sign')",  # Text-based
                "*[onclick*='login' i]", "*[onclick*='submit' i]"  # Event-based
            ]
            
            for selector in button_selectors:
                login_button = self.fast_wait_for_element(By.CSS_SELECTOR, selector, 1)
                if login_button:
                    break
            
            # Fallback: find any clickable button
            if not login_button:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
                if buttons:
                    login_button = buttons[0]  # Take first button as fallback

            if not login_button:
                logger.error("Could not find login button")
                return False

            # Click login button
            login_button.click()
            logger.info("Login submitted")

            # Wait for login to complete (check for dashboard or home page)
            try:
                # Wait for URL change or specific post-login elements
                self.wait.until(
                    lambda driver: driver.current_url != self.base_url)

                # Quick check for successful login (no delay needed)
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "error" not in current_url.lower():
                    logger.info(
                        f"Login successful! Redirected to: {current_url}")
                    return True
                else:
                    logger.error(
                        "Login failed - still on login page or error page")
                    return False

            except TimeoutException:
                logger.error("Timeout waiting for login to complete")
                return False

        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            return False

    def extract_data(self):
        """Create and return a data extractor instance"""
        from data_extractor import SuccessFactorsDataExtractor
        return SuccessFactorsDataExtractor(self)

    def extract_roles_data(self) -> List[Dict[str, Any]]:
        """
        Extract role data from the UI table at /sf/authz#/roleList
        Returns a list of role dictionaries
        """
        try:
            logger.info("Navigating to role list page...")
            
            # Navigate to the role list page
            role_url = f"{self.base_url}/sf/authz#/roleList"
            self.driver.get(role_url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Debug: Take screenshot and log current URL
            logger.info(f"Current URL after navigation: {self.driver.current_url}")
            screenshot_path = self.take_screenshot("role_page_debug.png")
            logger.info(f"Debug screenshot saved: {screenshot_path}")
            
            # Log page title and some source
            logger.info(f"Page title: {self.driver.title}")
            page_source = self.driver.page_source
            logger.info(f"Page source length: {len(page_source)}")
            
            # Check if table exists with different selectors
            table_found = False
            working_table_selector = None
            table_selectors = [
                "ui5-table[id='rolelist-table']",
                "ui5-table",
                "[role='table']",
                "table",
                ".sapMList",
                ".sapMTable",
                "[data-sap-ui-table]",
                "[class*='table']"
            ]
            
            for selector in table_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                        table_found = True
                        working_table_selector = selector
                        break
                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {str(e)}")
            
            if not table_found:
                logger.warning("No table elements found with any selector")
                # Save page source for debugging
                try:
                    with open("role_page_source.html", 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    logger.info("Page source saved to role_page_source.html")
                except Exception as save_error:
                    logger.warning(f"Could not save page source: {str(save_error)}")
                return []
            
            # Wait for the page to load and table to be present
            logger.info(f"Waiting for role list table to load using selector: {working_table_selector}")
            try:
                # Try the working selector first
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, working_table_selector)))
            except TimeoutException:
                logger.warning(f"Timeout waiting for '{working_table_selector}', trying fallback approach")
                # Wait a bit more and continue anyway
                time.sleep(3)
            
            # Additional wait for dynamic content to load
            time.sleep(3)
            
            # Try different row selectors based on what table type we found
            row_selectors = []
            if "ui5-table" in working_table_selector:
                row_selectors = ["ui5-table-row", "ui5-table-row-base", "[role='row']"]
            else:
                row_selectors = ["tr", "[role='row']", ".sapMListItem", ".sapMTableRow"]
            
            # Find all table rows
            table_rows = []
            for row_selector in row_selectors:
                try:
                    table_rows = self.driver.find_elements(By.CSS_SELECTOR, row_selector)
                    if table_rows:
                        logger.info(f"Found {len(table_rows)} rows using selector: {row_selector}")
                        break
                except Exception as e:
                    logger.debug(f"Row selector '{row_selector}' failed: {str(e)}")
            
            if not table_rows:
                logger.warning("No table rows found with any selector")
                return []
            
            logger.info(f"Found {len(table_rows)} table rows")
            
            roles_data = []
            
            for row_idx, row in enumerate(table_rows):
                try:
                    # Extract data from each cell using multiple approaches
                    role_data = {}
                    
                    # Try to get all cell elements from the row
                    cells = []
                    cell_selectors = [
                        "ui5-table-cell",
                        "td", 
                        "[role='cell']",
                        "[data-testid*='cell']",
                        ".sapMText",
                        ".sapMLabel"
                    ]
                    
                    for cell_selector in cell_selectors:
                        try:
                            cells = row.find_elements(By.CSS_SELECTOR, cell_selector)
                            if cells:
                                break
                        except Exception:
                            continue
                    
                    # If we found cells, try to extract data positionally
                    if cells and len(cells) >= 3:  # Assume at least 3 columns
                        try:
                            # Extract by position (adjust indices based on actual table structure)
                            role_data['id'] = cells[0].text.strip() if len(cells) > 0 else ""
                            role_data['name'] = cells[1].text.strip() if len(cells) > 1 else ""
                            role_data['user_type'] = cells[2].text.strip() if len(cells) > 2 else ""
                            role_data['description'] = cells[3].text.strip() if len(cells) > 3 else ""
                            role_data['status'] = cells[4].text.strip() if len(cells) > 4 else ""
                            role_data['rbp_only'] = cells[5].text.strip() if len(cells) > 5 else ""
                            role_data['last_modified'] = cells[6].text.strip() if len(cells) > 6 else ""
                            role_data['actions'] = cells[7].text.strip() if len(cells) > 7 else ""
                        except Exception as pos_error:
                            logger.debug(f"Positional extraction failed for row {row_idx}: {str(pos_error)}")
                    
                    # Fallback: Try data-testid attributes (original approach)
                    if not any(role_data.values()):  # If positional approach didn't work
                        try:
                            # Role ID
                            try:
                                id_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-role-id']")
                                role_data['id'] = id_cell.text.strip()
                            except NoSuchElementException:
                                role_data['id'] = ""
                            
                            # Name
                            try:
                                name_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-name']")
                                role_data['name'] = name_cell.text.strip()
                            except NoSuchElementException:
                                role_data['name'] = ""
                            
                            # User Type
                            try:
                                user_type_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-user-type']")
                                role_data['user_type'] = user_type_cell.text.strip()
                            except NoSuchElementException:
                                role_data['user_type'] = ""
                            
                            # Description
                            try:
                                desc_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-description']")
                                role_data['description'] = desc_cell.text.strip()
                            except NoSuchElementException:
                                role_data['description'] = ""
                            
                            # Status
                            try:
                                status_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-status']")
                                role_data['status'] = status_cell.text.strip()
                            except NoSuchElementException:
                                role_data['status'] = ""
                            
                            # RBP-Only
                            try:
                                rbp_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-rbp-only']")
                                role_data['rbp_only'] = rbp_cell.text.strip()
                            except NoSuchElementException:
                                role_data['rbp_only'] = ""
                            
                            # Last Modified
                            try:
                                last_mod_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-last-modified']")
                                role_data['last_modified'] = last_mod_cell.text.strip()
                            except NoSuchElementException:
                                role_data['last_modified'] = ""
                            
                            # Actions
                            try:
                                actions_cell = row.find_element(By.CSS_SELECTOR, "[data-testid='rolelist-table-cell-actions']")
                                role_data['actions'] = actions_cell.text.strip()
                            except NoSuchElementException:
                                role_data['actions'] = ""
                                
                        except Exception as testid_error:
                            logger.debug(f"Data-testid extraction failed for row {row_idx}: {str(testid_error)}")
                    
                    # Final fallback: Just get all text from the row
                    if not any(role_data.values()):
                        try:
                            all_text = row.text.strip()
                            if all_text:
                                # Split by common delimiters and assign to fields
                                parts = [part.strip() for part in all_text.split('\n') if part.strip()]
                                if parts:
                                    role_data['id'] = parts[0] if len(parts) > 0 else ""
                                    role_data['name'] = parts[1] if len(parts) > 1 else ""
                                    role_data['user_type'] = parts[2] if len(parts) > 2 else ""
                                    role_data['description'] = parts[3] if len(parts) > 3 else ""
                                    role_data['status'] = parts[4] if len(parts) > 4 else ""
                                    role_data['rbp_only'] = parts[5] if len(parts) > 5 else ""
                                    role_data['last_modified'] = parts[6] if len(parts) > 6 else ""
                                    role_data['actions'] = ""
                        except Exception as text_error:
                            logger.debug(f"Text extraction failed for row {row_idx}: {str(text_error)}")
                    
                    # Only add if we have at least an ID or name
                    if role_data.get('id') or role_data.get('name'):
                        roles_data.append(role_data)
                        logger.debug(f"Extracted role {row_idx + 1}: {role_data.get('id', 'N/A')} - {role_data.get('name', 'N/A')}")
                    else:
                        logger.debug(f"Skipped empty row {row_idx + 1}")
                        
                except Exception as e:
                    logger.warning(f"Error extracting data from row {row_idx + 1}: {str(e)}")
                    continue
            
            logger.info(f"Successfully extracted {len(roles_data)} roles")
            return roles_data
            
        except Exception as e:
            logger.error(f"Error extracting roles data: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    def fetch_role_permissions(self, role_id: str) -> Dict[str, Any]:
        """
        Fetch permissions for a specific role using OData API
        Returns the permission data as a dictionary
        """
        try:
            logger.info(f"Fetching permissions for role ID: {role_id}")
            
            # OData service root
            service_root = f"{self.base_url}/odatav4/iam/authorization/PAP.svc/v1/"
            permissions_url = f"{service_root}PermissionRoleEntity({role_id})?$expand=categories"
            
            # Use JavaScript fetch via Selenium to leverage browser session
            script = """
            var callback = arguments[arguments.length - 1];
            var url = arguments[0];
            
            fetch(url, {
              method: "GET",
              credentials: "include",
              headers: {
                "accept": "application/json",
                "odata-version": "4.0",
                "content-type": "application/json"
              }
            })
            .then(function(response) {
              if (!response.ok) {
                throw new Error("HTTP " + response.status + " - " + response.statusText);
              }
              return response.json();
            })
            .then(function(data) {
              callback({success: true, data: data});
            })
            .catch(function(error) {
              console.error("Fetch error:", error);
              callback({success: false, error: error.message});
            });
            """
            
            logger.debug(f"Making request to: {permissions_url}")
            
            # Set script timeout for async execution
            self.driver.set_script_timeout(30)
            
            result = self.driver.execute_async_script(script, permissions_url)
            
            if result and result.get('success'):
                logger.info(f"Successfully fetched permissions for role {role_id}")
                return result.get('data', {})
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                logger.error(f"Failed to fetch permissions for role {role_id}: {error_msg}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching permissions for role {role_id}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {}

    def get_page_type(self) -> str:
        """
        Determine what type of page we're currently on
        Returns: 'company_entry', 'login', 'dashboard', 'unknown'
        """
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower();
            
            # Check for company entry page
            if "companyentry" in current_url.lower() or "company id" in page_source:
                return "company_entry"
            
            # Check for login page
            if any(field in page_source for field in ["username", "password", "j_username", "j_password"]):
                return "login"
            
            # Check for dashboard/home page
            if any(indicator in page_source for indicator in ["dashboard", "home", "welcome", "logout"]):
                return "dashboard"
                
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error determining page type: {str(e)}")
            return "unknown"

    def fast_send_keys(self, element, text):
        """
        Send keys faster using JavaScript execution
        """
        try:
            # Use JavaScript for faster input
            self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", element, text)
            return True
        except Exception:
            # Fallback to normal send_keys
            element.clear()
            element.send_keys(text)
            return True

    def fast_wait_for_element(self, by_method, selector, timeout=2):
        """
        Quick wait for an element with shorter timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            return element
        except TimeoutException:
            return None

    def wait_for_element_and_get(self, by_method, selector, timeout=10):
        """
        Wait for an element and return it, or None if not found
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            return element
        except TimeoutException:
            logger.debug(f"Element not found: {selector}")
            return None

    def get_current_page_info(self) -> Dict[str, Any]:
        """Get information about the current page"""
        try:
            page_type = self.get_page_type()
            return {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_type': page_type,
                'page_source_length': len(self.driver.page_source)
            }
        except Exception as e:
            logger.error(f"Error getting page info: {str(e)}")
            return {}

    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"

            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved as {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return ""

    def close(self) -> None:
        """Close the WebDriver and clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")

    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """Main function to demonstrate the scraper"""
    try:
        with SuccessFactorsScraper() as scraper:
            # Navigate to login page
            if not scraper.navigate_to_login():
                logger.error("Failed to navigate to login page")
                return

            # Check what page we're on initially
            initial_page_info = scraper.get_current_page_info()
            logger.info(f"Initial page: {initial_page_info}")

            # Take screenshot of initial page
            scraper.take_screenshot("initial_page.png")

            # Attempt login (this will handle company entry if needed)
            if scraper.login():
                logger.info("Login successful!")

                # Get page info after login
                page_info = scraper.get_current_page_info()
                logger.info(f"After login page info: {page_info}")

                # Take screenshot after login
                scraper.take_screenshot("after_login.png")

                # Login complete - no waiting needed

            else:
                logger.error("Login failed!")
                scraper.take_screenshot("login_failed.png")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")


if __name__ == "__main__":
    main()
