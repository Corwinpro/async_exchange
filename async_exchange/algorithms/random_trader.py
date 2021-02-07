import asyncio
import random

from async_exchange.trader import Trader


BUY = "BUY"
SELL = "SELL"
RANDOM_CHOICE = {0: BUY, 1: SELL}
DEFAULT_PRICE = 10


class RandomTrader(Trader):
    async def sleep(self):
        sleep_time = random.random() * 1.0
        await asyncio.sleep(sleep_time)

    async def cycle(self):
        while True:
            await self.sleep()
            self.place_random_order()

    def place_random_order(self):
        buy_or_sell = RANDOM_CHOICE[random.randint(0, 1)]

        existing_buy_orders, existing_sell_orders = self.inspect_exchange()
        if len(existing_buy_orders) == 0 and len(existing_sell_orders) == 0:
            return self.submit_order(buy_or_sell, price=None, amount=None)

        best_buy = None
        best_sell = None
        if len(existing_buy_orders) != 0:
            best_buy = max(existing_buy_orders)
        if len(existing_sell_orders) != 0:
            best_sell = min(existing_sell_orders)

        if best_buy is None:
            best_buy = best_sell
        if best_sell is None:
            best_sell = best_buy

        median_price = (best_buy + best_sell) // 2
        deviation = int(median_price ** 0.5)
        random_price = median_price + random.randint(-deviation, deviation)

        if buy_or_sell == BUY:
            max_stocks = self.money // random_price
        else:
            max_stocks = self.stocks

        if max_stocks == 0:
            return

        random_stocks = random.randint(1, max_stocks)

        return self.submit_order(
            buy_or_sell, price=random_price, amount=random_stocks
        )

    def submit_order(self, buy_or_sell, price, amount):
        if price is None:
            price = DEFAULT_PRICE
        if amount is None:
            amount = random.randint(1, self.money // price)

        print(
            f"Trader {self._id} wants to {buy_or_sell} "
            f"{amount} stocks at {price}."
        )
        if buy_or_sell == BUY:
            operation = self.buy
        else:
            operation = self.sell

        operation(amount, price)
