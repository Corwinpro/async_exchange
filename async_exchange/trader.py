from async_exchange.orders import BuyOrder, SellOrder, _Order


class NotEnoughMoneyError(ValueError):
    pass


class NotEnoughStocksError(ValueError):
    pass


class Trader:
    _id = 1

    def __init__(self, exchange_api=None, money=100, stocks=10):
        self._money = None
        self._stocks = None

        self.exchange_api = exchange_api

        self.money = money
        self.stocks = stocks
        self._id = Trader._id
        Trader._id += 1

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, value):
        if value < 0:
            raise NotEnoughMoneyError
        self._money = value

    @property
    def stocks(self):
        return self._stocks

    @stocks.setter
    def stocks(self, value):
        if value < 0:
            raise NotEnoughStocksError
        self._stocks = value

    def sell(self, amount, price):
        self.exchange_api.process_order(SellOrder(self, amount, price))

    def buy(self, amount, price):
        self.exchange_api.process_order(BuyOrder(self, amount, price))

    def has_enough_money(self, money):
        if self.money < money:
            raise NotEnoughMoneyError
        return True

    def has_enough_stocks(self, stocks):
        if self.stocks < stocks:
            raise NotEnoughStocksError
        return True

    def inspect_exchange(self):
        return self.exchange_api.get_orderbook()

    @property
    def standing_orders(self):
        """ Get two tuples of standing orders from ``self``.
        """
        return self.exchange_api.standing_orders(self)

    def cancel_order(self, order: _Order) -> bool:
        """ Cancel the ``order``: the order will be removed from the
        exchange's order book. If the ``order`` has been successfully
        removed, returns ``True``. If the ``order`` cannot be removed,
        returns ``False``.
        """
        return self.exchange_api.cancel_order(order)

    def cancel_all_orders(self) -> bool:
        """ Cancel all orders the ``_Trader`` has submitted. Returns
        ``True`` iif all standing orders have been successfully removed.
        """
        buy_orders, sell_orders = self.standing_orders
        return all(
            self.cancel_order(order) for order in buy_orders + sell_orders
        )

    def __str__(self):
        return f"Trader {self._id}: stocks {self.stocks}, cash {self.money}"

    async def cycle(self):
        raise NotImplementedError
