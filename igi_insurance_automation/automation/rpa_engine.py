"""
RPA Engine using Selenium
Template-based automation for form filling and submission
"""

import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Handle imports for both module and direct execution
try:
    from ..config import RPA_TIMEOUT, RPA_HEADLESS
    from ..database.db import get_session
    from ..database.models import AutomationLog
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import RPA_TIMEOUT, RPA_HEADLESS
    from database.db import get_session
    from database.models import AutomationLog


class RPAEngine:
    """RPA Engine for automated form filling and submission"""
    
    def __init__(self):
        self.driver = None
        self.timeout = RPA_TIMEOUT
    
    def initialize_browser(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            if RPA_HEADLESS:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            return True, "Browser initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize browser: {str(e)}"
    
    def close_browser(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                return True, "Browser closed successfully"
            except Exception as e:
                return False, f"Error closing browser: {str(e)}"
        return True, "Browser already closed"
    
    def execute_automation_template(self, template):
        """
        Execute automation based on template
        
        Template format:
        {
            'url': 'https://example.com/form',
            'actions': [
                {'type': 'fill', 'selector': 'input[name="name"]', 'value': 'John Doe'},
                {'type': 'click', 'selector': 'button[type="submit"]'},
                {'type': 'wait', 'seconds': 2}
            ]
        }
        """
        if not self.driver:
            return False, "Browser not initialized. Please initialize browser first."
        
        try:
            # Navigate to URL
            url = template.get('url')
            if url:
                self.driver.get(url)
                time.sleep(1)  # Allow page to load
            
            # Execute actions
            for action in template.get('actions', []):
                action_type = action.get('type')
                
                if action_type == 'fill':
                    self._fill_field(action.get('selector'), action.get('value'))
                
                elif action_type == 'click':
                    self._click_element(action.get('selector'))
                
                elif action_type == 'wait':
                    time.sleep(action.get('seconds', 1))
                
                elif action_type == 'select':
                    self._select_option(action.get('selector'), action.get('value'))
            
            # Log successful automation
            self._log_automation(
                'RPA Execution',
                'Success',
                f"Successfully executed automation template for {url}",
                str(template)
            )
            
            return True, "Automation executed successfully"
        
        except Exception as e:
            # Log failed automation
            self._log_automation(
                'RPA Execution',
                'Failed',
                f"Failed to execute automation template",
                str(e)
            )
            return False, f"Automation failed: {str(e)}"
    
    def _fill_field(self, selector, value):
        """Fill a form field"""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(str(value))
        except Exception as e:
            raise Exception(f"Failed to fill field {selector}: {str(e)}")
    
    def _click_element(self, selector):
        """Click an element"""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
        except Exception as e:
            raise Exception(f"Failed to click element {selector}: {str(e)}")
    
    def _select_option(self, selector, value):
        """Select an option from dropdown"""
        try:
            from selenium.webdriver.support.ui import Select
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            select = Select(element)
            select.select_by_visible_text(value)
        except Exception as e:
            raise Exception(f"Failed to select option {selector}: {str(e)}")
    
    def fill_streamlit_form(self, form_data):
        """
        Specialized method to simulate form filling in Streamlit
        (For demo purposes - logs the action)
        """
        try:
            self._log_automation(
                'RPA - Streamlit Form Fill',
                'Success',
                'Simulated form filling in Streamlit application',
                str(form_data)
            )
            return True, "Form data processed successfully"
        except Exception as e:
            return False, f"Failed to process form data: {str(e)}"
    
    def _log_automation(self, automation_type, status, message, details):
        """Log automation activity to database"""
        try:
            session = get_session()
            log = AutomationLog(
                automation_type=automation_type,
                status=status,
                message=message,
                details=details
            )
            session.add(log)
            session.commit()
            session.close()
        except Exception as e:
            print(f"Failed to log automation: {str(e)}")
