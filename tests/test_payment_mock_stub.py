import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.library_service import (pay_late_fees, refund_late_fee_payment)
from unittest.mock import Mock
from services.payment_service import PaymentGateway

class TestPayLateFees:
    """Test suite for pay_late_fees() function"""
    
    def test_successful_payment(self, mocker):
        """Test successful payment processing"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 5.50,
                'days_overdue': 11,
                'status': 'implemented'
            }
        )
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={
                'book_id': 1,
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565'
            }
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (
            True,
            "txn_12345",
            "Payment processed successfully"
        )
        
        success, message, txn_id = pay_late_fees("123456", 1, mock_gateway)
        
        assert success is True
        assert "Payment successful!" in message
        assert txn_id == "txn_12345"
        
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=5.50,
            description="Late fees for 'The Great Gatsby'"
        )
    
    def test_payment_declined_by_gateway(self, mocker):
        """Test when payment gateway declines the payment"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 3.00, 'days_overdue': 6, 'status': 'implemented'}
        )
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={'book_id': 2, 'title': '1984', 'author': 'George Orwell', 'isbn': '9780451524935'}
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (
            False,
            None,
            "Insufficient funds"
        )
        
        success, message, txn_id = pay_late_fees("654321", 2, mock_gateway)
        
        assert success is False
        assert "Payment failed: Insufficient funds" in message
        assert txn_id is None
        
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="654321",
            amount=3.00,
            description="Late fees for '1984'"
        )
    
    def test_invalid_patron_id(self, mocker):
        """Test with invalid patron ID - mock should NOT be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        
        invalid_ids = ["12345", "1234567", "abc123", "", None]
        
        for patron_id in invalid_ids:
            success, message, txn_id = pay_late_fees(patron_id, 1, mock_gateway)
            
            assert success is False
            assert "Invalid patron ID" in message
            assert txn_id is None
        
        mock_gateway.process_payment.assert_not_called()
    
    def test_zero_late_fees(self, mocker):
        """Test when late fees are zero - mock should NOT be called"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'implemented'}
        )
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={'book_id': 3, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '9780061120084'}
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, txn_id = pay_late_fees("111111", 3, mock_gateway)
        
        assert success is False
        assert "No late fees to pay" in message
        assert txn_id is None
        
        mock_gateway.process_payment.assert_not_called()
    
    def test_network_error_exception(self, mocker):
        """Test exception handling when payment gateway raises network error"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 7.50, 'days_overdue': 15, 'status': 'implemented'}
        )
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={'book_id': 4, 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'isbn': '9780141439518'}
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = Exception("Network timeout")
        
        success, message, txn_id = pay_late_fees("222222", 4, mock_gateway)
        
        assert success is False
        assert "Payment processing error: Network timeout" in message
        assert txn_id is None
        
        mock_gateway.process_payment.assert_called_once()
    
    def test_invalid_book_id(self, mocker):
        """Test with invalid book ID"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 0, 'days_overdue': 0, 'status': 'error', 'message': 'Book not found'}
        )
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value=None
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, txn_id = pay_late_fees("123456", 999, mock_gateway)
        
        assert success is False
        assert txn_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_calculate_late_fee_error(self, mocker):
        """Test when calculate_late_fee_for_book returns error status"""
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 0, 'status': 'error', 'message': 'Book not borrowed'}
        )
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, txn_id = pay_late_fees("123456", 1, mock_gateway)
        
        assert success is False
        assert txn_id is None
        mock_gateway.process_payment.assert_not_called()


