def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers and store in history."""
        result = calculate_sum(a, b)
        self.history.append(f"Added {a} + {b} = {result}")
        return result
