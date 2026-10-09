import pytest
from decimal import Decimal
from app.services.debt_simplifier import simplify_debts


class TestDebtSimplifier:
    
    def test_debt_simplifier_basic(self):
        # LIKHO: Debt simplifier test
        balances = {
        1: Decimal(2000),
        2: Decimal(-1000),
        3: Decimal(-1000)
    }
    
        result = simplify_debts(balances)
        
        assert len(result) == 2
        assert result[0]["from_user"] == 2
        assert result[0]["to_user"] == 1
        assert result[0]["amount"] == Decimal(1000)
        assert result[1]["from_user"] == 3
        assert result[1]["to_user"] == 1
        assert result[1]["amount"] == Decimal(1000)