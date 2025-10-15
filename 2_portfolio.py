class Portfolio:
    """
    # The single class for the account's financial status.
    """
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # symbol -> position_details
        print(f"Portfolio initialized with starting capital: ${initial_capital:,.2f}")

    def can_transact(self, estimated_cost):
        """
        Checks if there is sufficient cash to cover the estimated cost of a trade.
        """
        return self.cash >= estimated_cost

    def update_on_fill(self, fill):
        """
        Updates cash and positions based on a trade execution (fill) object.
        """
        order = fill['order']
        symbol = order['symbol']
        
        if order['direction'] in: # Opening a position
            cost = fill['fill_price'] + fill['fees']
            self.cash -= cost
            self.positions[symbol] = {
                "entry_price": fill['fill_price'],
                "order_details": order # Store all details for re-pricing on exit
            }
            print(f"Portfolio Update: OPEN {symbol}. Cost: ${cost:.2f}. Remaining Cash: ${self.cash:,.2f}")

        elif order['direction'] == 'CLOSE': # Closing a position
            if symbol not in self.positions:
                print(f"Portfolio Warning: Received CLOSE for {symbol} but no position was found.")
                return
            
            proceeds = fill['fill_price'] - fill['fees']
            self.cash += proceeds
            del self.positions[symbol]
            print(f"Portfolio Update: CLOSE {symbol}. Proceeds: ${proceeds:.2f}. Remaining Cash: ${self.cash:,.2f}")
