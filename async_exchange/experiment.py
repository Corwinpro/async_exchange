import asyncio
import logging
from signal import SIGTERM, SIGINT

from async_exchange.exchange import Exchange

default_logger = logging.getLogger(__name__)


class Experiment:
    def __init__(self, traders, exchange=None, logger=None):
        self.traders = traders

        if logger is None:
            self.logger = default_logger

        if exchange is not None:
            self.exchange = exchange
        else:
            self.exchange = Exchange(logger=logger)

        for trader in self.traders:
            self.exchange.register_trader(trader)

    def run(self):
        asyncio.run(self._runnable())

    async def _runnable(self):
        loop = asyncio.get_running_loop()
        for signal in (SIGTERM, SIGINT):
            loop.add_signal_handler(signal, self.shutdown, signal)

        tasks = [trader.cycle() for trader in self.traders]
        group = asyncio.gather(*tasks, return_exceptions=False)
        try:
            await group
        except asyncio.CancelledError:
            default_logger.info("Experiment cancelled.")

    def shutdown(self, signal):
        loop = asyncio.get_running_loop()
        for task in asyncio.all_tasks(loop=loop):
            task.cancel()

        default_logger.info(f"Got signal: {signal!s}, shutting down.")
        loop.remove_signal_handler(SIGTERM)
        loop.add_signal_handler(SIGINT, lambda: None)

        self.exchange.shutdown()
