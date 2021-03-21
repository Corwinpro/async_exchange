import unittest

from async_exchange.exchange import Exchange
from async_exchange.trader import (
    Trader,
    NotEnoughMoneyError,
    NotEnoughStocksError,
)


class TestTrader(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange()
        api = self.exchange.api

        self.trader = Trader(exchange_api=api, money=100, stocks=10)

    def test_trader_money(self):
        self.assertEqual(self.trader.money, 100)

        self.trader.money = 1000
        self.assertEqual(self.trader.money, 1000)

        self.trader.money = 0
        self.assertEqual(self.trader.money, 0)

        with self.assertRaises(NotEnoughMoneyError):
            self.trader.money = -1

    def test_trader_has_enough_money(self):
        self.assertTrue(self.trader.has_enough_money(10))

        with self.assertRaises(NotEnoughMoneyError):
            self.trader.has_enough_money(10000)

    def test_trader_stocks(self):
        self.assertEqual(self.trader.stocks, 10)

        self.trader.stocks = 1000
        self.assertEqual(self.trader.stocks, 1000)

        self.trader.stocks = 0
        self.assertEqual(self.trader.stocks, 0)

        with self.assertRaises(NotEnoughStocksError):
            self.trader.stocks = -1

    def test_trader_has_enough_stocks(self):
        self.assertTrue(self.trader.has_enough_stocks(10))

        with self.assertRaises(NotEnoughStocksError):
            self.trader.has_enough_stocks(10000)

    def test_inspect_exchange(self):
        self.assertEqual(
            self.trader.inspect_exchange(), self.exchange.get_orderbook()
        )

    def test_sell(self):
        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 0)

        self.trader.sell(amount=5, price=12)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        self.assertEqual(len(self.exchange.buy_levels), 0)

        sell_order, = self.exchange.sell_levels[12]
        self.assertIs(self.trader, sell_order.owner)

    def test_buy(self):
        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 0)

        self.trader.buy(amount=5, price=12)

        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 1)

        buy_order, = self.exchange.buy_levels[12]
        self.assertIs(self.trader, buy_order.owner)

    def test_standing_orders(self):
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)

        self.trader.buy(amount=20, price=10)
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 1)
        buy_order, = buy_orders
        self.assertEqual(buy_order.price, 10)
        self.assertEqual(buy_order.amount, 20)
        self.assertEqual(len(sell_orders), 0)

        self.trader.sell(amount=30, price=40)
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 1)
        buy_order, = buy_orders
        self.assertEqual(buy_order.price, 10)
        self.assertEqual(buy_order.amount, 20)
        self.assertEqual(len(sell_orders), 1)
        sell_order, = sell_orders
        self.assertEqual(sell_order.price, 40)
        self.assertEqual(sell_order.amount, 30)

    def test_cancel_order_buy(self):
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)

        self.trader.buy(amount=20, price=10)
        (buy_order,), _ = self.trader.standing_orders

        result = self.trader.cancel_order(buy_order)
        self.assertTrue(result)
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)

        result = self.trader.cancel_order(buy_order)
        self.assertFalse(result)

    def test_cancel_order_sell(self):
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)

        self.trader.sell(amount=20, price=10)
        _, (sell_order,) = self.trader.standing_orders

        result = self.trader.cancel_order(sell_order)
        self.assertTrue(result)
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)

        result = self.trader.cancel_order(sell_order)
        self.assertFalse(result)

    def test_cancel_order_many_orders(self):
        self.trader.sell(amount=10, price=40)
        self.trader.sell(amount=20, price=30)
        self.trader.buy(amount=30, price=20)
        self.trader.buy(amount=40, price=10)

        (buy_order_1, buy_order_2), (
            sell_order_1,
            sell_order_2,
        ) = self.trader.standing_orders

        result = self.trader.cancel_order(buy_order_2)
        self.assertTrue(result)
        (actual_buy_order_1,), (
            actual_sell_order_1,
            actual_sell_order_2,
        ) = self.trader.standing_orders
        self.assertIs(actual_buy_order_1, buy_order_1)
        self.assertIs(actual_sell_order_1, sell_order_1)
        self.assertIs(actual_sell_order_2, sell_order_2)

        result = self.trader.cancel_order(sell_order_1)
        self.assertTrue(result)
        (actual_buy_order_1,), (
            actual_sell_order_2,
        ) = self.trader.standing_orders
        self.assertIs(actual_buy_order_1, buy_order_1)
        self.assertIs(actual_sell_order_2, sell_order_2)

    def test_cancel_all_orders(self):
        self.trader.sell(amount=10, price=40)
        self.trader.sell(amount=20, price=30)
        self.trader.buy(amount=30, price=20)
        self.trader.buy(amount=40, price=10)

        (buy_order_1, buy_order_2), (
            sell_order_1,
            sell_order_2,
        ) = self.trader.standing_orders

        self.trader.cancel_all_orders()
        buy_orders, sell_orders = self.trader.standing_orders
        self.assertEqual(len(buy_orders), 0)
        self.assertEqual(len(sell_orders), 0)


if __name__ == "__main__":
    unittest.main()
