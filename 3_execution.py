from pricing import price_down_and_out_call, price_up_and_out_put, get_implied_vol
from config import TRANSACTION_FEES

class Executor:
    """
    Receives a signal, prices the required option, and creates a trade order.
    """
    def __init__(self, market_simulator, portfolio):
        self.simulator = market_simulator
        self.portfolio = portfolio

    def process_signal(self, signal, current_tick):
        """
        Processes a signal from the strategy, calculates IV, and sends an order to the simulator.
        """
        if signal["signal"] in:
            T_days = signal["expiry_days"]
            underlying_price = current_tick["price"]
            reference_option_price = current_tick["reference_option_price"]
            reference_strike = current_tick["reference_option_strike"]

            # Using a call option to find IV
            implied_vol = get_implied_vol(reference_option_price, underlying_price, reference_strike, T_days, 'c')

            # Estimating the cost of the trade
            T_years = T_days / 365.0
            if signal["option_type"] == "DOWN_AND_OUT_CALL":
                estimated_price = price_down_and_out_call(
                    underlying_price, signal["strike_price"], signal["barrier_price"], T_years, implied_vol
                )
            else: # UP_AND_OUT_PUT
                estimated_price = price_up_and_out_put(
                    underlying_price, signal["strike_price"], signal["barrier_price"], T_years, implied_vol
                )
            
            estimated_cost = estimated_price + sum(TRANSACTION_FEES.values())

            # Check if portfolio allows the transaction
            if not self.portfolio.can_transact(estimated_cost):
                print(f"Order REJECTED: Insufficient funds for {signal['signal']} {signal['symbol']}. Required: ${estimated_cost:.2f}, Available: ${self.portfolio.cash:,.2f}")
                return None # Abort processing

            # Convert expiry from days to seconds
            expiry_seconds = signal["expiry_days"] * 24 * 60 * 60
            
            # Create a detailed order object to send for execution
            order = {
                "symbol": signal["symbol"],
                "type": signal["option_type"],
                "direction": signal["signal"],
                "strike": signal["strike_price"],
                "barrier": signal["barrier_price"],
                "expiry_timestamp": current_tick["timestamp"] + expiry_seconds,
                "volatility_at_order": implied_vol,
                "submission_timestamp": signal["signal_timestamp"]
            }
            # Send the order to be queued and delayed
            print(f"Order Submitted: {order['direction']} {order['symbol']}")
            return self.simulator.execute_order(order, current_tick)

        elif signal["signal"] in:
            # Create an order to close the current position
            close_order = {
                "direction": "CLOSE", 
                "symbol": signal["symbol"],
                "submission_timestamp": current_tick["timestamp"]
            }
            print(f"Close Order Submitted for {signal['symbol']}")
            return self.simulator.execute_order(close_order, current_tick)

        return None
