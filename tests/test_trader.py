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


if __name__ == "__main__":
    unittest.main()
