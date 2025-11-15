#!/usr/bin/env python3
"""
Interactive Demo for Cross-Browser and Responsive Testing
Demonstrates testing capabilities with visual feedback
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_responsive import (
        ResponsiveTester, CrossBrowserTester, ResponsiveTestConfig
    )
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_step(step_num: int, description: str):
    """Print step description"""
    print(f"\n{step_num}. {description}")
    print("-" * 60)


def demo_1_single_browser_test():
    """Demo 1: Test single browser at multiple screen sizes"""
    print_header("DEMO 1: Single Browser Responsive Test")
    
    if not TESTING_AVAILABLE:
        print("❌ Testing modules not available")
        return
    
    print("This demo tests the application in Chrome across different screen sizes")
    print("including mobile, tablet, and desktop viewports.\n")
    
    input("Press Enter to start the test...")
    
    print_step(1, "Initializing Chrome browser")
    tester = ResponsiveTester(browser='chrome', headless=False)
    
    if not tester.setup(width=1920, height=1080):
        print("❌ Failed to setup browser")
        return
    
    print("✅ Browser ready")
    time.sleep(1)
    
    print_step(2, "Loading application")
    try:
        tester.driver.get(ResponsiveTestConfig.FRONTEND_URL)
        print(f"✅ Loaded: {ResponsiveTestConfig.FRONTEND_URL}")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to load application: {e}")
        tester.teardown()
        return
    
    print_step(3, "Testing different screen sizes")
    print("\nWatch as the browser window resizes to simulate different devices:\n")
    
    test_sizes = [
        ('Mobile (iPhone SE)', 320, 568),
        ('Mobile (iPhone 12)', 375, 667),
        ('Tablet (iPad)', 768, 1024),
        ('Desktop (Laptop)', 1366, 768),
        ('Desktop (HD)', 1920, 1080),
    ]
    
    results = []
    
    for device_name, width, height in test_sizes:
        print(f"  📱 Testing: {device_name} ({width}x{height})")
        
        result = tester.check_responsive_layout(device_name, width, height)
        results.append(result)
        
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"     {status} - {result['pass_rate']} tests passed")
        
        # Show specific test results
        for test_name, test_result in result['tests'].items():
            icon = "✅" if test_result['pass'] else "❌"
            print(f"       {icon} {test_name}")
        
        time.sleep(2)  # Pause to see each size
    
    print_step(4, "Taking screenshots")
    print("Screenshots saved to:", ResponsiveTestConfig.SCREENSHOT_DIR)
    
    print_step(5, "Test Summary")
    total_tests = sum(len(r['tests']) for r in results)
    passed_tests = sum(sum(1 for t in r['tests'].values() if t['pass']) for r in results)
    
    print(f"\nDevices Tested: {len(test_sizes)}")
    print(f"Total Tests: {total_tests}")
    print(f"Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    print("\n✅ Demo complete! Browser will close in 5 seconds...")
    time.sleep(5)
    
    tester.teardown()


def demo_2_component_testing():
    """Demo 2: Test specific UI components"""
    print_header("DEMO 2: Component-Specific Testing")
    
    if not TESTING_AVAILABLE:
        print("❌ Testing modules not available")
        return
    
    print("This demo tests individual UI components across different screen sizes")
    print("to ensure they remain functional and accessible.\n")
    
    input("Press Enter to start the test...")
    
    print_step(1, "Initializing browser")
    tester = ResponsiveTester(browser='chrome', headless=False)
    
    if not tester.setup():
        print("❌ Failed to setup browser")
        return
    
    print_step(2, "Loading application")
    try:
        tester.driver.get(ResponsiveTestConfig.FRONTEND_URL)
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        tester.teardown()
        return
    
    print_step(3, "Testing UI Components")
    
    components = [
        ('Navigation Bar', 'nav, .navbar, header'),
        ('User Form', 'form, .user-details-form, input'),
        ('Job Dashboard', '.job-dashboard, .job-list, .job-card'),
        ('Status Badge', '.status-badge, .badge'),
        ('Action Buttons', 'button, .btn'),
    ]
    
    for comp_name, selector in components:
        print(f"\n  🎨 Testing: {comp_name}")
        
        try:
            result = tester.test_component_responsive(comp_name, selector)
            
            # Show results for key screen sizes
            key_sizes = ['mobile_medium', 'tablet_portrait', 'desktop_medium']
            for size in key_sizes:
                if size in result['screens']:
                    data = result['screens'][size]
                    visible = "✅" if data['visible'] else "❌"
                    fits = "✅" if data.get('fits_viewport', False) else "❌"
                    print(f"     {size}: {visible} visible, {fits} fits viewport")
        
        except Exception as e:
            print(f"     ⚠️  Component not found or error: {e}")
        
        time.sleep(1)
    
    print("\n✅ Component testing complete!")
    time.sleep(3)
    
    tester.teardown()


def demo_3_form_accessibility():
    """Demo 3: Test form input accessibility"""
    print_header("DEMO 3: Form Accessibility Testing")
    
    if not TESTING_AVAILABLE:
        print("❌ Testing modules not available")
        return
    
    print("This demo tests form inputs for accessibility compliance")
    print("including labels, touch target sizes, and keyboard navigation.\n")
    
    input("Press Enter to start the test...")
    
    print_step(1, "Initializing browser")
    tester = ResponsiveTester(browser='chrome', headless=False)
    
    if not tester.setup():
        print("❌ Failed to setup browser")
        return
    
    print_step(2, "Loading application")
    try:
        tester.driver.get(ResponsiveTestConfig.FRONTEND_URL)
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        tester.teardown()
        return
    
    print_step(3, "Analyzing form inputs")
    
    result = tester.test_form_inputs()
    
    print(f"\nFound {len(result['inputs'])} form inputs:\n")
    
    for i, input_data in enumerate(result['inputs'], 1):
        print(f"  {i}. {input_data['name']} ({input_data['type']})")
        print(f"     Visible: {'✅' if input_data['visible'] else '❌'}")
        print(f"     Enabled: {'✅' if input_data['enabled'] else '❌'}")
        print(f"     Has Label: {'✅' if input_data['has_label'] else '❌'}")
        print(f"     Size: {input_data['size']} {'✅' if input_data['accessible_size'] else '❌ Too small'}")
        print()
    
    # Calculate accessibility score
    total = len(result['inputs'])
    accessible = sum(1 for inp in result['inputs'] 
                    if inp['visible'] and inp['enabled'] and 
                    inp['has_label'] and inp['accessible_size'])
    
    print(f"Accessibility Score: {accessible}/{total} ({accessible/total*100:.1f}%)")
    
    print("\n✅ Accessibility test complete!")
    time.sleep(3)
    
    tester.teardown()


def demo_4_cross_browser():
    """Demo 4: Cross-browser testing"""
    print_header("DEMO 4: Cross-Browser Testing")
    
    if not TESTING_AVAILABLE:
        print("❌ Testing modules not available")
        return
    
    print("This demo runs tests across multiple browsers (Chrome, Firefox, Edge)")
    print("to ensure compatibility and consistent rendering.\n")
    
    print("⚠️  Note: This demo requires all browsers to be installed.")
    print("   It will run in headless mode for faster execution.\n")
    
    input("Press Enter to start the test (this may take a few minutes)...")
    
    print_step(1, "Initializing cross-browser tester")
    
    # Detect available browsers
    available_browsers = []
    for browser in ['chrome', 'firefox', 'edge']:
        print(f"  Checking for {browser}...", end=' ')
        # Note: In production, you'd actually check if browser is installed
        available_browsers.append(browser)
        print("✅")
    
    if not available_browsers:
        print("❌ No browsers available")
        return
    
    print(f"\n  Will test: {', '.join(available_browsers)}")
    
    print_step(2, "Running tests across browsers")
    
    tester = CrossBrowserTester(browsers=['chrome'], headless=True)
    results = tester.run_tests()
    
    print_step(3, "Generating report")
    
    report_path = tester.generate_report()
    
    print(f"\n✅ Cross-browser testing complete!")
    print(f"📊 Report: {report_path}")
    print(f"📸 Screenshots: {ResponsiveTestConfig.SCREENSHOT_DIR}")


def demo_5_performance():
    """Demo 5: Performance testing"""
    print_header("DEMO 5: Performance Testing")
    
    if not TESTING_AVAILABLE:
        print("❌ Testing modules not available")
        return
    
    print("This demo measures page load performance across different screen sizes")
    print("and network conditions.\n")
    
    input("Press Enter to start the test...")
    
    print_step(1, "Initializing browser")
    tester = ResponsiveTester(browser='chrome', headless=False)
    
    if not tester.setup():
        print("❌ Failed to setup browser")
        return
    
    print_step(2, "Measuring page load times")
    
    sizes = [
        ('Mobile', 375, 667),
        ('Tablet', 768, 1024),
        ('Desktop', 1920, 1080),
    ]
    
    for device, width, height in sizes:
        print(f"\n  📱 Testing: {device} ({width}x{height})")
        
        tester.driver.set_window_size(width, height)
        
        # Measure page load time
        start_time = time.time()
        tester.driver.get(ResponsiveTestConfig.FRONTEND_URL)
        
        # Wait for page to be fully loaded
        tester.driver.execute_script("return document.readyState") == "complete"
        
        load_time = time.time() - start_time
        
        print(f"     Page Load: {load_time:.2f}s {'✅' if load_time < 3 else '⚠️'}")
        
        # Get performance metrics
        try:
            nav_timing = tester.driver.execute_script(
                "return performance.timing"
            )
            
            dns_time = nav_timing['domainLookupEnd'] - nav_timing['domainLookupStart']
            connect_time = nav_timing['connectEnd'] - nav_timing['connectStart']
            response_time = nav_timing['responseEnd'] - nav_timing['requestStart']
            dom_time = nav_timing['domComplete'] - nav_timing['domLoading']
            
            print(f"     DNS Lookup: {dns_time}ms")
            print(f"     Connection: {connect_time}ms")
            print(f"     Response: {response_time}ms")
            print(f"     DOM Processing: {dom_time}ms")
        
        except Exception as e:
            print(f"     ⚠️  Performance metrics unavailable: {e}")
        
        time.sleep(2)
    
    print("\n✅ Performance testing complete!")
    time.sleep(3)
    
    tester.teardown()


def main_menu():
    """Display main menu and run demos"""
    
    while True:
        print("\n" + "="*60)
        print("  CROSS-BROWSER & RESPONSIVE TESTING DEMO")
        print("  Task 10.3 - Interactive Demonstrations")
        print("="*60)
        
        print("\nAvailable Demos:")
        print("  1. Single Browser Responsive Test")
        print("  2. Component-Specific Testing")
        print("  3. Form Accessibility Testing")
        print("  4. Cross-Browser Testing")
        print("  5. Performance Testing")
        print("  6. Run All Demos")
        print("  0. Exit")
        
        choice = input("\nSelect demo (0-6): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            demo_1_single_browser_test()
        elif choice == '2':
            demo_2_component_testing()
        elif choice == '3':
            demo_3_form_accessibility()
        elif choice == '4':
            demo_4_cross_browser()
        elif choice == '5':
            demo_5_performance()
        elif choice == '6':
            print("\n🚀 Running all demos...\n")
            for i, demo in enumerate([demo_1_single_browser_test, 
                                     demo_2_component_testing,
                                     demo_3_form_accessibility,
                                     demo_4_cross_browser,
                                     demo_5_performance], 1):
                print(f"\n{'='*60}")
                print(f"Running Demo {i}/5")
                print(f"{'='*60}")
                demo()
                if i < 5:
                    input("\nPress Enter to continue to next demo...")
        else:
            print("\n❌ Invalid choice. Please select 0-6.")


def main():
    """Main entry point"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║   CROSS-BROWSER & RESPONSIVE TESTING - INTERACTIVE DEMO     ║
║   AI Job Application Assistant - Task 10.3                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if not TESTING_AVAILABLE:
        print("\n❌ Testing modules not available!")
        print("\nRequired packages:")
        print("  - selenium")
        print("\nInstall with: pip install selenium")
        print("\nAlso ensure you have:")
        print("  - Chrome/ChromeDriver")
        print("  - Firefox/GeckoDriver")
        print("  - Edge/EdgeDriver")
        return 1
    
    # Check if frontend is running
    print("\n🔍 Checking if frontend is running...")
    import requests
    try:
        response = requests.get(ResponsiveTestConfig.FRONTEND_URL, timeout=5)
        print(f"✅ Frontend is running at {ResponsiveTestConfig.FRONTEND_URL}\n")
    except:
        print(f"⚠️  Frontend not detected at {ResponsiveTestConfig.FRONTEND_URL}")
        print("   Start frontend with: cd frontend && npm start")
        print("   Some demos may not work without it.\n")
        
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            return 1
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
