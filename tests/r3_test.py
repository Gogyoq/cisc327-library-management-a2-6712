import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (
    borrow_book_by_patron,
    return_book_by_patron,
    add_book_to_catalog
)

def test_borrow_book_valid_input():
    success, message = borrow_book_by_patron("123456", 1)
    return_book_by_patron("123456", 1)

    assert success == True
    assert "successfully borrowed" in message.lower() and "database error" not in message.lower()

def test_borrow_book_invalid_patron_id():
    success, message = borrow_book_by_patron("123", 1)

    assert success == False
    assert "invalid patron id" in message.lower()

def test_borrow_book_invalid_book_id():
    success, message = borrow_book_by_patron("123456", 20)

    assert success == False
    assert "book not found" in message.lower()

def test_borrow_multiple_same_book():
    add_book_to_catalog("R2_Test_Book", "Test Author", "1234567890144", 10)

    for i in range(0, 5): #borrows 5 books under Patron ID
        borrow_book_by_patron("654321", 4) #MAY NEED TO CHANGE BOOK ID IF MORE BOOKS THAN SAMPLE ARE ADDED
    
    success, message = borrow_book_by_patron("654321", 4)
    
    assert success == False
    assert "multiple copies" in message

    