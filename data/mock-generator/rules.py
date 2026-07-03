"""
Rules Module
Adheres to SRP.
Isolates complex business rules away from the data generation flow.
"""
import random

class NationalCodeGenerator:
    """
    Encapsulates the specific business rule for National Codes:
    - Must be exactly 10 digits.
    - No more than two consecutive identical digits.
    """
    @staticmethod
    def generate() -> str:
        code = ""
        for i in range(10):
            while True:
                next_digit = str(random.randint(0, 9))
                # Rule: Check if the last two digits are the same as the new one
                if len(code) >= 2 and code[-1] == next_digit and code[-2] == next_digit:
                    continue # Reject and generate a different digit
                
                code += next_digit
                break
        return code
