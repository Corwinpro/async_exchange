import unittest

from async_exchange.exchange import Exchange, ExchangeAPI
from async_exchange.trader import Trader
from async_exchange.orders import BuyOrder, SellOrder


class TestExchange(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange()
        api = self.exchange.api
        self.trader_1 = Trader(exchange_api=api, money=100, stocks=10)
        self.trader_2 = Trader(exchange_api=api, money=100, stocks=10)
        self.trader_3 = Trader(exchange_api=api, money=100, stocks=10)
        self.trader_4 = Trader(exchange_api=api, money=100, stocks=10)
        self.trader_5 = Trader(exchange_api=api, money=100, stocks=10)

    def test_register_trader(self):
        trader = Trader()
        self.assertIsNone(trader.exchange_api)

        self.exchange.register_trader(trader)
        self.assertIsNotNone(trader.exchange_api)
        self.assertIsInstance(trader.exchange_api, ExchangeAPI)

    def test_submit_buy_order(self):
        self.trader_1.buy(100, 10)

        self.assertEqual(len(self.exchange.sell_levels), 0)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[10]
        (existing_order,) = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

    def test_submit_sell_order(self):
        self.trader_1.sell(100, 10)

        self.assertEqual(len(self.exchange.buy_levels), 0)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[10]
        (existing_order,) = sell_level

        self.assertIsInstance(existing_order, SellOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

    def test_submit_nonmatching_sell_buy_orders(self):
        self.trader_1.buy(100, 10)
        self.trader_2.sell(42, 20)

        self.assertEqual(len(self.exchange.buy_levels), 1)
        buy_level = self.exchange.buy_levels[10]
        (existing_order,) = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 100)
        self.assertEqual(existing_order.price, 10)
        self.assertIs(existing_order.owner, self.trader_1)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[20]
        (existing_order,) = sell_level

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
        (existing_order,) = sell_level

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

        self.assertEqual(len(self.exchange.buy_levels), 0)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[80]
        (existing_order,) = sell_level

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

        self.assertEqual(len(self.exchange.buy_levels), 0)

        self.assertEqual(len(self.exchange.sell_levels), 1)
        sell_level = self.exchange.sell_levels[180]
        (existing_order,) = sell_level

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
        (existing_order,) = buy_level

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
        (existing_order,) = buy_level

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
        (existing_order,) = sell_level

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
        (existing_order,) = sell_level

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
        (existing_order,) = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 4)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(len(self.exchange.sell_levels), 0)

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
        (existing_order,) = buy_level

        self.assertIsInstance(existing_order, BuyOrder)
        self.assertEqual(existing_order.amount, 5)
        self.assertEqual(existing_order.price, 2)
        self.assertIs(existing_order.owner, self.trader_2)

        self.assertEqual(len(self.exchange.sell_levels), 0)

        self.assertEqual(self.trader_1.money, 100)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_1.stocks, 0)
        self.assertEqual(self.trader_2.stocks, 10)

    def test_sell_below_ask_price(self):
        self.trader_1.buy(1, 4)
        self.trader_2.buy(2, 3)
        self.trader_3.buy(3, 1)

        self.trader_4.sell(4, 2)

        sell_levels = self.exchange.sell_levels
        self.assertEqual(len(sell_levels), 1)

        (existing_sell_order,) = sell_levels[2]
        self.assertEqual(existing_sell_order.amount, 1)
        self.assertEqual(existing_sell_order.price, 2)
        self.assertIs(existing_sell_order.owner, self.trader_4)

        buy_levels = self.exchange.buy_levels
        self.assertEqual(len(buy_levels), 1)

        self.assertEqual(len(buy_levels[4]), 0)
        self.assertEqual(len(buy_levels[3]), 0)

        (existing_buy_order,) = buy_levels[1]
        self.assertEqual(existing_buy_order.amount, 3)
        self.assertEqual(existing_buy_order.price, 1)
        self.assertIs(existing_buy_order.owner, self.trader_3)

        self.assertEqual(self.trader_1.stocks, 11)
        self.assertEqual(self.trader_1.money, 96)

        self.assertEqual(self.trader_2.stocks, 12)
        self.assertEqual(self.trader_2.money, 94)

        self.assertEqual(self.trader_3.stocks, 10)
        self.assertEqual(self.trader_3.money, 100)

        self.assertEqual(self.trader_4.stocks, 7)
        self.assertEqual(self.trader_4.money, 110)

    def test_buy_above_sell_price(self):
        self.trader_1.sell(1, 4)
        self.trader_2.sell(2, 5)
        self.trader_3.sell(3, 7)

        self.trader_4.buy(4, 6)

        buy_levels = self.exchange.buy_levels
        self.assertEqual(len(buy_levels), 1)

        (existing_buy_order,) = buy_levels[6]
        self.assertEqual(existing_buy_order.amount, 1)
        self.assertEqual(existing_buy_order.price, 6)
        self.assertIs(existing_buy_order.owner, self.trader_4)

        sell_levels = self.exchange.sell_levels
        self.assertEqual(len(sell_levels), 1)

        (existing_sell_order,) = sell_levels[7]
        self.assertEqual(existing_sell_order.amount, 3)
        self.assertEqual(existing_sell_order.price, 7)
        self.assertIs(existing_sell_order.owner, self.trader_3)

        self.assertEqual(self.trader_1.stocks, 9)
        self.assertEqual(self.trader_1.money, 104)

        self.assertEqual(self.trader_2.stocks, 8)
        self.assertEqual(self.trader_2.money, 110)

        self.assertEqual(self.trader_3.stocks, 10)
        self.assertEqual(self.trader_3.money, 100)

        self.assertEqual(self.trader_4.stocks, 13)
        self.assertEqual(self.trader_4.money, 86)

    def test_buy_orders_ordered(self):
        self.trader_1.buy(2, 1)
        self.trader_2.buy(3, 1)

        self.trader_3.sell(1, 1)

        self.assertEqual(self.trader_1.stocks, 11)
        self.assertEqual(self.trader_1.money, 99)

        self.assertEqual(self.trader_2.stocks, 10)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_3.stocks, 9)
        self.assertEqual(self.trader_3.money, 101)

    def test_sell_orders_ordered(self):
        self.trader_1.sell(2, 1)
        self.trader_2.sell(3, 1)

        self.trader_3.buy(1, 1)

        self.assertEqual(self.trader_1.stocks, 9)
        self.assertEqual(self.trader_1.money, 101)

        self.assertEqual(self.trader_2.stocks, 10)
        self.assertEqual(self.trader_2.money, 100)

        self.assertEqual(self.trader_3.stocks, 11)
        self.assertEqual(self.trader_3.money, 99)


class TestExchangeAPI(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange()
        self.api = self.exchange.api

    def test_exchange_api(self):
        self.assertIsInstance(self.api, ExchangeAPI)
        self.assertEqual(self.api.process_order, self.exchange.process_order)
        self.assertEqual(
            self.api.standing_orders, self.exchange.standing_orders
        )
        self.assertEqual(self.api.get_orderbook, self.exchange.get_orderbook)


if __name__ == "__main__":
    unittest.main()