class TestRefundLateFeePayment:
    """Test suite for refund_late_fee_payment() function"""
    
    def test_successful_refund(self):
        """Test successful refund processing"""
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (
            True,
            "Refund processed successfully"
        )
        
        success, message = refund_late_fee_payment("txn_98765", 10.00, mock_gateway)
        
        assert success is True
        assert "Refund processed successfully" in message
        
        mock_gateway.refund_payment.assert_called_once_with("txn_98765", 10.00)
    
    def test_invalid_transaction_id(self):
        """Test rejection of invalid transaction IDs - mock should NOT be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        
        invalid_txn_ids = ["invalid", "123456", "", None, "trans_123"]
        
        for txn_id in invalid_txn_ids:
            success, message = refund_late_fee_payment(txn_id, 5.00, mock_gateway)
            
            assert success is False
            assert "Invalid transaction ID" in message
        
        mock_gateway.refund_payment.assert_not_called()
    
    def test_negative_refund_amount(self):
        """Test rejection of negative refund amounts - mock should NOT be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message = refund_late_fee_payment("txn_11111", -5.00, mock_gateway)
        
        assert success is False
        assert "Refund amount must be greater than 0" in message
        
        mock_gateway.refund_payment.assert_not_called()
    
    def test_zero_refund_amount(self):
        """Test rejection of zero refund amounts - mock should NOT be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message = refund_late_fee_payment("txn_22222", 0.00, mock_gateway)
        
        assert success is False
        assert "Refund amount must be greater than 0" in message
        
        mock_gateway.refund_payment.assert_not_called()
    
    def test_refund_exceeds_maximum(self):
        """Test rejection when refund amount exceeds $15 maximum - mock should NOT be called"""
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message = refund_late_fee_payment("txn_33333", 15.01, mock_gateway)
        
        assert success is False
        assert "Refund amount exceeds maximum late fee" in message
        
        mock_gateway.refund_payment.assert_not_called()
    
    def test_refund_gateway_failure(self):
        """Test when payment gateway fails to process refund"""
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (
            False,
            "Transaction not found"
        )
        
        success, message = refund_late_fee_payment("txn_44444", 8.50, mock_gateway)
        
        assert success is False
        assert "Refund failed: Transaction not found" in message
        
        mock_gateway.refund_payment.assert_called_once_with("txn_44444", 8.50)
    
    def test_refund_exception_handling(self):
        """Test exception handling when refund gateway raises error"""
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.side_effect = Exception("Database connection lost")
        
        success, message = refund_late_fee_payment("txn_55555", 12.00, mock_gateway)
        
        assert success is False
        assert "Refund processing error: Database connection lost" in message
        
        mock_gateway.refund_payment.assert_called_once()
    
    def test_refund_at_maximum_boundary(self):
        """Test refund at exactly $15 (boundary test)"""
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "Refund successful")
        
        success, message = refund_late_fee_payment("txn_66666", 15.00, mock_gateway)
        
        assert success is True
        mock_gateway.refund_payment.assert_called_once_with("txn_66666", 15.00)


class TestPaymentGatewayDirectly:
    """Test suite for PaymentGateway class directly"""
    
    def test_gateway_initialization(self):
        """Test PaymentGateway initialization with custom API key"""
        gateway = PaymentGateway(api_key="custom_key_123")
        assert gateway.api_key == "custom_key_123"
        assert gateway.base_url == "https://api.payment-gateway.example.com"
    
    def test_gateway_default_initialization(self):
        """Test PaymentGateway initialization with default API key"""
        gateway = PaymentGateway()
        assert gateway.api_key == "test_key_12345"
    
    def test_process_payment_invalid_amount_zero(self):
        """Test gateway rejects zero amount"""
        gateway = PaymentGateway()
        success, txn_id, message = gateway.process_payment("123456", 0, "Test")
        
        assert success is False
        assert txn_id == ""
        assert "Invalid amount" in message
    
    def test_process_payment_invalid_amount_negative(self):
        """Test gateway rejects negative amount"""
        gateway = PaymentGateway()
        success, txn_id, message = gateway.process_payment("123456", -10.00, "Test")
        
        assert success is False
        assert txn_id == ""
        assert "Invalid amount" in message
    
    def test_process_payment_exceeds_limit(self):
        """Test gateway rejects amount over $1000"""
        gateway = PaymentGateway()
        success, txn_id, message = gateway.process_payment("123456", 1001.00, "Test")
        
        assert success is False
        assert txn_id == ""
        assert "exceeds limit" in message
    
    def test_process_payment_invalid_patron_format(self):
        """Test gateway rejects invalid patron ID format"""
        gateway = PaymentGateway()
        
        # Test various invalid formats
        invalid_ids = ["12345", "1234567", "abc", ""]
        
        for patron_id in invalid_ids:
            success, txn_id, message = gateway.process_payment(patron_id, 10.00, "Test")
            assert success is False
            assert txn_id == ""
            assert "Invalid patron ID" in message
    
    def test_process_payment_successful(self):
        """Test gateway processes valid payment successfully"""
        gateway = PaymentGateway()
        success, txn_id, message = gateway.process_payment("123456", 10.50, "Late fees")
        
        assert success is True
        assert txn_id.startswith("txn_123456_")
        assert "processed successfully" in message
        assert "$10.50" in message
    
    def test_refund_payment_invalid_transaction_id(self):
        """Test gateway rejects invalid transaction IDs"""
        gateway = PaymentGateway()
        
        invalid_ids = ["", "invalid", "abc123"]
        
        for txn_id in invalid_ids:
            success, message = gateway.refund_payment(txn_id, 10.00)
            assert success is False
            assert "Invalid transaction ID" in message
    
    def test_refund_payment_invalid_amount(self):
        """Test gateway rejects invalid refund amounts"""
        gateway = PaymentGateway()
        
        success, message = gateway.refund_payment("txn_123456_12345", 0)
        assert success is False
        assert "Invalid refund amount" in message
        
        success, message = gateway.refund_payment("txn_123456_12345", -5.00)
        assert success is False
        assert "Invalid refund amount" in message
    
    def test_refund_payment_successful(self):
        """Test gateway processes valid refund successfully"""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("txn_123456_12345", 10.00)
        
        assert success is True
        assert "processed successfully" in message
        assert "$10.00" in message
        assert "Refund ID:" in message
    
    def test_verify_payment_status_invalid_transaction(self):
        """Test verify_payment_status with invalid transaction ID"""
        gateway = PaymentGateway()
        
        invalid_ids = ["", "invalid", "abc123"]
        
        for txn_id in invalid_ids:
            result = gateway.verify_payment_status(txn_id)
            assert result["status"] == "not_found"
            assert "not found" in result["message"]
    
    def test_verify_payment_status_valid_transaction(self):
        """Test verify_payment_status with valid transaction ID"""
        gateway = PaymentGateway()
        result = gateway.verify_payment_status("txn_123456_12345")
        
        assert result["transaction_id"] == "txn_123456_12345"
        assert result["status"] == "completed"
        assert "amount" in result
        assert "timestamp" in result
