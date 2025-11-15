#!/usr/bin/env python3
"""
Cross-Browser and Responsive Testing Suite
Tests UI components across different browsers, devices, and screen sizes
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")


class ResponsiveTestConfig:
    """Configuration for responsive testing"""
    
    # Screen sizes to test
    SCREEN_SIZES = {
        'mobile_small': (320, 568),      # iPhone SE
        'mobile_medium': (375, 667),     # iPhone 8
        'mobile_large': (414, 896),      # iPhone 11 Pro Max
        'tablet_portrait': (768, 1024),  # iPad
        'tablet_landscape': (1024, 768), # iPad Landscape
        'desktop_small': (1366, 768),    # Laptop
        'desktop_medium': (1920, 1080),  # Desktop
        'desktop_large': (2560, 1440),   # 2K Desktop
    }
    
    # Bootstrap breakpoints
    BREAKPOINTS = {
        'xs': 0,
        'sm': 576,
        'md': 768,
        'lg': 992,
        'xl': 1200,
        'xxl': 1400,
    }
    
    # Browsers to test
    BROWSERS = ['chrome', 'firefox', 'edge']
    
    # Frontend URL
    FRONTEND_URL = "http://localhost:3000"
    BACKEND_URL = "http://localhost:5000"
    
    # Timeout settings
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_TIMEOUT = 10
    
    # Screenshot directory
    SCREENSHOT_DIR = Path(__file__).parent.parent / "test_screenshots"


class BrowserDriver:
    """Manages browser driver instances"""
    
    def __init__(self, browser_name: str, headless: bool = False):
        self.browser_name = browser_name.lower()
        self.headless = headless
        self.driver = None
    
    def start(self, width: int = 1920, height: int = 1080):
        """Start browser driver"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not available")
        
        try:
            if self.browser_name == 'chrome':
                options = ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--window-size={width},{height}')
                self.driver = webdriver.Chrome(options=options)
            
            elif self.browser_name == 'firefox':
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=options)
                self.driver.set_window_size(width, height)
            
            elif self.browser_name == 'edge':
                options = EdgeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument(f'--window-size={width},{height}')
                self.driver = webdriver.Edge(options=options)
            
            else:
                raise ValueError(f"Unsupported browser: {self.browser_name}")
            
            self.driver.set_page_load_timeout(ResponsiveTestConfig.PAGE_LOAD_TIMEOUT)
            return self.driver
        
        except Exception as e:
            print(f"❌ Failed to start {self.browser_name}: {e}")
            return None
    
    def stop(self):
        """Stop browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


class ResponsiveTester:
    """Main responsive testing class"""
    
    def __init__(self, browser: str = 'chrome', headless: bool = False):
        self.browser_name = browser
        self.headless = headless
        self.driver = None
        self.test_results = []
        
        # Create screenshot directory
        ResponsiveTestConfig.SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    def setup(self, width: int = 1920, height: int = 1080):
        """Setup test environment"""
        browser_driver = BrowserDriver(self.browser_name, self.headless)
        self.driver = browser_driver.start(width, height)
        return self.driver is not None
    
    def teardown(self):
        """Cleanup test environment"""
        if self.driver:
            self.driver.quit()
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot"""
        if not self.driver:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.browser_name}_{name}_{timestamp}.png"
        filepath = ResponsiveTestConfig.SCREENSHOT_DIR / filename
        
        try:
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return ""
    
    def check_element_visible(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Check if element is visible"""
        try:
            element = WebDriverWait(self.driver, ResponsiveTestConfig.ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((by, selector))
            )
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False
    
    def get_element_size(self, selector: str, by: By = By.CSS_SELECTOR) -> Tuple[int, int]:
        """Get element dimensions"""
        try:
            element = self.driver.find_element(by, selector)
            size = element.size
            return (size['width'], size['height'])
        except:
            return (0, 0)
    
    def check_responsive_layout(self, screen_name: str, width: int, height: int) -> Dict[str, Any]:
        """Check responsive layout at specific screen size"""
        print(f"  Testing {screen_name} ({width}x{height})...")
        
        # Resize window
        self.driver.set_window_size(width, height)
        time.sleep(1)  # Wait for resize
        
        results = {
            'screen': screen_name,
            'width': width,
            'height': height,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Test 1: Check viewport
        viewport_width = self.driver.execute_script("return window.innerWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        results['tests']['viewport'] = {
            'pass': abs(viewport_width - width) < 50,  # Allow some tolerance
            'actual': f"{viewport_width}x{viewport_height}"
        }
        
        # Test 2: Check for horizontal scrollbar
        has_horizontal_scroll = self.driver.execute_script(
            "return document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )
        results['tests']['no_horizontal_scroll'] = {
            'pass': not has_horizontal_scroll,
            'message': 'No horizontal scrollbar' if not has_horizontal_scroll else 'Has horizontal scrollbar'
        }
        
        # Test 3: Check navigation/header
        nav_visible = self.check_element_visible('.navbar, header, [role="navigation"]')
        results['tests']['navigation_visible'] = {
            'pass': nav_visible,
            'message': 'Navigation visible' if nav_visible else 'Navigation not found'
        }
        
        # Test 4: Check main content area
        main_visible = self.check_element_visible('main, .container, [role="main"]')
        results['tests']['main_content_visible'] = {
            'pass': main_visible,
            'message': 'Main content visible' if main_visible else 'Main content not found'
        }
        
        # Test 5: Check buttons are touch-friendly (on mobile)
        if width < 768:  # Mobile
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button, a.btn, input[type="submit"]')
            touch_friendly = True
            for button in buttons[:5]:  # Check first 5 buttons
                size = button.size
                if size['width'] < 44 or size['height'] < 44:
                    touch_friendly = False
                    break
            results['tests']['touch_friendly_buttons'] = {
                'pass': touch_friendly,
                'message': 'Buttons ≥44px' if touch_friendly else 'Some buttons <44px'
            }
        
        # Test 6: Check text readability (font size)
        body_font_size = self.driver.execute_script(
            "return window.getComputedStyle(document.body).fontSize"
        )
        font_size_px = int(body_font_size.replace('px', ''))
        results['tests']['readable_text'] = {
            'pass': font_size_px >= 14,  # Minimum 14px
            'actual': body_font_size
        }
        
        # Test 7: Check for console errors
        logs = self.driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        results['tests']['no_console_errors'] = {
            'pass': len(errors) == 0,
            'count': len(errors),
            'errors': [e['message'] for e in errors[:3]]  # First 3 errors
        }
        
        # Take screenshot
        screenshot = self.take_screenshot(screen_name)
        results['screenshot'] = screenshot
        
        # Calculate pass rate
        passed = sum(1 for test in results['tests'].values() if test['pass'])
        total = len(results['tests'])
        results['pass_rate'] = f"{passed}/{total}"
        results['success'] = passed == total
        
        return results
    
    def test_component_responsive(self, component_name: str, selector: str) -> Dict[str, Any]:
        """Test specific component responsiveness"""
        print(f"\n  Testing component: {component_name}")
        
        results = {
            'component': component_name,
            'selector': selector,
            'screens': {}
        }
        
        for screen_name, (width, height) in ResponsiveTestConfig.SCREEN_SIZES.items():
            self.driver.set_window_size(width, height)
            time.sleep(0.5)
            
            screen_results = {
                'visible': self.check_element_visible(selector),
                'size': self.get_element_size(selector)
            }
            
            # Check if component fits in viewport
            if screen_results['size'][0] > 0:
                viewport_width = self.driver.execute_script("return window.innerWidth")
                screen_results['fits_viewport'] = screen_results['size'][0] <= viewport_width
            else:
                screen_results['fits_viewport'] = False
            
            results['screens'][screen_name] = screen_results
        
        return results
    
    def test_form_inputs(self) -> Dict[str, Any]:
        """Test form input accessibility and responsiveness"""
        print("\n  Testing form inputs...")
        
        results = {
            'test': 'form_inputs',
            'inputs': []
        }
        
        # Find all input elements
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input, textarea, select')
        
        for i, input_elem in enumerate(inputs[:10]):  # Test first 10
            input_type = input_elem.get_attribute('type') or 'text'
            input_name = input_elem.get_attribute('name') or f'input_{i}'
            
            input_results = {
                'name': input_name,
                'type': input_type,
                'visible': input_elem.is_displayed(),
                'enabled': input_elem.is_enabled(),
                'has_label': False
            }
            
            # Check for associated label
            input_id = input_elem.get_attribute('id')
            if input_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{input_id}"]')
                    input_results['has_label'] = True
                except:
                    pass
            
            # Check size
            size = input_elem.size
            input_results['size'] = f"{size['width']}x{size['height']}"
            input_results['accessible_size'] = size['height'] >= 32  # Minimum height
            
            results['inputs'].append(input_results)
        
        return results
    
    def run_full_test_suite(self, url: str = None) -> List[Dict[str, Any]]:
        """Run complete responsive test suite"""
        if url is None:
            url = ResponsiveTestConfig.FRONTEND_URL
        
        print(f"\n{'='*60}")
        print(f"Running Responsive Tests - {self.browser_name.upper()}")
        print(f"{'='*60}")
        
        all_results = []
        
        try:
            # Load the application
            print(f"\n📱 Loading application: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            
            # Test each screen size
            print("\n🔍 Testing screen sizes...")
            for screen_name, (width, height) in ResponsiveTestConfig.SCREEN_SIZES.items():
                result = self.check_responsive_layout(screen_name, width, height)
                all_results.append(result)
                
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"    {screen_name}: {status} ({result['pass_rate']})")
            
            # Test specific components (if they exist)
            print("\n🎨 Testing components...")
            components = [
                ('User Form', 'form, .user-details-form'),
                ('Job Dashboard', '.job-dashboard, .job-list'),
                ('Status Modal', '.modal, .status-modal'),
                ('Navigation', 'nav, .navbar'),
            ]
            
            for comp_name, selector in components:
                try:
                    comp_result = self.test_component_responsive(comp_name, selector)
                    all_results.append(comp_result)
                except Exception as e:
                    print(f"    ⚠️  {comp_name}: {e}")
            
            # Test forms
            form_result = self.test_form_inputs()
            all_results.append(form_result)
            
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
            import traceback
            traceback.print_exc()
        
        return all_results


class CrossBrowserTester:
    """Test across multiple browsers"""
    
    def __init__(self, browsers: List[str] = None, headless: bool = True):
        if browsers is None:
            browsers = ResponsiveTestConfig.BROWSERS
        self.browsers = browsers
        self.headless = headless
        self.results = {}
    
    def run_tests(self, url: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Run tests across all browsers"""
        if url is None:
            url = ResponsiveTestConfig.FRONTEND_URL
        
        print(f"\n{'='*60}")
        print("CROSS-BROWSER RESPONSIVE TESTING")
        print(f"Testing URL: {url}")
        print(f"Browsers: {', '.join(self.browsers)}")
        print(f"{'='*60}")
        
        for browser in self.browsers:
            print(f"\n🌐 Testing {browser.upper()}...")
            
            tester = ResponsiveTester(browser, self.headless)
            
            try:
                if tester.setup():
                    results = tester.run_full_test_suite(url)
                    self.results[browser] = results
                    print(f"\n✅ {browser.upper()} testing complete")
                else:
                    print(f"\n❌ Failed to setup {browser.upper()}")
                    self.results[browser] = []
            
            except Exception as e:
                print(f"\n❌ {browser.upper()} testing failed: {e}")
                self.results[browser] = []
            
            finally:
                tester.teardown()
        
        return self.results
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate test report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"responsive_test_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'browsers_tested': list(self.results.keys()),
            'results': self.results,
            'summary': self._generate_summary()
        }
        
        # Save JSON report
        output_path = ResponsiveTestConfig.SCREENSHOT_DIR / output_file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved: {output_path}")
        
        # Print summary
        self._print_summary()
        
        return str(output_path)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            'total_browsers': len(self.browsers),
            'browsers_passed': 0,
            'total_tests': 0,
            'tests_passed': 0,
            'screen_sizes_tested': len(ResponsiveTestConfig.SCREEN_SIZES),
            'critical_issues': [],
            'warnings': []
        }
        
        for browser, results in self.results.items():
            browser_passed = True
            
            for result in results:
                if 'tests' in result:
                    for test_name, test_result in result['tests'].items():
                        summary['total_tests'] += 1
                        if test_result['pass']:
                            summary['tests_passed'] += 1
                        else:
                            browser_passed = False
                            issue = {
                                'browser': browser,
                                'screen': result.get('screen', 'unknown'),
                                'test': test_name,
                                'details': test_result
                            }
                            
                            # Categorize issues
                            if 'console_errors' in test_name or 'horizontal_scroll' in test_name:
                                summary['critical_issues'].append(issue)
                            else:
                                summary['warnings'].append(issue)
            
            if browser_passed and len(results) > 0:
                summary['browsers_passed'] += 1
        
        summary['pass_rate'] = f"{summary['tests_passed']}/{summary['total_tests']}"
        summary['success_rate'] = (summary['tests_passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        return summary
    
    def _print_summary(self):
        """Print test summary"""
        summary = self._generate_summary()
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Browsers Tested: {summary['total_browsers']}")
        print(f"Browsers Passed: {summary['browsers_passed']}/{summary['total_browsers']}")
        print(f"Screen Sizes: {summary['screen_sizes_tested']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Tests Passed: {summary['pass_rate']} ({summary['success_rate']:.1f}%)")
        print(f"Critical Issues: {len(summary['critical_issues'])}")
        print(f"Warnings: {len(summary['warnings'])}")
        
        if summary['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in summary['critical_issues'][:5]:
                print(f"  - {issue['browser']}/{issue['screen']}: {issue['test']}")
        
        if summary['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in summary['warnings'][:5]:
                print(f"  - {warning['browser']}/{warning['screen']}: {warning['test']}")
        
        print(f"\n{'='*60}")


def main():
    """Main test runner"""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium is required for responsive testing")
        print("Install with: pip install selenium")
        return 1
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     CROSS-BROWSER & RESPONSIVE TESTING SUITE               ║
║     AI Job Application Assistant - Task 10.3               ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check if frontend is running
    import requests
    try:
        response = requests.get(ResponsiveTestConfig.FRONTEND_URL, timeout=5)
        print(f"✅ Frontend is running at {ResponsiveTestConfig.FRONTEND_URL}")
    except:
        print(f"⚠️  Frontend not detected at {ResponsiveTestConfig.FRONTEND_URL}")
        print("   Start frontend with: cd frontend && npm start")
        print("   Tests will run but may fail\n")
    
    # Run tests
    tester = CrossBrowserTester(
        browsers=['chrome'],  # Start with Chrome, add others as available
        headless=True  # Set to False to see browser
    )
    
    results = tester.run_tests()
    report_path = tester.generate_report()
    
    print(f"\n✅ Testing complete!")
    print(f"📸 Screenshots saved to: {ResponsiveTestConfig.SCREENSHOT_DIR}")
    print(f"📊 Report saved to: {report_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
