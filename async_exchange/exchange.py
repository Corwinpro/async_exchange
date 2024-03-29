from collections import defaultdict, deque
import logging

from async_exchange.orders import BuyOrder, SellOrder, _Order
from async_exchange.trader import (
    NotEnoughMoneyError,
    NotEnoughStocksError,
    Trader,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class Level(deque):
    pass


class Exchange:
    def __init__(self, logger=None):
        self.buy_levels = defaultdict(Level)
        self.sell_levels = defaultdict(Level)

        self._logger = logger

    def log_event(self, event_type, message):
        if self._logger is not None:
            self._logger.send_event(record_type=event_type, message=message)

    def __repr__(self):
        _repr = "\n______________\n"
        _repr += "Buy   |   Sell  price\n      |\n"
        _repr += "\n".join(
            f"      |- {sum(order.amount for order in level):4}   {price}"
            for price, level in sorted(self.sell_levels.items(), reverse=True)
            if sum(order.amount for order in level) > 0
        )
        _repr += "\n------+-------\n"
        _repr += "\n".join(
            f"{sum(order.amount for order in level):4} -|   {price:8}"
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
        if order.amount == 0:
            return

        if isinstance(order, BuyOrder):
            self._process_buy_order(order)
        elif isinstance(order, SellOrder):
            self._process_sell_order(order)

    def _exchange_assets(
        self, buyer: Trader, seller: Trader, stocks: int, money: int
    ):
        if stocks == 0:
            return

        buyer.has_enough_money(money)
        seller.has_enough_stocks(stocks)

        buyer.money -= money
        seller.money += money

        buyer.stocks += stocks
        seller.stocks -= stocks

        self.log_event(
            event_type="exchange",
            message={"price": money / stocks, "amount": stocks},
        )

    def _process_buy_order(self, order: BuyOrder):
        if order.amount <= 0:
            return

        current_best_sell = self.best_sell
        if current_best_sell is None or order.price < current_best_sell:
            self.buy_levels[order.price].append(order)
            return

        matched_sell_order = self.sell_levels[current_best_sell][0]
        stocks_to_transfer = min(order.amount, matched_sell_order.amount)
        money_to_transfer = stocks_to_transfer * matched_sell_order.price

        try:
            self._exchange_assets(
                order.owner,
                matched_sell_order.owner,
                stocks_to_transfer,
                money_to_transfer,
            )
        except NotEnoughMoneyError:
            logger.warning(
                f"Could not complete exchange: buyer {order.owner} does not"
                " have enough money. Adjusting the buyer's order and retrying"
                " the exchange."
            )
            buyer_can_afford = int(
                order.owner.money / matched_sell_order.price
            )
            order.amount = buyer_can_afford
            self._process_buy_order(order)
        except NotEnoughStocksError:
            _seller = matched_sell_order.owner
            logger.warning(
                f"Could not complete exchange: seller {_seller}"
                " does not have enough stocks. Adjusting the seller's order "
                "and retrying the exchange."
            )
            matched_sell_order.amount = matched_sell_order.owner.stocks
            self._process_buy_order(order)
        else:
            order.amount -= stocks_to_transfer
            matched_sell_order.amount -= stocks_to_transfer

            if matched_sell_order.amount == 0:
                self.sell_levels[current_best_sell].popleft()
                if len(self.sell_levels[current_best_sell]) == 0:
                    self.sell_levels.pop(current_best_sell)
            self._process_buy_order(order)

    def _process_sell_order(self, order: SellOrder):
        if order.amount <= 0:
            return

        current_best_buy = self.best_buy
        if current_best_buy is None or order.price > current_best_buy:
            self.sell_levels[order.price].append(order)
            return

        matched_buy_order = self.buy_levels[current_best_buy][0]
        stocks_to_transfer = min(order.amount, matched_buy_order.amount)
        money_to_transfer = stocks_to_transfer * matched_buy_order.price

        try:
            self._exchange_assets(
                matched_buy_order.owner,
                order.owner,
                stocks_to_transfer,
                money_to_transfer,
            )
        except NotEnoughMoneyError:
            logger.warning(
                f"Could not complete exchange: buyer {matched_buy_order.owner}"
                "  does not have enough money. Adjusting the buyer's order and"
                " retrying the exchange."
            )
            buyer_can_afford = int(
                matched_buy_order.owner.money / matched_buy_order.price
            )
            matched_buy_order.amount = buyer_can_afford
            self._process_sell_order(order)
        except NotEnoughStocksError:
            logger.warning(
                f"Could not complete exchange: seller {order.owner}"
                " does not have enough stocks. Adjusting the seller's order "
                "and retrying the exchange."
            )
            order.amount = order.owner.stocks
            self._process_sell_order(order)
        else:
            order.amount -= stocks_to_transfer
            matched_buy_order.amount -= stocks_to_transfer

            if matched_buy_order.amount == 0:
                self.buy_levels[current_best_buy].popleft()
                if len(self.buy_levels[current_best_buy]) == 0:
                    self.buy_levels.pop(current_best_buy)
            self._process_sell_order(order)

    def cancel_order(self, order: _Order) -> bool:
        """ Cancel the given ``order`` by removing it from the OrderBook.
        The order is identified by its ``id``.

        Note: the existing implementation is far from optimal because the
        ``Level`` is essentially a deque with O(n) complexity for removal by
        index. Alternative approaches are:
        - set the volume of the ``Order`` to zero in the orderbook (such that
        it does not yield actual exchange)
        - rework the ``Level`` to be an ordered dict
        """
        if isinstance(order, BuyOrder):
            level = self.buy_levels[order.price]
        elif isinstance(order, SellOrder):
            level = self.sell_levels[order.price]
        else:
            return False

        index_in_orderbook = None
        for index, existing_order in enumerate(level):
            if existing_order.id == order.id:
                index_in_orderbook = index
                break

        if index_in_orderbook is None:
            return False

        del level[index_in_orderbook]
        return True

    def standing_orders(self, trader):
        buy_orders = tuple(
            order
            for level in self.buy_levels.values()
            for order in level
            if order.owner is trader
        )
        sell_orders = tuple(
            order
            for level in self.sell_levels.values()
            for order in level
            if order.owner is trader
        )
        return buy_orders, sell_orders

    def get_orderbook(self):
        buy_orders = {
            price: sum(order.amount for order in level)
            for price, level in self.buy_levels.items()
        }
        sell_orders = {
            price: sum(order.amount for order in level)
            for price, level in self.sell_levels.items()
        }
        return buy_orders, sell_orders

    def register_trader(self, trader: Trader):
        """Register a ``trader`` in the Exchange.
        Provides the ``exchange_api`` to the ``trader``.
        """
        trader.exchange_api = self.api

    def shutdown(self):
        """Perform necessary actions to shutdown the ``Exchange`` instance."""
        pass

    @property
    def api(self):
        return ExchangeAPI(exchange=self)


class ExchangeAPI:
    def __init__(self, exchange: Exchange):
        self._process_order = exchange.process_order
        self._standing_orders = exchange.standing_orders
        self._get_order_book = exchange.get_orderbook
        self._cancel_order = exchange.cancel_order

    @property
    def process_order(self):
        return self._process_order

    @property
    def standing_orders(self):
        return self._standing_orders

    @property
    def get_orderbook(self):
        return self._get_order_book

    @property
    def cancel_order(self):
        return self._cancel_order
