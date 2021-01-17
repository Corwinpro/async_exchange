class _Order:
    def __init__(self, owner, amount, price):
        self.owner = owner
        self.amount = amount
        self.price = price

    def __repr__(self):
        return f"Trader {self.owner._id} {self.action} {self.amount}"

class BuyOrder(_Order):
    action = "buys"

class SellOrder(_Order):
    action = "sells"
