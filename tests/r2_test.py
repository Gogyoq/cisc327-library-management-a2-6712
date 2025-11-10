import pytest
from database import (
    get_all_books
)

books = get_all_books()

def test_all_book_ids():

    assert len(books) > 0

    for book in books:
        assert 'id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'isbn' in book
        assert 'available_copies' in book
        assert 'total_copies' in book





