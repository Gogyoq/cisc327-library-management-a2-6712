import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (
    search_books_in_catalog,
)
from database import (
    get_book_by_id
)

book = get_book_by_id(1)

def test_search_book_valid_input_title():
    results = search_books_in_catalog("The Great Gatsby", "title")
    
    assert results[0] == book
    

def test_search_book_valid_input_author():
    results = search_books_in_catalog("F. Scott Fitzgerald", "author")

    assert results[0] == book

def test_search_book_valid_input_isbn():
    results = search_books_in_catalog("9780743273565", "isbn")

    assert results[0] == book

def test_search_book_valid_input_partial():
    results = search_books_in_catalog("great gatsby", "title")

    assert results[0] == book