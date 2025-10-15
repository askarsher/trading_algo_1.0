from collections import deque
from config import EXECUTION_DELAY_MINUTES, SLIPPAGE_PERCENT, TRANSACTION_FEES
from pricing import price_down_and_out_call, price_up_and_out_put

class MarketSimulator:
    """
    Simulates execution delay, slippage, and transaction costs.
    Orders are 'pending' for 10 minutes, before being checked again for signal correctness.
    """
    def __init__(self, strategy, portfolio):
        self.pending_signal_queue = deque()
        self.strategy = strategy
        self.portfolio = portfolio

    def submit_signal_for_check(self, signal):
        self.pending_signal_queue.append(signal)
        print(f"Signal received for {signal['signal']} {signal['symbol']}. Awaiting delay check in {EXECUTION_DELAY_MINUTES} min.")

    def process_pending_signal(self, current_tick, current_bar_series):
        if not self.pending_signal_queue:
            return None

        delay_seconds = EXECUTION_DELAY_MINUTES * 60

        # Check the first signal in the queue
        pending_signal = self.pending_signal_queue

        if current_tick["timestamp"] >= pending_signal["signal_timestamp"] + delay_seconds:
            # Time before checking the signal
            signal_to_check = self.pending_signal_queue.popleft()

            #Re-run the strategy with current market data
            checked_signal = self.strategy.on_bar(current_bar_series)

            if checked_signal and checked_signal["signal"] == signal_to_check["signal"]:
                print(f"Signal CHECKED for {signal_to_check['signal']} {signal_to_check['symbol']}. Proceeding to execution.")
                # Return the original signal object as it contains the correct parameters
                return signal_to_check
            else:
                print(f"Signal ABORTED for {signal_to_check['signal']} {signal_to_check['symbol']}. Conditions no longer met.")
                return None
                
        return None

    def execute_order(self, order, current_tick):
        # EXECUTION LOGIC
        # 1. Get the market price at the moment of execution
        execution_underlying_price = current_tick["price"]

        # 2. Handle CLOSE orders 
        if order["direction"] == "CLOSE":
            symbol = order['symbol']
            if symbol not in self.portfolio.positions:
                print(f"Execution Error: Attempted to close non-existent position for {symbol}")
                return None

            # Retrieve open positions details from portfolio
            position_to_close = self.portfolio.positions[symbol]['order_details']
            remaining_seconds = position_to_close['expiry_timestamp'] - current_tick['timestamp']
            if remaining_seconds <= 0:
                theoretical_price = 0 # Option expired
            else:
                T_years = remaining_seconds / (365 * 24 * 60 * 60)

                # Use the correct pricing function with current market data
                if position_to_close["type"] == "DOWN_AND_OUT_CALL":
                    theoretical_price = price_down_and_out_call(
                        execution_underlying_price, position_to_close["strike"], position_to_close["barrier"], T_years, position_to_close["volatility_at_order"]
                    )
                elif position_to_close["type"] == "UP_AND_OUT_PUT":
                    theoretical_price = price_up_and_out_put(
                        execution_underlying_price, position_to_close["strike"], position_to_close["barrier"], T_years, position_to_close["volatility_at_order"]
                    )
                else:
                    theoretical_price = 0

            final_price = theoretical_price * (1 - SLIPPAGE_PERCENT)
        else:
            # Re-price the option at the new underlying price
            T_years = (order['expiry_timestamp'] - current_tick['timestamp']) / (365 * 24 * 60 * 60) # Time in years
            
            if order["type"] == "DOWN_AND_OUT_CALL":
                theoretical_price = price_down_and_out_call(
                    execution_underlying_price, order["strike"], order["barrier"], T_years, order["volatility_at_order"]
                )
            elif order["type"] == "UP_AND_OUT_PUT":
                theoretical_price = price_up_and_out_put(
                    execution_underlying_price, order["strike"], order["barrier"], T_years, order["volatility_at_order"]
                )
            else:
                theoretical_price = 0 # Fallback for unknown types

            # Handle BUY orders
            if order["direction"] == "BUY":
                final_price = theoretical_price * (1 + SLIPPAGE_PERCENT)
            else: # SELL
                final_price = theoretical_price * (1 - SLIPPAGE_PERCENT)

        # 4. Calculate fees
        fees = sum(TRANSACTION_FEES.values())

        # 5. Create a final "fill" object
        fill = {
            "order": order,
            "fill_price": final_price,
            "fill_timestamp": current_tick["timestamp"],
            "underlying_price_at_fill": execution_underlying_price,
            "fees": fees
        }
        return fill
