from uuid import uuid4


class _Order:
    def __init__(self, owner, amount, price):
        self.owner = owner
        self.amount = amount
        self.price = price

        self._id = uuid4()

    def __repr__(self):
        return f"Trader {self.owner._id} {self.action} {self.amount}"

    @property
    def id(self):
        return self._id


class BuyOrder(_Order):
    action = "buys"


class SellOrder(_Order):
    action = "sells"
