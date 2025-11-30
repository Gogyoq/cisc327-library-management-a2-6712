import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import os
import signal

@pytest.fixture(scope="module")
def flask_app():
    """Start Flask app before tests and stop after"""
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    process = subprocess.Popen(
        ['python', 'app.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(2)
    
    yield process
    
    # Cleanup: stop Flask app
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

@pytest.fixture(scope="function")
def page(flask_app, browser):
    """Create a new page for each test"""
    page = browser.new_page()
    yield page
    page.close()

class TestLibraryE2E:
    """End-to-end tests for library management system"""
    
    BASE_URL = "http://localhost:5000"
    
    def test_add_book_and_verify_in_catalog(self, page: Page):
        """
        Test Flow:
        1. Navigate to add book page
        2. Fill in book details (title, author, ISBN, copies)
        3. Submit the form
        4. Navigate to catalog page
        5. Verify the book appears in the catalog
        """
        # Navigate to add book page
        page.goto(f"{self.BASE_URL}/add_book")
        
        # Fill in book details
        test_title = "Project Hail Mary"
        test_author = "Andy Weir"
        test_isbn = "9780135957059"
        test_copies = "3"
        
        page.fill('input[name="title"]', test_title)
        page.fill('input[name="author"]', test_author)
        page.fill('input[name="isbn"]', test_isbn)
        page.fill('input[name="total_copies"]', test_copies)
        
        # Submit the form
        page.click('button[type="submit"]')
        
        # Wait for navigation or success message
        page.wait_for_load_state("networkidle")
        
        # Navigate to catalog page to verify book was added
        page.goto(f"{self.BASE_URL}/catalog")
        
        # Verify the book appears in the catalog
        expect(page.locator("body")).to_contain_text(test_title)
        expect(page.locator("body")).to_contain_text(test_author)
        expect(page.locator("body")).to_contain_text(test_isbn)
    
    def test_borrow_book_flow(self, page: Page):
        """
        Test Flow:
        1. Navigate to catalog
        2. Verify books are available
        3. Navigate to borrow book page
        4. Enter patron ID and ISBN
        5. Submit borrow request
        6. Verify confirmation message appears
        """
        # First, ensure there's a book in the catalog by adding one
        page.goto(f"{self.BASE_URL}/add_book")
        
        # Fill in book details
        test_title = "Hunger Games"
        test_author = "Suzanne Collins"
        test_isbn = "9780135957058"
        test_copies = "3"
        
        page.fill('input[name="title"]', test_title)
        page.fill('input[name="author"]', test_author)
        page.fill('input[name="isbn"]', test_isbn)
        page.fill('input[name="total_copies"]', test_copies)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Navigate to catalog to see available books
        page.goto(f"{self.BASE_URL}/catalog")
        
        # Verify the book appears in catalog
        expect(page.locator("body")).to_contain_text(test_title)
        expect(page.locator("body")).to_contain_text("Available")
        
        # Fill in patron ID (6 digits as per the pattern requirement)
        test_patron_id = "123456"
        
        # Find the patron_id input field for the first available book
        patron_input = page.locator('input[name="patron_id"]').first
        patron_input.fill(test_patron_id)
        
        # Click the borrow button
        borrow_button = page.locator('button.btn-success').first
        borrow_button.click()
        
        # Wait for page to reload
        page.wait_for_load_state("networkidle")
        
        # Verify success/confirmation message appears
        # Flask flash messages typically appear at the top of the page
        page_content = page.locator("body").inner_text().lower()
        
        # Check for success indicators
        success_indicators = [
            "success",
            "borrowed",
            "checkout",
            "confirmed",
            "borrow"
        ]
        
        assert any(indicator in page_content for indicator in success_indicators), \
            f"No confirmation message found. Page content: {page_content}"