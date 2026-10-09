import pytest
from decimal import Decimal
from app.services.split_calculator import equal_split, percentage_split, validate_exact_split


class TestSplitCalculator:
    
    def test_equal_split_basic(self):
        result = equal_split(Decimal(3000), 3)
        assert result == Decimal(1000)

    def test_equal_split_decimal(self):
       result =equal_split(Decimal(1000), 3)
       assert abs(result - Decimal("333.33")) < Decimal("1")

    def test_percentage_split(self):
        result = percentage_split(Decimal(3000), [Decimal(30), Decimal(40), Decimal(30)])
        assert result[0] == Decimal(900)
        assert result[1] == Decimal(1200)
        assert result[2] == Decimal(900)
        
    def test_exact_split_valid(self):
        result = validate_exact_split(Decimal(3000), [Decimal(1000), Decimal(2000)])
        assert result == True
        
    
    def test_exact_split_invalid(self):
        with pytest.raises(ValueError):
            validate_exact_split(Decimal(3000), [Decimal(1000), Decimal(1500)])