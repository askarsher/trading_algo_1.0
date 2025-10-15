import numpy as np
from config import LOOKBACK_PERIOD, STD_DEV_MULTIPLIER, OPTION_EXPIRY_DAYS

class MeanReversionStrategy:
    """
    Generates trading signals based on Bollinger Band re-crossing.
    
    - Buy Signal: Price crosses from below the lower band back inside.
    - Sell Signal: Price crosses from above the upper band back inside.
    - Exit Signal: Price crosses the moving average.
    """

    def on_bar(self, bar_series_deque):
        """
        Analyzes a series of bars and returns a signal object if conditions are met.
        """
        # Ensure we have enough data: lookback + one previous bar
        if len(bar_series_deque) < LOOKBACK_PERIOD + 1:
            return None

        # Convert to numpy array for calculation
        close_prices = np.array([bar['close'] for bar in bar_series_deque])

        # Calculate indicators using data prior to the latest bar
        previous_closes = close_prices[:-1]
        mean = np.mean(previous_closes)
        std = np.std(previous_closes)

        upper_band = mean + STD_DEV_MULTIPLIER * std
        lower_band = mean - STD_DEV_MULTIPLIER * std

        current_bar = bar_series_deque[-1]
        previous_bar = bar_series_deque[-2]

        # --- Entry Signals ---

        # Buy Signal: Oversold Reversal
        if previous_bar['close'] < lower_band and current_bar['close'] > lower_band:
            return self._generate_signal_details(current_bar, "BUY", mean, lower_band)

        # Sell Signal: Overbought Reversal
        if previous_bar['close'] > upper_band and current_bar['close'] < upper_band:
            return self._generate_signal_details(current_bar, "SELL", mean, upper_band)

        # --- Exit Signals ---

        # Exit Long: Price reverted to mean from below
        if previous_bar['close'] <= mean and current_bar['close'] > mean:
            return {"signal": "EXIT_LONG", "symbol": current_bar["symbol"]}

        # Exit Short: Price reverted to mean from above
        if previous_bar['close'] >= mean and current_bar['close'] < mean:
            return {"signal": "EXIT_SHORT", "symbol": current_bar["symbol"]}

        return None

    def _generate_signal_details(self, current_bar, signal_type, sma, band):
        """
        Creates a detailed signal object with option parameters.
        """
        if signal_type == "BUY":
            return {
                "signal": "BUY",
                "symbol": current_bar["symbol"],
                "option_type": "DOWN_AND_OUT_CALL",
                "strike_price": sma,
                "barrier_price": band,  # Set barrier at the band that was crossed
                "expiry_days": OPTION_EXPIRY_DAYS,
                "signal_price": current_bar["close"],
                "signal_timestamp": current_bar["timestamp"]
            }

        elif signal_type == "SELL":
            return {
                "signal": "SELL",
                "symbol": current_bar["symbol"],
                "option_type": "UP_AND_OUT_PUT",
                "strike_price": sma,
                "barrier_price": band,
                "expiry_days": OPTION_EXPIRY_DAYS,
                "signal_price": current_bar["close"],
                "signal_timestamp": current_bar["timestamp"]
            }

        # In case of unexpected signal_type
        return None
