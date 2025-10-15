import datetime
import random

# Import custom modules
from config import SYMBOLS, RISK_FREE_RATE
from feed import Feed
from portfolio import Portfolio
from pricing import price_vanilla_call
from strategy import MeanReversionStrategy
from execution import Executor
from market_conditions import MarketSimulator
from log import Logger
import analysis

class SimulatedClock:
    """
    Manages time passed in the backtest simulation
    """
    def __init__(self, start_date, tick_interval_seconds):
        self.current_time = start_date
        self.tick_interval = datetime.timedelta(seconds=tick_interval_seconds)

    def get_timestamp(self):
        """Returns the current simulated time as a Unix timestamp."""
        return self.current_time.timestamp()

    def advance(self):
        """Moves the clock forward by one tick interval."""
        self.current_time += self.tick_interval

# --- Mock API Client for Demonstration ---
class MockApiClient:
    """
    A mock API client to simulate fetching live tick data.
    """

    def __init__(self, clock):
        # Initialize each symbol with a base price of 100
        self.prices = {symbol: 100.0 for symbol in SYMBOLS}
        self.clock = clock

    def get_price(self, symbol):
        price = self.prices[symbol]
        # Apply small random fluctuation to simulate tick change
        price *= (1 + random.uniform(-0.001, 0.001))
        self.prices[symbol] = price
        return price

    def get_tick(self):
        symbol = SYMBOLS
        underlying_price = self.get_price(symbol)
        T_ref_years = 2 / 365.0
        sigma_ref = 0.2 # Assumed "true" volatility of ATM option
        reference_option_price = price_vanilla_call(underlying_price, underlying_price, T_ref_years, sigma_ref) * 1.02

        # Advance the clock
        timestamp = self.clock.get_timestamp()
        self.clock.advance()
        
        return {
            "symbol": symbol,
            "timestamp": timestamp,
            "price": underlying_price,
            "reference_option_price": reference_option_price,
            "reference_option_strike": underlying_price
        }


def main():
    """
    Main function to run the backtest.
    """
    print("Initializing trading system components...")

    # Backtest setup
    while True:
        date_str = input("--> Please enter the backtest start date (YYYY-MM-DD): ")
        try:
            # Parse the date part from the user's input
            parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            # Combine with a fixed start time (e.g., market open at 9:30 AM)
            start_date = parsed_date.replace(hour=9, minute=30, second=0)
            print(f"Backtest will start on: {start_date}")
            break  # Exit the loop if the date is valid
        except ValueError:
            print("--- Invalid date format. Please use YYYY-MM-DD. Try again. ---")

    sim_clock = SimulatedClock(start_date, TICK_INTERVAL)
    end_date = start_date + datetime.timedelta(days=15)
    
    # 1. Initialize all components
    api_client = MockApiClient(sim_clock)
    feed = Feed(api_client)
    portfolio = Portfolio(initial_capital=INITIAL_CAPITAL)
    strategy = MeanReversionStrategy()
    market_sim = MarketSimulator(strategy, portfolio)
    executor = Executor(market_sim, portfolio)
    logger = Logger()

    # 2. Main Backtest Loop
    while sim_clock.current_time < end_date:
        # A. Get the latest market data
        current_tick = api_client.get_tick()

        # B. Process the tick into bars (Feed yields completed bar series)
        for completed_bar_series in feed.process_tick(current_tick):
            if completed_bar_series:

                # C. New bar formed — check for a trading signal
                signal = strategy.on_bar(completed_bar_series)
                if signal:
                    # D. Send signal to be checked first
                    if "EXIT" in signal["signal"]:
                        fill = executor.process_signal(signal, current_tick)
                        if fill:
                            portfolio.update_on_fill(fill)
                            logger.log_trade_close(fill)
                    else:
                        market_sim.submit_signal_for_check(signal)

        # E. Check if any pending signals are ready to be checked
        current_bars = feed.bar_series.get(SYMBOLS)
        if current_bars:
            validated_signal = market_sim.process_pending_signal(checked_signal, current_tick)
            if validated_signal:
                # If signal is validated, process for execution
                fill = executor.process_signal(validated_signal, current_tick)
                if fill:
                    portfolio.update_on_fill(fill)
                    # Log the executed trade
                    if fill['order']['direction'] in:
                        logger.log_trade_open(fill)
                    elif fill['order']['direction'] == 'CLOSE':
                        logger.log_trade_close(fill)

        
    print("\nBacktest finished.")

    # 3. Run final performance analysis
    analysis.run_analysis(portfolio, logger.log_file_path)


if __name__ == "__main__":
    main()
