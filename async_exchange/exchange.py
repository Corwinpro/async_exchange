import asyncio
import time
import random
from collections import defaultdict, deque


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

class Level(deque):
    pass

class Exchange:
    def __init__(self):
        self.buy_levels = defaultdict(Level)
        self.sell_levels = defaultdict(Level)

    def __repr__(self):
        _repr = "\n______________\n"
        _repr += "Buy   |   Sell  vol\n      |\n"
        _repr += "\n".join(
            f"      |- {sum(order.amount for order in level):4}   {price}"
            for price, level in sorted(self.sell_levels.items(), reverse=True)
            if sum(order.amount for order in level) > 0
        )
        _repr += "\n------+-------\n"
        _repr += "\n".join(
            f"{sum(order.amount for order in level):4} -|  {price:8}"
            for price, level in sorted(self.buy_levels.items(), reverse=True)
            if sum(order.amount for order in level) > 0
        )
        _repr += "\n______________\n"
        return _repr

    @property
    def best_buy(self):
        try:
            best_buy_price = max(
                price
                for price, orders in self.buy_levels.items()
                if len(orders) > 0
            )
        except ValueError:
            return None
        else:
            return best_buy_price

    @property
    def best_sell(self):
        try:
            best_sell_price = min(
                price
                for price, orders in self.sell_levels.items()
                if len(orders) > 0
            )
        except ValueError:
            return None
        else:
            return best_sell_price

    def process_order(self, order):
        if isinstance(order, BuyOrder):
            self._process_buy_order(order)
        elif isinstance(order, SellOrder):
            self._process_sell_order(order)

    def _process_buy_order(self, order: BuyOrder):
        current_best_sell = self.best_sell
        if current_best_sell is None or order.price < current_best_sell:
            self.buy_levels[order.price].append(order)
        else:
            matched_sell_order = self.sell_levels[current_best_sell][0]

            if matched_sell_order.amount > order.amount:
                matched_sell_order.owner.money += order.amount * matched_sell_order.price
                matched_sell_order.owner.stocks -= order.amount

                order.owner.money -= order.amount * matched_sell_order.price
                order.owner.stocks += order.amount

                matched_sell_order.amount -= order.amount
            elif matched_sell_order.amount < order.amount:
                matched_sell_order.owner.money += matched_sell_order.amount * matched_sell_order.price
                matched_sell_order.owner.stocks -= matched_sell_order.amount

                order.owner.money -= matched_sell_order.amount * matched_sell_order.price
                order.owner.stocks += matched_sell_order.amount
                
                order.amount -= matched_sell_order.amount
                self.sell_levels[current_best_sell].popleft()
                self._process_buy_order(order)
            else:
                matched_sell_order.owner.money += order.amount * matched_sell_order.price
                matched_sell_order.owner.stocks -= order.amount

                order.owner.money += order.amount * matched_sell_order.price
                order.owner.stocks += order.amount

                self.sell_levels[current_best_sell].popleft()

    def _process_sell_order(self, order):
        current_best_buy = self.best_buy
        if current_best_buy is None or order.price > current_best_buy:
            self.sell_levels[order.price].append(order)
        else:
            matched_buy_order = self.buy_levels[current_best_buy][0]
            if matched_buy_order.amount > order.amount:
                matched_buy_order.owner.money -= order.amount * matched_buy_order.price
                matched_buy_order.owner.stocks += order.amount

                order.owner.money += order.amount * matched_buy_order.price
                order.owner.stocks -= order.amount

                matched_buy_order.amount -= order.amount
            elif matched_buy_order.amount < order.amount:
                matched_buy_order.owner.money -= matched_buy_order.amount * matched_buy_order.price
                matched_buy_order.owner.stocks += matched_buy_order.amount

                order.owner.money += matched_buy_order.amount * matched_buy_order.price
                order.owner.stocks -= matched_buy_order.amount

                order.amount -= matched_buy_order.amount
                self.buy_levels[current_best_buy].popleft()
                self._process_buy_order(order)
            else:
                matched_buy_order.owner.money -= order.amount * matched_buy_order.price
                matched_buy_order.owner.stocks += order.amount

                order.owner.money += order.amount * matched_buy_order.price
                order.owner.stocks -= order.amount

                self.buy_levels[current_best_buy].popleft()

    def standing_orders(self, trader):
        buy_orders = tuple(
            order
            for level in self.buy_levels
            for order in level
            if order.owner is trader
        )
        sell_orders = tuple(
            order
            for level in self.sell_levels
            for order in level
            if order.owner is trader
        )
        return buy_orders, sell_orders


exchange = Exchange()

class NotEnoughMoneyError(ValueError):
    pass

class NotEnoughStocksError(ValueError):
    pass


class Trader:
    _id = 1

    def __init__(self, money=100, stocks=10):
        self._money = None
        self._stocks = None

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
        exchange.process_order(
            SellOrder(self, amount, price)
        )

    def buy(self, amount, price):
        exchange.process_order(
            BuyOrder(self, amount, price)
        )

    def __str__(self):
        return f"Trader {self._id}: stocks {self.stocks}, cash {self.money}"


if __name__ == "__main__":

    trader_1 = Trader()
    trader_2 = Trader()

    trader_1.sell(30, 4)
    trader_1.sell(50, 5)
    trader_1.sell(5, 3)
    trader_2.buy(100, 1)
    print(exchange)

    trader_2.buy(40, 2)
    print(exchange)

    trader_1.buy(40, 5)
    print(exchange)
    