from decimal import Decimal
from typing import List, Dict

def simplify_debts(balances: Dict[int, Decimal]) -> List[Dict]:
    """
    Simplify debts into minimum transactions using greedy approach
    """
    
    giver = []
    receivers = []

    for user_id, balance in balances.items():
        if balance < 0:
            giver.append({"user_id": user_id, "amount": abs(balance)})
        elif balance > 0:
            receivers.append({"user_id": user_id, "amount": balance})

    transactions = []

    while giver and receivers:
        current_giver = giver[0]
        current_receiver = receivers[0]

        amount = min(current_giver["amount"], current_receiver["amount"])

        transactions.append({
            "from_user": current_giver["user_id"],
            "to_user": current_receiver["user_id"],
            "amount": amount
        })

        current_giver["amount"] -= amount
        current_receiver["amount"] -= amount

        if current_giver["amount"] == 0:
            giver.pop(0)

        if current_receiver["amount"] == 0:
            receivers.pop(0)

    return transactions