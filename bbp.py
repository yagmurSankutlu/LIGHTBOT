import decimal
from decimal import Decimal
from typing import List

def bbp_digit(n: int) -> str:
    """
    Calculate the nth hexadecimal digit of π using the BBP formula.
    
    The BBP formula states that:
    π = sum(1/16^k * (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6)) for k from 0 to ∞)
    """
    # Set precision to handle the calculation
    decimal.getcontext().prec = 1000
    
    def series_term(k: int, n: int) -> Decimal:
        """Calculate one term of the series for the nth digit."""
        dk = Decimal(k)
        sixteen_pow = Decimal(16) ** (dk - n)
        return sixteen_pow * (
            Decimal(4) / (Decimal(8) * dk + 1) -
            Decimal(2) / (Decimal(8) * dk + 4) -
            Decimal(1) / (Decimal(8) * dk + 5) -
            Decimal(1) / (Decimal(8) * dk + 6)
        )
    
    # Sum the series
    total = sum(series_term(k, n) for k in range(n + 1))
    
    # Extract fractional part
    frac = total - int(total)
    # Convert to hexadecimal
    hex_digit = hex(int(frac * 16))[2:].upper()
    return hex_digit

def compute_pi_hex_digits(num_digits: int) -> str:
    """
    Compute the first num_digits hexadecimal digits of π.
    """
    digits = []
    for i in range(num_digits):
        digits.append(bbp_digit(i))
    return ''.join(digits)

# Example usage to compute first 100 digits (as 16000 would take very long)
if __name__ == "__main__":
    num_digits = 100
    pi_hex = compute_pi_hex_digits(num_digits)
    
    # Save to file
    with open("pi_hex_digits.txt", "w") as file:
        file.write(pi_hex)
    
    print(f"First {num_digits} hexadecimal digits of π:")
    print(pi_hex)