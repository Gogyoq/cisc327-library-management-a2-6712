import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book2", "Test Author2", "1234567897452", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_negative_number_copies():
    """Test adding a book with a negative integer amount of copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)

    assert success == False
    assert "positive integer" in message

def test_add_book_invalid_author_name_too_long():
    """Test adding book with an author name exceeding 100 chars"""
    success, message = add_book_to_catalog("Test Book", "hpbcmamnxcnbbangzaduywajpwunrbkhwqpxbbuuegtkktgwtnwktjebcqzgdifrfuxykrhfnqzdnrrcvxpbwegxcvpudmbjggkpvfuxuckxzu", "1234567890123", 5)

    assert success == False
    assert "less than 100" in message