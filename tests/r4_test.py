import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (
    borrow_book_by_patron,
    return_book_by_patron
)

def test_return_book_valid_input():
    borrow_book_by_patron("056124", 1)
    success, message = return_book_by_patron("056124", 1)

    assert success == True
    assert "successfully returned" in message.lower()

def test_return_book_not_borrowed():
    borrow_book_by_patron("056124", 1)
    success, message = return_book_by_patron("333333", 1)
    return_book_by_patron("056124", 1)

    assert success == False
    assert "not borrowed" in message.lower()

def test_return_book_invalid_book_id():
    success, message = return_book_by_patron("123456", 20)

    assert success == False
    assert "book not found" in message.lower()

def test_return_book_invalid_patron_id():
    success, message = return_book_by_patron("123", 20)

    assert success == False
    assert "6 digits" in message

