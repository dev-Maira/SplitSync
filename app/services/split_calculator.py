from decimal import Decimal
from typing import List

def equal_split(total_amount: Decimal, count: int) -> Decimal:
    """
    Har person ka equal share
    """
                                                  
                                        
    return total_amount /count


def percentage_split(total_amount: Decimal, percentages: List[Decimal]) -> List[Decimal]:
    """
    Percentages se amounts nikalo
    Input: 3000, [30, 40, 30]
    Output: [900, 1200, 900]
    """
                              
    amounts = []
    
                                  
    for percentage in percentages:
         amount = (total_amount * percentage) / 100
         amounts.append(amount)
    
                    
    return amounts


def validate_exact_split(total_amount: Decimal, amounts: List[Decimal]) -> bool:
    """
    Check karo amounts sum to total
    """
                          
    total = sum(amounts)
    
                                  
    if total == total_amount:
        return True
    else:
        raise ValueError(f"Amounts sum to {total}, expected {total_amount}")