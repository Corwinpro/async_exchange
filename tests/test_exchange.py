import unittest

from async_exchange.exchange import Exchange
from async_exchange.trader import Trader
from async_exchange.orders import BuyOrder, SellOrder


class TestExchange(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange()
        self.trader_1 = Trader(
            exchange=self.exchange,
            money=100,
            stocks=10
        )
        self.trader_2 = Trader(
            exchange=self.exchange,
            money=100,
            stocks=10
        )

    def test_submit_buy_order(self):
        self.trader_1.buy(100, 10)

        self.assertEqual(len(self.exchange.sell_levels), 0)
        
        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[10]
        existing_order, = buy_level
        
        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

    def test_submit_sell_order(self):
        self.trader_1.sell(100, 10)

        self.assertEqual(len(self.exchange.buy_levels), 0)
        
        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[10]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

    def test_submit_nonmatching_sell_buy_orders(self):
        self.trader_1.buy(100, 10)
        self.trader_2.sell(42, 20)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[10]
        existing_order, = buy_level
        
        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[20]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 42)
        self.assertEqual(existing_order.price, 20)
        self.assertIs(existing_order.owner, self.trader_2)

    def test_submit_matching_sell_order(self):
        self.trader_1.buy(100, 10)
        self.trader_2.sell(5, 10)

        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 1)
        sell_level = self.exchange.buy_levels[10]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 95)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(self.trader_1.money, 100 - 10 * 5)
        self.assertEqual(self.trader_2.money, 100 + 10 * 5)

        self.assertEqual(self.trader_1.stocks, 10 + 5)
        self.assertEqual(self.trader_2.stocks, 10 - 5)

    def test_submit_matching_sell_order_not_enough_money(self):
        self.trader_1.buy(5, 80)
        self.trader_2.sell(5, 80)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        empty_buy_level = self.exchange.buy_levels[80]
        self.assertEqual(len(empty_buy_level), 0)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[80]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 4)
        self.assertEqual(existing_order.price, 80)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(self.trader_1.money, 20)
        self.assertEqual(self.trader_2.money, 180)

        self.assertEqual(self.trader_1.stocks, 11)
        self.assertEqual(self.trader_2.stocks, 9)

    def test_submit_matching_sell_order_not_enough_money_2(self):
        self.trader_1.buy(5, 180)
        self.trader_2.sell(5, 180)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        empty_buy_level = self.exchange.buy_levels[180]
        self.assertEqual(len(empty_buy_level), 0)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[180]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 5)
        self.assertEqual(existing_order.price, 180)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(self.trader_1.money, 100)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_1.stocks, 10)
        self.assertEqual(self.trader_2.stocks, 10)

    def test_submit_matching_sell_order_not_enough_stocks(self):
        self.trader_2.stocks = 1

        self.trader_1.buy(10, 2)
        self.trader_2.sell(5, 2)

        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 1)

        buy_level = self.exchange.buy_levels[2]
        existing_order, = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 9)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(self.trader_1.money, 98)
        self.assertEqual(self.trader_2.money, 102)

        self.assertEqual(self.trader_1.stocks, 11)
        self.assertEqual(self.trader_2.stocks, 0)

    def test_submit_matching_sell_order_not_enough_stocks_2(self):
        self.trader_2.stocks = 0

        self.trader_1.buy(10, 2)
        self.trader_2.sell(5, 2)

        self.assertEqual(len(self.exchange.sell_levels), 0)
        self.assertEqual(len(self.exchange.buy_levels), 1)

        buy_level = self.exchange.buy_levels[2]
        existing_order, = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 10)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(self.trader_1.money, 100)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_1.stocks, 10)
        self.assertEqual(self.trader_2.stocks, 0)

    def test_submit_matching_buy_order_not_enough_money(self):
        self.trader_1.sell(5, 80)
        self.trader_2.buy(5, 80)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        self.assertEqual(len(self.exchange.buy_levels), 0)
        sell_level = self.exchange.sell_levels[80]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 4)
        self.assertEqual(existing_order.price, 80)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(self.trader_1.money, 180)
        self.assertEqual(self.trader_2.money, 20)

        self.assertEqual(self.trader_1.stocks, 9)
        self.assertEqual(self.trader_2.stocks, 11)

    def test_submit_matching_buy_order_not_enough_money_2(self):
        self.trader_1.sell(5, 180)
        self.trader_2.buy(5, 180)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        self.assertEqual(len(self.exchange.buy_levels), 0)
        sell_level = self.exchange.sell_levels[180]
        existing_order, = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 5)
        self.assertEqual(existing_order.price, 180)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(self.trader_1.money, 100)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_1.stocks, 10)
        self.assertEqual(self.trader_2.stocks, 10)

    def test_submit_matching_buy_order_not_enough_stocks(self):
        self.trader_1.stocks = 1

        self.trader_1.sell(10, 2)
        self.trader_2.buy(5, 2)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[2]
        existing_order, = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 4)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[2]
        self.assertEqual(len(sell_level), 0)

        self.assertEqual(self.trader_1.money, 102)
        self.assertEqual(self.trader_2.money, 98)

        self.assertEqual(self.trader_1.stocks, 0)
        self.assertEqual(self.trader_2.stocks, 11)

    def test_submit_matching_buy_order_not_enough_stocks_2(self):
        self.trader_1.stocks = 0

        self.trader_1.sell(10, 2)
        self.trader_2.buy(5, 2)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[2]
        existing_order, = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 5)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[2]
        self.assertEqual(len(sell_level), 0)

        self.assertEqual(self.trader_1.money, 100)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_1.stocks, 0)
        self.assertEqual(self.trader_2.stocks, 10)


if __name__ == "__main__":
    unittest.main()
