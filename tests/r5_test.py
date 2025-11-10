import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
from services.library_service import (
    calculate_late_fee_for_book,
    borrow_book_by_patron,
    return_book_by_patron,
)
from flask import jsonify

def test_late_fee_valid_input():
    borrow_book_by_patron("123456", 1)
    late_fees = calculate_late_fee_for_book("123456", 1)
    assert isinstance(late_fees, dict)
    assert len(late_fees) > 0  # Should not be empty
    assert 'fee_amount' in late_fees
    assert 'days_overdue' in late_fees
    assert 'status' in late_fees

    return_book_by_patron("123456", 1)

def test_late_fee_invalid_patron_id():
    late_fees = calculate_late_fee_for_book("123", 1)
    success = False

    try:
        json.loads(jsonify(late_fees))  #check if return value converts to valid json
        success = True
    except:
        success = False

    assert success == False

def test_late_fee_invalid_book_id():
    late_fees = calculate_late_fee_for_book("123456", 20)
    success = False

    try:
        json.loads(jsonify(late_fees))  #check if return value converts to valid json
        success = True
    except:
        success = False

    assert success == False