import asyncio

from async_exchange.trader import Trader


class DummyMarketMaker(Trader):

    async def sleep(self):
        await asyncio.sleep(1.0)

    async def cycle(self):
        while True:
            await self.sleep()
            self.execute_actions()

    def execute_actions(self):
        own_buy_orders, own_sell_orders = self.exchange_api.standing_orders()
        if len(own_buy_orders):
            pass
        
        buy_orders, sell_orders = self.exchange_api.get_orderbook()

