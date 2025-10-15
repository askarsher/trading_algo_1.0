import time
from collections import deque
from config import SYMBOLS, BAR_INTERVAL_MINUTES

class Feed:
    """
    Handles fetching market data and aggregating ticks into time bars.
    """
    def __init__(self, api_client):
        self.api = api_client
        self.current_bar = {} # symbol -> bar data
        self.bar_series = {} # symbol -> deque of completed bars

    def process_tick(self, tick):
        """
        Processes a single tick, updates the current bar, and yields a
        completed bar when the interval is complete.
        """
        symbol = tick["symbol"]
        price = tick["price"]
        timestamp = tick["timestamp"]

        bar_interval_seconds = BAR_INTERVAL_MINUTES * 60
        bar_timestamp = int(timestamp / bar_interval_seconds) * bar_interval_seconds

        # Initialize bar series for new symbol
        if symbol not in self.bar_series:
            self.bar_series[symbol] = deque(maxlen=200) # Store last 200 bars
            self.current_bar[symbol] = {}

        # If a new bar interval has started
        if self.current_bar[symbol].get("timestamp")!= bar_timestamp:
            # Add the previously completed bar to the series
            if self.current_bar[symbol]:
                self.bar_series[symbol].append(self.current_bar[symbol])
                # Yield the completed bar for the strategy to process
                yield self.bar_series[symbol]

            # Start a new bar
            self.current_bar[symbol] = {
                "timestamp": bar_timestamp,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "symbol": symbol
            }
        else:
            # Update the current bar
            self.current_bar[symbol]["high"] = max(self.current_bar[symbol]["high"], price)
            self.current_bar[symbol]["low"] = min(self.current_bar[symbol]["low"], price)
            self.current_bar[symbol]["close"] = price
            yield None # No new bar completed
