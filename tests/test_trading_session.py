import unittest
from unittest import TestCase

from async_exchange.exchange import Exchange
from async_exchange.trader import Trader
from async_exchange.trading_session import TradingSession


class TestTradingSession(TestCase):
    def setUp(self):
        traders = [Trader()]
        exchange = Exchange()
        self.trading_session = TradingSession(
            traders=traders, exchange=exchange
        )

    def test_init(self):
        self.assertIsNotNone(self.trading_session.logger)

        (trader,) = self.trading_session.traders
        self.assertIsNotNone(trader.exchange_api)

    def test_init_default_exchange(self):
        trading_session = TradingSession(
            traders=[], exchange=None, logger=None
        )

        self.assertIsInstance(trading_session.exchange, Exchange)
        self.assertIsNone(trading_session.exchange._logger)


if __name__ == "__main__":
    unittest.main()
