import asyncio
import logging
from signal import SIGTERM, SIGINT
from typing import List

from async_exchange.exchange import Exchange
from async_exchange.trader import Trader

default_logger = logging.getLogger(__name__)


CANCEL_SIGNALS = (SIGTERM, SIGINT)


class TradingSession:
    """Trading session generator.

    Activates all ``traders`` that interact with the given ``exchange``.
    """

    def __init__(
        self, traders: List[Trader], exchange: Exchange = None, logger=None
    ):
        self.traders = traders

        if exchange is not None:
            self.exchange = exchange
        else:
            self.exchange = Exchange(logger=logger)

        if logger is None:
            self.logger = default_logger

        for trader in self.traders:
            self.exchange.register_trader(trader)

    def run(self):
        asyncio.run(self._runnable())

    async def _runnable(self):
        loop = asyncio.get_running_loop()
        for signal in CANCEL_SIGNALS:
            loop.add_signal_handler(signal, self.shutdown, signal)

        tasks = [trader.cycle() for trader in self.traders]
        group = asyncio.gather(*tasks, return_exceptions=False)
        try:
            await group
        except asyncio.CancelledError:
            default_logger.info("Trading session cancelled.")

    def shutdown(self, signal: str):
        loop = asyncio.get_running_loop()
        for task in asyncio.all_tasks(loop=loop):
            task.cancel()

        default_logger.info(f"Got signal: {signal!s}, shutting down.")
        loop.remove_signal_handler(SIGTERM)
        loop.add_signal_handler(SIGINT, lambda: None)

        self.exchange.shutdown()
