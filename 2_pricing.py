import math
import py_vollib.black_scholes.implied_volatility as iv
from config import RISK_FREE_RATE

def norm_cdf(x):
    """Normal CDF using math.erf"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def get_implied_vol(option_market_price, S, K, T, flag):
    """Calculates the implied volatility. Flag is 'c' for call and 'p' for put"""
    try:
        T_year = T / 365.0
        r = RISK_FREE_RATE
        implied_vol = iv.implied_volatility(option_market_price, S, K, T_year, r, flag)
        return implied_vol
    except Exception:
        return 0.20

#Will be utilizing Black-Scholes model and standard pricing parameters, where
# S - current price of the underlying 
# K - strike price
# B - barrier price
# T - time to expiration 
# sigma - volatility of the underlying (std dev of log returns)
def price_vanilla_call(S, K, T, sigma):
    """Prices a standard European call option using Black-Scholes."""
    if T <= 0:
        return max(0, S - K)
    r = RISK_FREE_RATE
    #standard solutions of the Black-Scholes model for a non-dividend paying asset 
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    return price

def price_vanilla_put(S, K, T, sigma):
    """Prices a standard European put option using Black-Scholes."""
    if T <= 0:
        return max(0, K - S)
    r = RISK_FREE_RATE
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    return price

def price_down_and_out_call(S, K, B, T, sigma):
    """Prices a standard Barrier down-and-out call option."""
    if B >= S:
        return 0  # Knocked out
    r = RISK_FREE_RATE
    vanilla_price = price_vanilla_call(S, K, T, sigma)
    #Reflection term make use of the in-out parity, s.t. Down-and-Out Call = Vanilla Call - Down-and-In Call
    #i.e. reflection_term = Down-and-In call implicitly defined, since we aren't making trading with Down-and-In calls
    reflection_term = (S / B) ** (1 - (2 * r / sigma**2)) * price_vanilla_call((B**2) / S, K, T, sigma)
    return vanilla_price - reflection_term

def price_up_and_out_put(S, K, B, T, sigma):
    """Prices a standard Barrier up-and-out put option."""
    if S >= B:
        return 0 # Knocked out
    r = RISK_FREE_RATE
    vanilla_price = price_vanilla_put(S, K, T, sigma)
    lam = (r + 0.5 * sigma**2) / (sigma**2)
    x1 = (math.log(B**2 / (S * K)) + lam * sigma**2 * T) / (sigma * math.sqrt(T))
    #Similar rationale for using the reflection_term as above
    reflection_term = (K * math.exp(-r * T) * (B / S)**(2 * lam - 2) * norm_cdf(-x1 * sigma * math.sqrt(T)) - S * (B / S)**(2 * lam) * norm_cdf(-x1))
    return vanilla_price - reflection_term
