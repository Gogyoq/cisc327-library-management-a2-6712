import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (
    get_patron_status_report
)

def test_patron_status_valid_input():
    results = get_patron_status_report("123456")

    assert "borrowed_books" in results
    assert "late_fees" in results
    assert "borrow_count" in results
    assert "borrow_history" in results

def test_patron_status_invalid_input():
    results = get_patron_status_report("123")

    assert "borrowed_books" not in results
    assert "late_fees" not in results
    assert "borrow_count" not in results
    assert "borrow_history" not in results
